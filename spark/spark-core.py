# -*- coding: utf-8 -*-

# Import required packages
import os
import sys

# Configuration properties
APP_NAME = 'spark-core'
MASTER = 'local[*]'
SPARK_HOME = 'C:\\spark\\spark-2.1.1-bin-hadoop2.7'
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
songs = sc.textFile('C:\\Users\\aolivares\\Desktop\\Procesamiento de datos\\tarea\\solutions\\scripts\\data\\songs.tsv')


def parseKickstarter(line):
    fields = line.split('\t')
    return fields

songs = songs.map(parseKickstarter)

def parseDuration(songs):
    duration = float(songs[6]) if songs[6] != '' else 0.0
    return (songs[1], duration)

max_listen = songs.map(parseDuration).sortBy(lambda songs: songs[1], ascending = False)
max_listen.map(lambda songs: songs[0]).first()

### La canción más larga es :   
##    "Electric Phase / Hot 'n' Ready / Pack It Up 'n' Go / Cherry / Out In The Street / Let It Roll / Too Hot To Handle




# 2. ¿Cuál es el estilo más rápido (tempo) en media?

def parseTempo(songs):
    tempo = float(songs[9]) if songs[9] != '' else 0.0
    return (songs[1], tempo)

max_tempo = songs.map(parseTempo).sortBy(lambda songs: songs[1], ascending = False)
max_tempo.map(lambda songs: songs[0]).first()




# 3. ¿Cuál es el album más ruidoso (loudness)? ¡¡OJO!! La escala de decibelios es negativa.

album = sc.textFile('C:\\Users\\aolivares\\Desktop\\Procesamiento de datos\\tarea\\solutions\\scripts\\data\\albums.tsv')

album = album.map(parseKickstarter)
def parseLoudness(songs):
    loudness= float(songs[12]) if songs[12] != '' else 0.0
    return (songs[5], loudness)

max_loudness = songs.map(parseLoudness)
max_loudness =max_loudness.join(album)
max_loudness = max_loudness.map(lambda el: el[1])
max_loudness.take(2)
group_album = max_loudness.sortBy(lambda loud: loud[0], ascending = False)
group_album.first()

### EL Album con la cancion mas ruidosa es Kongmanivong



# 4. ¿Cuales son los 5 artistas, ubicados en UK, con mayor número de canciones en escala menor (mode = 1)?
artist = sc.textFile('C:\\Users\\aolivares\\Desktop\\Procesamiento de datos\\tarea\\solutions\\scripts\\data\\artists.tsv')
artist = artist.map(parseKickstarter)


def parse_id(songs):
    return(songs[4], songs)

song_id_artist =songs.map(parse_id)
song_id_artist.take(2)
artist_mode = artist.map(lambda artist: (artist[0], artist))

artist_songs = artist_mode.join(song_id_artist)
artist_songs = artist_songs.map(lambda el: el[1])
artist_songs = artist_songs.filter( lambda el: el[1][13]=="1")
artist_songs = artist_songs.filter(lambda el: "uk" in (el[0][4]).lower())
artist_songs = artist_songs.map(lambda el: el[0])
artist_songs = artist_songs.map(lambda el:(el[1],1))
artist_songs.reduceByKey(lambda a,b: a+b).sortBy(lambda el: el[1], ascending = False).take(5)
#[('Radiohead', 7),
# ('Muse', 5),
# ('UK Subs', 5),
# ('Claire Hamill', 5),
# ('Marilyn Horne / Wiener Opernorchester / Henry Lewis', 4)]




# 5. Desde 1970 hasta hoy, ¿las canciones son más rápidas (tempo), altas (loudness) y cortas (duration) en media? 
#    Ordena los resultados por año ascendente. 
 
songs_year = songs.filter(lambda el: int(el[2])>=1970)

songs_tempo_year = songs_year.map(lambda el: (el[2], el[9]))
songs_tempo_year = songs_tempo_year.mapValues(lambda x: (x, 1)).reduceByKey(lambda x, y: (float(x[0])+float(y[0]), float(x[1])+float(y[1]))).mapValues(lambda x: float(x[0])/float(x[1]))

