#############################################
#             SERIES TEMPORALES             #
#############################################

# Se limpia el espacio de trabajo:

rm(list = ls())



# Carga de datos

datos <- read.csv("DatosSeries/numeroBajasEnfermedadLaboral.csv")

# Breve estudio de los datos cargados

class(datos)
str(datos)
dim(datos)
colnames(datos)
summary(datos)
head(datos)
tail(datos)


library(lubridate)
datos$fecha <- as.Date(dmy(datos$fecha), format = '%y-%m-%d')
head(datos)


# [1]. Se representan gr?ficamente los datos
################################################################

#install.packages("ggplot2")
library(ggplot2)

ggplot(aes(x= fecha, y = target), data = datos) + geom_line(color = '#008B8B') + 
  xlab('FECHA') + ylab('Bajas Laborales') + ggtitle("Bajas por Enfermedad Laboral")+scale_x_date(date_breaks = '6 months', date_labels = "%m%Y")+theme_bw()+
theme(plot.title = element_text(hjust =0.5))



# [2]. Se convierten los datos en un objeto de tipo time series
#      para poder aplicar sobre ellos las funciones de R
################################################################

datos.ts <- ts(datos$target, start=c(2001,01), end=c(2013,12), frequency=12)
class(datos.ts)



##########################################3

desc <- decompose(datos.ts)
plot(desc$figure)
plot(desc$trend)
plot(desc$seasonal)
plot(stl(datos.ts, s.window = "periodic"), col="#00688B")



library(forecast)

datos.train <- subset(datos, "2001-01-01"<=fecha & fecha<="2012-12-01")
datos.train.ts <- as.ts(datos.train$target, frequency = 12)

datos.validate <- subset(datos, fecha>"2012-12-01")
datos.validate.ts <- as.ts(datos.validate$target, frequency=12)

auto.arima(datos.train.ts)## arroja ARIMA(0,1,2) 



library(tseries)
#### test dickey fullermodelo
adf.test(datos.train.ts, alternative="stationary", k = 30)

#### la serie no es estacionaria

### Box cox 

library(MASS)
box_cox <- boxcox(target ~ fecha,
                  data = datos.train,
                  lambda = c(0, 0.5, 1))

lambda <- box_cox$x[which.max(box_cox$y)]
lambda  ## lambda cercano a cero sugiere una transformacion log

library(car)

## otra opcion
powerTransform(datos.train.ts)



# Hay que hacer una transformaci?n logar?tmica

datos.train2 <- datos.train
datos.validate2 <- datos.validate
datos.train$target <- log(datos.train$target)
datos.validate$target <- log(datos.validate$target)
head(datos.train)

datos.train.ts <- as.ts(datos.train$target, frequency = 12)

datos.validate.ts <- as.ts(datos.validate$target, frequency=12)


plot.ts(datos.train.ts)
plot.ts(sqrt(datos.train.ts))
plot.ts(log(datos.train.ts))

##################diferenciamos la series

serie_diff <- diff(datos.train.ts)
plot(serie_diff, type = "l")
adf.test(serie_diff, alternative="stationary")
########################################################
##########################################33

##############






# [6]. Ajuste de un modelo ARIMA a la serie
################################################################

# [6.1]. Funciones de autocorrelaci?n simple y parcial

acf(datos.train.ts, lag.max = 35, xlab = "Retardo",
    main= "Funci?n de autocorrelaci?n simple")

pacf(datos.train.ts, lag.max = 35, xlab = "Retardo",
     main = "Funci?n de autocorrelaci?n parcial")


######################### Diferenciando los datos


acf(diff(datos.train.ts))
pacf(diff(datos.train.ts), lag.max = 35)





################## Ajustamos un modelo AR(1) diferenciado


ajuste1 <- Arima((datos.train.ts),
                 order = c(1,1,0),
                 method = "ML")
ajuste1
plot(ajuste1)


# Matriz de correlaci?n de par?metros estimados

library(caschrono)

cor.arma(ajuste1)

ruidoBlancoLB <- function(modelo,listaRetardos){
  
  for (i in listaRetardos){
    print(Box.test(residuals(modelo),type="Ljung-Box", lag=i))
  }
}

ruidoBlancoLB(ajuste1,c(6,12,18,24,30,36,42,48))

# Versi?n 2: Esta funci?n de caschrono lo da m?s resumido:

