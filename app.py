# imports
import panel as pn
pn.extension('plotly')
#adding interact function
from panel.interact import interact
import plotly.express as px
import pandas as pd
import hvplot.pandas
import matplotlib.pyplot as plt
import os
from pathlib import Path
from dotenv import load_dotenv
import numpy as np

import warnings
warnings.filterwarnings('ignore')

# Read the Mapbox API key
load_dotenv()
map_box_api = os.getenv("MBOX_KEY")
# Set the mapbox access token
px.set_mapbox_access_token(map_box_api)

# Import the necessary CSVs to Pandas DataFrames

#importing the housing price and rent data per year and neighborhood 
sfo_data = pd.read_csv("sfo_neighborhoods_census_data.csv", index_col="year")

# Load neighborhoods coordinates data
neighborhood_corr = pd.read_csv("neighborhoods_coordinates.csv" , index_col='Neighborhood')

# Calculate the mean values for each neighborhood
neighborhood_avg = round(sfo_data.groupby(by='neighborhood').mean(),2)
neighborhood_avg.head()
    
# Join the average values with the neighborhood locations
neighborhood_avg_corr = pd.concat([neighborhood_avg , neighborhood_corr], axis= 1, join='inner').reset_index()
neighborhood_avg_corr.rename(columns={'index':'Neighborhood'} , inplace = True)
    

# Create a scatter mapbox to analyze neighborhood info
px.scatter_mapbox(
        neighborhood_avg_corr , 
        lat='Lat' ,
        lon = 'Lon', 
        size = 'sale_price_sqr_foot' ,
        color = 'gross_rent' ,
        color_continuous_scale = px.colors.cyclical.IceFire,
        zoom =10 , 
        width = 700, 
        height = 500 ,
        title = "Avarage Sale Price Per Sqaure Foot and Gross Rent in SFO"
    )

# Define Panel Visualization Functions
def housing_units_per_year():
    """Housing Units Per Year."""
    
    # Calculate the mean number of housing units per year (hint: use groupby) 
    sfo_data_by_year = sfo_data.groupby(by="year").mean().drop(columns = ["sale_price_sqr_foot","gross_rent"])
    # converting to integers 
    sfo_data_by_year['housing_units'] = sfo_data_by_year['housing_units'].astype("int64")
    #calculate the scales using the standard deviation from the min and max     
    ymin = min(sfo_data_by_year.housing_units)- np.std(sfo_data_by_year.housing_units)
    ymax = max(sfo_data_by_year.housing_units) + np.std(sfo_data_by_year.housing_units)
    
    plot =  sfo_data_by_year.hvplot( 
            kind = "bar",
            y = "housing_units",
            title="Housing Units in San Fransisco from 2010 to 2016",
            xlabel = "Year",
            ylabel = "Housing Units" ,
            ylim = [ ymin , ymax ],
            legend = False
            )
    return plot

def average_gross_rent():
    """Average Gross Rent in San Francisco Per Year."""
    
    # Calculate the average sale price per square foot and average gross rent
    sfo_avg_sale_rent = round(sfo_data.groupby(by="year").mean().drop(columns = "housing_units"),2)

    # converting to integers 
    sfo_avg_sale_rent['gross_rent']=sfo_avg_sale_rent['gross_rent'].astype("int64")

    # Line chart for average montly rent
    plot=  sfo_avg_sale_rent.hvplot(
            kind="line",
            title="Average Gross Rent by Year",
            color= "red",
            xlabel= "Year",
            y= "gross_rent",
            ylabel= "Average Gross Rent" ,
            legend = False
            )
    return plot 
    
def average_sales_price():
    """Average Sales Price Per Year."""
    
    # Calculate the average sale price per square foot and average gross rent
    sfo_avg_sale_rent = round(sfo_data.groupby(by="year").mean().drop(columns = "housing_units"),2)

    # converting to integers 
    sfo_avg_sale_rent['gross_rent']=sfo_avg_sale_rent['gross_rent'].astype("int64")
    
    # Line chart for average sale price per square foot
     
    plot =  sfo_avg_sale_rent.hvplot(
            kind="line",
            title="Average Price per SqFt by Year",
            color = "purple",
            xlabel= "Year",
            y= "sale_price_sqr_foot",
            ylabel= "Price per SqFt",
            legend = False
            )
    return plot

