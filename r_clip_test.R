totalarea = 'K:/ACCS_Work/Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/test/totalarea.shp'
grid = 'K:/ACCS_Work/Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/test/totalarea.shp'

library(rgdal)
library(sp)
library(buffer)
library(stringr)
library(rgeos)

totalarea_shape = readOGR(dsn=totalarea)
grid_shape = readOGR(dsn=grid)

grid_buffer = gBuffer(grid_shape, width = 10000, capStyle = 'SQUARE', joinStyle = 'MITRE')
clip = gIntersection(grid_buffer, totalarea_shape, byid = TRUE, drop_lower_td = TRUE)

writeOGR(clip, 'K:/ACCS_Work/Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/test/grid_buffer.shp', driver = "ESRI Shapefile")