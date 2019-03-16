
#####################################
###### Tare 2 Progrmacion en R ######
##    Armando Olivares            ##
####################################

# 1. Lee el fichero y asígnalo a una variable. 


datos_nba <- read.csv("shot_logs.csv", header = T, stringsAsFactors = F)


# 2. ¿De qué clase es el objeto?
class(datos_nba)

# 3. ¿Cómo se pueden ver el tipo de cada columna y una muestra de ejemplos?

str(datos_nba)


# 4. Muestra los primeros 15 registros del dataset. 
head(datos_nba, 15)


# 5. Muestra los últimos 20 registros del dataset.

tail(datos_nba, 20)

# 6. ¿Cuáles son las dimensiones del dataset? 

dim(datos_nba)

# 7. ¿Cuáles son los nombres de las variables del dataset? 
names(datos_nba)

# 8. La variable PTS_TYPE debería ser categórica. Crea un factor con 
#etiquetas para dicha columna (no hace falta que sea ordenable) y asígnalo 
#a la columna de nuevo. Es decir, el factor deberá de tener tantas categorías 
#como valores tiene la variable PTS_TYPE y cada una de esas categorías debe tener 
#una etiqueta (asigna a cada una de las categorías un nombre que creas que tiene sentido). 

head(datos_nba$PTS_TYPE)


datos_nba$PTS_TYPE <-  factor( datos_nba$PTS_TYPE, ordered = T, labels =   c("Doble", "Triple"))

str(datos_nba)


# 9. La variable FGM es variable booleana. Conviértela a variable booleana y asígnala a la columna de nuevo. 

datos_nba$FGM <- as.logical(datos_nba$FGM)

# 10. Calcula la suma de la columna PTS

sum(datos_nba$PTS)

# 11  Guarda en un vector (total) la suma de las columnas PTS y 
#SHOT_NUMBER. Es decir, el vector total deberá tener 2 elementos: el primero 
#conteniendo la suma de la columna PTS y el segundo con la suma de la columna SHOT_NU

total <- c(sum(datos_nba$PTS), sum(datos_nba$SHOT_NUMBER))
total

# 12  Qué variables son numéricas? PISTA: utiliza sapply junto con la función is.numeric. 

names(which(sapply(datos_nba, is.numeric)))


# 13  Utilizando el resultado anterior, selecciona aquellas columnas numéricas y calcula la media de todos los registros. 
sapply(datos_nba[ , names(which(sapply(datos_nba, is.numeric)))], mean)


# 14   Selecciona aquellos registros del dataset que contengan partidos jugados entre el 06  y 09 de noviembre de 2014 (incluidos). 
#Lo mismo, pero además en los que haya ganado el equipo local. 

library(dplyr)
datos_nba_aux <- datos_nba
datos_nba_aux%>%
  separate(MATCHUP, into =c("DATE", "TEAMS"), sep = "-")%>%
  mutate(date = ymd(DATE, locale="usa"))
  filter(date>= ymd("Nov 06, 2014", locale="usa"), date<=ymd("Nov 09, 2014", locale="usa"), LOCATION=="H", W=="W" )

# 15

head(datos_nba[, c(1:19)], 150)


# 16. Selecciona las 150 primeras filas y todas las columnas menos las dos últimas (sólo con índices negativos)

head(datos_nba[, -c(20:21)], 150)


# 17   Obtén los cuartiles de la variable SHOT_CLOCK. 
quantile(datos_nba$SHOT_CLOCK, na.rm = T)


# 18. Obtén los deciles de la variable SHOT_CLOCK. 
quantile(datos_nba$SHOT_CLOCK, prob = seq(0, 1, length = 11), type = 5, na.rm = T)


# 19. Obtén los estadísticos básicos de todas las variables en un solo comando. 
summary(datos_nba)

# 20. ¿Cuántos jugadores distintos aparecen en el dataset?

length(unique(datos_nba$player_name))

# 21. ¿Cuántos registros tienen un valor superior a 30 para la variable FINAL_MARGIN? 
length(datos_nba$FINAL_MARGIN[datos_nba$FINAL_MARGIN > 30])


# 22. Ordena de mayor a menor los 100 primeros elementos de la variable SHOT_DIST.

sort((head(datos_nba,100)$SHOT_DIST), decreasing = T)

# 23.  Ordena el dataset por la variable SHOT_DIST de manera ascendente. Inspecciona los primeros resultados para comprobar que se ha ordenado como se pide.
datos_nba <- datos_nba[order(datos_nba$SHOT_DIST),] 
tail(datos_nba, 20)

#  Obtén los índices de los registros para los que el valor de la variable SHOT_DIST es superior a la media.
which(datos_nba$SHOT_DIST > mean(datos_nba$SHOT_DIST))

# 25. Comprueba si alguna de las variables contiene NAs

colnames(datos_nba)[colSums(is.na(datos_nba)) > 0]

# 26. Obtén los registros para los que el valor de la variable SHOT_CLOCK es máximo. PISTA: cuidado con los NAs. 

which(datos_nba$SHOT_CLOCK ==max(datos_nba$SHOT_CLOCK, na.rm = T))

# 27. Comprueba utilizando el boxplot si la variable DRIBBLES tiene outliers
boxplot(datos_nba$DRIBBLES)


# 28.  Pinta un histograma de la variable SHOT_DIST. 
hist(datos_nba$SHOT_DIST)


# 29. 

cerca.lejos <- function(dist, limit=15) {
  if (dist < limit){
    return ("CERCA")
  }else {
    return("LEJOS")
  }
}

cerca.lejos(2)

# 30 Mediante una llamada a una de las funciones apply aplica la función anterior a toda la columna SHOT_DIST. El resultado obtenido debe ser almacenado en una nueva variable del data frame llamada cerca.lejos. 

datos_nba["cerca.lejos"] <- sapply(datos_nba$SHOT_DIST, cerca.lejos)