def average_price_by_neighborhood():
    """Average Prices by Neighborhood."""
    
    # Group by year and neighborhood and then create a new dataframe of the mean values
    sfo_by_year_neighborhood = round(sfo_data.groupby(by = ['year', 'neighborhood']).mean().reset_index(),2)

    # converting to integers 
    sfo_by_year_neighborhood[['housing_units','gross_rent']] = sfo_by_year_neighborhood[['housing_units','gross_rent']].astype("int64") 

    def avg_price_sqft_plot(Neigborhood):

        # create a temp list per chosen niegborhood
        temp_df = sfo_by_year_neighborhood[sfo_by_year_neighborhood["neighborhood"] == Neigborhood]

        #Create a hvplot and store in plot to be returned  
        plot = temp_df.hvplot.line(
            x="year",
            xlabel = "Year",
            y= "sale_price_sqr_foot",
            ylabel = "Avg. Sale Price per Square Foot", 
            title=f"Neighborhood : {Neigborhood} - Average Sale Price per SqFt Plot",
            xformatter = '%.0f',
            height = 350) 
        return plot 
    
    return interact(avg_price_sqft_plot,Neigborhood = sfo_by_year_neighborhood["neighborhood"].unique())



def top_most_expensive_neighborhoods():
    """Top 10 Most Expensive Neighborhoods."""
    # Group by year and neighborhood and then create a new dataframe of the mean values
    sfo_by_year_neighborhood = round(sfo_data.groupby(by = ['year', 'neighborhood']).mean().reset_index(),2)

    # converting to integers 
    sfo_by_year_neighborhood[['housing_units','gross_rent']] = sfo_by_year_neighborhood[['housing_units','gross_rent']].astype("int64") 
    
    # Getting the data from the top 10 expensive neighborhoods to own
    top_10_neighborhoods = sfo_by_year_neighborhood.groupby(by='neighborhood').mean().nlargest(10 , columns = 'sale_price_sqr_foot')
    
    # Plotting the data from the top 10 expensive neighborhoods
    return top_10_neighborhoods.hvplot.bar(
        x = "neighborhood",
        rot = 90 ,
        xlabel = "Neighborhood",
        y = "sale_price_sqr_foot", 
        ylabel = "Avg . Sale Price per Square Foot" ,
        title = "Top 10 Expensive Neighborhoods in SFO",
        height = 400
        )


def most_expensive_neighborhoods_rent_sales():
    """Comparison of Rent and Sales Prices of Most Expensive Neighborhoods."""   
    
    # Group by year and neighborhood and then create a new dataframe of the mean values
    sfo_by_year_neighborhood = round(sfo_data.groupby(by = ['year', 'neighborhood']).mean().reset_index(),2)

    # converting to integers 
    sfo_by_year_neighborhood[['housing_units','gross_rent']] = sfo_by_year_neighborhood[['housing_units','gross_rent']].astype("int64") 
    
        #creating a function to output the plot
    def top_10_expensive_plot(Neigborhood):

            # create a temp list grouping the 
            temp_df = sfo_by_year_neighborhood.groupby(by=['year','neighborhood']).mean().reset_index()
            ploting_df = temp_df.loc[temp_df['neighborhood'] == Neigborhood]

            #Create a hvplot and store in plot to be returned  
            plot = ploting_df.hvplot.bar(
                x='year' ,
                y = ['sale_price_sqr_foot' , 'gross_rent'] , 
                rot = 90 ,
                title = "Top 10 Expensive Neighborhoods in SFO" ,
                xlabel = "Neighborhood" ,
                ylabel = "Dollar Amount $" ,
                stacked = False ,
                height = 450

            )

            return plot

# plotting the interactive plot to show avg price per neighborhood
    return interact(top_10_expensive_plot,Neigborhood = sfo_by_year_neighborhood["neighborhood"].unique())
    
    
def parallel_coordinates():
    """Parallel Coordinates Plot."""

    #create a list grouped by Year and Neighborhood with avg prices 
    df_costs = sfo_data.groupby(by = ['year','neighborhood'])[['sale_price_sqr_foot','housing_units','gross_rent']].mean().reset_index()
    #find the top 10 neighborhoods
    df_expensive_neighborhoods = df_costs.groupby(by='neighborhood').mean().nlargest(10 , columns = 'sale_price_sqr_foot').reset_index()
    # Fetch the data from all expensive neighborhoods per year.
    df_expensive_neighborhoods_per_year = df_costs[df_costs["neighborhood"].isin(df_expensive_neighborhoods["neighborhood"])]
    
    # Parallel Coordinates Plot
    plot = px.parallel_coordinates(
        df_expensive_neighborhoods ,
        title= 'Parallel Coordinates Analysis for Most Expensive San Fransisci Neighborhoods',
        dimensions = ['sale_price_sqr_foot' , 'housing_units', 'gross_rent'],
        color = 'sale_price_sqr_foot',
        color_continuous_scale=px.colors.sequential.Inferno,
        labels = { 
            'sale_price_sqr_foot':'Sale Price per Sqr Foot' , 
            'housing_units': 'Number of Housing Units', 
            'gross_rent': 'Gross Rent'},
         height = 500,
        width = 1000 
        )
    return plot 



