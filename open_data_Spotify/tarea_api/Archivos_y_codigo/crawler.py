# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 22:52:00 2018

@author: aolivares
"""

import requests
from bs4 import BeautifulSoup as bs
import time
import pandas as pd
import re

fixed_url = "http://billboardtop100of.com/"
song_list = []


def append_to_df(df_song, year, rank, name, singer):
    df_song.loc[row, 0] =year
    df_song.loc[row, 1] =rank
    df_song.loc[row, 2] =name
    df_song.loc[row, 3] =singer



df_song = pd.DataFrame(columns=range(0,4))


                  
## Para 1940:
request_data = requests.get(fixed_url+"336-2")
data = request_data.text
soup = bs(data, "html.parser")
page =  (soup.find("p"))
start = 0
rank = 1
row =0
col = 0
for i in re.finditer("[0-9]\.", str(page), flags=0):
    end = str(page).find("<br/>", i.start())
    song_str = str(page)[i.start()+3:end].split("–")
    print(song_str[0])
    append_to_df(df_song, 1940, rank, song_str[1].replace("</p", "").replace("/", ""), song_str[0] , )
    rank +=1
    row +=1


for i in range(1941,2017):
    slug_url = fixed_url+ str(i)+"-"+"2"
    print(slug_url)
    request_data = requests.get(slug_url)
    data = request_data.text
    soup = bs(data, "html.parser")
    #print(soup)
    
    if soup.find_all("td"):
        for td in soup.find_all("td"):
            
            if col ==0:
                df_song.loc[row, col] =i
                col +=1
            if (i == 2015):
                df_song.loc[row, col]= td.find("h6").get_text()
            else:
                df_song.loc[row, col]= td.get_text()
            #print("Zero", col, row)
            col +=1
            if col >3:
                col = 0
                row +=1
        #time.sleep(5)
    else: 
        rank = 1
        if ( len(soup.find_all("p"))>2):
            
            for p in soup.find_all("p"):
                if len(p.text.split(".")) >1:
                    text_song = (p.text.split(".")[1][:p.text.split(".")[1].find("\n")]).split("by")
                    try:
                        append_to_df(df_song, i, rank, text_song[0], text_song[1] )
                        rank +=1
                    except:
                        continue
                    row +=1
        else:
            page =  (soup.find_all("p"))
            for nombre_interprete in re.finditer("\.", str(soup.find("p"))):
                end = str(page).find("<br/>", nombre_interprete.start())
                song_str = str(page)[nombre_interprete.start()+3:end].split("by")
                #print(song_str)
                print(len(song_str))
                if (len(song_list)>1):
                    append_to_df(df_song, i, rank, song_str[0], song_str[1].replace("</p", "").replace("/", "") )
                else: 
                    song_str = str(page)[nombre_interprete.start()+3:end].split("–")
                    append_to_df(df_song, i, rank, song_str[0], song_str[1].replace("</p", "").replace("/", "") )
                rank +=1
                row +=1
                

### Guardamos en formato .csv     #########################
df_song.columns = ["year", "rank", "singer", "song"]

df_song.to_csv("songs.csv")




df_song = pd.read_csv("songs.csv", encoding = "cp1252")


import matplotlib.pyplot as plt   
plt.hist(df_song.loc[:,0])     

import seaborn as sns
sns.set(color_codes=True)  
sns.distplot(df_song.loc[:,"0"], kde=False, rug=True);        
plt.hist(df_song.loc[:, "0"].value_counts())

df_song.loc[:,:]

sum(df_song.loc[:,"0"] == 1945)


df_song.to_csv("songs.csv")

data = request_data.text
soup = bs(data, "html.parser")
soup.find_all("td")
if soup.find_all("td"):
    print("zero")
else: 
    page =  (soup.find_all("p"))
    
len(soup.find_all("p"))    
    
print(str(page))
start = 0
for i in re.finditer("\.", str(page), flags=0):
    #start = 0
    #foo = re.search(i, str(page))
    #print(i.start())
    end = str(page).find("<br/>", i.start())
    #print(str(page)[i.start()+1:end])
    song_str = str(page)[i.start()+1:end].split("–")
    print(song_str[0])
    print(song_str[1].replace("</p", "").replace("/", ""))
    
    
for p in soup.find_all("p"):
    if len(p.text.split(".")) >1:
        text_song = (p.text.split(".")[1][:p.text.split(".")[1].find("\n")]).split("by")
        print(text_song[0])
        print(text_song[1])
         #print(p.text.split(".")[1].find("\n"))
         
         
         
page =  (soup.find_all("p"))
for nombre_interprete in re.finditer("\.", str(soup.find("p"))):
    end = str(page).find("<br/>", nombre_interprete.start())
    song_str = str(page)[nombre_interprete.start()+3:end].split("by")
    #print(song_str)
    print(len(song_str))
    if (len(song_list)>1):
        df_song.loc[row, 0] =i
        df_song.loc[row, 2] =song_str[0]
        df_song.loc[row, 3] =song_str[1].replace("</p", "").replace("/", "")
    else: 
        song_str = str(page)[nombre_interprete.start()+3:end].split("–")
        df_song.loc[row, 0] =i
        df_song.loc[row, 2] =song_str[0]
        df_song.loc[row, 3] =song_str[1].replace("</p", "").replace("/", "")
    row +=1