import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
        page_title='GitHub Data 🧑‍💻',
        page_icon='https://creazilla-store.fra1.digitaloceanspaces.com/icons/7914417/github-icon-md.png',
        layout="wide"
    )
st.sidebar.image('https://creazilla-store.fra1.digitaloceanspaces.com/icons/7914417/github-icon-md.png', width=200)
st.sidebar.markdown('# GitHub Repository Data Visualiser')
st.sidebar.markdown('This is a visualtization of a dataset capturing a collection of 1052 GitHub repositories')

# Sidebar footer
st.sidebar.markdown('---')
st.sidebar.write('Developed by Snigdha Bose')
st.sidebar.write('Contact here @[snigdhab7](https://github.com/snigdhab7)')
# Header
st.markdown('# GitHub Repository Data Visualisation WebApp')
@st.cache_data
def load_data():
    data = pd.read_csv('github_dataset.csv')
    return data

@st.cache_data
def load_repo_data():
    data = pd.read_csv('new_repository_data.csv', parse_dates=['created_at'])
    data['languages_used'] = data['languages_used'].apply(lambda x: eval(x) if pd.notna(x) else [])
    return data

# Define a function to create the layout for the "Data Overview" tab
repo_data = load_repo_data()

def data_overview():
    
    st.markdown('<a name="specific-section"></a>', unsafe_allow_html=True)
    

    # Load the data
   

    #data = load_repo_data()
    # Extract year from the 'created_at' column
    repo_data['created_at'] = pd.to_datetime(repo_data['created_at'])
    language_popularity = pd.DataFrame()
    

    # Use columns to create a grid layout
    col1, col2 = st.columns([1, 1])  # Split into 2 columns, 2:1 ratio

    # Bar chart for top 25 GitHub repositories by popularity (stars)
    top_25_repos = repo_data.nlargest(25, 'stars_count')
    bar_chart = px.bar(top_25_repos, x='stars_count', y='name', title='Top 25 Repositories by Stars')
    # Custom labels for the first graph
    bar_chart.update_xaxes(title_text="Stars Count")
    bar_chart.update_yaxes(title_text="Repository Name")
    col1.plotly_chart(bar_chart)

    unique_languages = set()
    for languages in repo_data['languages_used']:
        unique_languages.update(languages)

    # Create a MultiIndex DataFrame to store language popularity over the years
    language_popularity = pd.DataFrame(index=repo_data['created_at'], columns=list(unique_languages)).fillna(0)

    # Loop through the rows and populate the language popularity DataFrame
    for index, row in repo_data.iterrows():
        for language in row['languages_used']:
            language_popularity.loc[row['created_at'], language] += 1

    # Resample data by year and sum the counts for each language
    language_popularity_resampled = language_popularity.resample('Y').sum()
    top_10_languages = language_popularity_resampled.sum().sort_values(ascending=False).head(10).index

    remaining_languages = [language for language in unique_languages if language not in top_10_languages]
    language_popularity_resampled['Other'] = language_popularity_resampled[remaining_languages].sum(axis=1)

    language_popularity_resampled = language_popularity_resampled[top_10_languages]

    # Add title to the second graph
    fig = px.line(language_popularity_resampled, title='Language Popularity Over the Years')
    fig.update_xaxes(title_text="Year")
    fig.update_yaxes(title_text="Popularity Count")
    fig.update_layout(title_x=0)  # Center the title

    # Display the second graph
    col2.plotly_chart(fig)


    # Calculate user engagement metrics over time
    engagement_data = repo_data[['created_at', 'stars_count', 'forks_count', 'watchers']]
    engagement_data['Year'] = engagement_data['created_at'].dt.year

    # Group by year and calculate total engagement metrics
    engagement_by_year = engagement_data.groupby('Year').agg({
        'stars_count': 'sum',
        'forks_count': 'sum',
        'watchers': 'sum'
    }).reset_index()

    # Calculate engagement growth rates
    engagement_by_year['stars_growth_rate'] = engagement_by_year['stars_count'].pct_change() * 100
    engagement_by_year['forks_growth_rate'] = engagement_by_year['forks_count'].pct_change() * 100
    engagement_by_year['watchers_growth_rate'] = engagement_by_year['watchers'].pct_change() * 100
    # Create an area chart for engagement metrics
    engagement_area_fig = px.area(
        engagement_by_year,
        x='Year',
        y=['stars_count', 'forks_count', 'watchers'],
        labels={'Year': 'Year', 'value': 'Count'},
        title='User Engagement Over Time'
    )

    # Create an area chart for engagement growth rates
    growth_rate_area_fig = px.area(
        engagement_by_year,
        x='Year',
        y=['stars_growth_rate', 'forks_growth_rate', 'watchers_growth_rate'],
        labels={'Year': 'Year', 'value': 'Growth Rate (%)'},
        title='Engagement Growth Rates Over Time'
    )

    # Use columns to create a grid layout
    col3, col4 = st.columns([1, 1])

    # Display the engagement area chart in the first column
    col3.plotly_chart(engagement_area_fig)

    # Display the growth rates area chart in the second column
    col4.plotly_chart(growth_rate_area_fig)

    # Add a horizontal line to separate the sections
    
    st.write('<b style="font-size: 24px;">Repository Insights</b>', unsafe_allow_html=True)

    # Create a new row with two columns
    col5, col6 = st.columns([1, 1])

    repo_name = col5.selectbox('Select Repository', repo_data['name'].values)
    
    # Assuming each repository has a list of languages in a string format, we first need to convert it to a list
    # data['languages_used'] = data['languages_used'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])
    # Then we count the number of unique languages used across all repositories

 
    language_counts = repo_data['languages_used'].apply(lambda x: len(set(x)))
    max_languages = language_counts.max()

    # Calculate the Issue Resolution Efficiency
    repo_data['issue_resolution_efficiency'] = repo_data['pull_requests'] / (repo_data['commit_count'] + 1)  # +1 to avoid division by zero
    max_efficiency = repo_data['issue_resolution_efficiency'].max()

    # Calculate the Repository Popularity Index
    repo_data['popularity_index'] = (repo_data['stars_count'] + repo_data['forks_count'] + repo_data['watchers']) / 3
    max_popularity = repo_data['popularity_index'].max()

    # Calculate the Community Involvement Indicator
    repo_data['community_involvement'] = (repo_data['forks_count'] + repo_data['pull_requests']) / 2
    max_community_involvement = repo_data['community_involvement'].max()

    # Define function to create gauges
    def create_gauge(chart_title, value, max_value):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': chart_title},
            gauge={'axis': {'range': [None, max_value]}}
        ))
        # Reduce the size of the gauge
        fig.update_layout(width=300, height=300)
        return fig
    
    # Use columns to create a grid layout for the second row
    col7, col8, col9, col10 = st.columns(4)

    with col7:
        # Language Diversity Index for a specific repository
        if repo_name in repo_data['name'].values:
            # Find the index corresponding to the selected repository name
            selected_index = repo_data[repo_data['name'] == repo_name].index[0]
            st.markdown('<a name="specific-section"></a>', unsafe_allow_html=True)
            st.plotly_chart(create_gauge("Language Diversity Index", language_counts[selected_index], max_languages))

    with col8:
        # Issue Resolution Efficiency for a specific repository
        if repo_name in repo_data['name'].values:
            # Find the row corresponding to the selected repository name
            selected_row = repo_data[repo_data['name'] == repo_name]
            efficiency = selected_row['issue_resolution_efficiency'].values[0]
            st.plotly_chart(create_gauge("Issue Resolution Efficiency", efficiency, max_efficiency))

    with col9:
        # Repository Popularity Index for a specific repository
        if repo_name in repo_data['name'].values:
            # Find the index corresponding to the selected repository name
            repo_index = repo_data[repo_data['name'] == repo_name].index[0]
            st.plotly_chart(create_gauge("Repository Popularity Index", repo_data['popularity_index'][repo_index], max_popularity))

    with col10:
        # Community Involvement Indicator for a specific repository
        if repo_name in repo_data['name'].values:
            # Find the index corresponding to the selected repository name
            repo_index = repo_data[repo_data['name'] == repo_name].index[0]
            st.plotly_chart(create_gauge("Community Involvement Indicator", repo_data['community_involvement'][repo_index], max_community_involvement))

