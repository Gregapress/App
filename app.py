import streamlit as st
import pandas as pd
import re

# Function to parse the hotkeys file
def parse_hotkeys(file_path):
    hotkeys = []
    with open(file_path, 'r') as f:
        for line in f:
            if re.match(r'^\s*\*?\s*[A-Za-z0-9+]+', line):  # Match lines with hotkeys
                parts = re.split(r'\s{2,}', line.strip())
                if len(parts) == 2:
                    hotkeys.append({"Hotkey": parts[0].strip('* '), "Command": parts[1]})
    return pd.DataFrame(hotkeys)

# Function to categorize hotkeys
def categorize_hotkeys(df):
    if "Command" not in df.columns:  # Ensure "Command" column exists
        st.error("The parsed hotkeys data does not contain a 'Command' column.")
        return df
    categories = {
        "Editing": ["Bold", "Italic", "Underline", "EditUndo", "EditRedoOrRepeat", "FindReplace"],
        "Navigation": ["EditGoTo", "ViewDocmap", "GoToQuickmark"],
        "File Operations": ["FileNew", "FileOpen", "FileSave", "FilePrint", "FileClose"],
        "Formatting": ["InsertLink", "InsertComment", "InsertSymbol", "ToggleTagDisplay"],
    }
    df["Category"] = "Other"
    for category, commands in categories.items():
        df.loc[df["Command"].isin(commands), "Category"] = category
    return df

# Load and parse the hotkeys file
file_path = "ArborTextHotkeys.txt"  # Update this path if the file is elsewhere
try:
    hotkeys_df = parse_hotkeys(file_path)
    if hotkeys_df.empty:
        st.error("The hotkeys file is empty or not properly formatted.")
    else:
        # Categorize hotkeys
        hotkeys_df = categorize_hotkeys(hotkeys_df)
except Exception as e:
    st.error(f"Error loading or parsing the file: {e}")
    hotkeys_df = pd.DataFrame(columns=["Hotkey", "Command", "Category"])

# Streamlit app
st.title("PTC Arbortext Editor Hotkey Reference")

# Search bar
search_query = st.text_input("Search Hotkeys or Commands", "")

# Filter by category
st.sidebar.title("Filter by Category")
if not hotkeys_df.empty and "Category" in hotkeys_df.columns:
    category = st.sidebar.selectbox("Select Category", ["All"] + sorted(hotkeys_df["Category"].unique()))
    # Display results
    if search_query or category != "All":
        filtered_df = hotkeys_df[
            hotkeys_df["Hotkey"].str.contains(search_query, case=False, na=False) |
            hotkeys_df["Command"].str.contains(search_query, case=False, na=False)
        ]
        if category != "All":
            filtered_df = filtered_df[filtered_df["Category"] == category]
        st.write(filtered_df)
    else:
        st.write(hotkeys_df)
else:
    st.error("No data available to display.")
