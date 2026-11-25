import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
from streamlit_echarts import st_echarts
import requests
import os
import base64
from streamlit_lottie import st_lottie
from dotenv import load_dotenv
# # 🏏 Background function for Chatbot tab only
# def add_chatbot_bg(image_file):
#     with open(image_file, "rb") as f:
#         encoded_string = base64.b64encode(f.read()).decode()
#     bg_style = f"""
#     <style>
#     [data-testid="stAppViewContainer"] {{
#         background-image: linear-gradient(
#             rgba(0, 0, 0, 0.55),
#             rgba(0, 0, 0, 0.55)
#         ), url("data:image/jpeg;base64,{encoded_string}");
#         background-size: cover;
#         background-position: center;
#         background-repeat: no-repeat;
#     }}
#     [data-testid="stHeader"], [data-testid="stToolbar"] {{
#         background: rgba(0, 0, 0, 0);
#     }}
#     </style>
#     """
#     st.markdown(bg_style, unsafe_allow_html=True)

# Load environment variables
load_dotenv()

def get_api_response(messages):
    """Send messages to the API and get response"""
    url = "https://open-ai21.p.rapidapi.com/conversationllama"
    payload = {"messages": messages, "web_access": False}
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "open-ai21.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error making API request: {e}")
        return None


def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "api_key_set" not in st.session_state:
        st.session_state.api_key_set = bool(os.getenv("RAPIDAPI_KEY"))


def display_chat_messages():
    """Display chat messages in the UI"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# #  The Background code part 

# def get_base64_of_image(image_path):
#     with open(image_path, "rb") as image_file:
#         return base64.b64encode(image_file.read()).decode()

# def set_bg_from_local(image_file):
#     encoded_string = get_base64_of_image(image_file)
#     st.markdown(
#         f"""
#         <style>
#         .stApp {{
#             background-image: url("data:image/png;base64,{encoded_string}");
#             background-size: cover;
#         }}
#         </style>
#         """,
#         unsafe_allow_html=True
#     )


