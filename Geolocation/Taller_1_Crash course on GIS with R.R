setwd("~/Programas/CursoLocationIntelligence/Talleres/")	
library(RgoogleMaps)	
library(ggmap)	
library(rgdal)	
library(leaflet)	
library(lubridate)	
library(dplyr)	
library(raster)	
#' 	
#' 	
#' ## Objetivo	
#' 	
#' En este taller estudiaremos información geográfica, su análisis y visualización. En particular	
#' 	
#' - Aprenderemos como visualizar mapas, shapefiles, etc en `R`	
#' - Utilizaremos datos geolocalizados para estimar la residencia de usuarios	
#' - Utilizaremos datos geolocalizados para estimar la ley de la gravedad de retail	
#' - Utilizaremos esos modelos para determinar las zonas de atracción de centros comerciales	
#' 	
#' ## Visualización de información geográfica 	
#' 	
#' Hya muchas librerías de visualización de información geográfica. A estos sistemas se los conoce como GIS (Geografical Information Systems).	
#' 	
#' - Una lista de estas plataformas/sistemas se puede encontrar en la [Página en Wikipedia sobre GIS]( https://en.wikipedia.org/wiki/List_of_geographic_information_systems_software)	
#' 	
#' - Ejemplos importantes de estas plataformas GIS son:	
#'     - Los [productos Esri](http://esri.com), que incluyen el famoso ArcGIS (desktop y online versions)	
#'     - El servicio (español) [Carto](https://carto.com), un servicio online muy sencillo para mostrar información geográfica.	
#'     	
#' - En `R` hay muchas librerías para visualizar y analizar datos geográficos.	
#'     - Una lista de paquetes se puede encontrar en la [Task View for Spatial Statistics](https://cran.r-project.org/web/views/Spatial.html)	
#'     - Principalmente hay dos categorías	
#'         - Paquetes para tratar datos tipo `(lat, lon)` como `sp`, `maps`, `rgdal`, etc.	
#'         - Paquetes que ofrecen integración APIs de mapas como  Google Maps o OpenStreetMaps:  `RgoogleMaps`, `ggmap`, `leaflet`, etc.	
#'         	
#' - Lo mismo en `Python` 	
#'     - Python se integra muy bien con ArcGIS [Python wiki GIS](http://www.wiki.gis.com/wiki/index.php/Python)	
#'     	
#' ## Tipos de datos geográficos	
#' 	
#' <div class="columns-2">	
#' Recordamos que hay dos tipos de datos geográficos	
#' 	
#' - Raster o imágenes	
#'     - Como por ejemplo mapas de carreteras, fotografías aéreas, etc.	
#' 	
#' - Puntos, líneas o polígonos 	
#'     - Como por ejemplo las líneas que definen una carretera, el polígono que delimita un municipio o un punto que determina desde dónde se ha geo-localizado un tweet.	
#' 	
#' Vamos a ver cómo usar ambos.	
#' 	
#' ![Tipos de datos geográficos](./img/types.jpg)	
#' 	
#' </div> 	
#' 	
#' ## Usando raster data	
#' 	
#' En `R` hay muchos paquetes para descargar, tratar y analizar imagenes geográficas tipo raster. Empecemos con los que se descargan imágenes.	
#' 	
#' Básicamente estos paquetes descargan una imagen (raster) de un mapa y permiten mostrar sobre estos mapas puntos, líneas, polígonos, etc. 	
#' 	
#' Antes de pintar el mapa, vamos a bajarnos algunos puntos geolocalizados. En concreto los centros comerciales en la comunidad de Madrid (http://www.madrid.org/nomecalles/) 	
#' 	
centros <- read.table("./data/centros_comerciales.csv",header=T,stringsAsFactors = F)	
head(centros,2)	
#' 	
#' Como vemos los centros comerciales vienen georeferenciados con coordenadas lat lon	
#' 	
#' ## Paquetes con integración con APIs de mapas	
#' 	
#' Pintamos el mapa de Madrid con los puntos de los centros comerciales. Primero lo hacemos con el paquete  `RgoogleMaps` que toma los mapas de Google	
#' 	
require(RgoogleMaps)	
MadridMap <- GetMap(center = c(40.415364,-3.707398), zoom = 11,maptype="mobile")	
tmp <- PlotOnStaticMap(MadridMap,lon=centros$lon,lat=centros$lat,pch=20,cex=2,col=factor(centros$ETIQUETA))	
#' 	
#' 	
#' ## Paquetes con integración con APIs de mapas	
#' 	
#' Podemos cambiar el tipo de mapa para mostrar diferentes tipos de imágenes `maptype = c("roadmap", "mobile", "satellite", "terrain", "hybrid", "mapmaker-roadmap", "mapmaker-hybrid")	
#' 	
#' 	
MadridMap <- GetMap(center = c(40.415364,-3.707398), zoom = 11,maptype="hybrid")	
tmp <- PlotOnStaticMap(MadridMap,lon=centros$lon,lat=centros$lat,pch=20,cex=2,col=factor(centros$ETIQUETA))	
#' 	
#' 	
#' 	
#' 	
#' ## Paquetes con integración con APIs de mapas	
#' 	
#' Lo mismo lo podemos hacer con el paquete `ggmap` (https://github.com/dkahle/ggmap). Y un poco más fácil.	
#' 	
require(ggmap)	
mm <- get_map(location="Madrid",zoom=11)	
ggmap(mm)+geom_point(data=centros, aes(x=lon,y=lat,col=ETIQUETA))	
#' 	
#' 	
#' ## Paquetes con integración con APIs de mapas	
#' 	
#' Finalmente podemos hacer esto con visualización interactiva a través del paquete `leaflet` https://rstudio.github.io/leaflet/ Los mapas por defecto son de OpenStreetMap	
#' 	
#' 	
m <- leaflet(data=centros) %>% 	
  addTiles() %>% 	
  addMarkers(~lon, ~lat, popup = ~ as.character(ETIQUETA))	
