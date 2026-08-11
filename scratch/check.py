"""import ee
ee.Authenticate(auth_mode='notebook')"""
import ee
ee.Initialize(project='floodshield-504714')
print(ee.Number(1).add(1).getInfo())