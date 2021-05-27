import arcpy, os
arcpy.env.overwriteOutput = True

aprx = arcpy.mp.ArcGISProject(
    r"C:\LPA\Projects\MGAZonesProject\MGAZonesProject.aprx")

map12 = aprx.listMaps("Map12")[0]
map13 = aprx.listMaps("Map13")[0]
map14 = aprx.listMaps("Map14")[0]

placesLayer = map12.listLayers("Arizona Populated Places")[0]

lyt = aprx.listLayouts()[0]

mapFrame12 = lyt.listElements('MAPFRAME_ELEMENT', "Map Frame 12")[0]
mapFrame13 = lyt.listElements('MAPFRAME_ELEMENT', "Map Frame 13")[0]
mapFrame14 = lyt.listElements('MAPFRAME_ELEMENT', "Map Frame 14")[0]

srText12 = lyt.listElements('TEXT_ELEMENT',"Spatial Reference Text 12")[0]
srText13 = lyt.listElements('TEXT_ELEMENT',"Spatial Reference Text 13")[0]
srText14 = lyt.listElements('TEXT_ELEMENT',"Spatial Reference Text 14")[0]

#create pdf document object
finalPDF = r"C:\LPA\PDFs\UTMZones.pdf"
if arcpy.Exists(finalPDF):
    arcpy.Delete_management(finalPDF)
pdfDoc = arcpy.mp.PDFDocumentCreate(finalPDF)

placesSortedByNameList = sorted(
    [row[0] for row in arcpy.da.SearchCursor(
    placesLayer, "NAME")])
    
#create a dictionary of X, Y coordinates for each place
placesCoordsDict = {row[0]:row[1] for row in arcpy.da.SearchCursor(
    placesLayer, ["NAME","SHAPE@XY"])}

#create a spatial reference layer object for the places layer which will be
#the geographic coordinate system of the source feature class
srPlacesLayer = arcpy.Describe(placesLayer).spatialReference

#write a PDF page for each place in the sorted list.
#Use slice notation to only print the first 10 pages in the list

for pageCount, placeName in enumerate(placesSortedByNameList[:10]):
    xCoord, yCoord = placesCoordsDict[placeName]
    utmZone = 1 + int((xCoord + 180)/6)
    print("{0} is in zone {1}".format(placeName, utmZone))
    srUTM = arcpy.SpatialReference("NAD83(HARN) / Arizona West {0}".format(utmZone))

    geogFC = r"{0}\geogFC".format(aprx.defaultGeodatabase)
    projFC = r"{0}\projFC".format(aprx.defaultGeodatabase)

    arcpy.CreateFishnet_management(geogFC,
                                   "{0} {1}".format(xCoord - 0.25, yCoord - 0.25),
                                   "{0} {1}".format(xCoord - 0.25, yCoord + 0.25),
                                   0.5, 0.5, 1, 1,
                                   geometry_type = "POLYGON", labels = "NO_LABELS")
    arcpy.DefineProjection_management(geogFC, srPlacesLayer)
    arcpy.Project_management(geogFC,projFC,srUTM)
    projFCExtent = arcpy.Describe(projFC).extent
    
    if utmZone == 12:
        mapFrame12.visible = True
        mapFrame12.camera.setExtent(projFCExtent)
        mapFrame12.camera.scale = mapFrame12.camera.scale * 1.05
        mapFrame13.visible = False
        mapFrame14.visible = False
        srText12.visible = True
        srText13.visible = False
        srText14.visible = False
    elif utmZone == 13:
        mapFrame12.visible = False
        mapFrame13.visible = True
        mapFrame13.camera.setExtent(projFCExtent)
        mapFrame13.camera.scale = mapFrame13.camera.scale * 1.05
        mapFrame14.visible = False
        srText12.visible = False
        srText13.visible = True
        srText14.visible = False
    elif utmZone == 14:
        mapFrame12.visible = False
        mapFrame13.visible = False
        mapFrame14.visible = True
        mapFrame14.camera.setExtent(projFCExtent)
        mapFrame14.camera.scale = mapFrame14.camera.scale * 1.05
        srText12.visible = False
        srText13.visible = False
        srText14.visible = True
    else:
        print("Unexpected zone number of {0} encountered".format(utmZone))

    # Title text object
    titleText = lyt.listElements('TEXT_ELEMENT',"Title")[0]
    titleText.text = placeName

    # Export PDF for this country's page
    lyt.exportToPDF(r"C:\LPA\PDFs\test{0}.pdf".format(pageCount))
    pdfDoc.appendPages(r"C:\LPA\PDFs\test{0}.pdf".format(pageCount))

pdfDoc.savAndClose()
del pdfDoc
os.startfile(finalPDF)

del aprx
