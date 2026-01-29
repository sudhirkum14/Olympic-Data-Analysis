import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

# --- STEP 1: DATA LOADING & PREPROCESSING ---
@st.cache_data
def load_data():
    # Dataset load karna
    df = pd.read_csv("athlete_events.csv")
    region_df = pd.read_csv("noc_regions.csv")
    
    # 1. NOC ke basis pe region (Country Name) merge karna
    df = df.merge(region_df, on='NOC', how='left')
    
    # 2. Cleaning: Duplicate rows hatana
    df.drop_duplicates(inplace=True)
    
    # 3. Handling Missing Values (Jo aapne notebook mein kiya tha)
    df['Age'].fillna(df['Age'].mean(), inplace=True)
    df['Height'].fillna(df['Height'].mean(), inplace=True)
    df['Weight'].fillna(df['Weight'].mean(), inplace=True)
    
    # 4. ONE-HOT ENCODING (Medal columns create karna)
    # Isse 'Bronze', 'Gold', aur 'Silver' ke alag columns ban jayenge
    dummies = pd.get_dummies(df['Medal']).astype(int)
    df = pd.concat([df, dummies], axis=1)
    
    return df

df = load_data()

# --- STEP 2: MEDAL TALLY LOGIC ---
def fetch_medal_tally(df, year, country):
    # Team events mein multiple medals ko 1 count karne ke liye duplicates drop karna
    medal_df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    
    temp_df = medal_df
    if year == 'Overall' and country == 'Overall':
        pass
    elif year != 'Overall' and country == 'Overall':
        temp_df = temp_df[temp_df['Year'] == int(year)]
    elif year == 'Overall' and country != 'Overall':
        temp_df = temp_df[temp_df['region'] == country]
    else:
        temp_df = temp_df[(temp_df['Year'] == int(year)) & (temp_df['region'] == country)]

    # Groupby karke medals sum karna
    x = temp_df.groupby('region').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold', ascending=False).reset_index()
    x['Total'] = x['Gold'] + x['Silver'] + x['Bronze']
    
    return x

# --- STEP 3: STREAMLIT UI ---
st.sidebar.title("Olympic Analysis Dashboard")
user_menu = st.sidebar.radio(
    'Menu',
    ('Medal Tally', 'Overall Analysis','Country Analysis', 'Country-wise Analysis', 'India Special Focus','Olympic Records & Fun Facts', 'Athlete-wise Analysis','Gender Analysis', 'Athlete Physical Stats')
)

# --- 1. MEDAL TALLY PAGE ---
if user_menu == 'Medal Tally':
   st.header("Global Medal Distribution")
   # Sidebar filters
   years = sorted(df['Year'].unique().tolist(), reverse=True)
   years.insert(0, 'Overall')
   selected_year = st.sidebar.selectbox("Year", years)
    
   # Logic for Map and Tally
   temp_df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
   if selected_year != 'Overall':
        temp_df = temp_df[temp_df['Year'] == int(selected_year)]
    
   map_df = temp_df.groupby('NOC').sum()[['Gold', 'Silver', 'Bronze']].reset_index()
   map_df['Total'] = map_df['Gold'] + map_df['Silver'] + map_df['Bronze']
    
   # World Map Plot
   fig = px.choropleth(map_df, locations="NOC", color="Total", 
                        hover_name="NOC", color_continuous_scale=px.colors.sequential.Plasma,
                        title=f"Total Medals by Country ({selected_year})")
   st.plotly_chart(fig, use_container_width=True)
    
   st.subheader("Leaderboard")
   st.dataframe(map_df.sort_values('Gold', ascending=False), use_container_width=True)

# --- 2. OVERALL ANALYSIS ---
if user_menu == 'Overall Analysis':
    st.header("Top Statistics")
    
    editions = df['Year'].nunique() - 1 # 1906 is often excluded or counted
    cities = df['City'].nunique()
    sports = df['Sport'].nunique()
    athletes = df['Name'].nunique()
    nations = df['region'].nunique()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Editions", editions)
        st.metric("Athletes", athletes)
    with col2:
        st.metric("Hosts", cities)
        st.metric("Nations", nations)
    with col3:
        st.metric("Sports", sports)

    # Line Chart: Nations over time
    nations_over_time = df.drop_duplicates(['Year', 'region']).groupby('Year').count()['region'].reset_index()
    fig = px.line(nations_over_time, x="Year", y="region", title="Participating Nations over Years")
    st.plotly_chart(fig)

