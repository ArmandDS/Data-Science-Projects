from django.db import models

# Create your models here.

import pandas as pd
class Entrada(models.Model):
	titulo=models.CharField(max_length = 100)
	contenido = models.TextField()
	fecha = models.DateTimeField(auto_now_add= True)
	
	def __str__(self):
		return self.titulo