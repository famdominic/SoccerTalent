import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Page Configuration
st.set_page_config(
    page_title="U-21 Soccer Scout",
    page_icon="⚽",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        color: #1f77b4;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<p class="main-title">⚽ U-21 Soccer Talent & Value Scout</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Identify undervalued young football prospects using statistical performance metrics and market value gaps.</p>', unsafe_allow_html=True)

# Generate Sample Dataset
@st.cache_data
def load_scouting_data():
    np.random.seed(42)
    names = [
        "Mateo Silva", "Lukas Weber", "Gabriel Santos", "Enzo Rossi", 
        "Noah van Dijk", "Javier Martinez", "Amadou Diallo", "Kian Jensen",
        "Stefan Kovac", "Tariq Al-Farsi", "Dusan Petrovic", "Matteo Moretti",
        "Lucas Pereira", "Soren Lind", "Youssef El-Amrani", "Bence Varga"
    ]
    positions = ["Winger", "Central Midfielder", "Fullback", "Center Back", "Striker"]
    teams = ["FC Nordsjælland", "Genk", "Sporting B", "Feyenoord", "Dinamo Zagreb", "Braga", "Midtjylland", "AZ Alkmaar"]
    
    data = []
    for i, name in enumerate(names):
        pos = np.random.choice(positions)
        age = np.random.randint(17, 22)
        mins = np.random.randint(1200, 2800)
        
        # Performance metrics (per 90 minutes / normalized scales)
        prog_carries = round(np.random.uniform(2.0, 8.5), 2)
        xg_xa = round(np.random.uniform(0.15, 0.75), 2)
        def_duels_won = round(np.random.uniform(55.0, 82.0), 1)
        pass_accuracy = round(np.random.uniform(75.0, 91.0), 1)
        
        # Financials
        actual_val = round(np.random.uniform(1.5, 12.0), 1)  # Millions €
        
        data.append({
            "Player": name,
            "Age": age,
            "Position": pos,
            "Team": np.random.choice(teams),
            "Minutes": mins,
            "Prog Carries/90": prog_carries,
            "xG + xA/90": xg_xa,
            "Def Duels Won %": def_duels_won,
            "Pass Acc %": pass_accuracy,
            "Market Value (€M)": actual_val
        })
    
    df = pd.DataFrame(data)
    
    # Calculate an Expected Value based on performance output
    df["Performance Index"] = (
        (df["Prog Carries/90"] * 3) + 
        (df["xG + xA/90"] * 25) + 
        (df["Def Duels Won %"] * 0.4) + 
        (df["Pass Acc %"] * 0.3)
    ).round(1)
    
    df["Expected Value (€M)"] = (df["Performance Index"] * 0.35).round(1)
    df["Value Gap (€M)"] = (df["Expected Value (€M)"] - df["Market Value (€M)"]).round(1)
    
    return df

df = load_scouting_data()

# Sidebar Filters
st.sidebar.header("🔍 Scouting Filters")
max_age = st.sidebar.slider("Maximum Age", 16, 21, 21)
selected_position = st.sidebar.selectbox("Position Filter", ["All"] + list(df["Position"].unique()))

# Filter DataFrame
filtered_df = df[df["Age"] <= max_age]
if selected_position != "All":
    filtered_df = filtered_df[filtered_df["Position"] == selected_position]

# Sort by Bargain Score / Value Gap
filtered_df = filtered_df.sort_values(by="Value Gap (€M)", ascending=False).reset_index(drop=True)

# Main Metrics Layout
col1, col2, col3 = st.columns(3)
col1.metric("Prospects Tracked", len(filtered_df))
col2.metric("Average Market Value", f"€{filtered_df['Market Value (€M)'].mean():.1f}M")
col3.metric("Top Bargain Gap", f"+€{filtered_df['Value Gap (€M)'].max():.1f}M")

st.markdown("---")

# Data Table
st.subheader("📋 Ranked Under-21 Value Prospects")
st.markdown("Players sorted by **Value Gap** (Expected Value based on metrics minus current Market Value).")

# Display styled dataframe
st.dataframe(
    filtered_df[[
        "Player", "Age", "Position", "Team", "Minutes", 
        "Prog Carries/90", "xG + xA/90", "Market Value (€M)", "Expected Value (€M)", "Value Gap (€M)"
    ]],
    use_container_width=True
)

st.markdown("---")

# Player Comparison / Radar Breakdown Section
st.subheader("📊 Individual Prospect Deep Dive")
selected_player = st.selectbox("Select a player to review metrics profile:", filtered_df["Player"].tolist())

if selected_player:
    player_data = filtered_df[filtered_df["Player"] == selected_player].iloc[0]
    
    p_col1, p_col2 = st.columns([1, 2])
    
    with p_col1:
        st.markdown(f"### {player_data['Player']}")
        st.write(f"**Team:** {player_data['Team']}")
        st.write(f"**Age:** {player_data['Age']} | **Position:** {player_data['Position']}")
        st.write(f"**Minutes Played:** {player_data['Minutes']}")
        st.info(f"💡 **Scouting Summary:** Valued at **€{player_data['Market Value (€M)']}M**, but performs at a level worth approximately **€{player_data['Expected Value (€M)']}M**.")
        
    with p_col2:
        # Simple Bar Chart visualization for metrics comparison
        fig, ax = plt.subplots(figsize=(6, 3))
        metrics = ['Prog Carries', 'xG + xA', 'Def Duels %', 'Pass Acc %']
        # Normalize sample values for visual scaling
        values = [
            player_data['Prog Carries/90'] / 10 * 100,
            player_data['xG + xA/90'] * 100,
            player_data['Def Duels Won %'],
            player_data['Pass Acc %']
        ]
        
        bars = ax.barh(metrics, values, color='#1f77b4')
        ax.set_xlim(0, 100)
        ax.set_xlabel("Percentile Estimate / Metric Score")
        ax.set_title(f"Performance Profile: {player_data['Player']}")
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 2, bar.get_y() + bar.get_height()/2, f'{width:.1f}', 
                    va='center', ha='left', fontsize=9, color='black')
            
        st.pyplot(fig)