m	
#' 	
#' 	
#' ## Paquetes con integración con APIs de mapas	
#' 	
#' Aunque podemos también cambiar el tipo de mapas con los que trabajamos si le especificamos de dónde puede sacar los `tiles`	
#' 	
m <- leaflet(data=centros) %>% 	
  addTiles() %>% 	
  addMarkers(~lon, ~lat, popup = ~ as.character(ETIQUETA)) %>% addProviderTiles(providers$CartoDB.Positron)	
m	
#' 	
#' 	
#' 	
#' 	
#' ## Paquetes para trabajar con objetos geográficos	
#' 	
#' Hay otra manera de visualizar mapas sin utilizar imagenes (raster). Mediante polígonos que definen fronteras (paises, regiones, ciudades, etc.). Estos polígonos también se pueen utilizar para definir carreteras, accidentes geográficos, edificios, puntos de interés, etc. El formato más utilizado para trabajar con estos objetos espaciales es el de `shapefiles`. Otro muy extendido es GeoJSON o TopoJSON.	
#' 	
#' Hay muchos sitios para descargar los shapefiles de diferentes regiones administrativas, a diferentes niveles de resolución Por ejemplo:	
#' 	
#' - Shapefiles para los condados de EE.UU <br> https://www.census.gov/geo/maps-data/data/cbf/cbf_counties.html	
#' - Shapefiles para los municipios de España<br> http://www.ine.es/censos2011_datos/cartografia_censo2011_nacional.zip	
#' - Shapefiles para diferentes países a diferentes resoluciones administrativas<br> http://http://www.gadm.org	
#' - Shapefiles para los barrios/distritos de Madrid http://www.madrid.org/nomecalles/DescargaBDTCorte.icm	
#' 	
#' 	
#' ## Paquetes para trabajar con objetos geográficos	
#' 	
#' Hay muchos paquetes para trabajar con objetos geográficos en `R`. Los más importantes que vamos a ver son `rgdal` y `sp`. Por ejemplo, vamos a bajarnos los shapefiles de los barrios de Madrid y los visualizamos. Para cargar los shapefiles vamos a utilizar el paquete `rgdal` package	
#' 	
#' 	
par(mar=c(0,0,0,0))	
map_barrios <- readOGR(dsn ="./data/Barrios Madrid/",layer="200001469",encoding = "latin1",stringsAsFactors=F)	
plot(map_barrios)	
#' 	
#' 	
#' 	
#' ## Paquetes para trabajar con objetos geográficos	
#' 	
#' Cuando cargamos un shapefile en `R` se crea un objeto de la clase `SpatialPolygonsDataFrame` y tiene varias piezas de información:	
#' 	
#' - `map_barrios@polygons` es un data.frame espacial donde están cada uno de los polígonos (fronteras de los barrios) 	
#' - `map_barrios@data` es un data.frame con meta-información sobre cada polígono.	
#' - `map_barrios@proj4string` es una variable que muestra el tipo de proyección geográfica utilizada.	
#' 	
head(map_barrios@data,3)	
map_barrios@proj4string	
#' 	
#' 	
#' ## Paquetes para trabajar con objetos geográficos	
#' 	
#' Hay muchas funciones para trabajar, analizar y modificar estos objetos. Por ejemplo 	
#' 	
length(map_barrios) # nos dice cuantas `features` hay. En este caso polígonos	
extent(map_barrios) # nos da la extensión espacial del objeto	
#' 	
#' 	
#' Por otro lado `coordinates(map_barrios)` nos devuelve las coordenadas de los centros de cada polígono	
#' 	
#' 	
head(coordinates(map_barrios),2)	
#' 	
#' Como vemos las coordenadas no están en lat, lon. Eso es debido a que el mapa utiliza una proyección de datos geográficos diferente a la habitual	
#' 	
#' 	
map_barrios@proj4string	
#' 	
#' 	
#' ## Paquetes para trabajar con objetos geográficos	
#' 	
#' <div class="columns-2">	
#' 	
#' ¿Y qué es una proyección? Básicamente una proyección es un sistema de coordenadas que convierte una posición sobre el globo terráqueo en dos números (longitud y latitud). El problema es que hay varias maneras de hacerlo	
#' 	
#' - Proyección UTM 	
#'     - En vez de la tradicional de longitud y latitud da el punto en metros respecto a líneas (paralelos y meridianos) definidos sobre la superficie.	
#' 	
#' - Proyección WGS84	
#'     - Es un tipo de proyección esférica, donde cada punto se da en longitud y latitud que indican dónde está sobre la esfera. El GS84 es un estándar de cómo se define la esfera terráquea. se refiere a la diferente definición de esfera. En este caso es un elipsoide	
#'     - Esta es la tradicional	
#' 	
#' ![1984 World Geodetic System revision](./img/wgs84.png	
#' )	
#' 	
#' 	
#' </div> 	
#' 	
#' ## Paquetes para trabajar con objetos geográficos	
#' 	
#' Vamos a cambiar la proyección UTM que tiene nuestro shapefile a uno con WGS84	
#' 	
#' 	
WGS84 <- CRS("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")	
mapb <- spTransform(map_barrios,CRSobj=WGS84)	
proj4string(mapb)	
#' 	
#' 	
#' y ahora como vemos las coordenadas están en longitud/latitud	
#' 	
#' 	
head(coordinates(mapb),2)	
#' 	
#' 	
#' 	
#' ## Paquetes para trabajar con objetos geográficos	
#' 	
#' Podemos visualizar todos los polígonos o solo parte de ellos	
#' 	
par(mfrow=c(1,2))	
plot(mapb)	
plot(mapb[mapb@data$DESBDT %in% c("011 Palacio","015 Universidad"),])	
#' 	
#' 	
#' 	
#' ## Paquetes para trabajar con objetos geográficos	
#' 	
#' Podemos poner juntos imágenes raster con puntos (ya lo hemos visto) y también los polígonos. Por ejemplo, usando `ggmap` podemos poner los polígonos de los distritos de Madrid encima de un mapa raster. Para ello tenemos que convertir el objeto `SpatialDataFrame` a un `data.frame`utilizando el comando fortify	
#' 	
#' 	
map_f <- fortify(mapb)	
mm <- get_map(location="Madrid",zoom=11)	
ggmap(mm)+geom_polygon(aes(x=long,y=lat,group=group),data=map_f,fill="grey",size=.2,color='green',alpha=0.3)	
#' 	
#' 	
#' 	
#' ## Paquetes para trabajar con objetos geográficos	
#' 	
#' Lo mismo podemos hacer con leaflet	
#' 	
#' 	
leaflet(mapb) %>% addTiles() %>% addPolygons(weight=2,color="green",fillColor="gray",fillOpacity = 0.5)	
#' 	
#' 	
#' ## Paquetes para trabajar con objetos geográficos	
#' 	
#' Con leaflet es muy facil también mostrar diferentes capas. Por ejemplo vamos a mostrar los distritos y los centros comerciales	
#' 	
#' 	
leaflet(mapb) %>% addTiles() %>%	
  addPolygons(weight=2,color="green",fillColor="gray",fillOpacity = 0.5) %>%	
  addCircles(data=centros, lng= ~lon, lat=~lat,popup = ~ ETIQUETA)	
