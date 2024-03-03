import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Air Quality Dashboard 2013-2017 in 3 station Beijing 🇨🇳", layout="wide")
custom_category_order = [
    "Good",
    "Moderate",
    "Unhealthy for Sensitive Groups",
    "Unhealthy",
    "Very Unhealthy",
    "Hazardous"
]

st.title("Air Quality Dashboard 2013-2017 in 3 station Beijing 🇨🇳")

def calculate_data_by_station(df):
    data_by_station = df.groupby('station').size()
    return data_by_station

def calculate_rainy_average(df):
    rainy_average_pm25 = df.groupby('rain_category')['pm2.5'].mean()
    rainy_average_pm10 = df.groupby('rain_category')['pm10'].mean()
    rainy_average_so2 = df.groupby('rain_category')['so2'].mean()
    rainy_average_no2 = df.groupby('rain_category')['no2'].mean()
    rainy_average_co = df.groupby('rain_category')['co'].mean()
    rainy_average_o3 = df.groupby('rain_category')['o3'].mean()

    rainy_average_df = pd.DataFrame({
        'Rain Condition': rainy_average_pm25.index,
        'pm2.5': rainy_average_pm25.values,
        'pm10': rainy_average_pm10.values,
        'so2': rainy_average_so2.values,
        'no2': rainy_average_no2.values,
        'co': rainy_average_co.values,
        'o3': rainy_average_o3.values
    })
    rainy_average_df.set_index('Rain Condition', inplace=True)
    return rainy_average_df

def calculate_rainy_counts_by_year(df):
    rainy_counts_by_year = df.groupby([df['date'].dt.year, 'rain_category']).size()   
    rainy_counts_by_year_df = rainy_counts_by_year.reset_index()
    rainy_counts_by_year_df.columns = ['Year', 'Rain Category', 'Count']
    return rainy_counts_by_year_df

def calculate_hourly_average_pollutants(df):
    hourly_average_pm25 = df.groupby('hour')['pm2.5'].mean()
    hourly_average_pm10 = df.groupby('hour')['pm10'].mean()
    hourly_average_so2 = df.groupby('hour')['so2'].mean()
    hourly_average_no2 = df.groupby('hour')['no2'].mean()
    hourly_average_co = df.groupby('hour')['co'].mean()
    hourly_average_o3 = df.groupby('hour')['o3'].mean()

    hourly_average_df = pd.DataFrame({
        'hour': hourly_average_pm25.index,
        'average_pm25': hourly_average_pm25.values,
        'average_pm10': hourly_average_pm10.values,
        'average_so2': hourly_average_so2.values,
        'average_no2': hourly_average_no2.values,
        'average_co': hourly_average_co.values,
        'average_o3': hourly_average_o3.values
    })
    return hourly_average_df

def calculate_correlation_with_temp(df):
    correlation_df = combine_df[['temp', 'pm2.5', 'pm10', 'so2', 'no2', 'co', 'o3']].corr()
    return correlation_df

def calculate_yearly_averages(df):
    yearly_average_pm25 = df.groupby(df['date'].dt.year)['pm2.5'].mean()
    yearly_average_pm10 = df.groupby(df['date'].dt.year)['pm10'].mean()
    yearly_average_so2 = df.groupby(df['date'].dt.year)['so2'].mean()
    yearly_average_no2 = df.groupby(df['date'].dt.year)['no2'].mean()
    yearly_average_co = df.groupby(df['date'].dt.year)['co'].mean()
    yearly_average_o3 = df.groupby(df['date'].dt.year)['o3'].mean()
    yearly_average_df = pd.DataFrame({
        'Year': yearly_average_pm25.index,
        'pm2.5': yearly_average_pm25.values,
        'pm10': yearly_average_pm10.values,
        'so2': yearly_average_so2.values,
        'no2': yearly_average_no2.values,
        'co': yearly_average_co.values,
        'o3': yearly_average_o3.values
    })
    yearly_average_df.set_index('Year', inplace=True)
    return yearly_average_df

