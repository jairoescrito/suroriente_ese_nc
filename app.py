# -*- coding: utf-8 -*-.
"""
Created on Thu Nov 27 16:45:18 2025
@author: jairoescrito
"""
# app.py

# %% Importar liberías

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from unidecode import unidecode


# =============================================================================
# Primera parte: data_wrangling
# =============================================================================

# %% Leer datas

data_nc = pd.read_csv('datas/data_ESE.csv')
data_src = pd.read_csv('datas/data_ESE_sources.csv')

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

# %% Ajustes a las variables

# Excluir tildes de valores de nombres para garantizar uniformidad en valores por columna
for col in nc_final:
    if nc_final[col].dtype == 'object':
        nc_final[col] = nc_final[col].str.strip()
        nc_final[col] = nc_final[col].apply(
            lambda x: unidecode(x) if pd.notnull(x) else x)

# Eliminar NaN en los datos de UAS
nc_final['uas'] = nc_final['uas'].fillna('no aplica')
# %% Exportar dataset definitivo
nc_final.to_csv('datas/no_conformidades.csv',
                index=False,
                encoding='utf-8')


# =============================================================================
# Segunda parte: streamlit_app
# =============================================================================

# %% Leer data limpia

data = pd.read_csv('datas/no_conformidades.csv')

# %% Crear encabezado de la app

# Configurar página
st.set_page_config(
    page_title="Suroriente ESE",
    page_icon="logo.png",  # Archivo en misma carpeta
    layout="wide"
)

with st.container(horizontal=True, gap="medium"):
    st.write("")
    # Agregar logo
    st.image("logo.png",
             width=50)
    # Crear título de la aplicación
    st.header(
        'Empresa Social del Estado Suroriente ESE - Resumen de las no conformidades SOGCS')

# Línea horizontal de división
st.divider()

# %% Sección de filtros

# Agregar subtitulo para la sección de filtros
st.subheader("Selección de opciones de filtrado")

with st.container(horizontal=True, gap="medium"):
    st.write("")
    mun_selected = st.selectbox(
        label="Municipio:",
        options=["Todos"] + sorted(data['municipio'].unique().tolist())
    )

    if mun_selected == "Todos":
        uas_options = ["Todas"] + sorted(data['uas'].unique().tolist())
    else:
        uas_options = ["Todas"] + sorted(
            data[data['municipio'] == mun_selected]['uas'].unique().tolist()
        )

    uas_selected = st.selectbox(
        "UAS:", uas_options
    )

    std_selected = st.selectbox(
        "Estándar:",
        ["Todos"] + sorted(data['estandar'].unique().tolist())
    )
    st.write("")
# Línea horizontal de división
st.divider()

# %% Filtro del dataset

# Cuando todos los filtos tienen la opción todo(a)s
df = data.copy()

# Cuando hay una selección en el filtro de municipio
if mun_selected != 'Todos':
    df = df[df['municipio'] == mun_selected]
# Cuando hay una selección en el filtro de UAS adicional a la de municipio
if uas_selected != 'Todas':
    df = df[df['uas'] == uas_selected]
# Cuando hay una selección en el filtro de estándar adicional a la de municipio y UAS
if std_selected != 'Todos':
    df = df[df['estandar'] == std_selected]

# %% Tarjetas de conteo de no conformidades

with st.container(horizontal=True, gap="medium"):

    for _ in range(4):
        st.write("")

    st.subheader("Cantidad de no conformidades")

    for _ in range(4):
        st.write("")

with st.container(horizontal=True, gap="medium"):

    for _ in range(4):
        st.write("")

    st.metric(
        label="",
        value=len(df),
        width=180,
        height=70,
        border=False
    )

    for _ in range(4):
        st.write("")

st.divider()

# %% Tablas resumen

# Tabla resumen por auditoría
df_aud = df.groupby('fuente').size()
df_aud.name = 'cantidad'
df_aud = df_aud.sort_values(ascending=False)
df_aud = df_aud.reset_index()
df_aud['fuente'] = df_aud['fuente'].str.replace(
    'Visitas de verificacion de la Secretaria de Salud Departamental del Cauca', 'Visitas SSC')

# Tabla resumen por estándar
df_std = df.groupby('estandar').size()
df_std.name = 'cantidad'
df_std = df_std.sort_values(ascending=True)
df_std = df_std.reset_index()

# Tabla resumen por municipio
df_mun = df.groupby('municipio').size()
df_mun.name = 'cantidad'
df_mun = df_mun.sort_values(ascending=False)
df_mun = df_mun.reset_index()


# %% Grafico con plotly

col1, col2, col3 = st.columns(3)

with col1:
    fig = go.Figure(data=[go.Bar(
        y=df_aud['cantidad'],  # CATEGORÍAS en el eje Y
        x=df_aud['fuente'],  # VALORES en el eje X
        marker_color='orange',
    )])

    fig.update_layout(
        title_text='No conformidades por auditoría',
        xaxis_title='Auditoría',
        yaxis_title='Número de no conformidades'
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:

    fig = go.Figure(data=[go.Bar(
        x=df_std['cantidad'],
        y=df_std['estandar'],
        marker_color='teal',
        orientation='h'
    )])

    fig.update_layout(
        title_text='No conformidades por estándar',
        xaxis_title='Número de no conformidades',
        yaxis_title='Estándar'
    )

    st.plotly_chart(fig, use_container_width=True)

with col3:
    fig = go.Figure(data=[go.Bar(
        y=df_mun['cantidad'],
        x=df_mun['municipio'],
        marker_color='blue',
    )])

    fig.update_layout(
        title_text='No conformidades por municipio',
        xaxis_title='Municipio',
        yaxis_title='Número de no conformidades'
    )

    st.plotly_chart(fig, use_container_width=True)
