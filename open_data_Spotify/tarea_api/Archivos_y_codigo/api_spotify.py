# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 11:01:43 2018

@author: aolivares
"""

import pandas as pd 
import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials 
import time

#spoty = sp.Spotify() 
cid ="3e81bcfc307a4bcf9d658c0674059dfb" 
secret = "089b1522c02243a3953bc25267693e65" 
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
spoty = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
spoty.trace=True 


print(spoty.client_credentials_manager)


def get_id_song(song_list, q_singer):
    cond =-1
    for i, t in enumerate(song_list):
        #print(' ', i, type(t))
        for k,v in enumerate(t["artists"]):
            #print(type(v))
            if cond == -1:
                for ind, name in v.items():
                    #print(type(v["name"].lower()),type(("The Andrews Sisters").lower()) )
                    
                    if str(v["name"]).lower() == q_singer.lower():
                        print("True", i)
                        cond = i                    
                    else: 
                        print(v["name"])
            print(cond)
    return cond

def get_id_singer(song_list, q_song):
    cond =-1
    for i, t in enumerate(song_list):
        #print(' ', i, type(t))
        if cond ==-1:
            print(t["name"])
            if t["name"].lower() == q_song.lower():
                print (i)
                cond = i

    return cond




##########################################################################



########### leer el archivo de listado de canciones
df_song_list = pd.read_csv("songs.csv", encoding = "cp1252")


x= pd.DataFrame(columns=['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'type', 'id', 'uri', 'track_href', 'analysis_url', 'duration_ms', 'time_signature'])


#for index, row in df_song_list.iterrows():
for index, row in (df_song_list.loc[:,:]).iterrows():

    #print(row[3], row[4])
    zeros = False
    features = ""
    q_singer = row[3]
    q_song = row[4]
    result = spoty.search(q_song, limit=20, offset = 5)
    song_list =  result['tracks']['items']
    id_cond =  get_id_song(song_list, q_singer)
    print(id_cond)
    
    if (id_cond !=-1):
        #print(result['tracks']['items'][id_cond]["id"])
        audio_id= result['tracks']['items'][id_cond]["id"]
    else:
        #print("No encontrado")
        q_song= q_song.replace("’", "")
        #print (q_song.split("(")[0]) 
        if q_song.find("(") != 0:
            result = spoty.search(q_song.split("(")[0], limit=50, offset = 5)
        else:
            result = spoty.search(q_song.split(")")[1], limit=50, offset = 5)
        song_list =  result['tracks']['items']
        id_cond =  get_id_song(song_list, q_singer)
        print(id_cond)
        if id_cond == -1:
            result = spoty.search(q_singer, limit=50, offset = 5)
            song_list =  result['tracks']['items']
            id_cond =  get_id_singer(song_list, q_song)
            try:
                audio_id= result['tracks']['items'][id_cond]["id"]
                zeros = False
            except:
                features_zeros = {'danceability': 0, 'energy': 0, 'key': 0, 'loudness': 0, 'mode': 0, 'speechiness': 0, 'acousticness': 0, 'instrumentalness':0, 'liveness': 0, 'valence': 0, 'tempo': 0, 'type': 0, 'id': 0, 'uri': 0, 'track_href': 0, 'analysis_url': 0, 'duration_ms': 0, 'time_signature': 0}
                zeros= True
            print(id_cond)

    if not zeros:
        features = spoty.audio_features(audio_id)
        for feature in features:
            x = x.append([feature], ignore_index=True)
    else:
        x = x.append([features_zeros], ignore_index=True)
    
    time.sleep(1)
                


sum(x.sum(axis=1) ==0)
    
faltantes =x.loc[x.sum(axis=1) ==0]



#### Con los faltantes vamos a tomar el primer resultado en googgle, para ellos utilizaremos la libraria google

from googlesearch import search
import re
x1 = x
faltantes =x.loc[x.sum(axis=1) ==0]
for index, row in df_song_list.loc[faltantes.index].iterrows():
    #print(index, row[3], row[4]+ " track spotify  -karaoke")
    print(index, " ".join(row[3].split()[:2]).replace("feat.", " "),  row[4]+ " track spotify  -karaoke" )
    for url in search( " ".join(str(row[3]).split()[:2]).replace("feat.", " ")+ " " +row[4].replace("\n", " ")+ " track spotify  -karaoke", stop=1, num =1):
        #print(url)
        str_pos = url.find("track/")        
        if (str_pos != -1) and (re.match('^[\w-]+$', url[str_pos+7:])) :
            id_song_google = url[str_pos+6:]
            #print(index, id_song_google)
            features = spoty.audio_features(id_song_google)
            for feature in features:
                print((index), type(feature))
                x1.loc[index] = (pd.DataFrame(feature, index=[index])).loc[index]
                
            


( df_song_list.loc[x.loc[x.sum(axis=1) == 0].index, "year"].value_counts()).plot(kind = "bar")

sum(x.sum(axis=1) ==0)


##### Revisamos posibles filas duplicadas

#sum(y[y.columns.difference(['year'])].duplicated())

#Borramos las filas de las que no pudimos obtener valor:

x = x.drop(x.loc[x.sum(axis=1) ==0].index)


##### Construimos el Dataset y Guardamos como .csv
y =  pd.concat([df_song_list, x], axis=1)

del y['Unnamed: 0']

y = y.drop([41, 68, 127, 232, 270, 274, 428, 870, 1081, 1754, 3299, 4504, 5932, 6039, 6355])


y.to_csv("songs_spotify.csv")



###############################################################################fin


df_song_list.loc[x.loc[x.sum(axis=1) == 0].index, "year"].value_counts()
df_song_list.loc[x.loc[x.sum(axis=1) == 0].index, :].loc[df_song_list["year"] == 2002]


df_song_list.head()
df_song_list.tail()


x
x.columns
df_song_list.columns

y = df_song_list.merge(x,how="outer", left_on='0', right_on=index)
y =  pd.concat([df_song_list, x], axis=1)

del y['Unnamed: 0']

y.to_csv("songs_spotify.csv")

x1 = x
from googlesearch import search

faltantes =x.loc[x.sum(axis=1) ==0]
for index, row in df_song_list.loc[x.loc[x.sum(axis=1) == 0].index, :].iterrows():
    print("Search:", row[3]+ " " +row[4].replace("\n", "") + "track spotify" )
    for url in search( row[3]+ " " +row[4].replace("\n", "") + "track spotify", stop=1, num =3):
        print(url)
        str_pos = url.find("track/")        
        if (str_pos != -1) and (re.match('^[\w-]+$', url[str_pos+7:])) :
            id_song_google = url[str_pos+6:]
            print(index, id_song_google)
            features = spoty.audio_features(id_song_google)
            for feature in features:
                print((index), type(feature))
                x1.loc[index] = (pd.DataFrame(feature, index=[index])).loc[index]
            