data = load_data()


def language_distribution():
    
    language_count = data['language'].value_counts()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.write("Filter by Language")
        selected_language = st.selectbox('Select a Language', data['language'].unique(), index=1)
        filtered_data = data[data['language'] == selected_language]
        st.write(filtered_data)

    with col2:
        st.write("Box Plot - Stars Count by Language")
        fig = px.box(data, x='language', y='stars_count')
        fig.update_traces(marker=dict(color='pink'))
        st.plotly_chart(fig)
    st.write("Language Distribution")
    st.bar_chart(language_count)


def correlation_matrix():
    st.write("Correlation Matrix")
    numeric_data = data.select_dtypes(include=['float64', 'int64'])
    plt.figure(figsize=(10, 6))
    sns.heatmap(numeric_data.corr(), annot=True)
    st.pyplot(plt)



def scatter_plot():
    # Create two columns for the scatter plots
    col1, col2 = st.columns([1, 1])

    # Scatter plot 1 - Stars vs Forks
    scatter_plot_fig1 = px.scatter(data, x='stars_count', y='forks_count', hover_data=['repositories'],
                                  title='Stars vs Forks',
                                  labels={'stars_count': 'Stars Count', 'forks_count': 'Forks Count'})
    
    # Set the color to 'white' for the first scatter plot (constant color for all data points)
    scatter_plot_fig1.update_traces(marker=dict(color='white'))
    
    # Customize the layout if needed
    scatter_plot_fig1.update_layout(
        xaxis_title="Stars Count",
        yaxis_title="Forks Count",
    )
    
    # Display the first scatter plot in the first column
    col1.plotly_chart(scatter_plot_fig1)

    # Scatter plot 2 - Engagement vs Popularity
    scatter_plot_fig2 = px.scatter(data, x='stars_count', y='pull_requests', 
                                  title='Engagement vs. Popularity Scatter Plot',
                                  labels={'stars_count': 'Stars Count', 'pull_requests': 'Pull Requests'})

    # Customize the layout if needed
    scatter_plot_fig2.update_layout(
        xaxis_title="Stars Count",
        yaxis_title="Pull Requests",
        showlegend=True  # You can set this to False if you don't want a legend
    )

    # Display the second scatter plot in the second column
    col2.plotly_chart(scatter_plot_fig2)

    col3, col4 = st.columns([1, 1])
    # Calculate the number of watchers for each repository
    watchers_count = repo_data.groupby('name')['watchers'].max().reset_index()

    # Create a bar plot for watchers
    fig_watchers = px.bar(watchers_count, x='watchers', y='name', title='Watchers Count for Repositories')
    fig_watchers.update_traces(marker=dict(color='pink'))
    col3.plotly_chart(fig_watchers)
    # Add text below the scatter plots with CSS styling
    col4.markdown(
        "<div style='font-size: 14px; text-align: center; margin-top: 150px; margin-left: 100px;'><b>Stars are often an indicator of a repository's popularity or the attention it receives from the community. Forks are also associated with a repository's popularity, as they represent the number of times the repository has been forked by other users. Pull requests represent active contributions. Comparing them can show whether a repository's popularity aligns with its level of active engagement.</b></div>",
        unsafe_allow_html=True
    )
    #watchers_and_contributors()


def watchers_and_contributors():
    # Calculate the number of watchers for each repository
    watchers_count = repo_data.groupby('name')['watchers'].max().reset_index()

    # Create a bar plot for watchers
    st.write("Bar Plot - Watchers Count")
    fig_watchers = px.bar(watchers_count, x='watchers', y='name', title='Watchers Count for Repositories')
    st.plotly_chart(fig_watchers)

    # Calculate the number of contributors for each repository
    #contributors_count = data.groupby('repositories')['contributors'].max().reset_index()

    # Create a bar plot for contributors
    #st.write("Bar Plot - Contributors Count")
    #fig_contributors = px.bar(contributors_count, x='repositories', y='contributors', title='Contributors Count for Repositories')
    #st.plotly_chart(fig_contributors)




# Create tabs dictionary
# Create a dictionary of tabs with function references
tabs = {
    "Data Overview": data_overview,
    "Language Trends": language_distribution,
    "Correlation Matrix": correlation_matrix,
    "Popularity Insights": scatter_plot,
    
}


selected_tab = st.sidebar.selectbox("Select a tab:", list(tabs.keys()))



tabs[selected_tab]()