def create_category_counts_table(df):
    category_counts = pd.crosstab(df['station'], df['Category'])
    sorted_categories = category_counts.sum(axis=0).sort_values(ascending=False).index
    category_counts_sorted = category_counts[sorted_categories]
    return category_counts_sorted

def calculate_air_quality_percentage(df, custom_category_order):
    category_counts = df['Category'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
    category_order_mapping = {category: i for i, category in enumerate(custom_category_order)}
    category_counts['Category_Order'] = category_counts['Category'].map(category_order_mapping)
    category_counts = category_counts.sort_values(by='Category_Order')
    total_count = category_counts['Count'].sum()
    category_counts['Percentage'] = (category_counts['Count'] / total_count) * 100
    return category_counts

def calculate_air_quality_percentage_per_year(df, custom_category_order):
    category_counts_per_year = df.groupby([df['date'].dt.year, 'Category']).size().unstack(fill_value=0)
    category_counts_per_year['Total'] = category_counts_per_year.sum(axis=1)
    air_quality_percentage_per_year = category_counts_per_year.div(category_counts_per_year['Total'], axis=0) * 100
    air_quality_percentage_per_year.drop(columns=['Total'], inplace=True)
    air_quality_percentage_per_year = air_quality_percentage_per_year[custom_category_order]
    return air_quality_percentage_per_year

# Load data
combine_df = pd.read_csv('https://raw.githubusercontent.com/bulgogipedas/air-quality-streamlit/main/dashboard/combine_df.csv')

datetime_columns = ['date']
combine_df.sort_values(by="date", inplace=True)
combine_df.reset_index(inplace=True)

for column in datetime_columns:
    combine_df[column] = pd.to_datetime(combine_df[column])

min_date = combine_df['date'].min()
max_date = combine_df['date'].max()

with st.sidebar:
    st.image('https://img.freepik.com/free-vector/flat-world-water-day-event_23-2148853153.jpg')
    start_date, end_date = st.sidebar.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = combine_df[(combine_df['date'] >= str(start_date)) & 
                     (combine_df['date'] <= str(end_date))]

data_by_station = calculate_data_by_station(main_df)
rainy_average_df = calculate_rainy_average(main_df)
rainy_counts_by_year_df = calculate_rainy_counts_by_year(main_df)
hourly_average_df = calculate_hourly_average_pollutants(main_df)
correlation_df = calculate_correlation_with_temp(main_df)
yearly_avaerage_df = calculate_yearly_averages(main_df)
category_counts_sorted = create_category_counts_table(main_df)


col1, col2, col3, col4 = st.columns(4)
with col1:
    total_data = len(main_df)  # Menghitung jumlah data keseluruhan
    st.metric(label="Total Data", value=total_data)

station_data_counts = calculate_data_by_station(main_df)
station_columns = [col2, col3, col4]
index = 0

for station, count in station_data_counts.items():
    with station_columns[index]:
        st.metric(label=f"Data {station}", value=count)
    # Menggeser indeks ke kolom berikutnya
    index = (index + 1) % 3  # Menggunakan modulus 3 untuk memastikan loop ke 0 setelah mencapai 3

st.markdown("---")
st.subheader("Air Quality Index")
# Hitung persentase kualitas udara berdasarkan kategori per tahun
air_quality_percentage_per_year = calculate_air_quality_percentage_per_year(main_df, custom_category_order)

tab1, tab2, tab3 = st.tabs(["AQI per Category", "AQI per Year", "AQI per station"])

with tab1:
    fig_line = px.line(air_quality_percentage_per_year,
                    x=air_quality_percentage_per_year.index,  
                    y=air_quality_percentage_per_year.columns, 
                    title='Air Quality Percentage by Category per Year',
                    labels={'value': 'Percentage', 'index': 'Year'},
                    markers=True,
                    color_discrete_sequence=px.colors.qualitative.Set3
                    )
    st.plotly_chart(fig_line, use_container_width=True)  # Menggunakan use_container_width untuk membuat visualisasi dinamis

air_quality_percentage = calculate_air_quality_percentage(main_df, custom_category_order)
with tab2:
    fig = px.pie(air_quality_percentage, 
                values='Percentage', 
                names='Category', 
                title='Air Quality Percentage by Category',
                color_discrete_sequence=px.colors.qualitative.Set3)

    # Customize layout
    fig.update_traces(textposition='inside', textinfo='percent')
    fig.update_layout(legend_title='Air Quality Categories')

    st.plotly_chart(fig, use_container_width=True)  
with tab3:
    fig = px.bar(category_counts_sorted, 
                y=category_counts_sorted.index,  
                x=category_counts_sorted.columns,
                orientation='h',
                color_discrete_sequence=px.colors.qualitative.Set3,
                title='Air Quality Category Counts per Station',
                labels={'Count': 'Count', 'index': 'Station'}
                )

    # Add legend and customize layout
    fig.update_layout(
        legend_title='Air Quality Categories',
        legend=dict(title='Air Quality Categories', orientation='h', yanchor='top', xanchor='left', x=0),
        yaxis_title='Station',
        xaxis_title='Count',
        margin=dict(l=100, r=50, t=70, b=70),
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)  
color_scheme = px.colors.qualitative.Set3

# Define station colors using Set3 color scheme
station_colors = {'Wanliu': color_scheme[0], 'Shunyi': color_scheme[1], 'Dongsi': color_scheme[2]}

# Create traces for each station
traces = []
for station, color in station_colors.items():
    trace = go.Histogram(x=combine_df[combine_df['station'] == station]['pm2.5'],
                         histnorm='probability density',
                         name=station,
                         marker=dict(color=color))
    traces.append(trace)

# Create layout
layout = go.Layout(title='Distribution of Air Pollution Levels (PM2.5) in Each Observation Station',
                   xaxis=dict(title='Air Pollution Level (PM2.5)'),
                   yaxis=dict(title='Probability Density'))

# Create figure
fig = go.Figure(data=traces, layout=layout)

fig.update_layout(legend=dict(title='Observation Station'))
st.plotly_chart(fig, use_container_width=True)

fig = ff.create_annotated_heatmap(
    z=correlation_df.values,
    x=correlation_df.columns.tolist(),
    y=correlation_df.index.tolist(),
    colorscale=px.colors.qualitative.Set3,
    showscale=True,
    zmin=-1,  
    zmax=1,   
    zmid=0,   
    colorbar=dict(title='Correlation'),  
    hoverongaps=False,  
    annotation_text=correlation_df.values.round(2),  
    font_colors=['black', 'white'],  
)

fig.update_layout(
    title='Correlation between Temperature and Air Pollution Parameters',
    xaxis_title='',
    yaxis_title='Air Pollution Parameters',
    xaxis=dict(tickangle=0),
    yaxis=dict(tickangle=0)
)

st.plotly_chart(fig)


rainy_average_df_sorted = rainy_average_df.apply(lambda x: x.sort_values(ascending=False), axis=1)

# Create empty list to store traces
traces = []

# Loop through each pollutant and assign color from Set3 palette
for i, column in enumerate(rainy_average_df_sorted.columns):
    trace = go.Bar(
        y=rainy_average_df_sorted.index,  # Use index as y-axis for horizontal bar chart
        x=rainy_average_df_sorted[column],  # Use pollutant values as x-axis
        name=column,
        orientation='h',  # Set orientation to horizontal (barh)
        marker=dict(color=color_scheme[i])  # Assign color from Set3 palette
    )
    traces.append(trace)

layout = go.Layout(
    title='Average Pollutant Levels by Rain Condition',
    xaxis=dict(title='Average Pollutant Level'),  # Adjust x-axis title for horizontal bar chart
    yaxis=dict(title='Rain Condition'),
    barmode='group'
)
fig = go.Figure(data=traces, layout=layout)
st.plotly_chart(fig, use_container_width=True)
st.caption('Copyright (c) Rafli Ardiansyah 2024')