# --- 3. COUNTRY-WISE ANALYSIS ---
if user_menu == 'Country-wise Analysis':
    country_list = sorted(df['region'].dropna().unique().tolist())
    selected_country = st.sidebar.selectbox('Select Country', country_list)

    # Filter data for country
    country_df = df.dropna(subset=['Medal'])
    country_df = country_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    country_df = country_df[country_df['region'] == selected_country]
    
    final_df = country_df.groupby('Year').count()['Medal'].reset_index()
    fig = px.line(final_df, x="Year", y="Medal", title=f"{selected_country} Medals over Years")
    st.plotly_chart(fig)

# --- 4. INDIA SPECIAL FOCUS ---
if user_menu == 'India Special Focus':
    st.header("India's Olympic Journey 🇮🇳")
    
    # India filtering
    india_df = df[df['region'] == 'India']
    india_medals = india_df.dropna(subset=['Medal']).drop_duplicates(subset=['Games', 'Year', 'Sport', 'Event', 'Medal'])
    
    # Metric cards for India
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Gold", int(india_medals['Gold'].sum()))
    with c2:
        st.metric("Total Silver", int(india_medals['Silver'].sum()))
    with c3:
        st.metric("Total Bronze", int(india_medals['Bronze'].sum()))

    # India performance over time
    india_line = india_medals.groupby('Year').count()['Medal'].reset_index()
    fig_india = px.line(india_line, x="Year", y="Medal", title="India's Medal Growth over Years", markers=True)
    st.plotly_chart(fig_india)

    # Top Sports for India
    st.subheader("India's Best Sports")
    india_sports = india_medals.groupby('Sport').count()['Medal'].sort_values(ascending=False).reset_index()
    fig_sport = px.bar(india_sports, x='Sport', y='Medal', color='Medal', title="Medals by Sport")
    st.plotly_chart(fig_sport)

# --- 4. ATHLETE-WISE ANALYSIS ---
if user_menu == 'Athlete-wise Analysis':
    st.header("Top 15 Athletes")
    sport_list = sorted(df['Sport'].unique().tolist())
    sport_list.insert(0, 'Overall')
    selected_sport = st.sidebar.selectbox('Select Sport', sport_list)
    
    temp_df = df.dropna(subset=['Medal'])
    if selected_sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == selected_sport]
        
    top_athletes = temp_df['Name'].value_counts().reset_index().head(15)
    top_athletes.columns = ['Name', 'Total Medals']
    st.table(top_athletes)

# --- 3. COUNTRY ANALYSIS (Host Advantage) ---
if user_menu == 'Country Analysis':
    country_list = sorted(df['region'].dropna().unique().tolist())
    selected_country = st.sidebar.selectbox('Select Country', country_list)
    
    country_df = df[df['region'] == selected_country].dropna(subset=['Medal'])
    country_df = country_df.drop_duplicates(subset=['Games', 'Year', 'Sport', 'Event', 'Medal'])
    
    # Medals by Sport (Bar Chart)
    st.subheader(f"Medals Won by {selected_country} in Different Sports")
    sport_medal = country_df.groupby('Sport').count()['Medal'].reset_index().sort_values('Medal', ascending=False)
    fig = px.bar(sport_medal, x='Sport', y='Medal', color='Medal', text_auto=True)
    st.plotly_chart(fig)

