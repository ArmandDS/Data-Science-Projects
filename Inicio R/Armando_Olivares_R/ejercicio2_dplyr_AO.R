#####################################
###### Tarea 2 Progrmacion en R ######
##    Armando Olivares            ##
####################################

# Ejercicio 2 DPLYR
#Cargamos la libreria a utilizar
library(dplyr)

# Cargamos los datos
datos_nba <- read.csv("shot_logs.csv", header = T, stringsAsFactors = F)

head(datos_nba)
# 1. Calcula los puntos total marcados en cada uno de los partidos
x <- datos_nba%>%
  group_by(GAME_ID)%>%
  summarise(Total_pts = sum(PTS, na.rm = T))
 


# 2. Ordena de mayor  a menor el dataset según la suma anterior. 

# Mutate
datos_nba%>% inner_join(x)%>%
  arrange(desc(Total_pts))


# 3. Calcula el número total de puntos marcados por mes del año y por día de la semana.  

nba_mes_dia <- datos_nba%>%
    mutate(MONTH = substr(datos_nba$MATCHUP, start=0, stop=3), DAY =substr(datos_nba$MATCHUP, start=4, stop=6) )%>%
    group_by(MONTH, DAY)%>%
    summarise(Total_pts = sum(PTS, na.rm = T))

#  4. Calcula el mes en el que se marcaron más triples. 
mes_mas_triples <- nba_mes_dia%>%
  group_by(MONTH)%>%
  summarise(month_pts = sum(Total_pts, na.rm = T))%>%
  arrange(desc(month_pts))


mes_mas_triples[1,]



# 5. Calcula el jugador que ha tirado a canasta desde más lejos

datos_nba %>%
  arrange(desc(SHOT_DIST))%>%
  select(player_name, SHOT_DIST)%>%
  filter(SHOT_DIST== max(SHOT_DIST))
  


# 6. Para todos los partidos jugados en martes, calcular el número total 
# de regates realizados, distancia máxima de tiro y la media del SHOT_CLOCK.  

datos_nba <- mutate(datos_nba, YEAR = str_extract(datos_nba$MATCHUP, regex("[0-9]{4}")), MONTH = substr(datos_nba$MATCHUP, start=0, stop=3), DAY = str_extract(datos_nba$MATCHUP, regex("[0-9]{2}")) )

filter(datos_nba, wday(ymd(paste(datos_nba$YEAR, datos_nba$MONTH, datos_nba$DAY, sep="-")),  label= T) == "Tues")%>%
  group_by(GAME_ID)%>%
  summarise(Total_DRIBBLES = sum(DRIBBLES, na.rm = T), MAX_SHOOT_DIST = max(SHOT_DIST), MEAN_SHOT_CLOCK = mean(SHOT_CLOCK, na.rm = T))
  


