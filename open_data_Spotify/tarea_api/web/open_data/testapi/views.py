from django.shortcuts import render, render_to_response
from django.core import serializers
# Create your views here.
from django.core.paginator import Paginator, InvalidPage, EmptyPage

#from django.core.urlresolvers import reverse

from testapi.models import *
import numpy as np
import pandas as pd
import json



	
def main(request):
	entrada = Entrada.objects.all().order_by("-fecha")
	paginator = Paginator(entrada,3)
	try:
		pagina = int(request.GET.get("page", '1'))
	except VaueError: pagina =1
		
	try: 
		entrada = paginator.page(pagina)
	except (InvalidPage, EmptyPage):
		entrada =paginator.page(paginator.num_pages)
		
	return render_to_response("index.html", dict(entrada=entrada, usuario=request.user))
	

	
def codigo(request):
	entrada = Entrada.objects.all().order_by("-fecha")
	paginator = Paginator(entrada,3)
	try:
		pagina = int(request.GET.get("page", '1'))
	except VaueError: pagina =1
		
	try: 
		entrada = paginator.page(pagina)
	except (InvalidPage, EmptyPage):
		entrada =paginator.page(paginator.num_pages)
		
	return render_to_response("codigo.html", dict(entrada=entrada, usuario=request.user))


	
def proceso(request):
	entrada = Entrada.objects.all().order_by("-fecha")
	paginator = Paginator(entrada,3)
	try:
		pagina = int(request.GET.get("page", '1'))
	except VaueError: pagina =1
		
	try: 
		entrada = paginator.page(pagina)
	except (InvalidPage, EmptyPage):
		entrada =paginator.page(paginator.num_pages)
		
	return render_to_response("proceso.html", dict(entrada=entrada, usuario=request.user))
		
	
	

from django.http import JsonResponse
import os.path

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

print(__file__)

##songs = pd.read_csv('songs_spotify.csv' , encoding = "cp1252", index_col=0)
	

def get_decada(request):
    import os
    from os.path import abspath, dirname

		
    songs = pd.read_csv(abspath(dirname(__file__))+'\\songs_spotify.csv' , encoding = "cp1252", index_col=0)
    del songs["0"]
    dato = request.GET.get('dato')
    seleccion = request.GET.get('seleccion')
    grupo_year  = request.GET.get('grupo')
    print(seleccion + " Seleccion")
    #grupo = [str(x) for x in grupo]
    #print(dato)
    cancion_list = []
    if dato.isdigit():
        print(dato)
		
        grupo =(songs.loc[(songs.year.between(int(dato)-11,int(dato), inclusive=False) )].select_dtypes(include=[np.number]).drop(["duration_ms", "year", "rank", "mode", "time_signature" , "key", "tempo"], axis=1)).drop_duplicates().mean()
        grupo = grupo.tolist()
        grupo_parcial = pd.read_csv(abspath(dirname(__file__))+'\\grupo'+str(int(seleccion)-10)+'.csv',index_col=0 )
        ngrupo = grupo_parcial.shape[0]
        cancion = []
        
    else:
        cancion = np.array(songs.loc[(songs[ "song"]).str.contains(str(dato))].select_dtypes(include=[np.number]).drop(["duration_ms", "year", "rank", "mode", "time_signature" , "key", "tempo"], axis=1))[0]
        cancion = cancion.tolist()
        grupo_parcial = pd.read_csv(abspath(dirname(__file__))+'\\grupo'+str(int(seleccion)-10)+'.csv',index_col=0 )
        ngrupo = grupo_parcial.shape[0]
        grupo =np.array(grupo_parcial.loc[ grupo_parcial.grupo == int(grupo_year),:].drop(["year", "grupo"], axis=1))[0]
        grupo = grupo.tolist()
    respuestas = {"grupo": grupo, "cancion":cancion, "ngrupo": ngrupo }

    dato = {
        'is_taken': True
    }
    if dato['is_taken']:
        dato['error_message'] = 'Error Ha Ocurrido.'
    return JsonResponse(respuestas, safe=False)