# --- 4. GENDER ANALYSIS ---
if user_menu == 'Gender Analysis':
    st.header("Gender Participation & Success")
    
    # Men vs Women participation over time
    men = df[df['Sex'] == 'M'].drop_duplicates(['Year', 'Name']).groupby('Year').count()['Name'].reset_index()
    women = df[df['Sex'] == 'F'].drop_duplicates(['Year', 'Name']).groupby('Year').count()['Name'].reset_index()
    
    final = men.merge(women, on='Year', how='left').fillna(0)
    final.columns = ['Year', 'Male', 'Female']
    
    fig = px.line(final, x="Year", y=["Male", "Female"], title="Male vs Female Participation Over Years")
    st.plotly_chart(fig)
    
    # Medal distribution by gender
    st.subheader("Medals won by Gender")
    gender_medals = df.dropna(subset=['Medal']).groupby('Sex').count()['Medal'].reset_index()
    fig_pie = px.pie(gender_medals, values='Medal', names='Sex', hole=0.4)
    st.plotly_chart(fig_pie)
if user_menu == 'Olympic Records & Fun Facts':
    st.header("🏆 Olympic World Records & Fun Facts")

    # Metrics for unique counts
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"Total Sports Played: **{df['Sport'].nunique()}**")
    with c2:
        st.info(f"Total Unique Events: **{df['Event'].nunique()}**")

    st.markdown("---")
    
    # Function to display record cards
    def record_card(title, name, team, sport, year, value, unit):
        st.subheader(title)
        col_a, col_b = st.columns([1, 2])
        with col_a:
            st.metric(label="Value", value=f"{value} {unit}")
        with col_b:
            st.write(f"**Name:** {name}")
            st.write(f"**Team:** {team} | **Sport:** {sport}")
            st.write(f"**Olympic Games:** {year}")

    # 1. Youngest Athlete (NaNs hatakar real min nikalna)
    youngest_row = df[df['Age'] == df['Age'].min()].iloc[0]
    record_card("👶 Youngest Athlete", youngest_row['Name'], youngest_row['region'], 
                youngest_row['Sport'], youngest_row['Games'], int(youngest_row['Age']), "Years")

    # 2. Oldest Athlete
    oldest_row = df[df['Age'] == df['Age'].max()].iloc[0]
    record_card("👴 Oldest Athlete", oldest_row['Name'], oldest_row['region'], 
                oldest_row['Sport'], oldest_row['Games'], int(oldest_row['Age']), "Years")

    # 3. Tallest Athlete
    tallest_row = df[df['Height'] == df['Height'].max()].iloc[0]
    record_card("📏 Tallest Athlete", tallest_row['Name'], tallest_row['region'], 
                tallest_row['Sport'], tallest_row['Games'], int(tallest_row['Height']), "cm")

    # 4. Heaviest Athlete
    heaviest_row = df[df['Weight'] == df['Weight'].max()].iloc[0]
    record_card("🐘 Heaviest Athlete", heaviest_row['Name'], heaviest_row['region'], 
                heaviest_row['Sport'], heaviest_row['Games'], int(heaviest_row['Weight']), "kg")

    st.markdown("---")
    st.write("💡 *Note: Ye records available dataset ke 120 saal ke itihaas par based hain.*")

# --- 5. ATHLETE PHYSICAL STATS ---
if user_menu == 'Athlete_Physical Stats':
    st.header("Physical Attributes of Medalists")
    
    sport_list = sorted(df['Sport'].unique().tolist())
    selected_sport = st.sidebar.selectbox('Select Sport', sport_list)
    
    temp_df = df.dropna(subset=['Medal'])
    if selected_sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == selected_sport]
    
    # Height vs Weight Scatter Plot
    fig = px.scatter(temp_df, x="Height", y="Weight", color="Medal", 
                     symbol="Sex", title=f"Height vs Weight for {selected_sport} Medalists")
    st.plotly_chart(fig)
    
    # Age Distribution (KDE Plot)
    st.subheader("Age Distribution of Medalists")
    gold = temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna()
    silver = temp_df[temp_df['Medal'] == 'Silver']['Age'].dropna()
    bronze = temp_df[temp_df['Medal'] == 'Bronze']['Age'].dropna()
    
    fig_age = ff.create_distplot([gold, silver, bronze], ['Gold', 'Silver', 'Bronze'], 
                                 show_hist=False, show_rug=False)
    st.plotly_chart(fig_age)