# --- Page Configuration ---
st.set_page_config(
    page_title="ODI Analysis Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E86C1;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .tab-header {
        font-size: 1.8rem;
        color: #17A589;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F0F2F6;
        border-radius: 8px;
        padding: 15px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2E86C1;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- Data Loading and Caching ---
@st.cache_data
def load_data():
    try:
        # Read CSV files
        bowling_df = pd.read_csv('bowling_clean.csv')
        fow_df = pd.read_csv("fow_clean.csv")
        partnership_df = pd.read_csv("partnership_clean.csv")
        player_info_df = pd.read_csv('player_info_clean.csv')
        batting_df = pd.read_csv("player_batting_summary.csv")

        # Clean unwanted numeric data in 'team' and 'opposition'
        team_mask = pd.to_numeric(bowling_df['team'], errors='coerce').isna()
        opposition_mask = pd.to_numeric(bowling_df['opposition'], errors='coerce').isna()
        bowling_df = bowling_df[team_mask & opposition_mask]

        # Merge player names for clarity
        bowling_df = bowling_df.merge(
            player_info_df[['player_id', 'player_name']],
            left_on='bowler id', right_on='player_id', how='left'
        )

        partnership_df = partnership_df.merge(
            player_info_df[['player_id', 'player_name']],
            left_on='player1', right_on='player_id', how='left'
        )
        partnership_df.rename(columns={'player_name': 'player1_name'}, inplace=True)

        partnership_df = partnership_df.merge(
            player_info_df[['player_id', 'player_name']],
            left_on='player2', right_on='player_id', how='left'
        )
        partnership_df.rename(columns={'player_name': 'player2_name'}, inplace=True)

        fow_df_named = fow_df.merge(
            player_info_df[['player_id', 'player_name']],
            left_on='player', right_on='player_id', how='left'
        )

        batting_df = pd.read_csv("player_batting_summary.csv")

# 🧠 Check what columns are present
        if 'player_id' in batting_df.columns:
            batting_df = batting_df.merge(
                player_info_df[['player_id', 'player_name']],
                on='player_id',
                how='left'
            )
        elif 'player' in batting_df.columns:
            batting_df = batting_df.merge(
            player_info_df[['player_id', 'player_name']],
            left_on='player',
            right_on='player_id',
            how='left'
            )
        elif 'player_name' not in batting_df.columns:
        # If no id or name column exists, just copy names manually
            batting_df['player_name'] = "Unknown Player"

# 🧩 Normalize column names for boundaries
        batting_df.rename(columns={'Fours': '4s', 'Sixes': '6s'}, inplace=True)

        # Return 4 datasets to match main()
        return bowling_df, fow_df_named, partnership_df,batting_df

    except FileNotFoundError:
        st.error("⚠️ Data files not found. Please ensure all CSV files are in the same directory.")
        return None, None, None, None
    
# --- Main App ---
def main():
    st.markdown('<h1 class="main-header"> 🏏 Crickalytics ODI </h1>', unsafe_allow_html=True)
    
    bowling_df, fow_df_named, partnership_df, batting_df = load_data()

    if bowling_df is None:
        return

    st.sidebar.title("📊 Dashboard Controls")
    st.sidebar.markdown("---")
    
    st.sidebar.header("Dataset Overview")
    total_matches = bowling_df['Match ID'].nunique()
    total_players = pd.concat([partnership_df['player1_name'], partnership_df['player2_name']]).nunique()
    total_wickets = bowling_df['wickets'].sum()
    
    st.sidebar.metric("Total Matches Analyzed", f"{total_matches}")
    st.sidebar.metric("Total Players Found", f"{total_players}")
    st.sidebar.metric("Total Wickets Taken", f"{int(total_wickets)}")


    
    tab1,tab2,tab3, tab4, tab5, tab6= st.tabs(["🤖 Chatbot","🏠 Home","👤 player Analysis", "🌍 Team Analysis", "📊 Match Analysis", "🤝 Partnership Analysis"])

    with tab1:
        # get_api_response()
        
        st.markdown("### 🧠 Cricket Chat AI Assistant")
        st.markdown("Ask anything about ODI Cricket — players, records, stats, and more!")
        st.markdown("---")

     #   # Optional: background for chatbot
        st.markdown("""
            <style>
            [data-testid="stAppViewContainer"] {
                background-image: url('https://your-image-link-here.jpg');
                background-size: cover;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }
            </style>
        """, unsafe_allow_html=True)

        # Initialize chat session
        initialize_session_state()

        # Check API key
        if not st.session_state.api_key_set:
            st.error("❌ RAPIDAPI_KEY not found in environment variables!")
            st.info("Please set up your .env file with RAPIDAPI_KEY before using this app.")
        else:
            with st.sidebar:
                st.header("🛠️ Chat Controls")
                if st.button("🗑️ Clear Chat", type="secondary"):
                    st.session_state.messages = []
                    st.rerun()

            # Display chat history
            chat_container = st.container()
            with chat_container:
                display_chat_messages()

            # User input and AI response
            if prompt := st.chat_input("Type your cricket question here..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.write(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("🤔 Thinking..."):
                        response_data = get_api_response(st.session_state.messages)
                        if response_data:
                            assistant_response = response_data.get('result', response_data.get('message', response_data.get('content', 'Could not process your request.')))
                            st.write(assistant_response)
                            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                        else:
                            error_msg = "Sorry, I'm having trouble connecting right now."
                            st.error(error_msg)
                            st.session_state.messages.append({"role": "assistant", "content": error_msg})

    with tab2:
        home_tab()
    with tab3:
        player_analysis_tab(bowling_df, fow_df_named, partnership_df,batting_df)
    with tab4:
        team_analysis_tab(bowling_df, fow_df_named, partnership_df)
    with tab5:
        match_analysis_tab(bowling_df, fow_df_named, partnership_df)
    with tab6:
        partnership_analysis_tab(partnership_df)

# ✅ HOME TAB FUNCTION
def home_tab():
    st.markdown('<h2 class="tab-header">🏠 Home — ODI Cricket Analysis</h2>', unsafe_allow_html=True)

    st.markdown("""
    Welcome to **Crickalytic ODI**, an interactive dashboard designed to explore and analyze 
    the world of **One Day International (ODI) Cricket** (1971–2024).

    ### 🎯 Purpose
    - Discover which teams dominate ODIs.
    - Compare batting and bowling performances.
    - Analyze country-wise player contributions.
    - Visualize match and tournament trends.

    ### 📂 Dataset Overview
    This dashboard uses **6 key ODI datasets** that capture every aspect of the game:
    1. 🏆 Final Match Summary  
    2. 🏏 Player Batting Summary  
    3. 🎯 Fall of Wickets (FOW)  
    4. 👤 Player Info  
    5. 🤝 Partnership Data  
    6. 🎯 Bowling Summary  

    ---
    Below you can explore a preview of all 6 datasets (first 50 rows each) 👇
    """)

    try:
        match_df = pd.read_csv("Final_match_summary.csv")
        batting_df = pd.read_csv("player_batting_summary.csv")
        fow_df = pd.read_csv("fow_clean.csv")
        player_info_df = pd.read_csv("player_info_clean.csv")
        partnership_df = pd.read_csv("partnership_clean.csv")
        bowling_df = pd.read_csv("bowling_clean.csv")

        st.subheader("🏆 Final Match Summary")
        st.dataframe(match_df.head(50))

        st.subheader("🎯 Fall of Wickets (FOW) Data")
        st.dataframe(fow_df.head(50))

        st.subheader("👤 Player Info Data")
        st.dataframe(player_info_df.head(50))

        st.subheader("🤝 Partnership Data")
        st.dataframe(partnership_df.head(50))

        st.subheader("🎯 Player Bowling Summary")
        st.dataframe(bowling_df.head(50))

        st.subheader("🏏 Player Batting Summary")
        st.dataframe(batting_df.head(50))


    except FileNotFoundError:
        st.error("⚠️ One or more dataset files are missing. Please check your directory.")

    st.markdown("""
    ---
    ### 📌 Navigation Guide
    - **🏠 Home:** Overview and datasets  
    - **👤 Player Analysis:** Explore batting and bowling stats  
    - **🌍 Team Analysis:** Compare team performances  
    - **📊 Match Analysis:** Match-by-match breakdowns  
    - **🤝 Partnership Analysis:** Best batting partnerships  
    - **🤖 Chatbot:** Ask cricket-related questions  

    Enjoy exploring the exciting world of ODI cricket with **Crickalytics ODI**! 🏏✨
    """)


def create_death_overs_analysis(bowling_df):
    """Analyze death overs (40-50) performance"""
    death_overs = bowling_df[bowling_df['overs'].between(41, 50)].copy()
    powerplay = bowling_df[bowling_df['overs'].between(1, 10)].copy()
    middle_overs = bowling_df[bowling_df['overs'].between(11, 40)].copy()
    
    # Team performance by phase
    phase_data = []
    for phase_name, phase_df in [('Powerplay (1-10)', powerplay), 
                                ('Middle (11-40)', middle_overs), 
                                ('Death (40-50)', death_overs)]:
        phase_stats = phase_df.groupby('team').agg({
            'wickets': 'sum',
            'economy': 'mean',
            'conceded': 'sum'
        }).reset_index()
        phase_stats['phase'] = phase_name
        phase_data.append(phase_stats)
    
    phase_comparison = pd.concat(phase_data, ignore_index=True)
    
    # Create the visualization
    fig = px.bar(
        phase_comparison,
        x='team',
        y='economy',
        color='phase',
        barmode='group',
        title='Team Economy Rate by Match Phase',
        hover_data=['wickets', 'conceded'],
        labels={'economy': 'Economy Rate', 'team': 'Team'}
    )
    fig.update_layout(
        xaxis_tickangle=45,
        height=500,
        showlegend=True
    )
    return fig

def player_analysis_tab(bowling_df, fow_df_named, partnership_df,batting_df):
    st.markdown('<h2 class="tab-header">👤 Bowler Performance Deep Dive</h2>', unsafe_allow_html=True)
    
    st.subheader("Bowling Performance")
    total_wickets_per_bowler = bowling_df.groupby('player_name')['wickets'].sum()
    wicket_takers_list = total_wickets_per_bowler[total_wickets_per_bowler > 0].index.tolist()
    bowler_list = sorted(wicket_takers_list)
    selected_bowler = st.selectbox("Select a Bowler", bowler_list)
    player_bowling_stats = bowling_df[bowling_df['player_name'] == selected_bowler]
    
    # Chart 1: Wickets vs Opposition
    player_vs_opposition = player_bowling_stats.groupby('opposition')['wickets'].sum().reset_index()
    fig_vs_opposition = px.bar(player_vs_opposition, x='opposition', y='wickets', title=f"{selected_bowler}'s Wickets vs Opposition", color_discrete_sequence=px.colors.sequential.Aggrnyl)
    st.plotly_chart(fig_vs_opposition, use_container_width=True)

    # Chart 2: Bowler Economy Rate Distribution (NEW)
    fig_economy_box = px.box(player_bowling_stats, y='economy', title=f"Economy Rate Consistency for {selected_bowler}", points="all")
    fig_economy_box.update_traces(marker=dict(color='#17A589'))
    st.plotly_chart(fig_economy_box, use_container_width=True)

        # ====================== 🏏 PLAYER BATTING PERFORMANCE SECTION ======================
    @st.cache_data
    def load_and_aggregate_data(csv_path):
        """
        Loads ball-by-ball data and aggregates it to a 
        per-player, per-match level.
        """
        try:
            df = pd.read_csv(csv_path, low_memory=False)
            
            # --- 1. Pre-process Data ---
            # Calculate balls faced (exclude wides)
            df['balls_faced'] = df['wides'].apply(lambda x: 0 if x > 0 else 1)
            # Calculate 4s and 6s
            df['fours'] = df['runs_off_bat'].apply(lambda x: 1 if x == 4 else 0)
            df['sixes'] = df['runs_off_bat'].apply(lambda x: 1 if x == 6 else 0)

            # --- 2. Aggregate Batting Stats ---
            # Group by match and striker to get runs, balls, etc. per innings
            batting_df = df.groupby(['match_id', 'striker']).agg(
                runs=('runs_off_bat', 'sum'),
                balls_faced=('balls_faced', 'sum'),
                fours=('fours', 'sum'),
                sixes=('sixes', 'sum')
            ).reset_index()
            
            # Rename for clarity
            batting_df = batting_df.rename(columns={'striker': 'player_name'})

            # Calculate 50s and 100s for that innings
            batting_df['is_50'] = batting_df['runs'].apply(lambda x: 1 if (x >= 50 and x < 100) else 0)
            batting_df['is_100'] = batting_df['runs'].apply(lambda x: 1 if x >= 100 else 0)

            # --- 3. Get Dismissal Data ---
            # Find out who was dismissed in each match
            dismissals_df = df[df['player_dismissed'].notna()][['match_id', 'player_dismissed']].drop_duplicates()
            dismissals_df['is_dismissed'] = 1
            
            # Merge dismissal data back into batting data
            batting_df = batting_df.merge(
                dismissals_df, 
                left_on=['match_id', 'player_name'], 
                right_on=['match_id', 'player_dismissed'],
                how='left'
            )
            batting_df['is_dismissed'] = batting_df['is_dismissed'].fillna(0) # 0 if not out

            # --- 4. Add Match Info ---
            match_info = df[['match_id', 'start_date', 'venue']].drop_duplicates()
            batting_df = batting_df.merge(match_info, on='match_id', how='left')
            
            # Convert date for correct plotting
            batting_df['start_date'] = pd.to_datetime(batting_df['start_date'])
            batting_df = batting_df.sort_values(by='start_date')
            
            return batting_df

        except FileNotFoundError:
            st.error(f"Error: The file '{csv_path}' was not found.")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"An error occurred during data processing: {e}")
            return pd.DataFrame()

    # Load the aggregated data
    batting_df = load_and_aggregate_data('ODI_Match_Data.csv')

    if not batting_df.empty:
        
        # ====================== 🏏 PLAYER BATTING PERFORMANCE SECTION ======================
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("🏏 Player Batting Performance Analysis")

        # Get unique player names from batting_df
        player_list = sorted(batting_df['player_name'].dropna().unique())
        selected_player = st.selectbox("Select a Player for Batting Analysis", player_list, index=player_list.index("AB de Villiers") if "AB de Villiers" in player_list else 0)

        # Filter batting data for the selected player
        player_batting_data = batting_df[batting_df['player_name'] == selected_player]

        if not player_batting_data.empty:
            
            # --- Calculate Career Metrics (The CORRECT way) ---
            total_runs = player_batting_data['runs'].sum()
            matches_played = player_batting_data['match_id'].nunique()
            total_balls_faced = player_batting_data['balls_faced'].sum()
            total_dismissals = player_batting_data['is_dismissed'].sum()
            
            # Calculate average (handle division by zero if never dismissed)
            if total_dismissals > 0:
                average_runs = round(total_runs / total_dismissals, 2)
            else:
                average_runs = total_runs # Or np.nan if you prefer
                
            # Calculate career strike rate (handle division by zero)
            if total_balls_faced > 0:
                strike_rate = round((total_runs / total_balls_faced) * 100, 2)
            else:
                strike_rate = 0.0

            total_fours = player_batting_data['fours'].sum()
            total_sixes = player_batting_data['sixes'].sum()
            total_centuries = player_batting_data['is_100'].sum()
            total_fifties = player_batting_data['is_50'].sum()

            # --- Display Key Batting Metrics ---
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Runs", f"{int(total_runs)}")
            col2.metric("Matches Played", f"{matches_played}")
            col3.metric("Average Runs", f"{average_runs}")
            col4.metric("Strike Rate", f"{strike_rate}")

            col5, col6, col7, col8 = st.columns(4)
            col5.metric("Fours (4s)", f"{int(total_fours)}")
            col6.metric("Sixes (6s)", f"{int(total_sixes)}")
            col7.metric("Half-Centuries (50s)", f"{int(total_fifties)}")
            col8.metric("Centuries (100s)", f"{int(total_centuries)}")

            # --- Chart: Runs per Match ---
            # This will now show a point for EACH match
            fig_runs = px.line(
                player_batting_data,
                x='start_date',
                y='runs',
                title=f"Runs per Match - {selected_player}",
                markers=True,
                labels={'start_date': 'Match Date', 'runs': 'Runs Scored'},
                hover_data=['venue', 'balls_faced']
            )
            fig_runs.update_traces(
                hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>Runs</b>: %{y}<br><b>Venue</b>: %{customdata[0]}<extra></extra>"
            )
            st.plotly_chart(fig_runs, use_container_width=True)

            # --- Chart: Boundary Breakdown ---
            boundary_data = pd.DataFrame({
                'Boundary Type': ['Fours (4s)', 'Sixes (6s)'],
                'Count': [int(total_fours), int(total_sixes)]
            })
            fig_boundaries = px.pie(
                boundary_data, 
                names='Boundary Type', 
                values='Count',
                title=f"Boundary Breakdown for {selected_player}",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_boundaries.update_traces(textposition='inside', textinfo='percent+label+value')
            st.plotly_chart(fig_boundaries, use_container_width=True)

        else:
            st.warning(f"No batting records found for {selected_player}.")
    else:
        st.error("Batting data could not be loaded or processed.")

    

    st.subheader("Batting & Dismissal")

    partner_players_1 = partnership_df['player1_name'].dropna().unique()
    partner_players_2 = partnership_df['player2_name'].dropna().unique()
    dismissed_players = fow_df_named['player_name'].dropna().unique()
    all_batting_players = set(partner_players_1) | set(partner_players_2) | set(dismissed_players)
    batsman_list = sorted(list(all_batting_players))

    selected_batsman = st.selectbox("Select a Batsman", batsman_list)

    # --- DISMISSAL ANALYSIS ---
    st.markdown("#### Dismissal Analysis")

    player_dismissals = fow_df_named[fow_df_named['player_name'] == selected_batsman]
    dismissal_counts = player_dismissals['wicket'].value_counts().reset_index()
    dismissal_counts.columns = ['wicket', 'count']

    # Function to create descriptive labels
    def get_wicket_label(w_num):
        w_num = int(w_num)
        if w_num == 1: return "1st Wicket"
        if w_num == 2: return "2nd Wicket"
        if w_num == 3: return "3rd Wicket"
        return f"{w_num}th Wicket"

    dismissal_counts['wicket_label'] = dismissal_counts['wicket'].apply(get_wicket_label)

    # Prepare labels and values
    labels = dismissal_counts['wicket_label']
    values = dismissal_counts['count']

    # Create donut chart using Plotly
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.5,  # donut shape
                textinfo='label+percent',
                hovertemplate=(
                    '<b>Wicket Position:</b> %{label}<br>'
                    '<b>Times Dismissed:</b> %{value}<br>'
                    '<b>Percentage:</b> %{percent}'
                ),
                marker=dict(
                    colors=[
                        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
                        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
                    ],
                    line=dict(color='#FFFFFF', width=2)
                )
            )
        ]
    )

    # Update layout
    fig.update_layout(
        title=dict(
            text=f"Dismissal Position for {selected_batsman}",
            x=0.5,
            xanchor='center',
            font=dict(size=18, family="Arial", color="black")
        ),
        showlegend=True,
        legend=dict(title="Wicket Position", orientation="v", x=0, y=0.5),
        height=500,
        margin=dict(t=50, b=50, l=50, r=50)
    )

    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)
        
    # Chart 4: Top Partners
    st.subheader(f"Top 10 Partners for {selected_batsman}")
    player_partnerships = partnership_df[(partnership_df['player1_name'] == selected_batsman) | (partnership_df['player2_name'] == selected_batsman)].copy()
    player_partnerships['partner_name'] = player_partnerships.apply(lambda row: row['player2_name'] if row['player1_name'] == selected_batsman else row['player1_name'], axis=1)
    top_partners = player_partnerships.groupby('partner_name')['partnership runs'].sum().sort_values(ascending=False).reset_index()
    fig_partners = px.bar(top_partners.head(10), x='partner_name', y='partnership runs', title=f"Total Partnership Runs with {selected_batsman}", color_discrete_sequence=px.colors.sequential.ice)
    st.plotly_chart(fig_partners, use_container_width=True)



