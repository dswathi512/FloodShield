#!/usr/bin/env python3
"""
GeoShield quantitative validation: predicted flood map vs reference flood mask.

Usage (Windows, from the outputs folder):
    python validate_geoshield.py
    python validate_geoshield.py --ref reference_flood_mask_aligned.tif --pred geoshield_prediction_nodata_fixed.tif

Requires: rasterio, numpy
"""
import argparse, json, math, sys
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.windows import Window

TOL_PX = 1e-3  # tolerance (in pixels) for "grid-aligned"


def describe(path):
    with rasterio.open(path) as s:
        a = s.read(1)
        info = dict(
            path=str(path), width=s.width, height=s.height, count=s.count,
            dtype=s.dtypes[0], crs=str(s.crs), nodata=s.nodata,
            mask_flags=[str(f) for f in s.mask_flag_enums[0]],
            res=s.res, bounds=tuple(s.bounds), transform=s.transform,
        )
        u, c = np.unique(a, return_counts=True)
        info["unique"] = {float(k): int(v) for k, v in zip(u, c)}
    return info


def read_valid(src, band=1):
    """Return (data, valid_mask). Valid = not NoData per metadata AND GDAL mask band,
    AND not NaN. NoData is never treated as class 0."""
    a = src.read(band)
    valid = src.read_masks(band) > 0           # GDAL mask band (covers nodata / alpha / internal mask)
    if src.nodata is not None:
        valid &= ~np.isclose(a.astype("float64"), src.nodata) if not np.isnan(src.nodata) else ~np.isnan(a)
    valid &= ~np.isnan(a.astype("float64"))
    return a, valid


def align_prediction_to_reference(ref_src, pred_src):
    """Return (pred_array, pred_valid) on the reference grid, plus a note on method."""
    p, pv = read_valid(pred_src)
    rt, pt = ref_src.transform, pred_src.transform
    same_res = (math.isclose(rt.a, pt.a, rel_tol=1e-9) and math.isclose(rt.e, pt.e, rel_tol=1e-9))
    same_crs = ref_src.crs == pred_src.crs
    col_off = (rt.c - pt.c) / pt.a      # reference origin expressed in prediction pixel units
    row_off = (rt.f - pt.f) / pt.e
    int_offset = (abs(col_off - round(col_off)) < TOL_PX and abs(row_off - round(row_off)) < TOL_PX)

    H, W = ref_src.height, ref_src.width
    out = np.zeros((H, W), dtype=p.dtype)
    out_valid = np.zeros((H, W), dtype=bool)

    if same_crs and same_res and int_offset:
        co, ro = int(round(col_off)), int(round(row_off))
        # overlap of reference window with prediction raster, in prediction pixel coords
        c0, r0 = max(co, 0), max(ro, 0)
        c1, r1 = min(co + W, pred_src.width), min(ro + H, pred_src.height)
        if c1 > c0 and r1 > r0:
            out[r0 - ro:r1 - ro, c0 - co:c1 - co] = p[r0:r1, c0:c1]
            out_valid[r0 - ro:r1 - ro, c0 - co:c1 - co] = pv[r0:r1, c0:c1]
        note = (f"Exact integer pixel offset (col={co}, row={ro}); prediction sliced onto the "
                f"reference grid. NO resampling, so classes are untouched.")
    else:
        # Fall back to nearest-neighbour resampling (preserves binary classes)
        reproject(p, out, src_transform=pt, src_crs=pred_src.crs,
                  dst_transform=rt, dst_crs=ref_src.crs, resampling=Resampling.nearest)
        vv = np.zeros((H, W), dtype="uint8")
        reproject(pv.astype("uint8"), vv, src_transform=pt, src_crs=pred_src.crs,
                  dst_transform=rt, dst_crs=ref_src.crs, resampling=Resampling.nearest)
        out_valid = vv > 0
        note = "Grids not on a common pixel lattice; prediction resampled with nearest neighbour."
    return out, out_valid, note, (col_off, row_off)


