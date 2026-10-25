
import ee
import config as c

ee.Initialize(project=c.PROJECT_ID)


def get_before_after_image():
    aoi = ee.Geometry.Rectangle(c.AOI_CORDS)

    collection = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(aoi)
        .filter(ee.Filter.eq("instrumentMode", "IW"))
        .filter(
            ee.Filter.listContains(
                "transmitterReceiverPolarisation", "VH"
            )
        )
        .select("VH")
    )

    before_collection = collection.filterDate(
        c.BEFORE_START, c.BEFORE_END
    )

    after_collection = collection.filterDate(
        c.AFTER_START, c.AFTER_END
    )

    before_count = before_collection.size().getInfo()
    after_count = after_collection.size().getInfo()

    if before_count == 0 or after_count == 0:
        raise ValueError(
            f"No images found — before: {before_count}, "
            f"after: {after_count}"
        )

    print(f"Before images: {before_count}")
    print(f"After images: {after_count}")

    # Find matching pass direction and relative orbit.
    before_info = before_collection.aggregate_array(
        "orbitProperties_pass"
    ).getInfo()
    before_orbits = before_collection.aggregate_array(
        "relativeOrbitNumber_start"
    ).getInfo()

    after_info = after_collection.aggregate_array(
        "orbitProperties_pass"
    ).getInfo()
    after_orbits = after_collection.aggregate_array(
        "relativeOrbitNumber_start"
    ).getInfo()

    before_pairs = set(zip(before_info, before_orbits))
    after_pairs = set(zip(after_info, after_orbits))
    common_pairs = before_pairs & after_pairs

    if not common_pairs:
        raise ValueError(
            "No matching Sentinel-1 pass/orbit found. "
            "Adjust the before/after date ranges."
        )

    orbit_pass, relative_orbit = sorted(common_pairs)[0]

    print(f"Selected pass: {orbit_pass}")
    print(f"Selected relative orbit: {relative_orbit}")

    before_collection = (
        before_collection
        .filter(ee.Filter.eq("orbitProperties_pass", orbit_pass))
        .filter(
            ee.Filter.eq(
                "relativeOrbitNumber_start", relative_orbit
            )
        )
    )

    after_collection = (
        after_collection
        .filter(ee.Filter.eq("orbitProperties_pass", orbit_pass))
        .filter(
            ee.Filter.eq(
                "relativeOrbitNumber_start", relative_orbit
            )
        )
    )

    before_image = (
        before_collection.median()
        .focal_mean(radius=50, units="meters")
        .clip(aoi)
    )

    after_image = (
        after_collection.median()
        .focal_mean(radius=50, units="meters")
        .clip(aoi)
    )

    print("Before bands:", before_image.bandNames().getInfo())
    print("After bands:", after_image.bandNames().getInfo())

    return before_image, after_image


if __name__ == "__main__":
    before, after = get_before_after_image()
    print("Image preparation completed.")
