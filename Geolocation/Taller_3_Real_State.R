#' ---	
#' title: 'Master in Data Science and Big Data 2017-2018 - Real State'	
#' author: "Esteban Moro"	
#' date: "5 de Mayo de 2018"	
#' output:	
#'   ioslides_presentation:	
#'     logo: ./img/afi.png	
#'     smaller: yes	
#'     widescreen: yes	
#'     toc: true	
#'     toc_depth: 2	
#'   beamer_presentation: default	
#' ---	
#' 	
#' 	
knitr::opts_chunk$set(cache=T,fig.align='center',message=FALSE,warning=FALSE)	
rm(list = ls());gc()	
setwd("~/Programas/CursoAplicacionesRedesSocialesMDS/Talleres/")	
library(RgoogleMaps)	
library(ggmap)	
library(rgdal)	
library(leaflet)	
library(lubridate)	
library(dplyr)	
library(raster)	
library(data.table)	
#' 	
#' 	
#' ## Objetivo	
#' 	
#' Entender cómo usar los datos geolocalizados para problemas inmobiliarios	
#' 	
#' En especial	
#' 	
#' - Entender cuáles son los factores que importan más en el precio de una casa	
#' 	
#' - Modelizar el precio de un inmueble de acuerdo a variables geo-espaciales	
#' 	
#' - Visualizar el mercado de oferta de viviendas	
#' 	
#' 	
#' ## Location Intelligence en el mercado inmobiliario	
#' 	
#' Uno de los sectores en el que Location Intelligence es más importante es del mercado inmobiliario. 	
#' 	
#' De hecho una de las máximas del mercado inmobiliario es que las tres cosas que más importan para el precio de una casa son:	
#' 	
#' "Location, Location, Location"	
#' 	
#' Entender mejor cómo las variables geo-espaciales influyen en el precio de un inmueble y en sus cambios nos permite:	
#' 	
#' - Manejar mejor las carteras de inmuebles (inversores)	
#' 	
#' - Detectar oportunidades de inversión (inversores, compradores)	
#' 	
#' - Mejorar las promociones de nuevos inmuebles	
#' 	
#' 	
#' ## Location Intelligence en el mercado inmobiliario	
#' 	
#' Hay mucha literatura sobre cuáles son las variables del barrio y de la ciudad que más afectan al precio de un inmueble. Por ejemplo:	
#' 	
#' - La distancia al centro	
#' 	
#' - El tener una parada de metro cerca	
#' 	
#' - El hecho de que sea una zona nueva 	
#' 	
#' - Que haya otros medios de transporte	
#' 	
#' - Que haya un parque cerca. O un supermercado	
#' 	
#' - O que no haya cierto tipos de negocio cerca	
#' 	
#' - El nivel de ruido/contaminación de la zona, etc.	
#' 	
#' Todas estas variables son de Location Intelligence.	
#' 	
#' 	
#' ## Location Intelligence en el mercado inmobiliario	
#' 	
#' La visualización y sobre todo la modelización de cómo impactan estas variables en el precio es lo que hace que Location Intelligence sea tan importante en el mercado inmobiliario.	
#' 	
#' En España hay varias empresas que dan este tipo de servicios de Location Intelligence	
#' 	
#' - Carto https://carto.com/blog/building-real-estate-investment-strategy-location-intelligence/	
#' - Geoblink https://www.geoblink.com/real-estate/	
#' 	
#' y en otros países:	
#' 	
#' - Zillow https://www.zillow.com/data-science/	
#' - Trulia http://www.dataversity.net/a-look-inside-trulias-data-science/	
#' - ReX Real Estate (un mercado llevado por AI) https://www.rexchange.com	
#' 	
#' 	
#' ## Location Intelligence en el mercado inmobiliario	
#' 	
#' <div class="columns-2">	
#' 	
#' Y qué variables son las más importantes? Muchas. Recomiendo leer el libro editado por Zillow	
#' 	
#' 	
#' - Propiedades de la casa	
#'     - Superficie	
#'     - Número de habitaciones	
#'     - Instalaciones	
#'     - Etc.	
#' - Propiedades del vecindario	
#'     - Transporte	
#'     - Zona urbana/suburbana	
#'     - Tiendas	
#'     - Instalaciones 	
#'     - Etc.	
#'     	
#'     	
#' ![](./img/zillowbook.jpg)    	
#' </div>   	
#' 	
#' 	
#' ## Taller: Precio de vivienda en Madrid    	
#' 	
#' Vamos a ver un ejemplo de cómo utilizar variables geo-espaciales para enteder el precio de la vivienda en Madrid. Para ello vamos a utilizar una lista de precio de viviendas.	
#' 	
#' 	
precios_vivienda <- fread("./data/precios_vivienda.csv")	
head(precios_vivienda,4)	
#' 	
#' Como vemos cada vivienda viene definida por su geolocalización y una serie de propiedades de ella, incluyendo el precio y superficie.	
#' 	
#' ## Taller: Precio de vivienda en Madrid    	
#' 	
#' Los precios tienen mucha variabilidad	
#' 	
ggplot(precios_vivienda,aes(x=price)) + geom_density(fill="red") + scale_x_log10()	
#' 	
#' 	
#' ## Taller: Precio de vivienda en Madrid    	
#' 	
#' Quitamos las casas que valen menos de 50000€. 	
#' 	
precios_vivienda<- precios_vivienda[price>50000]	
#' 	
#' 	
#' Así varía el precio por metro cuadrado	
#' 	
ggplot(precios_vivienda,aes(x=price/size)) + geom_density(fill="red") + scale_x_log10()	
#' 	
#' 	
#' ## Taller: Precio de vivienda en Madrid    	
#' 	
#' El precio varia entre	
#' 	
range(precios_vivienda$price)	
#' 	
#' 	
#' Donde el precio medio por metro cuadrado es	
#' 	
#' 	
mean(precios_vivienda$price/precios_vivienda$size)	
#' 	
#' 	
#' ## Taller: Precio de vivienda en Madrid    	
#' 	
#' Vamos a visualizar cómo depende el precio de la vivienda para cada uno de los barrios de Madrid. Para ello lo primero es situar cada inmueble en su barrio	
#' 	
#' Cargamos los shapefiles de los barrios de Madrid	
#' 	
barrios <- readOGR("/Users/emoro/Programas/CursoLocationIntelligence/Talleres/data/Barrios Madrid/",layer="200001469",stringsAsFactors = F,encoding = "latin1")	
#' 	
#' 	
#' Como siempre utilizamos la proyección WGS84	
#' 	
WGS84 <- CRS("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")	
mapb <- spTransform(barrios,CRSobj=WGS84)	
#' 	
#' 	
#' ## Taller: Precio de vivienda en Madrid    	
#' 	
#' Utilizamos la funcion `over` para saber en qué barrio está cada uno de los inmuebles	
#' 	
pps <- SpatialPoints(cbind(precios_vivienda$longitude,	
                           precios_vivienda$latitude),proj4str=WGS84)	
