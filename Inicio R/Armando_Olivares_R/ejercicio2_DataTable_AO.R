#######################################
# Ejercicio 2: data.table            #
#######################################


## Cargamos la libreria
library(data.table)

# Cargamos los datos
datos_nba <- read.csv("shot_logs.csv", header = T, stringsAsFactors = F)

head(datos_nba)

# 1  Calcula los puntos total marcados en cada uno de los partidos.

data_table_nba <- data.table(datos_nba)


total_pts <- data_table_nba[, list(TOTAL_PTS=sum(PTS, na.rm = TRUE)),by = GAME_ID]


# 2. Ordena de mayor  a menor el dataset según la suma anterior. 
 data_table_nba <- merge(data_table_nba, total_pts, by="GAME_ID")[order(-TOTAL_PTS)]

 
# 3. Calcula el número total de puntos marcados por mes del año y por día de la semana. 

 data_table_nba <- data_table_nba[, year := str_extract(data_table_nba[,MATCHUP,], regex("[0-9]{4}"))][,MONTH := substr(data_table_nba[,MATCHUP,], start=0, stop=3)][,  DAY := str_extract(data_table_nba[,MATCHUP,], regex("[0-9]{2}"))]
 
 total_pts_mes_dia <- data_table_nba[, list(TOTAL_PTS=sum(PTS, na.rm = TRUE)),by = list(MONTH, DAY)]
 

# 4. Calcula el mes en el que se marcaron más triples. 
data_table_nba[PTS_TYPE>2,][, list(total_3 =sum(PTS)), by = MONTH][order(-total_3)][1,]

#~5. 5. Calcula el jugador que ha tirado a canasta desde más lejos.  

data_table_nba[, list(long_dist =max(SHOT_DIST)), by = player_name][order(-long_dist)][1,]

 
#   6. Para todos los partidos jugados en martes, calcular el número total de regates realizados, distancia máxima de tiro y la media del SHOT_CLOCK.  

data_table_nba[ wday(ymd(paste(data_table_nba[,year], data_table_nba[,MONTH], data_table_nba[,DAY], sep="-")),  label= T) == "Tues"][, list(nro_dribbles = sum(DRIBBLES, na.rm = T), MAX_DIST= max(SHOT_DIST), MEAN_SHOT_CLOCK = mean(SHOT_CLOCK, na.rm = T)), by =GAME_ID ]