songs_loud_year = songs_year.map(lambda el: (el[2], el[12]))
songs_loud_year = songs_loud_year.mapValues(lambda x: (x, 1)).reduceByKey(lambda x, y: (float(x[0])+float(y[0]), float(x[1])+float(y[1]))).mapValues(lambda x: float(x[0])/float(x[1]))

songs_duration_year = songs_year.map(lambda el: (el[2], el[6]))
songs_duration_year = songs_duration_year.mapValues(lambda x: (x, 1)).reduceByKey(lambda x, y: (float(x[0])+float(y[0]), float(x[1])+float(y[1]))).mapValues(lambda x: float(x[0])/float(x[1]))

song_year_final = songs_tempo_year.join(songs_loud_year).join(songs_duration_year).mapValues(lambda x: x[0] + (x[1], ))
song_year_final.sortBy(lambda el: el[0], ascending = True).take(5)




# 6. ¿Cuál es el estilo que más abusa de los efectos de fade in y fade out (mayor número de segundos en zona de fade)?

#fade_out -fade_in

songs_fade = songs.map(lambda el: (el[14],float(el[8])- float(el[7])))
songs_fade.take(2)
songs_fade.mapValues(lambda x: (x, 1)).reduceByKey(lambda x, y: (float(x[0])+float(y[0]), float(x[1])+float(y[1]))).mapValues(lambda x: float(x[0])/float(x[1])).sortBy(lambda el: el[1], ascending =False).first()



# 7. ¿Cual es el top 10 de artistas más populares (hotness)?
artist.sortBy(lambda el: el[2], ascending =False).take(10)



# 8. Del top 10 de artistas populares, ¿cuál es su canción más popular (hotness)?


artist2 = artist.sortBy(lambda el: el[2], ascending =False)
artist_map = artist2.map(lambda el : (el[0], (el[1], el[2])))
songs_map = songs.map(lambda el : (el[4], (el[1], el[3])))

artist_song_join = artist_map.join(songs_map)

artist_song_join2 = artist_song_join.map(lambda el : el[1])
artist_song_join2.take(2)
artist_song_join2.sortBy(lambda el: (el[0][1], el[1][1]), ascending =False).take(20)

def parseListaSongs(el):
    if el[1][1] == "" or el[1][1] == 'NA':
        x  = 0
    else:
        x = el[1][1]

    return((el[0][0],el[0][1]), (el[1][0], x))

def bestRating(el1, el2):
    if float(el1[1]) > float(el2[1]):
        return el1
    else:
        return el2

artist_song_join2.map(parseListaSongs).reduceByKey(bestRating).sortBy(lambda el: (float(el[0][1]), float(el[1][1])), ascending = False).take(10)



# 9. ¿Qué artista utiliza métricas (time_signature) más altas?

artist_time_sig = artist.map(lambda el : (el[0], el[1]))
song_time_sig = songs.map(lambda el : (el[4], el[10]))
artist_time_sig = artist_time_sig.join(song_time_sig)
artist_time_sig.map(lambda el : el[1]).mapValues(lambda x: (x, 1)).reduceByKey(lambda x, y: (float(x[0])+float(y[0]), float(x[1])+float(y[1]))).mapValues(lambda x: float(x[0])/float(x[1])).sortBy(lambda el : float(el[1]), ascending=False).take(10)


# 10. ¿Qué nivel de reconocimiento (famliarity) máximo se consigue con cada escala (key)? 

artist_familiarity = artist.map(lambda el : (el[0], el[3]))
song_key = songs.map(lambda el : (el[4], el[11]))

max_familiarity = artist_familiarity.join(song_key)

def maxFamiliarity(el1, el2):
    if el1 == "NA":
        el1 = 0
    if el2 == "NA":
        el2 =0
    if float(el1) > float(el2):
        return el1
    else:
        return el2
  

max_familiarity.map(lambda el: (el[1][1], el[1][0])).reduceByKey(maxFamiliarity).sortBy(lambda el : float(el[1]), ascending = False).collect()



# Stop the spark context
sc.stop()
