import streamlit as st
import pandas as pd
import os
import altair as alt

def load_and_process_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(os.path.dirname(current_dir), 'blackjack_results.csv')
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at {csv_path}")
        
    df = pd.read_csv(csv_path)
    df['Cumulative_Wins'] = df['Result'].eq('Win').cumsum()
    df['Cumulative_Losses'] = df['Result'].eq('Loss').cumsum()
    df['Cumulative_Pushes'] = df['Result'].eq('Push').cumsum()
    df['Win_Rate'] = df['Cumulative_Wins'] / df['Round']
    return df

def main():
    st.set_page_config(page_title="Blackjack Simulation Analysis", layout="wide")
    st.title("Blackjack Simulation Results Dashboard")

    try:
        df = load_and_process_data()
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Hands", len(df))
        with col2:
            st.metric("Final Balance", f"${df['Running_Money'].iloc[-1]}")
        with col3:
            win_rate = (df['Result'] == 'Win').mean() * 100
            st.metric("Win Rate", f"{win_rate:.1f}%")
        with col4:
            profit = df['Running_Money'].iloc[-1] - 1000
            st.metric("Net Profit/Loss", f"${profit}")

        # Balance Progress
        st.subheader("Balance Progress")
        st.line_chart(df.set_index('Round')['Running_Money'])

        # Outcome Distribution
        st.subheader("Outcome Distribution")
        st.bar_chart(df['Result'].value_counts())

        # Win Rate Progress
        st.subheader("Win Rate Over Time")
        st.line_chart(df.set_index('Round')['Win_Rate'])

        # Recent Results
        st.subheader("Recent Hands")
        st.dataframe(df.tail(10)[['Round', 'Result', 'Running_Money', 'Debug']])

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please run the simulation first to create the CSV file.")

if __name__ == "__main__":
    main()