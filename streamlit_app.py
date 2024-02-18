############### Import all important libraries #####################

import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import json
import requests 
import streamlit as st 
from streamlit_lottie import st_lottie 

from PIL import Image

import folium
from folium.plugins import FastMarkerCluster, MarkerCluster
from streamlit_folium import st_folium
from mpl_toolkits.basemap import Basemap  
import os
import warnings
warnings.filterwarnings('ignore')

################## Page Setup ####################

st.set_page_config(page_title="Earthquake Data Analysis", page_icon=":earth_asia:",layout="wide")

st.title(" :earth_asia: Earthquake Data Analysis")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

################# User Upload CSV File #########################
fl = st.file_uploader(":file_folder: Upload a file (Uploaded file should have depth, mag, latitude, longitude and date columns)",type=(["csv"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = "ISO-8859-1")
else:
    df = pd.read_csv("earthquake_country_continent_cleaned_data.csv", encoding = "ISO-8859-1")

##################### Date Selection (Min Date and Max Date) ###########################
date_col1, date_col2 = st.columns((2))
df["date"] = pd.to_datetime(df["date"])

# Getting the min and max date 
startDate = pd.to_datetime(df["date"]).min()
endDate = pd.to_datetime(df["date"]).max()

with date_col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with date_col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["date"] >= date1) & (df["date"] <= date2)].copy()

#################### Create a sidebar ###########################
with st.sidebar:

    ############ Create sidebar Animation of Globe ###################
    def load_lottiefile(filepath: str):
        with open(filepath, "r") as f:
            return json.load(f)


    def load_lottieurl(url: str):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
        
    lottie_earth = load_lottiefile("globe.json")

    st_lottie(
        lottie_earth,
        speed=1,
        reverse=False,
        loop=True,
        quality="medium", # medium ; high
        height=None,
        width=None,
        key=None,
    )

    ############# Create sidebar slection for Continent and Country #################

    st.sidebar.header("Choose your filter: ")
    # Create for Continent
    continent = st.sidebar.multiselect("Pick your continent", df["continent"].unique())
    if not continent:
        df2 = df.copy()
    else:
        df2 = df[df["continent"].isin(continent)]

    # Create for Country
    country = st.sidebar.multiselect("Pick the country", df2["country"].unique())
    if not country:
        df3 = df2.copy()
    else:
        df3 = df2[df2["country"].isin(country)]


    ############ Filter the data based on Continent and Country ################

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
    
    ################ About the project ##################
    with st.expander("About"):
        st.markdown(
            """
            In our earthquake project, we used Apache Hadoop's 
            fully distributed mode for distributed storage and 
            processing, PySpark for data cleaning, Python for 
            preprocessing and modeling, Tableau for visualization
            and Streamlit for interactive web apps. Our machine
            learning model predicts earthquake magnitudes, aiding
            in risk assessment.
            """
        )

######################### KPI METRICS ##############################
mag_min = filtered_df.mag.min()
mag_max = filtered_df.mag.max()

depth_min = filtered_df.depth.min()
depth_max = filtered_df.depth.max()

total_count = filtered_df.shape[0]

met_col1, met_col2, met_col3, met_col4, met_col5, met_col6 = st.columns(6)

with met_col1:

    ####################### Animation with KPI paramenters #####################
    def load_lottiefile(filepath: str):
        with open(filepath, "r") as f:
            return json.load(f)


    def load_lottieurl(url: str):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
        
    lottie_kpi = load_lottiefile("dashboard.json")

    st_lottie(
        lottie_kpi,
        speed=1,
        reverse=False,
        loop=True,
        quality="medium", # medium ; high
        height=None,
        width=None,
        key=None,
    )

met_col2.metric("Minimum Magnitude", mag_min)
met_col3.metric("Maximum Magnitude", mag_max)
met_col4.metric("Minimum Depth", depth_min)
met_col5.metric("Maximum Depth", depth_max)
met_col6.metric("Total Earthquakes", total_count)

###################3 Create 2 TABS FOR OVERALL CHARTS (MAP AND JOINT PLOT) #######################
map_tab1, joint_tab2 = st.tabs(
        [
            "ALL EARTHQUAKE DATA 3D MAP",
            "JOINTPLOT (MAGNITUDE VS DEPTH)"
        ]
    )

################# Overall Insights PNG (Globe and Histogram for Magnitude and Depth) ########################

with map_tab1:
    st.subheader("Overall Earthquake Insights (Map and Histogram) ")
    st.image('overall_insights.png', use_column_width = True)

################# Joint PLot ###########################
    
with joint_tab2:
    #st.subheader("Jointplot (Magnitude vs Depth) ")
    #st.image('joint_plot.png', use_column_width = True)

    image = Image.open('joint_plot.png')
    new_image = image.resize((750, 350))
    st.image(new_image, use_column_width = True)


############### HeatMap for Mag more than 4 #################


# mag_more_4 = filtered_df[filtered_df.mag>4]
# st.subheader('HeatMap with respect to Magnitude')
# map_fig  = px.density_mapbox(mag_more_4, lat = 'latitude', lon = 'longitude', z = 'mag', radius = 10, 
#                           center = dict(lat = mag_more_4.latitude.mean(), lon = mag_more_4.longitude.mean()),
#                           zoom = 1,  
#                           mapbox_style = 'stamen-watercolor',
#                           hover_name = 'country',
#                           hover_data = ['mag', 'depth'])

# st.plotly_chart(map_fig, use_container_width = True)