Box.test.2(residuals(ajuste1),
           nlag = c(6,12,18,24,30,36,42,48),
           type="Ljung-Box")


#####################################test residuos

tsdiag(ajuste1)



############################Ajuste residuos


par(mfrow=c(2,1))
acf(ajuste1$residuals, lag.max = 45, xlab = "Retardo", main="", lwd=3)
pacf(ajuste1$residuals, lag.max = 45,  xlab = "Retardo", main="", lwd=3)




ajuste2 <- Arima(datos.train.ts,
                 order = c(1,1,1),
                 method = "ML")
ajuste2

tsdiag(ajuste2)


acf(ajuste2$residuals, lag.max = 45, xlab = "Retardo", main="")
pacf(ajuste2$residuals,  lag.max = 45,xlab = "Retardo", main="")

Box.test.2(residuals(ajuste2),
           nlag = c(6,12,18,24,30,36,42,48),
           type="Ljung-Box")


cor.arma(ajuste2)

######################################ajustr 3


ajuste3 <- Arima(datos.train.ts,
                 order = c(2,1,1),
                 method = "ML")
ajuste3

tsdiag(ajuste3)

acf(ajuste3$residuals, lag.max = 45, xlab = "Retardo", main="")

pacf(ajuste3$residuals,  lag.max = 45,xlab = "Retardo", main="")

Box.test.2(residuals(ajuste3),
           nlag = c(6,12,18,24,30,36,42,48),
           type="Ljung-Box")

cor.arma(ajuste3)

##################################### ajuste 4

library(lmtest)
ajuste4 <- Arima(datos.train.ts,
                 order = c(1,1,0),
                 seasonal = list(order = c(0,0,1), period=12),
                 method = "ML")
ajuste4
coeftest(ajuste4)
tsdiag(ajuste4)

acf(ajuste4$residuals, lag.max = 45, xlab = "Retardo", main="", lwd=3)
pacf(ajuste4$residuals,  lag.max = 45,xlab = "Retardo", main="", lwd=3)

Box.test.2(residuals(ajuste4),
           nlag = c(6,12,18,24,30,36,42,48),
           type="Ljung-Box")

cor.arma(ajuste4)
plot(ajuste4)



################################# 5

ajuste5 <- Arima(datos.train.ts,
                 order = c(1,1,0),
                 seasonal = list(order = c(1,0,1), period=12),
                 method = "ML")
ajuste5

coeftest(ajuste5)
acf(ajuste5$residuals, lag.max = 45, xlab = "Retardo", main="", lwd = 3)
pacf(ajuste5$residuals,  lag.max = 45,xlab = "Retardo", main="", lwd= 3)

Box.test.2(residuals(ajuste5),
           nlag = c(6,12,18,24,30,36,42,48),
           type="Ljung-Box")

cor.arma(ajuste5)



####################### 6

ajuste3 <- Arima(datos.train.ts,
                 order = c(1,1,0),
                 seasonal = list(order = c(0,1,1), period=12),
                 method = "ML")
ajuste3

tsdiag(ajuste3)

acf(ajuste3$residuals, lag.max = 45, xlab = "Retardo", main="", lwd = 3)
pacf(ajuste3$residuals,  lag.max = 45,xlab = "Retardo", main="", lwd = 3)

Box.test.2(residuals(ajuste3),
           nlag = c(6,12,18,24,30,36,42,48),
           type="Ljung-Box")

cor.arma(ajuste3)



############################7
ajuste7 <- Arima(datos.train.ts,
                 order = c(4,1,1),
                 method = "ML")
ajuste7

tsdiag(ajuste7)

acf(ajuste7$residuals, lag.max = 50, xlab = "Retardo", main="")
pacf(ajuste7$residuals,  lag.max = 45,xlab = "Retardo", main="")

Box.test.2(residuals(ajuste7),
           nlag = c(6,12,18,24,30,36,42,48),
           type="Ljung-Box")

cor.arma(ajuste7)



################################## 8

library(caschrono)
library(lmtest)
ajuste6 <- Arima(datos.train.ts,
                 order = c(1,1,1),
                 seasonal = list(order = c(0,1,1), period=12),
                 method = "ML")

ajuste6

coeftest(ajuste6)
tsdiag(ajuste6)

acf(ajuste6$residuals, lag.max = 25, xlab = "Retardo", main="", lwd = 3)
pacf(ajuste6$residuals,  lag.max = 25,xlab = "Retardo", main="", lwd = 3)