def pixel_areas_km2(transform, height, width):
    """Per-row ellipsoid-aware (authalic sphere) area of a lon/lat cell, km^2. Not square degrees."""
    R = 6371.0072  # authalic radius of WGS84, km
    dlon = math.radians(abs(transform.a))
    lat_top = transform.f + np.arange(height) * transform.e
    lat_bot = lat_top + transform.e
    la1, la2 = np.radians(lat_top), np.radians(lat_bot)
    return R ** 2 * dlon * np.abs(np.sin(la1) - np.sin(la2))   # shape (height,)


def safe_div(n, d):
    return float("nan") if d == 0 else n / d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="reference_flood_mask_aligned.tif")
    ap.add_argument("--pred", default="geoshield_prediction_nodata_fixed.tif")
    ap.add_argument("--json", default="geoshield_validation_results.json")
    args = ap.parse_args()

    print("=== 1. RASTER INTEGRITY ===")
    for name, path in (("REFERENCE", args.ref), ("PREDICTION", args.pred)):
        d = describe(path)
        print(f"\n[{name}] {d['path']}")
        print(f"  size {d['width']} x {d['height']}  ({d['width']*d['height']:,} px)  bands={d['count']}  dtype={d['dtype']}")
        print(f"  CRS {d['crs']}   pixel size {d['res']}")
        print(f"  bounds {d['bounds']}")
        print(f"  nodata metadata: {d['nodata']}   GDAL mask flags: {d['mask_flags']}")
        print(f"  raw unique values: {d['unique']}")

    with rasterio.open(args.ref) as rs, rasterio.open(args.pred) as ps:
        if rs.crs != ps.crs:
            print("WARNING: CRS differ", rs.crs, ps.crs)
        ref, ref_valid = read_valid(rs)
        pred, pred_valid, note, offs = align_prediction_to_reference(rs, ps)
        grids_identical = (rs.width, rs.height, rs.transform) == (ps.width, ps.height, ps.transform)
        print(f"\nGrids identical: {grids_identical}")
        print(f"Prediction origin relative to reference origin (pixels): col={offs[0]:.4f}, row={offs[1]:.4f}")
        print("Alignment:", note)

        # Pixel-area weights (km^2) per row on the reference grid
        row_area = pixel_areas_km2(rs.transform, rs.height, rs.width)

    total_ref_px = ref.size
    ref_is_class = ref_valid & np.isin(ref, (0, 1))
    pred_is_class = pred_valid & np.isin(pred, (0, 1))
    non_binary_ref = int((ref_valid & ~np.isin(ref, (0, 1))).sum())
    non_binary_pred = int((pred_valid & ~np.isin(pred, (0, 1))).sum())
    cmp_mask = ref_is_class & pred_is_class
    n_valid = int(cmp_mask.sum())
    n_excluded = int(total_ref_px - n_valid)

    r = ref[cmp_mask].astype(np.uint8)
    p = pred[cmp_mask].astype(np.uint8)
    TP = int(((r == 1) & (p == 1)).sum())
    FP = int(((r == 0) & (p == 1)).sum())
    FN = int(((r == 1) & (p == 0)).sum())
    TN = int(((r == 0) & (p == 0)).sum())

    ref_flood = int((r == 1).sum()); ref_non = int((r == 0).sum())
    pred_flood = int((p == 1).sum()); pred_non = int((p == 0).sum())

    print("\n=== 2. COMPARISON AREA ===")
    print(f"Reference grid pixels:              {total_ref_px:,}")
    print(f"Valid reference pixels:             {int(ref_valid.sum()):,}   (non-class values: {non_binary_ref})")
    print(f"Prediction pixels covering ref grid:{int(pred_valid.sum()):,}   (non-class values: {non_binary_pred})")
    print(f"Valid comparison pixels:            {n_valid:,}")
    print(f"Excluded pixels:                    {n_excluded:,}")
    print(f"Reference flood / non-flood:        {ref_flood:,} / {ref_non:,}")
    print(f"Predicted flood / non-flood:        {pred_flood:,} / {pred_non:,}")

    print("\n=== 3. CONFUSION MATRIX ===")
    print(f"TP={TP:,}  FP={FP:,}  FN={FN:,}  TN={TN:,}")
    print("                 Pred 1        Pred 0")
    print(f"  Ref 1     {TP:>10,}    {FN:>10,}")
    print(f"  Ref 0     {FP:>10,}    {TN:>10,}")

    checks = [
        ("TP + FN = valid reference flood px", TP + FN, ref_flood),
        ("FP + TN = valid reference non-flood px", FP + TN, ref_non),
        ("TP + FP = predicted flood px", TP + FP, pred_flood),
        ("TN + FN = predicted non-flood px", TN + FN, pred_non),
        ("TP+FP+FN+TN = valid comparison px", TP + FP + FN + TN, n_valid),
    ]
    print("\n=== 4. CONSISTENCY CHECKS ===")
    all_ok = True
    for label, lhs, rhs in checks:
        ok = lhs == rhs; all_ok &= ok
        print(f"  {'PASS' if ok else 'FAIL'}  {label}: {lhs:,} vs {rhs:,}")
    if not all_ok:
        print("Consistency check FAILED - metrics not reliable."); sys.exit(1)

    precision = safe_div(TP, TP + FP)
    recall = safe_div(TP, TP + FN)
    f1 = safe_div(2 * TP, 2 * TP + FP + FN)
    iou = safe_div(TP, TP + FP + FN)
    acc = safe_div(TP + TN, n_valid)
    spec = safe_div(TN, TN + FP)
    kappa = float("nan")
    if n_valid:
        pe = ((TP + FP) * (TP + FN) + (TN + FN) * (TN + FP)) / n_valid ** 2
        kappa = safe_div(acc - pe, 1 - pe)
    fmt = lambda x: "undefined (zero denominator)" if math.isnan(x) else f"{100*x:.2f}%"

    print("\n=== 5. METRICS ===")
    for k, v in (("Precision", precision), ("Recall", recall), ("F1-score", f1),
                 ("IoU", iou), ("Overall accuracy", acc), ("Specificity", spec)):
        print(f"  {k:<18}{fmt(v)}")
    print(f"  {'Cohen kappa':<18}{kappa:.4f}" if not math.isnan(kappa) else "  Cohen kappa       undefined")

    # Areas (geodesically sensible; NOT square degrees)
    rows = np.where(cmp_mask)[0]
    pf = (pred == 1) & cmp_mask; rf = (ref == 1) & cmp_mask
    area_pred = float((row_area[:, None] * pf).sum())
    area_ref = float((row_area[:, None] * rf).sum())
    area_tp = float((row_area[:, None] * (pf & rf)).sum())
    print("\n=== 6. FLOOD AREA (authalic-sphere cell areas, km^2) ===")
    print(f"  Reference flood: {area_ref:,.2f} km2   Predicted flood: {area_pred:,.2f} km2   Overlap (TP): {area_tp:,.2f} km2")
    print(f"  Predicted/Reference area ratio: {safe_div(area_pred, area_ref):.4f}")

    out = dict(TP=TP, FP=FP, FN=FN, TN=TN, valid_pixels=n_valid, excluded_pixels=n_excluded,
               reference_flood=ref_flood, predicted_flood=pred_flood,
               precision=precision, recall=recall, f1=f1, iou=iou, accuracy=acc,
               specificity=spec, kappa=kappa, area_ref_km2=area_ref, area_pred_km2=area_pred,
               area_tp_km2=area_tp, checks_all_pass=all_ok)
    with open(args.json, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved {args.json}")


if __name__ == "__main__":
    main()