###################3 Create 3 TABS FOR BASIC CHARTS #######################
continent_tab1, histogram_tab2, time_tab3 = st.tabs(
        [
            "CONTINENT WISE DATA (MAGNITUDCE AND DEPTH)",
            "HISTOGRAM (MAGNITUDE AND DEPTH)",
            "TIME SERIES ANALYSIS"
        ]
    )


################ Create group by continent charts (Magnitude and Depth median) ##############################

with continent_tab1:

    group_col1, group_col2 = st.columns((2))

    continent_mag_df = filtered_df.groupby(by = ["continent"], as_index = False)['mag'].median()
    continent_depth_df = filtered_df.groupby(by = ["continent"], as_index = False)['depth'].median()

    with group_col1:
        st.subheader("Continent-Wise Magnitude")
        fig = px.bar(continent_mag_df, x = "continent", y = "mag", template = "seaborn")
        st.plotly_chart(fig,use_container_width=True, height = 100)

    with group_col2:
        st.subheader("Continent-Wise Depth")
        fig = px.bar(continent_depth_df, x = "continent", y = "depth", template = "seaborn")
        st.plotly_chart(fig,use_container_width=True, height = 100)

    ################### To download the grouped data for above charts ####################################
        
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

################### Create histogram for magnitude and depth ###################################

with histogram_tab2:

    hist_cl1, hist_cl2 = st.columns((2))

    with hist_cl1:
        st.subheader("Magnitude Histogram")
        fig = px.histogram(filtered_df, x="mag", nbins=10, color_discrete_sequence=['indianred'])
        fig.update_traces(marker_line_width=2,marker_line_color="white")
        st.plotly_chart(fig,use_container_width=True, height = 100)

    with hist_cl2:
        st.subheader("Depth Histogram")
        fig = px.histogram(filtered_df, x="depth", nbins=10, color_discrete_sequence=['indianred'])
        fig.update_traces(marker_line_width=2,marker_line_color="white")    
        st.plotly_chart(fig,use_container_width=True, height = 100)


################### Time Series Data (Earthquake over the year) #############################
with time_tab3:

    filtered_df["year"] = filtered_df["date"].dt.to_period("Y")
    remove_2023_df = filtered_df[filtered_df.year != '2023']
    st.subheader('Earthquakes Over The Year')

    linechart = pd.DataFrame(remove_2023_df.groupby(remove_2023_df["year"].dt.strftime("%Y"))["id"].count()).reset_index()
    fig = px.line(linechart, x = "year", y="id", labels = {"id": "Number of earthquakes"})

    fig.update_layout( 
        xaxis = dict(
            tickmode = 'linear',
            tick0 = 0.0,
            dtick = 1
        )
    )
    fig.add_shape(type="line",
        x0=linechart['year'].values[0], y0=linechart['id'].mean(), x1=linechart['year'].values[-1], y1=linechart['id'].mean(),
        line=dict(
            color="Red",
            width=2,
            dash="dashdot",
        ),
            name='Mean'
    )

    st.plotly_chart(fig ,use_container_width=True, height = 150)

####################### CREATE MAPS #########################

###################3 Create 3 TABS FOR MAP CHARTS #######################
flatmap_tab1, markers_tab2, cluster_tab3 = st.tabs(
        [
            "ALL AFFECTED AREAS",
            "EARTHQUAKE WITH MAGNITUDE MORE THAN 7",
            "CLUSTER FOR MAGNITUDE GREATER THAN 5"
        ]
    )

################  2D Map of Earth with all data points ########################

with flatmap_tab1:
    st.subheader('All Affected Areas')
    m = Basemap(projection='mill',llcrnrlat=-80,urcrnrlat=80, llcrnrlon=-180,urcrnrlon=180,lat_ts=20,resolution='c', width=12000000,height=9000000)  
    
    longitudes = filtered_df["longitude"].tolist()  
    latitudes = filtered_df["latitude"].tolist()  
    
    x,y = m(longitudes,latitudes) 
    plt.title("All Affected Areas")  
    m.plot(x, y, "o", markersize = 2, color = 'blue')  
    m.drawcoastlines()  
    m.fillcontinents(color='coral',lake_color='aqua')  
    m.drawmapboundary()  
    m.drawcountries()  

    plt.savefig('Map.png')
    st.image('Map.png', use_column_width = True)


################## Create folium Map (Markers) ################################

####### But create a new dataframe from filtered data for mag>7 (MARKERS) #########
earthquake_mg_7 = filtered_df[filtered_df.mag>7]

with markers_tab2:
    st.subheader("Magnitude Greater Than 7")

    m = folium.Map([earthquake_mg_7['latitude'].mean(), earthquake_mg_7['longitude'].mean()],
                zoom_start=1, min_zoom = 1, max_zoom = 6)

    for i in range(len(earthquake_mg_7)): # add markers for all datapoints
        folium.Marker([earthquake_mg_7.iloc[i]['latitude'], earthquake_mg_7.iloc[i]['longitude']], popup=earthquake_mg_7.iloc[i]['country']).add_to(m)
            
    # call to render Folium map in Streamlit
    st_folium(m, use_container_width=True, height = 250)


################# Creater a cluster map for mag > 5 (CLUSTER MAP) ##########################
earthquake_mg_5 = filtered_df[filtered_df.mag>5]

###### Mark earthquakes epicenters with Magnitude more than 5 using CircleMarker #############

with cluster_tab3:
    st.subheader('Magnitude Greater Than 5')

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
