

#####################################
###### Tare 2 Progrmacion en R ######
##    Armando Olivares            ##
####################################

#Medición de tiempos. Implementa una función utilizando un bucle for que busque el primer elemento 
#divisible entre dos dentro de un vector. Cambia la implementación anterior por un bucle while. 
#Comprueba cómo afecta el tamaño del vector a ambas implementaciones. 
#Realiza mediciones de tiempos con la función proc.time(). 

funcion_test_for_proc <- function(x){
  for (i in 1:length(x) ) { 
    if(x[i]%%2==0){
      print(x[i])
      break
     }
  }
}





funcion_test_while_proc <- function(x){
  
  i = 1
  while(i <length(x)){
 
    if(x[i]%%2==0){
      print(x[i])
      #break
      i=length(x)+1
    }else{
      i=i+1
    }
}
}


x2 <- round(runif(100000000, 0.0, 1.)*91)

### Para la implemantación con el for tenemos:
ptm <- proc.time()
funcion_test_for_proc(x2)
proc.time() -ptm

### Para el while
ptm <- proc.time()
funcion_test_while_proc(x2)
proc.time() - ptm


