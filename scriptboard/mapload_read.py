# 2018-06-02

import osgeo
import osgeo.ogr as ogr
import osgeo.osr as osr

MAPPATH = "C:/Users/peter/Documents/TempDocs/Files/Upperdandy/Suburbs_UTM.shp"

driver = ogr.GetDriverByName('ESRI Shapefile')  # Create the Shapefile driver
print "Driver: ", type(driver)
datasource = driver.Open(MAPPATH)
print "DataSource: ", type(datasource)
if datasource is None:
    print "Could not open shapefile!"
    # return None     # Return none if there is no map

layer = datasource.GetLayer(0)  # Get the first layer, which should be the only layer!
print "Layer: ", type(layer)
xmin, xmax, ymin, ymax = layer.GetExtent()
print xmin, xmax, ymin, ymax

spatialref = layer.GetSpatialRef()
inputprojcs = spatialref.GetAttrValue("PROJCS")
if inputprojcs is None:
    print "Warning, spatial reference epsg cannot be found"

featurecount = layer.GetFeatureCount()
print "Total feature", featurecount

for i in range(featurecount):
    feature = layer.GetFeature(i)

    # GET ATTRIBUTES
    layerDefinition = layer.GetLayerDefn()
    attribute_count = layerDefinition.GetFieldCount()
    attnames = []
    for att in range(attribute_count):
        fieldName = layerDefinition.GetFieldDefn(att).GetName()
        fieldTypeCode = layerDefinition.GetFieldDefn(att).GetType()
        fieldType = layerDefinition.GetFieldDefn(att).GetFieldTypeName(fieldTypeCode)
        fieldValue = feature.GetFieldAsString(fieldName)
        attnames.append((fieldName, fieldTypeCode, fieldType, fieldValue))
    print attnames
    print "Feature: ", type(feature)

    geom = feature.GetGeometryRef()     # GET GEOMETRY
    print "Geom: ", type(geom)

    area = geom.GetArea() / 1000000.0
    print "Area", area

    #Projection

    print geom.GetGeometryType()
    geometrycount = geom.GetGeometryCount()
    if geom.GetGeometryName() == 'MULTIPOLYGON':
        for g in geom:
            print g.GetGeometryCount()
            ring = g.GetGeometryRef(0)
            print "Ring: ", type(ring)
            points = ring.GetPointCount()
            print "Ring Points: ", points
            coordinates = []
            for j in range(points):
                coordinates.append((ring.GetX(j), ring.GetY(j)))

            print coordinates
    else:
        ring = geom.GetGeometryRef(0)
        print "Ring: ", type(ring)

        if ring.GetGeometryType() == -2147483645:   # POLYGON25D
            ring.FlattenTo2D()
            ring = ring.GetGeometryRef(0)

        points = ring.GetPointCount()
        print "Ring Points: ", points
        coordinates = []
        for j in range(points):
            coordinates.append((ring.GetX(j), ring.GetY(j)))

        print coordinates