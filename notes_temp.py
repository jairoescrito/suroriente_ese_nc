# -*- coding: utf-8 -*-
"""
Created on Mon Dec  1 21:24:53 2025

@author: jairoescrito
"""
'''
# SIDEBAR SLICERS (Like Excel/Power BI)
st.sidebar.header("📊 Slicers / Filters")

# 1. Multi-select slicer
selected_fuente = st.sidebar.multiselect(
    "Select fuente:",
    options=data['fuente'].unique(),
    default=data['fuente'].unique()  # All selected by default
)

# 2. Single select slicer
selected_product = st.sidebar.selectbox(
    "Select municipio:",
    options=["All"] + data['municipio'].unique().tolist()
)

# 3. Slider slicer (for numeric values)
sales_year = st.sidebar.slider(
    "year:",
    min_value=int(data['año'].min()),
    max_value=int(data['año'].max()),
    value=(int(data['año'].min()), int(data['año'].max()))
)

# 4. Radio button slicer
selected_uas = st.sidebar.radio(
    "Select uas:",
    options=["All"] + data['uas'].unique().tolist()
)
'''
