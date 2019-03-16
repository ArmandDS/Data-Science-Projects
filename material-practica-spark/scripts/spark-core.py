# -*- coding: utf-8 -*-

# Import required packages
import os
import sys

# Configuration properties
APP_NAME = 'spark-core'
MASTER = 'local[*]'
SPARK_HOME = '<ruta a Spark local>'
PYSPARK_LIB = 'pyspark.zip'
PY4J_LIB = 'py4j-0.10.4-src.zip'

# Spark initialization
os.environ['SPARK_HOME'] = SPARK_HOME
sys.path.insert(0, os.path.join(SPARK_HOME, 'python'))
sys.path.insert(0, os.path.join(SPARK_HOME, 'python', 'lib'))
sys.path.insert(0, os.path.join(SPARK_HOME, 'python', 'lib', PYSPARK_LIB))
sys.path.insert(0, os.path.join(SPARK_HOME, 'python', 'lib', PY4J_LIB))

from pyspark import SparkContext, SparkConf

conf = SparkConf().setAppName(APP_NAME)
conf = conf.setMaster(MASTER)
sc = SparkContext.getOrCreate(conf = conf)


# 1. ¿Cuál es la canción más larga (duration) del set de datos suministrado?


# 2. ¿Cuál es el estilo más rápido (tempo) en media?


# 3. ¿Cuál es el album más ruidoso (loudness)? ¡¡OJO!! La escala de decibelios es negativa.


# 4. ¿Cuales son los 5 artistas, ubicados en UK, con mayor número de canciones en escala menor (mode = 1)?


# 5. Desde 1970 hasta hoy, ¿las canciones son más rápidas (tempo), altas (loudness) y cortas (duration) en media? 
#    Ordena los resultados por año ascendente. 


# 6. ¿Cuál es el estilo que más abusa de los efectos de fade in y fade out (mayor número de segundos en zona de fade)?


# 7. ¿Cual es el top 10 de artistas más populares (hotness)?


# 8. Del top 10 de artistas populares, ¿cuál es su canción más popular (hotness)?


# 9. ¿Qué artista utiliza métricas (time_signature) más altas?


# 10. ¿Qué nivel de reconocimiento (famliarity) máximo se consigue con cada escala (key)? 


# Stop the spark context
sc.stop()