def team_analysis_tab(bowling_df, fow_df, partnership_df):
    st.markdown('<h2 class="tab-header">🌍 Comparative Team Analysis</h2>', unsafe_allow_html=True)
    
    # --- ENHANCED MAP CHART ---
    st.subheader("Global Wicket Takers Distribution")

    # Aggregate wickets for ALL teams for the map
    total_wickets_map = bowling_df.groupby('team')['wickets'].sum().reset_index()

    fig_map = px.choropleth(
        total_wickets_map,
        locations='team',
        locationmode='country names',
        color='wickets',
        hover_name='team',
        color_continuous_scale=px.colors.sequential.Plasma,
        title='Total Wickets Taken by Country'
    )

    # Increase the size and enhance the appearance
    fig_map.update_layout(
        height=600,  # Increased height
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular'
        ),
        margin={"r":0,"t":50,"l":0,"b":0},
        title_font_size=20,
        title_x=0.5  # Center the title
    )

    # Improve the color scale with better formatting
    fig_map.update_coloraxes(
        colorbar=dict(
            title="Wickets",
            thickness=15,
            len=0.75,
            x=0.02,
            y=0.5
        )
    )

    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")

        # --- Comparison Section ---
    team_list = sorted(bowling_df['team'].unique())
    st.subheader("Team Performance Comparison")

    default_teams = team_list[:3] if len(team_list) >= 3 else team_list
    selected_teams = st.multiselect("Select Teams to Compare", team_list, default=default_teams)

    if selected_teams:
        comparison_bowling_df = bowling_df[bowling_df['team'].isin(selected_teams)]
        comparison_partnership_df = partnership_df[partnership_df['team'].isin(selected_teams)]

        # Chart 1: Total Wickets Taken
        total_wickets = comparison_bowling_df.groupby('team')['wickets'].sum().reset_index()

        # Color palette for teams
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        team_colors = {team: colors[i % len(colors)] for i, team in enumerate(total_wickets['team'])}

        # --- Plotly Bar Chart: Total Wickets ---
        fig_wickets = go.Figure(
            data=[
                go.Bar(
                    x=total_wickets['team'],
                    y=total_wickets['wickets'],
                    text=total_wickets['wickets'],
                    textposition='auto',
                    marker_color=[team_colors[t] for t in total_wickets['team']],
                    hovertemplate="<b>Team:</b> %{x}<br><b>Wickets:</b> %{y}<extra></extra>"
                )
            ]
        )

        fig_wickets.update_layout(
            title=dict(
                text="Total Wickets Taken (Selected Teams)",
                x=0.5,
                font=dict(size=18, color='black', family="Arial")
            ),
            xaxis=dict(title="Team", tickangle=45),
            yaxis=dict(title="Wickets"),
            height=400,
            showlegend=False,
            margin=dict(t=50, b=80, l=60, r=40)
        )

        st.plotly_chart(fig_wickets, use_container_width=True)

        # Chart 2: Average Partnership Runs
        avg_partnership = comparison_partnership_df.groupby('team')['partnership runs'].mean().reset_index()
        avg_partnership['partnership runs'] = avg_partnership['partnership runs'].round(2)

        # --- Plotly Bar Chart: Average Partnership Runs ---
        fig_partnership = go.Figure(
            data=[
                go.Bar(
                    x=avg_partnership['team'],
                    y=avg_partnership['partnership runs'],
                    text=avg_partnership['partnership runs'],
                    textposition='auto',
                    marker_color=[team_colors.get(t, '#1f77b4') for t in avg_partnership['team']],
                    hovertemplate="<b>Team:</b> %{x}<br><b>Average Partnership Runs:</b> %{y}<extra></extra>"
                )
            ]
        )

        fig_partnership.update_layout(
            title=dict(
                text="Average Partnership Runs by Team",
                x=0.5,
                font=dict(size=18, color='black', family="Arial")
            ),
            xaxis=dict(title="Team", tickangle=45),
            yaxis=dict(title="Average Runs"),
            height=400,
            showlegend=False,
            margin=dict(t=50, b=80, l=60, r=40)
        )

        st.plotly_chart(fig_partnership, use_container_width=True)

    st.markdown("---")

    # Phase-wise Performance
    st.subheader("⏱️ Match Phase Performance")
    fig_death_overs = create_death_overs_analysis(bowling_df)
    st.plotly_chart(fig_death_overs, use_container_width=True)
    
    # You can also add additional phase analysis charts:
    
    # Wickets by phase comparison
    st.subheader("🎯 Wickets by Match Phase")
    
    # Calculate wickets by phase for each team
    phases = {
        'Powerplay (1-10)': (1, 10),
        'Middle Overs (11-40)': (11, 40),
        'Death Overs (41-50)': (41, 50)
    }
    
    phase_wickets_data = []
    for phase_name, (start, end) in phases.items():
        phase_df = bowling_df[bowling_df['overs'].between(start, end)]
        wickets_by_team = phase_df.groupby('team')['wickets'].sum().reset_index()
        wickets_by_team['phase'] = phase_name
        phase_wickets_data.append(wickets_by_team)
    
    if phase_wickets_data:
        phase_wickets_df = pd.concat(phase_wickets_data, ignore_index=True)
        
        fig_wickets_phase = px.bar(
            phase_wickets_df,
            x='team',
            y='wickets',
            color='phase',
            barmode='group',
            title='Wickets Taken by Team in Different Match Phases',
            labels={'wickets': 'Total Wickets', 'team': 'Team'}
        )
        fig_wickets_phase.update_layout(xaxis_tickangle=45, height=500)
        st.plotly_chart(fig_wickets_phase, use_container_width=True)
        
    # Team-specific phase performance selector
    st.subheader("🔍 Detailed Team Phase Analysis")
    
    team_list = sorted(bowling_df['team'].unique())
    selected_team = st.selectbox("Select Team for Detailed Phase Analysis", team_list)
    
    if selected_team:
        team_bowling = bowling_df[bowling_df['team'] == selected_team].copy()
        
        # Define phases
        team_bowling['phase'] = pd.cut(
            team_bowling['overs'],
            bins=[0, 10, 40, 50],
            labels=['Powerplay (1-10)', 'Middle Overs (11-40)', 'Death Overs (41-50)']
        )
        
        team_phase_stats = team_bowling.groupby('phase').agg({
            'wickets': 'sum',
            'economy': 'mean',
            'conceded': 'sum',
            'overs': 'count'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Wickets by phase for selected team
            fig_team_wickets = px.pie(
                team_phase_stats,
                values='wickets',
                names='phase',
                title=f'{selected_team} - Wickets Distribution by Phase',
                hole=0.4
            )
            st.plotly_chart(fig_team_wickets, use_container_width=True)
        
        with col2:
            # Economy by phase for selected team
            fig_team_economy = px.bar(
                team_phase_stats,
                x='phase',
                y='economy',
                title=f'{selected_team} - Economy Rate by Phase',
                color='economy',
                color_continuous_scale='RdYlGn_r'
            )
            st.plotly_chart(fig_team_economy, use_container_width=True)
    

            # --- Head-to-Head Section ---
    st.subheader("Head-to-Head Analysis")

    team1 = st.selectbox("Select Team 1", team_list, index=0, key='team1_h2h')

    # Find possible opponents for the selected team
    opponents1 = bowling_df[bowling_df['team'] == team1]['opposition'].unique()
    opponents2 = bowling_df[bowling_df['opposition'] == team1]['team'].unique()
    h2h_team_list = sorted(list(set(opponents1) | set(opponents2)))

    if h2h_team_list:
        team2 = st.selectbox("Select Team 2", h2h_team_list, index=0, key='team2_h2h')

        if team1 and team2:
            # Filter head-to-head matches between selected teams
            h2h_bowling = bowling_df[
                ((bowling_df['team'] == team1) & (bowling_df['opposition'] == team2)) |
                ((bowling_df['team'] == team2) & (bowling_df['opposition'] == team1))
            ]

            # Calculate total wickets for each team
            h2h_wickets = h2h_bowling.groupby('team')['wickets'].sum().reset_index()

            team1_wickets = (
                h2h_wickets[h2h_wickets['team'] == team1]['wickets'].iloc[0]
                if not h2h_wickets[h2h_wickets['team'] == team1].empty
                else 0
            )
            team2_wickets = (
                h2h_wickets[h2h_wickets['team'] == team2]['wickets'].iloc[0]
                if not h2h_wickets[h2h_wickets['team'] == team2].empty
                else 0
            )

            # --- Plotly Bar Chart ---
            fig_h2h = go.Figure()

            fig_h2h.add_trace(
                go.Bar(
                    name=team1,
                    x=["Wickets"],
                    y=[team1_wickets],
                    text=[team1_wickets],
                    textposition='auto',
                    marker_color="#1f77b4",
                    hovertemplate=f"<b>Team:</b> {team1}<br><b>Wickets:</b> %{{y}}<extra></extra>"
                )
            )

            fig_h2h.add_trace(
                go.Bar(
                    name=team2,
                    x=["Wickets"],
                    y=[team2_wickets],
                    text=[team2_wickets],
                    textposition='auto',
                    marker_color="#ff7f0e",
                    hovertemplate=f"<b>Team:</b> {team2}<br><b>Wickets:</b> %{{y}}<extra></extra>"
                )
            )

            # Update layout
            fig_h2h.update_layout(
                title=dict(
                    text=f"Head-to-Head: {team1} vs {team2}",
                    x=0.5,
                    font=dict(size=18, color='black', family="Arial")
                ),
                xaxis=dict(title="", tickangle=0, showticklabels=True),
                yaxis=dict(title="Wickets"),
                barmode='group',  # side-by-side bars
                height=400,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=60, b=80, l=60, r=40)
            )

            st.plotly_chart(fig_h2h, use_container_width=True)

    else:
        st.warning(f"No head-to-head match data found for {team1} in this dataset.")
def match_analysis_tab(bowling_df, fow_df_named, partnership_df):
    st.markdown('<h2 class="tab-header">📊 Detailed Match Breakdown</h2>', unsafe_allow_html=True)
    
    valid_bowling_matches = set(bowling_df[bowling_df['overs'] <= 50]['Match ID'].unique())
    valid_fow_matches = set(fow_df_named[fow_df_named['over'] <= 50]['Match ID'].unique())
    match_ids = sorted(list(valid_bowling_matches.intersection(valid_fow_matches)))
    selected_match_id = st.selectbox("Select a Match to Analyze", match_ids)
    
    if not selected_match_id:
        return
    
    match_bowling = bowling_df[bowling_df['Match ID'] == selected_match_id]
    match_fow = fow_df_named[fow_df_named['Match ID'] == selected_match_id]
    match_partnership = partnership_df[partnership_df['Match ID'] == selected_match_id]
    
    # --- Chart 1: Innings Progression with Wickets ---
    st.markdown("#### Innings Progression")
    
    # --- Prepare Innings Data for Area Chart ---
    match_bowling_match = match_bowling.copy()

    # Sum conceded runs per team per over
    match_bowling_match['over_number'] = match_bowling_match['overs'].astype(int) + 1
    innings_data = (
        match_bowling_match.groupby(['opposition', 'over_number'])['conceded']
        .sum()
        .reset_index()
        .rename(columns={'opposition': 'batting_team', 'conceded': 'runs'})
    )

    # Ensure overs 1–50 exist for each team
    teams_in_match = innings_data['batting_team'].unique()
    full_overs_df = pd.DataFrame({'over_number': range(1, 51)})

    all_teams_data = []
    for team in teams_in_match:
        team_data = innings_data[innings_data['batting_team'] == team]
        team_data = full_overs_df.merge(team_data, on='over_number', how='left').fillna(0)
        team_data['batting_team'] = team
        team_data['runs'] = team_data['runs'].astype(int)  # convert to integer
        team_data['cumulative_score'] = team_data['runs'].cumsum()
        all_teams_data.append(team_data)

    final_innings_data = pd.concat(all_teams_data)

    # --- Plot Area Chart ---
    fig_combined = go.Figure()
    colors = px.colors.qualitative.Plotly

    for i, team in enumerate(teams_in_match):
        team_data = final_innings_data[final_innings_data['batting_team'] == team]
        fig_combined.add_trace(go.Scatter(
            x=team_data['over_number'],
            y=team_data['cumulative_score'],
            mode='lines',
            fill='tozeroy',
            name=team,
            line=dict(color=colors[i])
        ))

        # Add wicket markers
        team_fow_data = match_fow[match_fow['team'] == team].copy()
        if not team_fow_data.empty:
            team_fow_data['over_int'] = team_fow_data['over'].astype(float).astype(int) + 1
            fig_combined.add_trace(go.Scatter(
                x=team_fow_data['over_int'],
                y=team_fow_data['runs'],
                mode='markers',
                marker=dict(color=colors[i], size=10, line=dict(width=1, color='DarkSlateGrey')),
                name=f"{team} Wickets",
                text=team_fow_data['player_name'],
                hovertemplate='<b>Player Dismissed:</b> %{text}<br><b>Over:</b> %{x}<br><b>Score:</b> %{y}<extra></extra>',
                showlegend=False
            ))

    fig_combined.update_layout(
        title="Innings Progression with Wicket Markers",
        xaxis_title="Overs",
        yaxis_title="Cumulative Score",
        xaxis=dict(range=[1, 50], showgrid=True, gridcolor='lightgrey'),
        yaxis=dict(showgrid=True, gridcolor='lightgrey'),
        plot_bgcolor='white'
    )

    st.plotly_chart(fig_combined, use_container_width=True)

    
    # --- Chart 3: Partnership Breakdown ---
    st.markdown("#### Partnership Breakdown")
    if not match_partnership.empty:
        fig_partnership_breakdown = px.bar(
            match_partnership.sort_values(by='for wicket'), 
            x='partnership runs', 
            y='team', 
            color='for wicket', 
            orientation='h', 
            title="Partnerships by Wicket"
        )
        st.plotly_chart(fig_partnership_breakdown, use_container_width=True)
    
    # --- Chart 4: Bowler Performance Summary ---
    st.markdown("#### Bowler Performance Summary")
    bowler_summary = match_bowling.groupby(['team', 'player_name']).agg(
        Overs=('overs', 'max'),
        Wickets=('wickets', 'sum'),
        Conceded=('conceded', 'sum'),
        Economy=('economy', 'first')
    ).reset_index()
    
    fig_bowler_perf = px.bar(
        bowler_summary.sort_values('Wickets', ascending=False),
        x='player_name', 
        y='Wickets', 
        color='team',
        hover_data=['Overs', 'Conceded', 'Economy'], 
        title="Wickets Taken by Bowlers in the Match"
    )
    st.plotly_chart(fig_bowler_perf, use_container_width=True)


def partnership_analysis_tab(partnership_df):
    st.markdown('<h2 class="tab-header">🤝 Partnership Deep Dive</h2>', unsafe_allow_html=True)
    
    # --- Top N Charts Section ---
    num_to_display = st.number_input("Select number of top partnerships to display:", min_value=5, max_value=50, value=10, step=5)
    
    st.subheader(f"Top {num_to_display} Highest Partnerships")
    top_partnerships_df = partnership_df.nlargest(num_to_display, 'partnership runs').copy()
    top_partnerships_df.dropna(subset=['player1_name', 'player2_name'], inplace=True)
    top_partnerships_df['pair'] = top_partnerships_df['player1_name'] + " & " + top_partnerships_df['player2_name']
    fig_top_partnerships = px.bar(top_partnerships_df, x='partnership runs', y='pair', orientation='h', title=f"Top {num_to_display} Highest Individual Partnerships", color='partnership runs', color_continuous_scale='OrRd')
    fig_top_partnerships.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top_partnerships, use_container_width=True)

    st.subheader(f"Top {num_to_display} Most Successful Pairs")
    partnership_analysis_df = partnership_df.copy()
    partnership_analysis_df.dropna(subset=['player1_name', 'player2_name'], inplace=True)
    partnership_analysis_df['pair_key'] = partnership_analysis_df.apply(lambda row: tuple(sorted((row['player1_name'], row['player2_name']))), axis=1)
    prolific_pairs = partnership_analysis_df.groupby('pair_key')['partnership runs'].sum().nlargest(num_to_display).reset_index()
    prolific_pairs['pair'] = prolific_pairs['pair_key'].apply(lambda x: f"{x[0]} & {x[1]}")
    fig_prolific_pairs = px.bar(prolific_pairs, x='partnership runs', y='pair', orientation='h', title=f"Top {num_to_display} Most Prolific Batting Pairs", color='partnership runs', color_continuous_scale='Cividis')
    fig_prolific_pairs.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_prolific_pairs, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- Scatter Plot Section with NEW Filter ---
    st.subheader("Partnership Run Rate Analysis")

    team_list_partnership = sorted(partnership_df['team'].dropna().unique())
    default_teams_scatter = team_list_partnership[:2] if len(team_list_partnership) >= 2 else team_list_partnership
    selected_teams_scatter = st.multiselect(
        "Select teams to display on the scatter plot:",
        team_list_partnership,
        default=default_teams_scatter,
        key='scatter_team_select'
    )
    
    scatter_df = partnership_df[partnership_df['partnership balls'] > 0].copy()
    scatter_df['run_rate'] = (scatter_df['partnership runs'] / scatter_df['partnership balls']) * 100

    if selected_teams_scatter:
        filtered_scatter_df = scatter_df[scatter_df['team'].isin(selected_teams_scatter)]
        
        fig_scatter_pr = px.scatter(filtered_scatter_df, x='partnership balls', y='partnership runs',
                                    title="Partnership Pace (Runs vs. Balls)",
                                    color='team',  # Color by team for clear comparison
                                    hover_data=['player1_name', 'player2_name', 'for wicket', 'run_rate'],
                                    labels={'partnership balls': 'Balls Faced', 'partnership runs': 'Runs Scored'})
        st.plotly_chart(fig_scatter_pr, use_container_width=True)
    else:
        st.warning("Please select at least one team to display the scatter plot.")



if __name__ == "__main__":
    main()