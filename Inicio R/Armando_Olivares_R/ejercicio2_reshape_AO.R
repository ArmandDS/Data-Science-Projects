
######### Ejerccio 2 Realizado con reshape2


## Cargamos las Librarias a utilizar
library(reshape2)

### Leemos el Archivo

datos_nba <- read.csv("shot_logs.csv", header = T, stringsAsFactors = F)


## Separamos las columnas

datos_nba_vars <- colsplit(datos_nba$MATCHUP,  "-", c("DATE", "TEAMS"))

## Aplicamos el formateo a las columnas

Sys.setlocale("LC_TIME", "C")

datos_nba_vars$DATE = as.Date(datos_nba_vars$DATE, format = "%b %d, %Y")
datos_nba_vars$TEAMS = gsub("@","vs.", datos_nba_vars$TEAMS)

datos_nba_vars <- cbind(ID = c(1:nrow(datos_nba_vars)), datos_nba_vars, datos_nba[, c(5, 12, 14)])

head(datos_nba_vars)

## Creamos el long dataset con la funcion melt
long_df <- melt(datos_nba_vars, id.vars = c("ID", "DATE", "TEAMS"), variable.name = "VARIABLE", value.name = "VALUE")

# Creamoe el wide dataset

wide_df <- dcast(long_df, ID + DATE + TEAMS ~ VARIABLE, value.var = "VALUE")


# Comparamos los df
all(datos_nba_vars == wide_df)

