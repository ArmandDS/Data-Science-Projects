# -*- coding: utf-8 -*-

# Import required packages
import os
import sys

# Configuration properties
APP_NAME = 'spark-sql-queries'
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

songs_df.createOrReplaceTempView('songs')
artist_df.createOrReplaceTempView('artist')
albums_df.createOrReplaceTempView('albums')



# 1. ¿Cuál es la canción más larga (duration) del set de datos suministrado?
spark.sql('''SELECT songs.title_song, songs.duration
             FROM songs
             ORDER BY songs.duration DESC''').show(1)

# 2. ¿Cuál es el estilo más rápido (tempo) en media?

spark.sql('''SELECT songs.style, avg(songs.tempo) as avg_tempo
             FROM songs
             GROUP BY songs.style
             ORDER BY avg_tempo DESC''').show(1)

# 3. ¿Cuál es el album más ruidoso (loudness)? ¡¡OJO!! La escala de decibelios es negativa.

spark.sql('''SELECT albums.title, avg(songs.loudness) as avg_loud, albums.title
             FROM songs, albums
             WHERE songs.album_id = albums.album_id
             GROUP BY albums.title
             ORDER BY avg_loud DESC''').show(1)


# 4. ¿Cuales son los 5 artistas, ubicados en UK, con mayor número de canciones en escala menor (mode = 1)?

spark.sql('''SELECT   artist.name, count(songs.mode) as total
             FROM songs, artist
             WHERE songs.artist_id = artist.artist_id 
             AND songs.mode = 1 
             AND artist.location rlike 'UK+'
             GROUP By (artist.name)
             ORDER by total DESC
             ''').show(5)




# 5. Desde 1970 hasta hoy, ¿las canciones son más rápidas (tempo), altas (loudness) y cortas (duration) en media? 
#    Ordena los resultados por año ascendente. 


spark.sql('''SELECT  songs.year,avg(songs.tempo), avg(songs.loudness), avg(songs.duration) 
             FROM songs
             WHERE songs.year >= 1970 
             GROUP BY songs.year
             ORDER BY  songs.year ASC''').show(10)



# 6. ¿Cuál es el estilo que más abusa de los efectos de fade in y fade out (mayor número de segundos en zona de fade)?

spark.sql('''SELECT  songs.style, avg(songs.start_of_fade_out - songs.end_of_fade_in) as total
             FROM songs
             WHERE songs.year >= 1970 
             GROUP BY songs.style
             ORDER BY  total DESC''').show(10)



# 7. ¿Cual es el top 10 de artistas más populares (hotness)?


spark.sql('''SELECT   artist.name, artist.hotness
             FROM artist
             ORDER by artist.hotness DESC
             ''').show(10)



# 8. Del top 10 de artistas populares, ¿cuál es su canción más popular (hotness)?


spark.sql('''
          select name, max_artist, max_songs, title_song
          from(
          Select t1.artist_id, t1.max_artist, t2.max_songs
          from(
          SELECT  artist.artist_id,max(artist.hotness) as max_artist
             FROM  artist
             GROUP BY artist.artist_id 
             ORDER by max_artist DESC ) t1
            inner join (SELECT  songs.artist_id,max(songs.hotness_song) as max_songs
             FROM  songs
             GROUP BY songs.artist_id 
             ORDER by max_songs DESC ) t2
            on t1.artist_id = t2.artist_id
            order by (max_artist, max_artist) DESC) t3
            inner  join( SELECT  artist.name, artist.artist_id, songs.title_song, songs.hotness_song
             FROM songs, artist
             WHERE songs.artist_id = artist.artist_id  ) t4
            on t3.artist_id = t4.artist_id
            and t3.max_songs = t4.hotness_song
             ORDER by (max_artist,max_songs) DESC
            
             ''').show(10)




# 9. ¿Qué artista utiliza métricas (time_signature) más altas?

spark.sql('''SELECT  artist.name,  avg(songs.time_signature) as total
             FROM songs, artist
             WHERE songs.artist_id = artist.artist_id 
             GROUP BY artist.name
             ORDER by total DESC
             ''').show(10)




# 10. ¿Qué nivel de reconocimiento (famliarity) máximo se consigue con cada escala (key)? 



spark.sql('''SELECT   songs.key, max(artist.familiarity) as max_familiarity
             FROM songs, artist
             WHERE songs.artist_id = artist.artist_id 
             GROUP BY songs.key
             ORDER by max_familiarity DESC
             ''').show()




# Stop the spark session
spark.stop() 

