# -*- coding: utf-8 -*-

# Import required packages
import os
import sys

# Configuration properties
APP_NAME = 'spark-sql-functions'
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

from pyspark import SparkConf
from pyspark.sql import SparkSession

conf = SparkConf().setAppName(APP_NAME)
conf = conf.setMaster(MASTER)
spark = SparkSession.builder.config(conf = conf).getOrCreate()
sc = spark.sparkContext

from pyspark.sql.types import Row
from pyspark.sql.functions import lower, col, greatest

artist = sc.textFile('data/artists.tsv')
songs= sc.textFile('data/songs.tsv')
album = sc.textFile('data/albums.tsv')

def parseArtist(line):
    fields = line.split('\t')
    return Row(artist_id = fields[0],
               name = fields[1],
               hotness= float(fields[2]) if fields[2] != 'NA' else 0.0,
               familiarity = float(fields[3]) if fields[3] != 'NA' else 0.0,
               location = fields[4])

def parseAlbum(line):
    fields = line.split('\t')
    return Row(album_id = fields[0],
               title = fields[1])

def parseSong(line):
    fields = line.split('\t')
    return Row(song_id = fields[0],
               title_song = fields[1],
               year = int(fields[2]) if fields[2] != 'NA' else 0,
               hotness_song= float(fields[3]) if fields[3] != 'NA' else 0.0,
               artist_id =fields[4],
               album_id = fields[5],
               duration = float(fields[6]) if fields[6] != 'NA' else 0.0,
               end_of_fade_in= float(fields[7]) if fields[7] != 'NA' else 0.0,
               start_of_fade_out= float(fields[8]) if fields[8] != 'NA' else 0.0,
               tempo = float(fields[9]) if fields[9] != 'NA' else 0.0,
               time_signature = float(fields[10]) if fields[10] != 'NA' else 0.0,
               key = int(fields[11]) if fields[11] != 'NA' else 0,
               loudness = float(fields[12]) if fields[12] != 'NA' else 0.0,
               mode = int(fields[13]) if fields[13] != 'NA' else 0,
               style = fields[14])

artist = artist.map(parseArtist)
songs= songs.map(parseSong)
albums = album.map(parseAlbum)

songs_df = spark.createDataFrame(songs)
artist_df = spark.createDataFrame(artist)
albums_df = spark.createDataFrame(albums)

# 1. ¿Cuál es la canción más larga (duration) del set de datos suministrado?
songs_df.count()
songs_df.select(songs_df.title, songs_df.duration).orderBy('duration', ascending = False).show(1)

# 2. ¿Cuál es el estilo más rápido (tempo) en media?

songs_df.select(songs_df.style, songs_df.tempo).groupBy(songs_df.style).mean().orderBy('avg(tempo)', ascending = False).show(1)

# 3. ¿Cuál es el album más ruidoso (loudness)? ¡¡OJO!! La escala de decibelios es negativa.

song_album_df = albums_df.join(songs_df, on = 'album_id', how = 'inner')
song_album_df.select(song_album_df.title, song_album_df.loudness).groupBy(song_album_df.title).mean().orderBy('avg(loudness)', ascending = False).show(1)

# 4. ¿Cuales son los 5 artistas, ubicados en UK, con mayor número de canciones en escala menor (mode = 1)?
song_artist_df =artist_df.join(songs_df, on = 'artist_id', how = 'inner')
song_artist_df.filter(((lower(song_artist_df.location).rlike( "uk+")))  & (song_artist_df.mode == 1) ).select(song_artist_df.name).groupBy(song_artist_df.name).count().orderBy('count', ascending = False).show(5)

# 5. Desde 1970 hasta hoy, ¿las canciones son más rápidas (tempo), altas (loudness) y cortas (duration) en media? 
#    Ordena los resultados por año ascendente. 

songs_df.filter(songs_df.year >=1970).select(songs_df.title_song, songs_df.year, songs_df.duration, songs_df.loudness, songs_df.tempo).groupBy(songs_df.year).mean().orderBy('year', ascending = True).show()
# 6. ¿Cuál es el estilo que más abusa de los efectos de fade in y fade out (mayor número de segundos en zona de fade)?

songs_df.select(songs_df.style, (-songs_df.end_of_fade_in +songs_df.start_of_fade_out).alias('fade_effect')).groupBy("style").mean().orderBy('avg(fade_effect)', ascending = False).show()
## qawwali
# 7. ¿Cual es el top 10 de artistas más populares (hotness)?
artist_df.select(artist_df.name, artist_df.hotness).orderBy('hotness', ascending = False).show(10)

# 8. Del top 10 de artistas populares, ¿cuál es su canción más popular (hotness)?

artist_10 = artist_df.select(artist_df.name, artist_df.artist_id, artist_df.hotness).orderBy('hotness', ascending = False)
song_artist_df =artist_10.join(songs_df, on = 'artist_id', how = 'inner')

song_artist_df.select(song_artist_df.name, song_artist_df.hotness, song_artist_df.hotness_song, song_artist_df.title_song).groupBy(["name",  "title_song"]).max().orderBy(['max(hotness)', 'max(hotness_song)'], ascending = False).take(10)



# 9. ¿Qué artista utiliza métricas (time_signature) más altas?

song_artist_df =artist_df.join(songs_df, on = 'artist_id', how = 'inner')
song_artist_df.select(song_artist_df.name, song_artist_df.time_signature).groupBy("name").mean().orderBy('avg(time_signature)', ascending = False).show(10)

# 10. ¿Qué nivel de reconocimiento (famliarity) máximo se consigue con cada escala (key)? 

song_artist_df =artist_df.join(songs_df, on = 'artist_id', how = 'inner')
song_artist_df.select(song_artist_df.familiarity, song_artist_df.key).groupBy("key").max().show()
# Stop the spark session
spark.stop() 