#' 	
#' 	
#' 	
#' 	
#' 	
#' ## Choropleths	
#' 	
#' Una de las visualizacións de información geográfica más utilizada es dibujar los polígonos con colores proporcionales a una variable (choropleths). Por ejemplo, vamos a pintar los barrios con color proporcional a la población en cada uno. 	
#' 	
#' Primero nos bajamos la población de los barrios de Madrid de <br> http://www-2.munimadrid.es/TSE6/control/seleccionDatosBarrio	
#' 	
pob_barrios <- read.csv("./data/Madrid-Poblacion_Barrios.csv")	
#' 	
#' Añadimos a la tabla del mapa una columna que sea la población (uniendo por el GEOCODIGO)	
#' 	
mapb@data$pob <- pob_barrios$Población[match(as.numeric(mapb$GEOCODIGO),pob_barrios$GEOCODIGO)]	
head(mapb@data)	
#' 	
#' 	
#' ## Choropleths	
#' 	
#' Creamos una paleta de colores log-proporcional a la población	
#' 	
par(mar=c(0,0,0,0))	
xx <- log(mapb@data$pob)	
xx <- (xx-min(xx))/(max(xx)-min(xx)) #normalizamos [0,1]	
xcolor <- rgb(xx,0,0) #colores entre negro y rojo	
plot(mapb,col=xcolor,border=xcolor)	
#' 	
#' 	
#' ## Choropleths	
#' 	
#' Como siempre, mucho mejor con el paquete `leaflet`	
#' 	
#' 	
m <- leaflet(data = mapb) %>% 	
  addPolygons(fillColor= ~ rgb(xx,0,0),weight=1,fillOpacity = 0.8,popup=mapb@data$DESBDT)	
