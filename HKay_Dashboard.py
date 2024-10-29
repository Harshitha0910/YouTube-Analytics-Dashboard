import pandas as pd
import datetime
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Set the page configuration
st.set_page_config(
    page_title="YouTube Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
/* Main page styling */
.main {
    padding: 2rem;
    background-color: #f8f9fa;
}

/* Custom background with overlay */
.stApp {
    background: linear-gradient(135deg, #fad0c4 0%, #C2185B 99%, #fad0c4 100%);
}

/* Card styling for metrics */
.stMetric {
    background-color: rgba(255, 255, 255, 0.9) !important;
    padding: 1rem !important;
    border-radius: 0.5rem !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    transition: transform 0.2s ease-in-out !important;
}

/*.stMetric:hover {
    transform: translateY(-2px);
}*/ 

/* Headers styling */
h1 {
    color: #ffffff !important;
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    text-align: center;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    margin-bottom: 2rem !important;
}

h2, h3 {
    color: #ffffff !important;
    font-weight: 600 !important;
    margin-top: 1.5rem !important;
}

/* Sidebar styling */
.css-1d391kg {
    background-color: rgba(251, 251, 251, 0.9) !important;
}

.sidebar .sidebar-content {
    background-color: rgba(251, 251, 251, 0.9) !important;
}

/* DataFrame styling */
.dataframe {
    background-color: rgba(255, 255, 255, 0.9) !important;
    border-radius: 0.5rem !important;
    padding: 1rem !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
}

/* Plotly chart container styling */
.plotly-chart-container {
    background-color: rgba(255, 255, 255, 0.9) !important;
    border-radius: 0.5rem !important;
    padding: 1rem !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    margin: 1rem 0 !important;
}

/* Button styling */
.stButton>button {
    background-color: #667eea !important;
    color: white !important;
    border-radius: 0.5rem !important;
    padding: 0.5rem 1rem !important;
    border: none !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.2s ease-in-out !important;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
}

/* Select box styling */
.stSelectbox {
    background-color: rgba(255, 255, 255, 0.9) !important;
    border-radius: 0.5rem !important;
    padding: 0.5rem !important;
}

/* Divider styling */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, #ffffff, transparent);
    margin: 2rem 0;
}

/* Write/Text styling */
.stWrite {
    color: #ffffff !important;
    line-height: 1.6 !important;
    font-size: 1.1rem !important;
}

/* Tab styling */
.css-1d391kg .tab {
    font-weight: bold !important; /* Make tabs bold */
}

.css-1d391kg .tab:hover {
    font-weight: bold !important; /* Keep bold on hover */
    color: inherit !important;  /* Maintain original color on hover */
    
}
</style>
""", unsafe_allow_html=True)



# Add a title and subtitle
st.title("📊 Ken Jee's YouTube Channel Analysis Dashboard 📊")

# Add a brief introduction
st.write("""
**Welcome to the YouTube Analytics Dashboard! 📺 
In this app, I have analyzed the YouTube channel **Ken Jee**'s data as a practice purpose inspired by his own video. 
I have visualized and analyzed various video metrics, including views, likes, engagement rates, and more. 
Use the sidebar to navigate between aggregated metrics and individual video analysis.**
""")

# Add a divider for better visual separation
st.markdown("---")

# Step 2: Define functions for data styling and processing
def style_negative(v, props=''):
    try:
        return props if v < 0 else None
    except:
        pass

def style_positive(v, props=''):
    try:
        return props if v > 0 else None
    except:
        pass    

def audience_simple(country):
    if country == 'US':
        return 'USA'
    elif country == 'IN':
        return 'India'
    else:
        return 'Other'

# Step 3: Define function that reads data
@st.cache_data
def load_data():
    try:
        # Read and preprocess datasets
        df_agg = pd.read_csv("Aggregated_Metrics_By_Video.csv").iloc[1:, :]

        # Preprocess datasets
        df_agg.columns = ['Video', 'Video title', 'Video publish time', 'Comments added', 'Shares', 'Dislikes', 'Likes',
                          'Subscribers lost', 'Subscribers gained', 'RPM(USD)', 'CPM(USD)', 'Average % viewed', 'Average view duration',
                          'Views', 'Watch time (hours)', 'Subscribers', 'Your estimated revenue (USD)', 'Impressions', 'Impressions ctr(%)']

        df_agg['Video publish time'] = pd.to_datetime(df_agg['Video publish time'], errors='coerce')
        df_agg['Average view duration'] = df_agg['Average view duration'].apply(lambda x: datetime.datetime.strptime(x, '%H:%M:%S') if isinstance(x, str) else pd.NaT)
        df_agg['Avg_duration_sec'] = df_agg['Average view duration'].apply(lambda x: x.second + x.minute * 60 + x.hour * 3600 if pd.notna(x) else 0)
        df_agg['Engagement_ratio'] = (df_agg['Comments added'] + df_agg['Shares'] + df_agg['Dislikes'] + df_agg['Likes']) / df_agg['Views']
        df_agg['Views / sub gained'] = df_agg['Views'] / df_agg['Subscribers gained'].replace(0, pd.NA)
        df_agg.sort_values('Video publish time', ascending=False, inplace=True)

        # Read other datasets
        df_agg_sub = pd.read_csv("Aggregated_Metrics_By_Country_And_Subscriber_Status.csv")
        df_comments = pd.read_csv("All_Comments_Final.csv")
        df_time = pd.read_csv("Video_Performance_Over_Time.csv")
        df_time['Date'] = pd.to_datetime(df_time['Date'], errors='coerce')

        return df_agg, df_agg_sub, df_comments, df_time

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None, None

# Load data with loading spinner
with st.spinner('Loading data...'):
    df_agg, df_agg_sub, df_comments, df_time = load_data()

if df_agg is None:
    st.error("Failed to load data. Please check your data files and try again.")
    st.stop()

# Sidebar
add_sidebar = st.sidebar.selectbox('Aggregate or Individual Video', ('Aggregate Metrics', 'Individual Video Analysis'))

# Metrics explanation
with st.sidebar.expander("ℹ️ Metrics Explanation"):
    st.markdown("""
    - **Views**: Total number of video views
    - **Engagement ratio**: (Comments + Shares + Likes + Dislikes) / Views
    - **RPM(USD)**: Revenue per thousand views
    - **Average % viewed**: Average percentage of video watched
    - **Subscribers gained**: New subscribers from the video
    """)

if add_sidebar == 'Aggregate Metrics':
    # Create tabs
    tab1, tab2 = st.tabs(["📈 Key Metrics", "📊 Detailed Analytics"])

    with tab1:
       
    # Date filter
        min_date = df_agg['Video publish time'].min().date()
        max_date = df_agg['Video publish time'].max().date()

        date_filter = st.date_input(
            "Filter by date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date  # Restricts the max date to the max in the dataset
            )

        df_agg_filtered = df_agg[
            (df_agg['Video publish time'].dt.date >= date_filter[0]) &
            (df_agg['Video publish time'].dt.date <= date_filter[1])
            ]

    # Metrics
        df_agg_metrics = df_agg_filtered[['Views', 'Likes', 'Subscribers', 'Shares', 'Comments added',
                                      'RPM(USD)', 'Average % viewed', 'Avg_duration_sec', 
                                      'Engagement_ratio', 'Views / sub gained']]

        metric_date_6mo = df_agg_filtered['Video publish time'].max() - pd.DateOffset(months=6)
        metric_date_12mo = df_agg_filtered['Video publish time'].max() - pd.DateOffset(months=12)

        metric_medians6mo = df_agg_filtered[df_agg_filtered['Video publish time'] >= metric_date_6mo][df_agg_metrics.columns].median()
        metric_medians12mo = df_agg_filtered[df_agg_filtered['Video publish time'] >= metric_date_12mo][df_agg_metrics.columns].median()

        col1, col2, col3, col4, col5 = st.columns(5)
        columns = [col1, col2, col3, col4, col5]

        count = 0
        for i in metric_medians6mo.index:
            with columns[count]:
                delta = (metric_medians6mo[i] - metric_medians12mo[i]) / metric_medians12mo[i]
                st.metric(label=i, value=round(metric_medians6mo[i], 1), delta="{:.2%}".format(delta))
                count += 1
                if count >= 5:
                    count = 0
        
        

    with tab2:
        
        
        df_agg_diff = df_agg_filtered.copy()
        df_agg_diff['Publish_date'] = df_agg_diff['Video publish time'].apply(lambda x: x.date())
        df_agg_diff_final = df_agg_diff.loc[:, ['Video title', 'Publish_date', 'Views', 'Likes', 
                                            'Subscribers', 'Shares', 'Comments added', 'RPM(USD)', 
                                            'Average % viewed', 'Avg_duration_sec', 'Engagement_ratio', 
                                            'Views / sub gained']]
        if df_agg_diff_final['Average % viewed'].dtype == 'float' or df_agg_diff_final['Average % viewed'].dtype == 'int':
        # Uncomment the following line if your values are whole numbers (e.g., 50 for 50%)
            df_agg_diff_final['Average % viewed'] = df_agg_diff_final['Average % viewed'] / 100
        df_agg_diff_final['Average % viewed'] = df_agg_diff_final['Average % viewed'].clip(upper=1.0)
    
    
        format_dict = {}
        for col in df_agg_diff_final.columns:
            if col in ['Average % viewed', 'Engagement_ratio']:  # Percentage columns
                format_dict[col] = '{:.1%}'
            elif col == 'Views / sub gained':  # Ensure "Views / sub gained" is displayed as a whole number
                format_dict[col] = '{:,.0f}'
            elif pd.api.types.is_numeric_dtype(df_agg_diff_final[col]):  # General integer formatting for numeric columns
                format_dict[col] = '{:,.0f}'

    
        st.dataframe(
        df_agg_diff_final.style.hide()
        .applymap(style_negative, props='color:red;')
        .applymap(style_positive, props='color:green;')
        .format(format_dict)
    )
        

elif add_sidebar == 'Individual Video Analysis':
    st.write("Individual Video Performance")

    videos = tuple(df_agg['Video title'])
    video_select = st.selectbox('Pick a Video:', videos)

    agg_filtered = df_agg[df_agg['Video title'] == video_select]
    agg_sub_filtered = df_agg_sub[df_agg_sub['Video Title'] == video_select]
    agg_sub_filtered['Country'] = agg_sub_filtered['Country Code'].apply(audience_simple)
    agg_sub_filtered.sort_values('Is Subscribed', inplace=True)
    
    if 'days_published' not in df_time.columns:
        # Assuming 'Date' is the date of the record and `Video publish time` is the publish date
        df_time = df_time.merge(df_agg[['Video title', 'Video publish time']], 
                                left_on='Video Title', 
                                right_on='Video title', 
                                how='left')
        df_time['days_published'] = (df_time['Date'] - df_time['Video publish time']).dt.days
    
    # Filter data for selected video after calculating 'days_published'
    agg_time_filtered = df_time[df_time['Video Title'] == video_select]
    first_30 = agg_time_filtered[agg_time_filtered['days_published'].between(0, 30)]
    first_30 = first_30.sort_values('days_published')

    # Create and style the first chart
    fig = px.bar(agg_sub_filtered, 
                 x='Views', 
                 y='Is Subscribed',
                 color='Country',
                 orientation='h',
                 title='Views by Subscription Status and Country')

    fig.update_layout(
        plot_bgcolor='rgba(255,255,255,0.9)',
        paper_bgcolor='rgba(255,255,255,0.9)',
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode='closest'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Create and style the second chart
    agg_time_filtered = df_time[df_time['Video Title'] == video_select]
    first_30 = agg_time_filtered[agg_time_filtered['days_published'].between(0, 30)]
    first_30 = first_30.sort_values('days_published')

    fig2 = go.Figure()

    # Add traces with styling
    fig2.add_trace(go.Scatter(
        x=first_30['days_published'],
        y=first_30['Views'].cumsum(),
        mode='lines',
        name='Current Video',
        line=dict(color='#764ba2', width=4)
    ))

    fig2.update_layout(
        title='View Comparison First 30 Days',
        xaxis_title='Days Since Published',
        yaxis_title='Cumulative views',
        plot_bgcolor='rgba(255,255,255,0.9)',
        paper_bgcolor='rgba(255,255,255,0.9)',
        hovermode='x unified',
        hoverlabel=dict(bgcolor="white"),
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig2, use_container_width=True)






















