# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 08:11:18 2018

@author: aolivares
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import seaborn as sns; sns.set() 


np.random.seed(13)

songs = pd.read_csv('songs_spotify.csv' , encoding = "cp1252", index_col=0)
del songs["0"]
songs.head()
print(songs.shape)

### Reseteamos el indices para tener los numero correlativos
songs = songs.reset_index(drop=True)

#### Seleccionamos solo varibles numericas
new_songs = songs.select_dtypes(include=[np.number])
new_songs.head()

pd.isnull(new_songs).sum()

from sklearn.cluster import affinity_propagation

list_year = [1940, 1950,1960,1970,1980,1990,2000,2010]

for year in list_year:
    
    ndf= new_songs.loc[new_songs.year.between(year, year+9), : ]
    
    ndf = ndf.drop(["duration_ms", "year", "rank", "mode", "time_signature" , "key", "tempo"], axis=1)
    
    ndf = ndf.drop_duplicates()

    if ndf.shape[0]> 450:
        ndf = ndf.sample(n=450)
    generacion = ndf.index
    
    ### Estandarizamos con la correlacion
    ndf = ndf.T
    ndf /= ndf.std(axis=0)
    
    
    ### Calcular Matrix de precicion
    
    x_p = (ndf).cov()
    
 
    x_p = np.linalg.inv(x_p)
    
    partial_corr = x_p.copy()
    d = 1 / np.sqrt(np.diag(partial_corr))
    partial_corr *= d
    partial_corr *= d[:, np.newaxis]
    non_zero = (np.abs(np.triu(partial_corr, k=1)) > 0.01)
    
    
    
    ## Construimos los cluster
    cluster_centers_indices , groups = affinity_propagation(x_p,damping=0.95, preference=-5)
    
    groups
    groups.max()
    
    
    
    
    ### Con los index de non zero contruyo el json 
    to_json = pd.DataFrame(columns = ["source", "target", "value"])
    aux= 0
    
    #names = songs.loc[ndf.columns, "song"]
    names = songs.loc[generacion, "song"]
    #sing = songs.loc[ndf.columns, "singer"]
    for i, elem in names.reset_index(drop = True).iteritems():
        #print(elem, type(i))
        #print((non_zero[i].nonzero())[0].size)
        #print(i)
        for ind in non_zero[i].nonzero()[0][i:]:
            #print("source:",elem,"target:", names.reset_index(drop = True)[ind])
            to_json.loc[aux, "source"] = i
            to_json.loc[aux, "target"] =  ind
            to_json.loc[aux, "value"] = 1
            aux +=1
    
 
###### Para Guardar el Json con el Formato adecuado:  
    
    with open("data"+str(year)+".json", "a", encoding= "UTF8") as f:
        f.write('{"nodes": [')
        for i in range(groups.max() + 1):
            #print('Cluster %i: %s' % ((i + 1), ', '.join(names[groups == i])))
            auxiliar = 0
            for name in names[groups == i]:
                f.write('{"name":"'+name+'", "group":'+str(i)+'}, \n' )

        f.write('],"links": ')
        f.write(to_json.to_json(orient='records'))
        f.write('}')
            
##### Generamos el Archivo con las metricas de cada grupo:
    ndf_to_csv = pd.DataFrame(columns = ndf.T.columns)
    for i in range(groups.max() + 1):
       ndf_to_csv.loc[i,:] = ndf.T[groups ==i].mean()
       ndf_to_csv.loc[i, "year"] = year
       ndf_to_csv.loc[i, "grupo"] = i
    
### Guardamos el archivo por década para recuperarlos en la visualización
    ndf_to_csv.to_csv("grupo"+str(year)+".csv")
            
            
            
            