oo <- over(pps,as(mapb,"SpatialPolygons"))	
#' 	
#' 	
#' Y añadimos una columna a los inmuebles que refleje su barrio	
#' 	
precios_vivienda$barrio <- mapb@data$DESBDT[oo]	
head(precios_vivienda,3)	
#' 	
#' 	
#' ## Taller: Precio de vivienda en Madrid    	
#' 	
#' Calculamos el promedio del precio por metro cuadrado y el número de inmuebles para cada barrio	
#' 	
precios_barrio <- precios_vivienda[,.(precio_medio_m2=mean(price/size),num_inmuebles=length(price)),.(barrio)]	
head(precios_barrio,3)	
#' 	
#' 	
#' Ponemos esa información en los datos del mapa	
#' 	
mapb2 <- merge(mapb,precios_barrio,by.x="DESBDT",by.y="barrio")	
#' 	
#' 	
#' 	
#' ## Taller: Precio de vivienda en Madrid    	
#' Visualizamos el precio medio como un choropleth	
#' 	
#' 	
pal <- colorNumeric(palette = "Blues",domain = mapb2$precio_medio_m2)	
leaflet(mapb2) %>% addTiles() %>% 	
  addPolygons(fillColor =~pal(precio_medio_m2),stroke = F,	
              popup=~paste(DESBDT,"<br>",precio_medio_m2),fillOpacity = 0.9)	
#' 	
#' 	
#' 	
#' ## Taller: Modelización precio vivienda en Madrid	
#' 	
#' Como hemos visto, la principal variable que explica el precio de la vivienda es la superficie	
#' 	
#' 	
ggplot(precios_vivienda,aes(x=size,y=price)) + geom_point() + stat_smooth() + scale_x_log10() + scale_y_log10()	
#' 	
#' 	
#' ## Taller: Modelización precio vivienda en Madrid	
#' 	
#' Lo cual se refleja en un simple modelo	
#' 	
fit <- lm(log(price) ~ log(size), data=precios_vivienda)	
summary(fit)	
#' 	
#' 	
#' ## Taller: Modelización precio vivienda en Madrid	
#' 	
#' ¿Cómo influyen las otras propiedades del inmueble? Hacemos un modelo que incluya el número de habitaciones, si es exterior o no, etc	
#' 	
fit <- lm(log(price) ~ log(size) + rooms + as.factor(exterior)+bathrooms, data = precios_vivienda)	
summary(fit)	
#' 	
#' 	
#' ## Taller: Modelización precio vivienda en Madrid	
#' 	
#' Veamos ahora cómo influyen las variables de localización. Por ejemplo, la distancia al centro. Añadimos una columna a los datos que nos de la distancia al centro	
#' 	
lon_center <- -3.70379 #centro de Madrid = Plaza del Sol	
lat_center <- 40.416775	
dist_center <- spDistsN1(cbind(precios_vivienda$longitude,precios_vivienda$latitude),	
                         c(lon_center,lat_center),longlat = T)	