Box.test.2(residuals(ajuste6),
           nlag = c(6,12,18,24,30,36,42,48),
           type="Ljung-Box")

cor.arma(ajuste6)


# Residuo antes de incluir intervenciones

acf(ajuste6$residuals, lag.max=25, xlab="Retardo", main="")
pacf(ajuste6$residuals, lag.max=25, xlab="Retardo", main="")

prediccion <- as.data.frame(predict(ajuste6, n.ahead=12))


#L?mites de confianza al 95%

U <- prediccion$pred + 2*prediccion$se
L <- prediccion$pred - 2*prediccion$se

ts.plot(datos.train.ts, prediccion$pred, U, L, col=c(1,2,4,4), lty = c(1,1,2,2))
legend("bottomleft", c("Actual", "Forecast", "Error Bounds (95% Confidence)"),
       col=c(1,2,4), lty=c(1,1,2))


# Se definen los regresores (festividades )

calendario <- datos[,-c(2,6)]

library(lubridate)

calendario.train <- subset(calendario, "2001-01-01"<=fecha & fecha<="2012-12-01")
calendario.train <- as.matrix(calendario.train[,2:ncol(calendario.train)])
calendario.validate <- subset(calendario,fecha>"2012-12-01")
calendario.validate <- as.matrix(calendario.validate[,2:ncol(calendario.validate)])




# Se añade el calendario al Arima ajustado:

ajuste6ConCalendario <- Arima(datos.train.ts,
                            order = c(1,1,1),
                            seasonal = list(order = c(0,1,1), period=12),
                            method="ML",
                            xreg = calendario.train)

ajuste6ConCalendario



coeftest(ajuste6ConCalendario)

Box.test.2(residuals(ajuste6ConCalendario),
           nlag = c(6,12,18,24,30,36,42,48),
           type="Ljung-Box")
tsdiag(ajuste6ConCalendario)

acf(ajuste6ConCalendario$residuals, lag.max = 25, xlab = "Retardo", main="")
pacf(ajuste6ConCalendario$residuals,  lag.max = 25,xlab = "Retardo", main="")


########### El año bisiesto no es significativo lo extraemos del modelo

ajuste6ConCalendario <- Arima(datos.train.ts,
                              order = c(1,1,1),
                              seasonal = list(order = c(0,1,1), period=12),
                              method="ML",
                              xreg = calendario.train[, 1:2])

ajuste6ConCalendario

coeftest(ajuste6ConCalendario)
cor.arma(ajuste6ConCalendario)


Box.test.2(residuals(ajuste6ConCalendario),
           nlag = c(6,12,18,24,30,36,42,48),
           type="Ljung-Box")
tsdiag(ajuste6ConCalendario)

acf(ajuste6ConCalendario$residuals, lag.max = 25, xlab = "Retardo", main="")
pacf(ajuste6ConCalendario$residuals,  lag.max = 25,xlab = "Retardo", main="")




############ Identificacion de outliers

library(tsoutliers)
listaOutliers <- locate.outliers(ajuste6ConCalendario$residuals,
                                 pars = coefs2poly(ajuste6ConCalendario),
                                 types = c("AO", "LS", "TC"),cval=3)
listaOutliers

plot.ts(datos.train.ts, x = datos.train$fecha, axes = FALSE, ann = FALSE, frame.plot = TRUE)
par(new=TRUE)
plot((datos.train$tasaParoMensual), x=datos.train$fecha , col="darkred", type = "l",  xaxp = c(1,2,4000))
plot.ts(ajuste6ConCalendario$residuals, x = as.factor(), axis(side=1, at=c(0:144)), grid())
### se idenfitica los aoutlieer  AO 92 y el LS 83, que incluiremos en el modelo

outliers <- outliers(c( "AO","LS"), c(73, 65))
outliersVariables <- outliers.effects(outliers, length(ajuste6ConCalendario$residuals))
calendarioMasOutliers <- cbind(calendario.train,outliersVariables)

ajusteConOutliers <- Arima(datos.train.ts,
                           order = c(1,1,1),
                           seasonal = list(order = c(0,1,1), period=12),
                           method="ML",
                           xreg = calendarioMasOutliers[, -c(3)])

ajusteConOutliers
coeftest(ajusteConOutliers)

cor.arma(ajusteConOutliers)