m	
	
#' 	
#' 	
#' 	
#' ## Choropleths	
#' 	
#' El paquete `leaflet' también tiene opciones para hacer las paletas de colores de manera automática (https://rstudio.github.io/leaflet/colors.html)	
#' 	
pal <- colorNumeric(palette="Blues",domain=log(mapb@data$pob))	
m <- leaflet(data = mapb) %>% addTiles() %>% 	
  addPolygons(fillColor= ~ pal(log(mapb@data$pob)),weight=1,fillOpacity = 0.8,popup=mapb@data$DESBDT)	
m	
#' 	
#' 	
#' 	
#' ## Choropleths	
#' 	
#' Y hay muchas opciones para hacer más interesantes el resultado final (https://rstudio.github.io/leaflet/choropleths.html). Por ejemplo, podemos añadir una leyenda para informar sobre los valores	
#' 	
#' 	
pal <- colorNumeric(palette="Blues",domain=log(mapb@data$pob))	
m <- leaflet(data = mapb) %>% addTiles() %>% 	
  addPolygons(fillColor= ~ pal(log(mapb@data$pob)),weight=1,fillOpacity = 0.8,popup=mapb@data$DESBDT) %>% addLegend(pal=pal,values=~log(mapb@data$pob))	
m	
#' 	
#' 	
#' ## Geolocalizar puntos	
#' 	
#' Una de las operaciones más usuales en datos espaciales es encontrar el polígono (polígonos) donde se encuentra un punto.  Para eso utilizamos la función `over` en el paquete `sp`	
#' 	
#' Por ejemplo: ¿en qué barrio está el Bernabeu y el Calderón? 	
#' 	
gps_Bernabeu <- c(-3.687909,40.4544)	
gps_Calderon <- c(-3.720589,40.40671)	
#' 	
#' 	
#' Transformamos estos puntos a `SpatialPoints` ya que el paquete `sp` solo entiende este tipo de objetos	
#' 	
#' 	
pto_matrix <- rbind(gps_Bernabeu,gps_Calderon)	
pps1 <- SpatialPoints(pto_matrix,proj4str=WGS84)	
#' 	
#' 	
#' Finalmente encontramos el índice (número de polígono) en el que están los puntos y el barrio	
#' 	
id_polygon <- over(pps1,as(mapb,"SpatialPolygons"))	
mapb@data[id_polygon,]	
#' 	
#' 	
#' ## Calcular distancias y áreas.	
#' 	
#' Otra de las operaciones más habituales en datos geo-espaciales es medir distancias de un punto a otro o el área de un polígono.	
#' 	
#' Para medir la distancia entre dos puntos, utilizaremos la función `spDists` o `spDistsN2` del paquete `sp`. Por ejemplo, esta es la matriz de distancias entre el Bernabeu y el Calderon	
#' 	
spDists(pto_matrix,longlat=T) #calcula todas las distancias entre todas las filas de pto_matrix	
#' 	
#' 	
#' o entre todas las filas y una de ellas en particular	
#' 	
spDistsN1(pto_matrix,pto_matrix[1,],longlat=T)	
#' 	
#' 	
#' 	
#' ## Calcular distancias y áreas.	
#' 	
#' Lo mismo para las áreas. Podemos utilizar la función `area` del paquete raster que da el área en metros cuadrados. Por ejemplo, esto es lo que ocupa en km2 el barrio de Los Jerónimos	
#' 	
#' 	
area(mapb[grep("Jerónimos",mapb@data$DESBDT),]) / 1000000	
#' 	
#' 	
#' mientras que él área del barrio del Pardo es	
#' 	
#' 	
#' 	
area(mapb[grep("Pardo",mapb@data$DESBDT),]) / 1000000	
#' 	
#' 	
#' 	
#' 	
#' ## Ejercicio 1	
#' 	
#' - Repetir el proceso de bajada de los shapefiles y de la población para las secciones censales de la comunidad de Madrid.	
#' 	
#' - Mostrar en una visualización tipo choropleth la población de cada sección censal.	
#' 	
#' - Mostrar en otra visualización tipo choropleth el porcentaje de población extranjera en cada sección censal.	
#' 	
#' ## Ejercicio 1	
#' 	
#' Para obtener los datos de las secciones censales tenemos que ir a la página del INE: http://www.ine.es/censos2011_datos/cen11_datos_resultados_seccen.htm	
#' 	
#' Donde tenemos dos tipos de archivos:	
#' 	
#' - Indicadores para secciones censales (en formato CSV mejor). Mirad también el archivo de "Relación de Indicadores" para saber cuáles son.	
#' - Contorno de las secciones censales en formato shapefile. 	
#' 	
#' 	
#' ## Ejercicio 1	
#' 	
#' Cargamos los datos de las secciones censales de la comunidad 13 (Madrid)	
#' 	
indicadores <- read.table("./data/indicadores_seccion_censal_csv/C2011_ccaa13_Indicadores.csv",sep=",",header=T)	
#' 	
#' 	
#' 	
#' Y los shapefiles de las secciones censales	
#' 	
map_censales <- readOGR(dsn ="./data/cartografia_censo2011_nacional/",layer="SECC_CPV_E_20111101_01_R_INE",stringsAsFactors=F)	
#' 	
#' ## Ejercicio 1	
#' 	
#' Como antes las secciones censales están en otra proyección	
#' 	
#' 	
proj4string(map_censales)	
#' 	
#' 	
#' Asi que la cambiamos a WGS84	
#' 	
WGS84 <- CRS("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")	
mapc <- spTransform(map_censales,CRSobj=WGS84)	
proj4string(mapc)	
#' 	
#' 	
#' 	
#' y os quedamos solo con las de la Comunidad de Madrid	
#' 	
#' 	
mapc <- mapc[mapc@data$CCA == 13,]	
#' 	
#' 	
#' 	
#' ## Ejercicio 1	
#' 	
#' Para unir los datos de los indicadores y de los shapefiles vamos a utilizar el indicador único `CUSEC`. Pero el archivo de los indicadores no lo tiene. Se lo ponemos	
#' 	
#' 	
require(stringr)	
poblacion <- data.frame(CUSEC = paste(	
                          str_pad(indicadores$cpro, 2, pad = "0"),	
                          str_pad(indicadores$cmun, 3, pad = "0"),	
                          str_pad(indicadores$dist, 2, pad = "0"),	
                          str_pad(indicadores$secc, 3, pad = "0"), sep=""),	
                          poblacion = indicadores$t1_1)	
#' 	
#' Y los juntamos	
#' 	
mapc@data$poblacion <- poblacion$poblacion[match(mapc@data$CUSEC,poblacion$CUSEC)]	
#' 	
#' 	
