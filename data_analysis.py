# -*- coding: utf-8 -*-.
"""
Editor de Spyder

Este es un archivo temporal.
"""
# %% Importar liberías

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from unidecode import unidecode

# %% Leer datas

data_nc = pd.read_csv('data_ESE.csv')
data_src = pd.read_csv('data_ESE_sources.csv')

# %% Organizar datos de las NC

# Nombres de las columnas del dataset de NC
col_nc = data_nc.columns
# Excluir las filas con NaN
nc = data_nc[~data_nc['Núm.'].isna()]
# Extraer la columna de los numerales que se pierde
# cuando se eliminan los NaN
numerales = data_nc[['Núm.', 'Norma y Numeral']]
numerales = numerales.ffill()
numerales = numerales[numerales['Norma y Numeral']
                      != 'Resolución 3100 de 2019:'].dropna().drop_duplicates()
# Extraer solo las columnas con información de interés
nc = nc[['Núm.', 'Descripción', 'Proceso', 'Fecha de Creación',]]
nc_clean = pd.merge(nc, numerales, on='Núm.')

# %% Organizar datos de fuentes de NC

# Nombres de las columnas del dataset de NC
col_src = data_src.columns
# Extraer datos solo de NC y las columnas de interés
sources = data_src[data_src['Tipo'] == 'No Conformidad'][['Num', 'Fuente']]


# %% Crear dataset global

# Ajustar nombres de columnas del dataset nc_clean
# Extraer los nombres en una lista
col_nc = nc_clean.columns.tolist()
# Pasar todo a minúscula y quitar tildes -unidecode quita tildes-
col_nc = [unidecode(item.lower()) for item in col_nc]
# Eliminar espacios en blanco y puntos
col_nc = [item.replace(".", "") for item in col_nc]
col_nc = [item.replace(" ", "_") for item in col_nc]
# Reemplazar nombres en el dataset nc_clean
nc_clean.columns = col_nc

# Ajustar nombres de columnas del dataset sources
col_src = sources.columns.tolist()
# Pasar todo a minúscula
col_src = [item.lower() for item in col_src]
# Reemplazar nombres en el dataset sources
sources.columns = col_src

# Unir datasets
nc_all = pd.merge(nc_clean, sources, on='num')

# %% Enriquecer el dataset de NC

# Verificar únicos en fuente
'''nc_all['fuente'].unique()'''

# Reemplazar uno de los valores para garantizar homogeneidad en los datos de la variable (Fuente - Municipio - UAS)
nc_all['fuente'] = nc_all['fuente'].str.replace(
    'Auditoría de Calidad - AIC',
    'Auditoría de Calidad AIC',
    regex=False
)

# Separar Fuente - Municipio - UAS como columnas independientes
fuente_split = nc_all['fuente'].str.split('-', expand=True)
# Nombrar columnas
fuente_split.columns = ['fuente', 'municipio', 'uas']
# Agregar las nuevas columnas al dataset
nc_final = pd.concat([nc_all.iloc[:, :-1], fuente_split], axis=1)
# Verificar tipos de variables
'''nc_final.info()'''
# Cambiar columna fecha_de_creación a formato fecha
nc_final['fecha_de_creacion'] = pd.to_datetime(
    nc_final['fecha_de_creacion'], errors='coerce')
# Extraer año mes y día en variables independientes
nc_final['año'] = nc_final['fecha_de_creacion'].dt.year
nc_final['mes'] = nc_final['fecha_de_creacion'].dt.month
nc_final['dia'] = nc_final['fecha_de_creacion'].dt.day
# Eliminar la variable de fecha completa
del (nc_final['fecha_de_creacion'])
# Ajustar nombre de columna norma_y_numeral
nc_final.columns = ['num', 'descripcion', 'proceso', 'estandar', 'fuente',
                    'municipio', 'uas', 'año', 'mes', 'dia']

# %% Exportar dataset definitivo
nc_final.to_csv('no_conformidades.csv',
                index=False,
                encoding='utf-8')