Box.test.2(residuals(ajusteConOutliers),
           nlag = c(6,12,18,24,30,36,42,48),
           type="Ljung-Box")
tsdiag(ajusteConOutliers)

par(new =T)
par(mfrow=c(2,1))
acf(ajusteConOutliers$residuals, lag.max = 25, xlab = "Retardo", main="", lwd= 3)
pacf(ajusteConOutliers$residuals,  lag.max = 25,xlab = "Retardo", main="", lwd= 3)

plot(ajusteConOutliers$residuals, axis(side=1, at=c(0:144)))




######################################### Aprox Finitas TasaParo

calendarioTP <- datos[,-c(2, 6)]

calendario.train <- subset(calendarioTP, "2001-01-01"<=fecha & fecha<="2012-12-01")
calendario.train <- as.matrix(calendario.train[,2:ncol(calendario.train)])
calendario.validate <- subset(calendarioTP,fecha>"2012-12-01")
calendario.validate <- as.matrix(calendario.validate[,2:ncol(calendario.validate)])

tp.s <- as.ts((log(datos$tasaParoMensual)), frequency= 12)
library(TSA)
for( i in seq(1,48)){
diix <- tp.s - zlag(tp.s, 1)
#diff1 <- zlag(tp.s,1)
ajuste6ConCalendarioTP <- Arima(datos.train.ts,
                              order = c(1,1,1),
                              seasonal = list(order = c(0,1,1), period=12),
                              method="ML",
                              xreg = cbind(calendario.train[, c(1,2)], lag=diix[1:144], outliersVariables ))

ajuste6ConCalendarioTP
print(i)
print(coeftest(ajuste6ConCalendarioTP))
}
cor.arma(ajuste6ConCalendarioTP)


Box.test.2(residuals(ajuste6ConCalendarioTP),
           nlag = c(6,12,18,24,30,36,42,48),
           type="Ljung-Box")
tsdiag(ajuste6ConCalendarioTP)

acf(ajuste6ConCalendarioTP$residuals, lag.max = 25, xlab = "Retardo", main="", na.action = na.pass)
pacf(ajuste6ConCalendarioTP$residuals,  lag.max = 25,xlab = "Retardo", main="", na.action = na.pass)






#################################Prediccion


outliersNews <-outliersVariables[133:144,]
calendarioToPredict <- cbind(calendario.validate[, c(1,2)],  outliersNews)

prediccion <- as.data.frame(predict(ajusteConOutliers, n.ahead=12,newxreg=calendarioToPredict), na.action= na.pass)


#Límites de confianza al 95%
# Si hubiesemos hecho una transformación habría que desacerla, en este caso no se ha hecho

U <- prediccion$pred + 2*prediccion$se
L <- prediccion$pred - 2*prediccion$se
par(mfrow=c(1,1))
ts.plot(exp(datos.train.ts), exp(prediccion$pred), exp(U), exp(L), col=c(1,2,4,4), lty = c(1,1,2,2))
legend("bottomleft", c("Actual", "Forecast", "Error Bounds (95% Confidence)"),
       col=c(1,2,4), lty=c(1,1,1), cex=0.65)



##### El MAPE con los datos Predichos vs Reales


# Deshacemos el logaritmo


realYPredMensual <- data.frame(Fecha = datos.validate$fecha,
                              Real = exp(datos.validate$target),
                              Prediccion = exp(prediccion$pred+0.5*prediccion$se**2))

realYPredMensual$MAPE <- abs(100*(realYPredMensual$Real-realYPredMensual$Prediccion)/realYPredMensual$Real)

mean(realYPredMensual$MAPE, na.rm = T)

realYPredMensual$MAPE[1]
realYPredMensual$MAPE[12]




ts.plot(datos.validate2$target, exp(prediccion$pred), col=c("navy","darkgreen"))
legend("bottomleft", c("Actual", "Forecast"),
       col=c("navy","darkgreen"), lty=c(1,1,2))





#################################Prediccion SSbre Training

pred <- as.data.frame(ajusteConOutliers$fitted)
realYPrediccionTrainning <- cbind(datos.train,pred)
realYPrediccionTrainning$MAPEM <- abs(100*(exp(realYPrediccionTrainning$target)-exp(realYPrediccionTrainning$x))/exp(realYPrediccionTrainning$target))
mean(realYPrediccionTrainning$MAPEM, na.rm =1)