precios_vivienda$dist_center <- dist_center	
#' 	
#' 	
#' Y modelizamos de nuevo	
#' 	
fit <- lm(log(price) ~ log(size) + rooms + as.factor(exterior) + 	
            bathrooms + dist_center, data = precios_vivienda)	
summary(fit)$coefficients	
#' 	
#' 	
#' ## Taller: Modelización precio vivienda en Madrid	
#' 	
#' Aunque el modelo ya es muy bueno, vamos a ver si el error es diferente por barrios	
#' 	
precios_vivienda$fitted <- fitted(fit)	
error_barrios <- precios_vivienda[,.(MAE_medio=mean(abs(log(price)-fitted)/fitted)),.(barrio)]	
#' 	
#' 	
#' donde vemos que hay barrios donde el modelo tiene mucho error	
#' 	
error_barrios[MAE_medio > 0.04]	
#' 	
#' 	
#' ## Taller: Modelización precio vivienda en Madrid	
#' 	
#' Visualizamos ese error	
#' 	
mapb2 <- merge(mapb2,error_barrios,by.x="DESBDT",by.y="barrio")	
pal <- colorNumeric(palette = "Blues",domain = mapb2$MAE_medio)	
leaflet(mapb2) %>% addTiles() %>% 	
  addPolygons(fillColor =~pal(MAE_medio),stroke = F,	
              popup=~paste(DESBDT,"<br>",MAE_medio),fillOpacity = 0.9)	
#' 	
#' 	
#' ## Ejercicio 1: Efecto de la distancia al metro	
#' 	
#' Vamos a ver si el que el inmueble esté cerca del metro tiene algún efecto en el precio. Para ello nos bajamos la geolocalización de las paradas de metro de [Nomecalles](http://www.madrid.org/nomecalles/DescargaBDTCorte.icm)	
#' 	
#' 	
bocas <- readOGR(dsn="./data/Transportes y comunicaciones_ Metro (bocas)/",layer="bocas")	
#' 	
#' Y las transformamos a lat/long	
#' 	
WGS84 <- CRS("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")	
bocas2 <- spTransform(bocas,CRSobj=WGS84)	
#' 	
#' 	
#' Ponemos la latitud y la longitud en los datos	
#' 	
cc <- coordinates(bocas2)	
bocas2@data$lon <- cc[,1]	
bocas2@data$lat <- cc[,2]	
#' 	
#' 	
#' ## Ejercicio 1: Efecto de la distancia al metro	
#' 	
#' Ahora tenemos que determinar la distancia a la boca de metro más cercana. Definimos una función que, a partir de un punto nos da la distancia más corta a una boca de metro	
#' 	
distance_boca <- function(lon,lat){	
  dd <- spDistsN1(cbind(bocas2@data$lon,bocas2@data$lat),c(lon,lat),longlat = T)	
  min(dd)	
}	
#' 	
#' 	
#' Por ejemplo la distancia a la boca más cercana del centro de la Puerta del Sol es	
#' 	
distance_boca(lon_center,lat_center)	
#' 	
#' es decir, apenas unos metros	
#' 	
#' 	
#' ## Ejercicio 1: Efecto de la distancia al metro	
#' 	
#' Calculamos la distancia a cada uno de los inmuebles	
#' 	
precios_vivienda[, distancia_metro:=mapply(distance_boca,longitude,latitude)]	
#' 	
#' 	
#' Influye?	
#' 	
fit <- lm(log(price) ~ log(size) + rooms + as.factor(exterior) + 	
            bathrooms + dist_center + distancia_metro, data = precios_vivienda)	
summary(fit)$coefficients	
#' 	
#' 	
#' 	
#' ## Ejercicio 2: Efecto de la distancia a un supermercado	
#' 	
#' Repetir el ejercicio anterior para los supermercados, galerias de alimentación y mercadillos	
#' 	
#' 	
#' 	
#' ## Ejercicio 3: Visualización de oportunidades	
#' 	
#' - Identificar los inmuebles que tienen un precio por metro cuadrado mucho menor que la media de su barrio	
#' 	
#' - Visualizar dichos inmuebles en un mapa	
#' 	
