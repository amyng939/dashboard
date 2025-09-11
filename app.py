import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import json

st.set_page_config(
    page_title="NYC Rodent Inspection",
    page_icon="🐀",
    layout="wide",
    initial_sidebar_state="expanded")

alt.theme.enable("dark")

df = pd.read_csv("data/Rodent_Inspection_2020-2025_condensed.csv")

# with open("data/2020 Neighborhood Tabulation Areas (NTAs)_20250911.geojson") as geo_file:
#     nyc_nta_geo = json.load(geo_file)

with open("data/Borough Boundaries_20250911.geojson") as geo_file:
    nyc_boro_geo = json.load(geo_file)

with st.sidebar:
    st.title('🐀 NYC Rodent Inspection')
    
    year_list = list(df.INSPECTION_YEAR.unique())[::-1]
    
    selected_year = st.selectbox('Select a year', year_list, index=len(year_list)-1)
    df_selected_year = df[df['INSPECTION_YEAR'] == selected_year]
    df_selected_year_sorted = df_selected_year.sort_values(by="NUMBER_OF_INSPECTIONS", ascending=False)
    # df_selected_year_nta_counts = df_selected_year['NTA'].value_counts().rename_axis('NTA').reset_index(name='NUMBER_OF_INSPECTIONS')
    df_selected_year_boro_counts = df_selected_year.groupby('BOROUGH')['NUMBER_OF_INSPECTIONS'].sum().reset_index()

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

    st.image("image/pizza-rat-buzzfeed.jpg", caption="Rat with pizza found in a NYC Subway Station")


def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, geojson=nyc_boro_geo, featureidkey="properties.boroname",
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(df_selected_year.groupby('BOROUGH')['NUMBER_OF_INSPECTIONS'].sum())),
                               labels={'NUMBER_OF_INSPECTIONS':'# of Inspections'}
                              )
    choropleth.update_geos(fitbounds="geojson", visible=False)
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(bgcolor='rgba(32, 25, 25, 1)')
    )
    return choropleth

col = st.columns((4.5, 2), gap='medium')

with col[0]:
    st.markdown('#### Total Borough Inspections')
    
    choropleth = make_choropleth(df_selected_year_boro_counts, 'BOROUGH', 'NUMBER_OF_INSPECTIONS', selected_color_theme)
    st.plotly_chart(choropleth, use_container_width=True)

    st.markdown(f"<h5>Total Inspections: {df_selected_year['NUMBER_OF_INSPECTIONS'].sum()}</h5>", unsafe_allow_html=True)

with col[1]:
    st.markdown('#### Top Neighbourhoods Inspected')

    st.dataframe(df_selected_year_sorted,
                 column_order=("NTA", "NUMBER_OF_INSPECTIONS"),
                 hide_index=True,
                 width='stretch',
                 column_config={
                    "NTA": st.column_config.TextColumn(
                        "NTA*",
                    ),
                    "NUMBER_OF_INSPECTIONS": st.column_config.ProgressColumn(
                        "# of Inspections",
                        format="%.0f", # integer
                        min_value=0,
                        max_value=max(df_selected_year['NUMBER_OF_INSPECTIONS']),
                     )}
                 )
    
    with st.expander('About', expanded=True):
        st.write('''
            - Data: [NYC Open Data - Department of Health and Mental Hygiene](<https://data.cityofnewyork.us/Health/Rodent-Inspection/p937-wjvj/about_data>).
            - GeoJSON for Boroughs: [NYC Open Data - Department of City Planning](<https://data.cityofnewyork.us/City-Government/Borough-Boundaries/gthc-hcne/data_preview>).
            - :orange[***What is NTA?**]: NTA stands for Neighborhood Tabulation Areas, which was created by the Department of City Planning to make minimum-sized neighborhoods for statistical realibility.
            - I chose this dataset because it sounds interesting to see how common rodent inspections happen in our city and if it's concentrated in specific neighborhoods.
                To restate the official database description, this may not be indicative of rat populations but just more inspections in certain neighborhoods.
            ''')
        
# - GeoJSON for NTAs: [NYC Open Data - Department of City Planning](<https://data.cityofnewyork.us/City-Government/2020-Neighborhood-Tabulation-Areas-NTAs-/9nt8-h7nd/about_data>).