def parallel_categories():
    """Parallel Categories Plot."""
    
    #create a list grouped by Year and Neighborhood with avg prices 
    df_costs = sfo_data.groupby(by = ['year','neighborhood'])[['sale_price_sqr_foot','housing_units','gross_rent']].mean().reset_index()
    #find the top 10 neighborhoods
    df_expensive_neighborhoods = df_costs.groupby(by='neighborhood').mean().nlargest(10 , columns = 'sale_price_sqr_foot').reset_index()
    # Fetch the data from all expensive neighborhoods per year.
    df_expensive_neighborhoods_per_year = df_costs[df_costs["neighborhood"].isin(df_expensive_neighborhoods["neighborhood"])]
    
    # Parallel Categories Plot
    plot = px.parallel_categories(
        df_expensive_neighborhoods,
        title= 'Parallel Categories Analysis for Most Expensive San Fransisci Neighborhoods',
        dimensions = ['neighborhood','sale_price_sqr_foot' , 'housing_units', 'gross_rent'],
        color = 'sale_price_sqr_foot',
        color_continuous_scale=px.colors.sequential.Inferno,
        labels = { 
            'sale_price_sqr_foot':'Sale Price per Sqr Foot' , 
            'housing_units': 'Number of Housing Units', 
            'gross_rent': 'Gross Rent'
        },
        height = 500,
        width = 1000 
        )
    
    return plot



def neighborhood_map():
    """Neighborhood Map."""

    # Calculate the mean values for each neighborhood
    neighborhood_avg = round(sfo_data.groupby(by='neighborhood').mean(),2)
    neighborhood_avg.head()
    
    # Join the average values with the neighborhood locations
    neighborhood_avg_corr = pd.concat([neighborhood_avg , neighborhood_corr], axis= 1, join='inner').reset_index()
    neighborhood_avg_corr.rename(columns={'index':'Neighborhood'} , inplace = True)
    
    # Set the mapbox access token
    px.set_mapbox_access_token(map_box_api)
    # Create a scatter mapbox to analyze neighborhood info
    return px.scatter_mapbox(
        neighborhood_avg_corr , 
        lat='Lat' ,
        lon = 'Lon', 
        size = 'sale_price_sqr_foot' ,
        color = 'gross_rent' ,
        color_continuous_scale = px.colors.cyclical.IceFire,
        zoom =10 , 
        width = 1000, 
        height = 600 ,
        title = "Avarage Sale Price Per Sqaure Foot and Gross Rent in SFO"
    )


def sunburst():
    """Sunburst Plot."""
    
    #create a list grouped by Year and Neighborhood with avg prices 
    df_costs = sfo_data.groupby(by = ['year','neighborhood'])[['sale_price_sqr_foot','housing_units','gross_rent']].mean().reset_index()
    #find the top 10 neighborhoods
    df_expensive_neighborhoods = df_costs.groupby(by='neighborhood').mean().nlargest(10 , columns = 'sale_price_sqr_foot').reset_index()
    # Fetch the data from all expensive neighborhoods per year.
    df_expensive_neighborhoods_per_year = df_costs[df_costs["neighborhood"].isin(df_expensive_neighborhoods["neighborhood"])]
    
    # Sunburst Plot
    plot = px.sunburst(
        df_expensive_neighborhoods_per_year,
        title= 'Sunbusrt Analysis fir Most Expensive San Fransisco Neighborhoods by Year',
        path = [ 'year' , 'neighborhood'],
        values = 'gross_rent',
        color = 'gross_rent',
        color_continuous_scale='RdBu' ,
        color_continuous_midpoint=np.average(df_expensive_neighborhoods_per_year['gross_rent']),
        height = 700,
        width = 1000 
        )
    return plot

# Create a Title for the Dashboard
page = pn.Column("# Realestate Analysis of San Fransisco from 2010 to 2016 - [source code](https://github.com/JQH84/Rental-Analysis-Dashboard) ")

# Create a tab layout for the dashboard
welcome = pn.Column("""
This dashboard presents a visual analysis of historical prices of house units, sale price per square foot and gross rent in
San Francisco, California from 2010 to 2016. You can navigate through the tabs above to explore more details about the
evolution of the real estate market on The Golden City across these years.

""", neighborhood_map())

year_market = pn.Column(housing_units_per_year(),average_gross_rent(),average_sales_price())

neighborhood = pn.Column(average_price_by_neighborhood(),top_most_expensive_neighborhoods(),most_expensive_neighborhoods_rent_sales())

parallel = pn.Column(parallel_coordinates(),parallel_categories()) 

sinburst = pn.Column(sunburst())

# Create the dashboard
sfo_dashboard_page = pn.Tabs (
    
    ("Welcome", welcome),
    ("Yearly Market Analysis" , year_market),
    ("Neighborhood Analysis" , neighborhood),
    ("Parllel Plots Analysis" , parallel),
    ("Sunburst Plot Analysis" , sunburst)
)

#append the tabs to page where the title exists before rendering
page.append(sfo_dashboard_page)

# Serve the# dashboard
page.servable(title='Rental Analysis Dashboard')
