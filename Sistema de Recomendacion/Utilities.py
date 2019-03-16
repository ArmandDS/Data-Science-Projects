# -*- coding: iso-8859-1 -*-

import numpy as np
import pandas as pd
import sys
import string
import nltk
import re

###################################################################### boxplots, histogramas, corrs
def tokenizacion(text):
	"""Se tokeniza el texto, al que anteriormente se cuelve todos los string en minúsculas y se eliminan palabras de una o dos palabras
    
    Args: 
        text: Texto del que se desea tokenizar.
        
    """
	text = text.lower()
	text = re.sub('[0-9]+', '', text)
	text = re.sub('\\b\\w{1,2}\\b', '', text)
	x = nltk.word_tokenize(text)
	return x


def removeStopwords(text):
	"""Se eliminan palabras que carecen de significado
    
    Args: 
        text: Texto del que se desea eliminar las palabras sin significado.
        
    """
	
	stopw = nltk.corpus.stopwords.words('spanish')
	stopw = stopw + ["juguete", "juguetes", "edad", "máxima", "recomendada", "incluye"]
	x = [w.strip() for w in text if w not in stopw]
	return x


def removePunctuation(text):
	"""Se eliminan signos de puntuación
    
    Args: 
        text: Texto del que se desea eliminar los sigbos de puntuación.
        
    """
	stopp = list(string.punctuation)
	stopp.append("''")
	stopp.append("")
	x = [w.strip() for w in text if w not in stopp]
	return x

def arrayToString(text):
	"""Se eliminan signos de puntuación
    
    Args: 
        text: Texto del que se desea eliminar los sigbos de puntuación.
        
    """
	x = ' '.join(text)
	return x	