import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import folium
from folium.plugins import FastMarkerCluster, MarkerCluster
from streamlit_folium import st_folium
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Earthquake Data Analysis", page_icon=":earth_asia:",layout="wide")

st.title(" :earth_asia: Earthquake Data Analysis")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = "ISO-8859-1")
else:
    df = pd.read_csv("earthquake_country_continent_cleaned_data.csv", encoding = "ISO-8859-1")

col1, col2 = st.columns((2))
df["date"] = pd.to_datetime(df["date"])

# Getting the min and max date 
startDate = pd.to_datetime(df["date"]).min()
endDate = pd.to_datetime(df["date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["date"] >= date1) & (df["date"] <= date2)].copy()


st.sidebar.header("Choose your filter: ")
# Create for Region
continent = st.sidebar.multiselect("Pick your continent", df["continent"].unique())
if not continent:
    df2 = df.copy()
else:
    df2 = df[df["continent"].isin(continent)]

# Create for State
country = st.sidebar.multiselect("Pick the country", df2["country"].unique())
if not country:
    df3 = df2.copy()
else:
    df3 = df2[df2["country"].isin(country)]


# Filter the data based on Continent and Country

if not continent and not country:
    filtered_df = df
elif not country:
    filtered_df = df[df["continent"].isin(continent)]
elif not continent:
    filtered_df = df[df["country"].isin(country)]
elif country:
    filtered_df = df3[df["country"].isin(country)]
elif continent:
    filtered_df = df3[df["continent"].isin(continent)]
elif continent and country:
    filtered_df = df3[df["continent"].isin(continent) & df3["country"].isin(country)]

# Create group by continent charts
continent_mag_df = filtered_df.groupby(by = ["continent"], as_index = False)['mag'].median()
continent_depth_df = filtered_df.groupby(by = ["continent"], as_index = False)['depth'].median()


with col1:
    st.subheader("Continent-Wise Magnitude")
    fig = px.bar(continent_mag_df, x = "continent", y = "mag", template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col2:
    st.subheader("Continent-Wise Depth")
    fig = px.bar(continent_depth_df, x = "continent", y = "depth", template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

# To download the grouped data
    
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Magnitude_ViewData"):
        st.write(continent_mag_df)
        csv = continent_mag_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Magnitude.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

with cl2:
    with st.expander("Depth_ViewData"):
        st.write(continent_depth_df)
        csv = continent_depth_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Depth.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

# Create histogram for magnitude and depth
        
hist_cl1, hist_cl2 = st.columns((2))

with hist_cl1:
    st.subheader("Magnitude Histogram")
    fig = px.histogram(filtered_df, x="mag", nbins=10, color_discrete_sequence=['indianred'])
    fig.update_traces(marker_line_width=2,marker_line_color="white")
    st.plotly_chart(fig,use_container_width=True, height = 200)

with hist_cl2:
    st.subheader("Depth Histogram")
    fig = px.histogram(filtered_df, x="depth", nbins=10, color_discrete_sequence=['indianred'])
    fig.update_traces(marker_line_width=2,marker_line_color="white")    
    st.plotly_chart(fig,use_container_width=True, height = 200)


# Time Series Data
time_cl1, scatter_cl2 = st.columns((2))

with time_cl1:
    filtered_df["year"] = filtered_df["date"].dt.to_period("Y")
    st.subheader('Yearly Time Series Analysis')

    linechart = pd.DataFrame(filtered_df.groupby(filtered_df["year"].dt.strftime("%Y"))["id"].count()).reset_index()
    fig2 = px.line(linechart, x = "year", y="id", labels = {"id": "Number of earthquakes"},
                   height=500, width = 1000,template="gridon")
    st.plotly_chart(fig2,use_container_width=True, height = 200)

with scatter_cl2:
    # Create a scatter plot
    st.subheader('Relationship Between Magnitude and Depth')
    data1 = px.scatter(filtered_df, x = "mag", y = "depth")
    st.plotly_chart(data1,use_container_width=True, height = 200)

# CREATE MAPS

map_cl1, map_cl2 = st.columns((2))

# Create folium Map (Markers)
# But create a new dataframe from filtered data for mag>7
earthquake_mg_7 = filtered_df[filtered_df.mag>7]

with map_cl1:
    st.subheader("Earthquake Of Magnitude Greater Than 7")

    m = folium.Map([earthquake_mg_7['latitude'].mean(), earthquake_mg_7['longitude'].mean()],
                zoom_start=1, min_zoom = 1, max_zoom = 6)

    for i in range(len(earthquake_mg_7)): # add markers for all datapoints
        folium.Marker([earthquake_mg_7.iloc[i]['latitude'], earthquake_mg_7.iloc[i]['longitude']], popup=earthquake_mg_7.iloc[i]['country']).add_to(m)
        
    # call to render Folium map in Streamlit
    st_folium(m, use_container_width=True, height = 250)


# Creater a cluster map for mag > 5
earthquake_mg_5 = filtered_df[filtered_df.mag>5]

# Mark earthquakes epicenters with Magnitude more than 5 using CircleMarker:
with map_cl2:
    st.subheader('Cluster For Magnitude Greater Than 5')

    mc = MarkerCluster(name="Marker Cluster")

    folium_map = folium.Map([earthquake_mg_5['latitude'].mean(), earthquake_mg_5['longitude'].mean()],
                zoom_start=1, min_zoom = 1, max_zoom = 6) 

    for i in range(len(earthquake_mg_5)):
        
        folium.CircleMarker(location=[earthquake_mg_5.iloc[i]['latitude'], earthquake_mg_5.iloc[i]['longitude']],
                            radius= 1.5 * earthquake_mg_5.iloc[i]['mag'],
                            color="red",
                            fill=True).add_to(mc)
        
    mc.add_to(folium_map)
    folium.LayerControl().add_to(folium_map)

    st_folium(folium_map, use_container_width=True, height = 250)