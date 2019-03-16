
#####################################
###### Tare 2 Progrmacion en R ######
##    Armando Olivares            ##
####################################


library(dplyr)
library(tidyr)
library(lubridate)



datos_nba <- read.csv("shot_logs.csv", header = T, stringsAsFactors = F)
datos_nba_nuevo <-datos_nba%>%
separate( MATCHUP, into=c("DATE", "TEAMS"), sep = "-")
Sys.setlocale("LC_TIME", "C")

datos_nba_nuevo$DATE = as.Date(datos_nba_nuevo$DATE, format = "%b %d, %Y")
datos_nba_nuevo$TEAMS = gsub("@","vs.", datos_nba_nuevo$TEAMS)
#datos_nba_nuevo["id"] = c(1:nrow(datos_nba_nuevo))
datos_nba_nuevo <- cbind(ID = c(1:nrow(datos_nba_nuevo)), datos_nba_nuevo)
head(datos_nba_nuevo)


# Creamos el Long Dataset  seleccionando primero las columnas solicitadas y luego utilizando la funcion gather del paquete tidyr
datos_nba_sub <- (datos_nba_nuevo[,c(1,3,4,7,14,16)])
long_nba <- gather( datos_nba_sub, my_key, my_value, SHOT_RESULT, FINAL_MARGIN, SHOT_DIST)

# Creamos a partir del dataset anterior el wide dataset

wide_nba <- spread(long_nba, my_key, my_value ) 

# Comparamos los DF para demostrart que son iguales
all(datos_nba_sub == wide_nba)


