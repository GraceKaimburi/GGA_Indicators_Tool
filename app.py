import streamlit as st
import pandas as pd
import os
import io
from shutil import copyfile
from openpyxl import load_workbook
from io import BytesIO
from dotenv import load_dotenv
import zipfile
import tempfile

# Force disable Google Drive integration (remove this line once you have credentials.json)
drive_enabled = False

# Load environment variables
load_dotenv(dotenv_path='.env')

# Your Google Drive Folder ID - Update this with your folder ID
DRIVE_FOLDER_ID = "1V9oik7onvQpvyl4y9mUh5MPOmom4GrkO"

# Set Streamlit page config to use full screen width
st.set_page_config(layout="wide", page_title="GGA Indicators - Tagging & Selection Management System")

# Apply custom CSS for improved UI
# Update the CSS for the indicator cards in your app.py file
# Replace the existing CSS block with this one that uses dark theme for cards

st.markdown("""
<style>
    .main-header {
        font-size: 28px !important;
        font-weight: bold;
        margin-bottom: 20px;
        color: white;
        text-align: center;
    }
    .sub-header {
        font-size: 18px !important;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        color: white;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    p, li {
        margin-bottom: 0.2em;
        line-height: 1.3em;
    }
    /* Updated indicator card to match dark theme */
    .indicator-card {
        background-color: #1e1e1e; /* Dark background */
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        border-left: 4px solid #0078ff;
        color: white; /* Light text */
    }
    .indicator-card strong {
        color: #00bfff; /* Light blue for titles */
    }
    .indicator-card small {
        color: #cccccc; /* Light gray for smaller text */
    }
    .tag-pill {
        display: inline-block;
        background-color: #333333; /* Dark background for pills */
        padding: 2px 6px;
        border-radius: 10px;
        font-size: 12px;
        margin-right: 5px;
        margin-bottom: 5px;
        color: #00bfff; /* Light blue text */
    }
    .tag-section {
        margin-top: 5px;
        padding-top: 5px;
        border-top: 1px solid #444; /* Darker border */
    }
    .tabs-container {
        margin-bottom: 20px;
    }
    .scrollable-content {
        max-height: 600px;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid #333; /* Darker border */
        border-radius: 5px;
        background-color: #0e1117; /* Match streamlit dark theme */
    }
    .stSelectbox, .stCheckbox {
        font-size: 14px !important;
    }
    .stButton > button {
        font-size: 14px !important;
    }
    .data-table {
        font-size: 12px !important;
    }
    .status-badge-selected {
        background-color: #1e4620; /* Darker green */
        color: #4caf50; /* Lighter green text */
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 12px;
        font-weight: bold;
    }
    .status-badge-unselected {
        background-color: #4e1c24; /* Darker red */
        color: #f44336; /* Lighter red text */
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 12px;
        font-weight: bold;
    }
    /* Also fix any white backgrounds in the app */
    .stExpander {
        background-color: #1e1e1e !important;
        border-color: #333 !important;
    }
    /* Fix checkboxes and text */
    .st-bq {
        background-color: #1e1e1e !important;
        color: white !important;
    }
    /* Fix other potential white backgrounds */
    div[data-testid="stVerticalBlock"] {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# --- CONFIG ---
# Try to set up Google Drive if credentials exist
try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    from google.oauth2 import service_account
    from googleapiclient.http import MediaIoBaseDownload
    
    # Setup for Google Drive integration
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    SERVICE_ACCOUNT_FILE = 'credentials.json'

    if os.path.exists(SERVICE_ACCOUNT_FILE) and not drive_enabled:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        drive_service = build('drive', 'v3', credentials=creds)
        drive_enabled = True
        st.sidebar.success("Google Drive integration enabled")
except Exception as e:
    drive_enabled = False
    st.sidebar.warning(f"Google Drive integration disabled: {e}")

# Default file paths
DEFAULT_EXCEL_FILE = 'Indicators_1000.xlsx'
TEMPLATE_FILE = 'Indicators_1000.xlsx'

# --- AUTHENTICATION SYSTEM ---
# User management with simplified credentials
def setup_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    # Simplified hardcoded credentials for easier access
    USERS = {
        'admin': 'admin123',
        'user1': 'pass123',
        'user2': 'pass123',
        'grace': 'pass123',
        'user3': 'pass123',
        'user4': 'pass123',
        'user5': 'pass123',
    }
    
    return USERS

def login_page():
    USERS = setup_auth()
    
    
    # Display title with direct st.title instead of markdown div
    st.title("GGA Indicators - Tagging & Selection System")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Please log in to continue")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        login_btn = st.button("Login")
        if login_btn:
            if username in USERS and USERS[username] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.is_admin = (username == 'admin')
                st.rerun()
            else:
                st.error("Invalid username or password")
        
        st.info("Default credentials: Username: 'user1', Password: 'pass123'")

# --- DATA LOADING FUNCTIONS ---
@st.cache_data(ttl=600)
def load_excel_data(file_path):
    try:
        if not os.path.exists(file_path):
            st.error(f"File not found: {file_path}")
            return pd.DataFrame()
        return pd.read_excel(file_path)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def load_user_data(username, default_file=DEFAULT_EXCEL_FILE, drive_folder_id=DRIVE_FOLDER_ID):
    if not drive_enabled:
        return load_excel_data(default_file), default_file
    
    user_filename = f'updated_{username}.xlsx'
    
    # Search for the file in Google Drive
    try:
        query = f"name = '{user_filename}'"
        if drive_folder_id:
            query += f" and '{drive_folder_id}' in parents"
            
        response = drive_service.files().list(q=query, fields="files(id, name)", spaces='drive').execute()
        files = response.get('files', [])
        
        if files:
            file_id = files[0]['id']
            request = drive_service.files().get_media(fileId=file_id)
            fh = BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            fh.seek(0)
            return pd.read_excel(fh), user_filename
    except Exception as e:
        st.warning(f"Could not load from Drive: {e}")
    
    # Fallback to default file
    return load_excel_data(default_file), user_filename

def save_user_data(df, filename, drive_folder_id=DRIVE_FOLDER_ID):
    # Save locally
    df.to_excel(filename, index=False)
    
    if not drive_enabled:
        return "Saved locally only (Drive disabled)"
    
    # Save to Google Drive
    try:
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        
        file_metadata = {
            'name': filename,
            'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        }
        
        if drive_folder_id:
            file_metadata['parents'] = [drive_folder_id]
        
        media = MediaIoBaseUpload(output, mimetype=file_metadata['mimeType'])
        
        # Check if file exists
        query = f"name = '{filename}'"
        if drive_folder_id:
            query += f" and '{drive_folder_id}' in parents"
            
        response = drive_service.files().list(q=query, fields="files(id, name)", spaces='drive').execute()
        files = response.get('files', [])
        
        if files:
            # Update existing file
            file_id = files[0]['id']
            updated_file = drive_service.files().update(
                fileId=file_id,
                media_body=media,
                fields='id'
            ).execute()
            return f"Updated on Drive (ID: {updated_file.get('id')})"
        else:
            # Create new file
            uploaded_file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            return f"Saved to Drive (ID: {uploaded_file.get('id')})"
    except Exception as e:
        return f"Error saving to Drive: {e}"

# --- MAPPING AND CONSTANTS ---
def get_column_mapping():
    return {
        'water': 'Water',
        'health': 'Health',
        'infrastructure': 'Infrastructure',
        'food': 'Food',
        'poverty': 'Poverty',
        'biodiversity': 'Biodiversity',
        'cultural heritage': 'Cultural Heritage'
    }

def get_gga_targets():
    return [
        "Input",
        "Process",
        "Output",
        "Outcome"
    ]

def get_moi_fields():
    return ["Enabling factor", "MOI-finance", "MOI-technology", "MOI-Capacity building"]

# --- APP CORE FUNCTIONS ---
def setup_session_state():
    """Initialize session state variables"""
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "Select"
    
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
        
    if 'unsaved_changes' not in st.session_state:
        st.session_state.unsaved_changes = False
        
    if 'pending_values' not in st.session_state:
        st.session_state.pending_values = {}
        
    if 'show_confirm' not in st.session_state:
        st.session_state.show_confirm = False
        
    if 'filtered_df' not in st.session_state:
        st.session_state.filtered_df = None
        
    # Load data if not already loaded
    if 'df' not in st.session_state:
        if st.session_state.authenticated:
            try:
                df, _ = load_user_data(st.session_state.username, drive_folder_id=DRIVE_FOLDER_ID)
                st.session_state.df = df
                
                # Ensure selection columns exist
                if 'selected_global' not in st.session_state.df.columns:
                    st.session_state.df['selected_global'] = 0
                if 'selected_contextual' not in st.session_state.df.columns:
                    st.session_state.df['selected_contextual'] = 0
            except Exception as e:
                st.error(f"Error loading data: {e}")
                st.session_state.df = pd.DataFrame()  # Create empty DataFrame as fallback

def app_header():
    """Render the application header with tabs"""
    # Display title with direct st.title instead of markdown div
    st.title("GGA Indicators - Tagging & Selection System")

    col1, col2, col3, col4 = st.columns([3, 3, 3, 1])
    with col1:
        st.button("Tag Indicators", 
                 on_click=lambda: st.session_state.update(current_tab="Tag"),
                 type="primary" if st.session_state.current_tab == "Tag" else "secondary")
        
    with col2:
        st.button("Select Indicators", 
                 on_click=lambda: st.session_state.update(current_tab="Select"),
                 type="primary" if st.session_state.current_tab == "Select" else "secondary")
    with col3:
        st.button("View Indicator Details", 
                 on_click=lambda: st.session_state.update(current_tab="Details"),
                 type="primary" if st.session_state.current_tab == "Details" else "secondary")
    with col4:
        st.button("Logout", on_click=lambda: st.session_state.update(authenticated=False))
    
    st.markdown(f"Logged in as: **{st.session_state.username}**" + 
               (" (Administrator)" if st.session_state.username == 'admin' else ""))
    st.divider()

def find_indicator_criteria_cols(df):
    """Find criteria columns in the dataframe"""
    crit_columns = []
    for possible_name in ['CRIT1', 'CRIT2', 'CRIT3']:
        for col in df.columns:
            if possible_name.lower() in str(col).lower():
                crit_columns.append(col)
                break
    return crit_columns

def find_column_by_content(df, keywords):
    """Find a column that contains specific keywords"""
    for col in df.columns:
        if any(keyword.lower() in str(col).lower() for keyword in keywords):
            return col
    return None

# --- TAB CONTENTS ---
def select_indicators_tab():
    """Tab for selecting and filtering indicators"""
    column_mapping = get_column_mapping()
    
    st.markdown('<div class="sub-header">Indicator Selection and Filtering</div>', unsafe_allow_html=True)
    
    left_panel, right_panel = st.columns([3, 5], gap="large")
    
    with left_panel:
        with st.container():
            st.markdown("### Filter Indicators")
            
            # Check which thematic areas actually exist in the DataFrame
            thematic_areas = []
            if 'Thematic Area' in st.session_state.df.columns:
                thematic_areas = st.session_state.df['Thematic Area'].dropna().unique().tolist()
            else:
                st.error("No 'Thematic Area' column found in your data. Please check your Excel file structure.")
                thematic_areas = ["No thematic areas found"]

            filter_by_theme = st.selectbox(
                "Filter by thematic area:",
                options=["All"] + thematic_areas,
                index=0
            )
            
            # Find the indicator type column
            indicator_type_col = 'Indicator Type'  # Use the actual column name from your Excel
            if indicator_type_col in st.session_state.df.columns:
                types = st.session_state.df[indicator_type_col].dropna().unique().tolist()
                selected_type = st.selectbox(
                    f"Filter by indicator type:",
                    options=["All"] + types,
                    index=0
                )
            else:
                selected_type = "All"
                st.warning(f"No '{indicator_type_col}' column found")
            
            show_full_list_checkbox = st.checkbox("Show full list of relevant components and targets", value=False)
            
            # Apply filters
            filtered_df = st.session_state.df.copy()
            
            # Apply thematic area filter
            if filter_by_theme != "All" and 'Thematic Area' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Thematic Area'] == filter_by_theme]
            
            # Apply indicator type filter  
            if selected_type != "All" and indicator_type_col in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[indicator_type_col] == selected_type]
            
            # Find criteria columns
            crit_columns = find_indicator_criteria_cols(filtered_df)
            
            if crit_columns:
                # Convert to numeric first, handling non-numeric values
                for col in crit_columns:
                    filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce').fillna(0)
                
                filtered_df['Score'] = filtered_df[crit_columns].sum(axis=1)
                filtered_df = filtered_df.sort_values(by='Score', ascending=False)
            
            st.session_state.filtered_df = filtered_df
            
            st.write(f"Displaying {len(filtered_df)} filtered records:")
            
            with st.container():
                st.markdown('<div class="scrollable-content">', unsafe_allow_html=True)
                
                if len(filtered_df) == 0:
                    st.info("No records match your filter criteria. Try changing the filters.")
                
                for idx, row in filtered_df.iterrows():
                    indicator_name = row.get('Indicators', f"Indicator {idx}")
                    
                    # Determine indicator metadata
                    thematic_area = row.get('Thematic Area', '')
                    indicator_type = row.get('Indicator Type', '')
                    reporting_status = row.get('Already reported?', '')
                    
                    # Display indicator card
                    st.markdown(f"""
                    <div class="indicator-card">
                        <strong>{indicator_name}</strong>
                        <div class="tag-section">
                            <small>Theme: {thematic_area}</small>
                            {f" | <small>Type: {indicator_type}</small>" if indicator_type else ""}
                            {f" | <small>{reporting_status}</small>" if reporting_status else ""}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Show details if requested
                    if show_full_list_checkbox:
                        st.markdown("<div style='margin-top:5px'><small><b>Details:</b></small></div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='tag-pill'>Theme: {thematic_area}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='tag-pill'>Type: {indicator_type}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='tag-pill'>Status: {reporting_status}</div>", unsafe_allow_html=True)
                    
                    # Selection checkboxes
                    col1, col2 = st.columns(2)
                    with col1:
                        global_selected = st.checkbox(
                            "Select as Global Indicator", 
                            value=bool(row.get('selected_global', 0)), 
                            key=f"global_{idx}"
                        )
                    with col2:
                        contextual_selected = st.checkbox(
                            "Select as Contextual Indicator", 
                            value=bool(row.get('selected_contextual', 0)), 
                            key=f"contextual_{idx}"
                        )
                    
                    # Update selection status in dataframe
                    st.session_state.df.at[idx, 'selected_global'] = 1 if global_selected else 0
                    st.session_state.df.at[idx, 'selected_contextual'] = 1 if contextual_selected else 0
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    with right_panel:
        st.markdown("### Selected Indicators Summary")
        
        # Count selected indicators
        global_selected = st.session_state.df[st.session_state.df['selected_global'] == 1]
        contextual_selected = st.session_state.df[st.session_state.df['selected_contextual'] == 1]
        
        # Try to find the reporting status column
        report_col = 'Already reported?'  # Use the actual column name from your Excel
        
        # Create statistics tabs
        tab1, tab2 = st.tabs(["Global Indicators", "Contextual Indicators"])
        
        with tab1:
            st.write(f"**{len(global_selected)} Global Indicators Selected**")
            
            if report_col in global_selected.columns and not global_selected.empty:
                # Group by reporting status
                report_counts = global_selected[report_col].value_counts()
                st.write("Distribution by reporting framework:")
                for framework, count in report_counts.items():
                    st.write(f"- {framework}: {count}")
            
            # Show coverage by thematic area and indicator type
            if 'Thematic Area' in global_selected.columns and 'Indicator Type' in global_selected.columns and not global_selected.empty:
                if len(global_selected) > 0:
                    st.write("Distribution by thematic area and indicator type:")
                    pivot_table = pd.pivot_table(
                        global_selected,
                        values='selected_global',
                        index=['Thematic Area'],
                        columns=['Indicator Type'],
                        aggfunc='count',
                        fill_value=0
                    )
                    st.dataframe(pivot_table, use_container_width=True)
            
            # Show list of selected indicators
            if not global_selected.empty and 'Indicators' in global_selected.columns:
                st.write("Selected global indicators:")
                indicators_list = global_selected['Indicators'].tolist()
                for i, indicator in enumerate(indicators_list):
                    st.write(f"{i+1}. {indicator}")
            else:
                st.info("No global indicators selected yet")
        
        with tab2:
            st.write(f"**{len(contextual_selected)} Contextual Indicators Selected**")
            
            if report_col in contextual_selected.columns and not contextual_selected.empty:
                # Group by reporting status
                report_counts = contextual_selected[report_col].value_counts()
                st.write("Distribution by reporting framework:")
                for framework, count in report_counts.items():
                    st.write(f"- {framework}: {count}")
            
            # Show coverage by thematic area and indicator type
            if 'Thematic Area' in contextual_selected.columns and 'Indicator Type' in contextual_selected.columns and not contextual_selected.empty:
                if len(contextual_selected) > 0:
                    st.write("Distribution by thematic area and indicator type:")
                    pivot_table = pd.pivot_table(
                        contextual_selected,
                        values='selected_contextual',
                        index=['Thematic Area'],
                        columns=['Indicator Type'],
                        aggfunc='count',
                        fill_value=0
                    )
                    st.dataframe(pivot_table, use_container_width=True)
            
            # Show list of selected indicators
            if not contextual_selected.empty and 'Indicators' in contextual_selected.columns:
                st.write("Selected contextual indicators:")
                indicators_list = contextual_selected['Indicators'].tolist()
                for i, indicator in enumerate(indicators_list):
                    st.write(f"{i+1}. {indicator}")
            else:
                st.info("No contextual indicators selected yet")
        
        # Export buttons
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Save Selections"):
                user_file = f'updated_{st.session_state.username}.xlsx'
                result = save_user_data(df=st.session_state.df, filename=user_file, drive_folder_id=DRIVE_FOLDER_ID)
                st.success(f"Selections saved! {result}")
        
        with col2:
            # Get only the selected indicators (either global or contextual)
            selected_df = st.session_state.df[
                (st.session_state.df['selected_global'] == 1) | 
                (st.session_state.df['selected_contextual'] == 1)
            ].copy()
            
            if len(selected_df) > 0:
                # Prepare download buffer with only selected records
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    selected_df.to_excel(writer, index=False)
                output.seek(0)
                
                st.download_button(
                    f"Download Selection ({len(selected_df)} indicators)",
                    data=output,
                    file_name=f"selected_indicators_{st.session_state.username}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("No indicators selected yet. Select indicators before downloading.")
                
        if st.button("Clear All Selections"):
            st.session_state.df['selected_global'] = 0
            st.session_state.df['selected_contextual'] = 0
            st.success("All selections cleared!")
            
def tag_indicators_tab():
    """Tab for tagging individual indicators"""
    st.markdown('<div class="sub-header">Indicator Tagging Interface</div>', unsafe_allow_html=True)
    
    df = st.session_state.df
    
    # Check if dataframe is empty
    if len(df) == 0:
        st.error("No data found. Please check your data file.")
        return
    
    column_mapping = get_column_mapping()
    gga_targets = get_gga_targets()
    moi_fields = get_moi_fields()
    
    # Define column groups - FIXED to check if columns exist
    gga_cols = []
    for target in gga_targets:
        if target in df.columns:
            gga_cols.append(target)
    
    water_component_cols = []
    for component in column_mapping.values():
        if component in df.columns:
            water_component_cols.append(component)
    
    # Find enabling/MOI columns - FIXED to check if columns exist
    enabling_cols = []
    for field in moi_fields:
        if field in df.columns:
            enabling_cols.append(field)
    
    # Try to find indicator type columns
    indicator_type_col = 'Indicator Type'  # Use actual column name from your Excel
    report_col = 'Already reported?'       # Use actual column name from your Excel
    
    indicator_cols = []
    if indicator_type_col in df.columns:
        indicator_cols.append(indicator_type_col)
    if report_col in df.columns:
        indicator_cols.append(report_col)
    
    total_records = len(df)
    current_index = st.session_state.get('current_index', 0)
    
    # Ensure current_index is in bounds
    current_index = min(max(0, current_index), total_records - 1)
    st.session_state.current_index = current_index
    
    # Navigation function
    def rerun_to_record(target_index):
        target_index = min(max(0, target_index), total_records - 1)
        st.session_state['current_index'] = target_index
        st.rerun()
    
    def confirm_navigation(target_index):
        target_index = min(max(0, target_index), total_records - 1)
        st.session_state['pending_target'] = target_index
        st.session_state['show_confirm'] = True
        st.rerun()
    
    # Navigation confirmation dialog
    if st.session_state.get('show_confirm', False):
        with st.container():
            st.warning("You have unsaved changes. Do you want to save before continuing?")
            col_decision = st.columns(2)
            target = st.session_state.get('pending_target', current_index)
            
            if col_decision[0].button("Save and Continue"):
                for col, val in st.session_state.get('pending_values', {}).items():
                    df.at[current_index, col] = 'X' if val is True else (' ' if val is False else val)
                
                user_file = f'updated_{st.session_state.username}.xlsx'
                save_user_data(df=df, filename=user_file, drive_folder_id=DRIVE_FOLDER_ID)
                st.session_state['unsaved_changes'] = False
                st.session_state['pending_values'] = {}
                st.session_state['show_confirm'] = False
                rerun_to_record(target)
            
            if col_decision[1].button("Ignore and Continue"):
                st.session_state['unsaved_changes'] = False
                st.session_state['pending_values'] = {}
                st.session_state['show_confirm'] = False
                rerun_to_record(target)
    
    # Navigation controls
    col_nav = st.columns([1, 4, 1, 1])
    
    if col_nav[0].button("Previous") and current_index > 0:
        if st.session_state.get('unsaved_changes', False):
            confirm_navigation(current_index - 1)
        else:
            rerun_to_record(current_index - 1)
    
    col_nav[1].markdown(f"### Record {current_index + 1} of {total_records}")
    
    if col_nav[2].button("Next") and current_index < total_records - 1:
        if st.session_state.get('unsaved_changes', False):
            confirm_navigation(current_index + 1)
        else:
            rerun_to_record(current_index + 1)
    
    col_nav[3].button("Go to First", 
                     on_click=lambda: confirm_navigation(0) if st.session_state.get('unsaved_changes', False) else rerun_to_record(0))
    
    # Get current record
    row = df.iloc[current_index]
    i = current_index
    
    # ID column
    id_col = None
    for col_name in ['ID', 'Id', 'id', 'identifier']:
        if col_name in df.columns:
            id_col = col_name
            break
    
    # Indicator name
    name_col = None
    for col_name in ['Indicators', 'Name', 'indicator_name', 'IndicatorName']:
        if col_name in df.columns:
            name_col = col_name
            break
            
    if name_col is None:
        indicator_name = f"Record {i+1}"
    else:
        indicator_name = row.get(name_col, f"Record {i+1}")
    
    # Display tagging interface
    with st.expander(f"Indicator: {indicator_name}", expanded=True):
        updated_values = {}
        
        # Indicator selection status
        st.markdown("##### Indicator Selection Status")
        status_col1, status_col2 = st.columns(2)
        with status_col1:
            global_status = st.checkbox("Selected as Global Indicator", 
                                     value=bool(row.get('selected_global', 0)),
                                     key=f"global_status_{i}")
            df.at[i, 'selected_global'] = 1 if global_status else 0
        
        with status_col2:
            contextual_status = st.checkbox("Selected as Contextual Indicator", 
                                         value=bool(row.get('selected_contextual', 0)),
                                         key=f"contextual_status_{i}")
            df.at[i, 'selected_contextual'] = 1 if contextual_status else 0
        
        st.divider()
        
        # Thematic Area section
        thematic_area_col = 'Thematic Area'
        if thematic_area_col in df.columns:
            st.markdown("##### 1. Thematic Area")
            options = sorted(df[thematic_area_col].dropna().unique().tolist())
            if options:
                current_val = row.get(thematic_area_col, options[0] if options else "")
                updated_values[thematic_area_col] = st.selectbox(
                    "Thematic Area", 
                    options=options,
                    index=options.index(current_val) if current_val in options else 0,
                    key=f"thematic_area_{i}",
                    on_change=lambda: st.session_state.update({'unsaved_changes': True})
                )
        
        # Indicator Type section
        if indicator_type_col in df.columns:
            st.markdown("##### 2. Indicator Type")
            options = sorted(df[indicator_type_col].dropna().unique().tolist())
            if options:
                current_val = row.get(indicator_type_col, options[0] if options else "")
                updated_values[indicator_type_col] = st.selectbox(
                    "Indicator Type", 
                    options=options,
                    index=options.index(current_val) if current_val in options else 0,
                    key=f"indicator_type_{i}",
                    on_change=lambda: st.session_state.update({'unsaved_changes': True})
                )
        
        # Reporting Status section
        if report_col in df.columns:
            st.markdown("##### 3. Reporting Status")
            options = sorted(df[report_col].dropna().unique().tolist())
            if options:
                current_val = row.get(report_col, options[0] if options else "")
                updated_values[report_col] = st.selectbox(
                    "Reporting Status", 
                    options=options,
                    index=options.index(current_val) if current_val in options else 0,
                    key=f"reporting_status_{i}",
                    on_change=lambda: st.session_state.update({'unsaved_changes': True})
                )
        
        # Other attributes section  
        if indicator_cols:
            st.markdown("##### 4. Other Attributes")
            for col in indicator_cols:
                if col not in [thematic_area_col, indicator_type_col, report_col] and col in row.index:
                    # For dropdown fields
                    options = df[col].dropna().unique().tolist()
                    if options:
                        key = f"{col}_{i}"
                        current_val = row[col] if pd.notna(row[col]) else options[0]
                        updated_values[col] = st.selectbox(
                            col, 
                            options, 
                            index=options.index(current_val) if current_val in options else 0, 
                            key=key, 
                            on_change=lambda: st.session_state.update({'unsaved_changes': True})
                        )
        
        st.session_state['pending_values'] = updated_values
        
        if st.button(f"Save Record {i+1}"):
            for col, val in updated_values.items():
                df.at[i, col] = 'X' if val is True else (' ' if val is False else val)
            
            user_file = f'updated_{st.session_state.username}.xlsx'
            result = save_user_data(df=df, filename=user_file, drive_folder_id=DRIVE_FOLDER_ID)
            st.session_state['unsaved_changes'] = False
            st.session_state['pending_values'] = {}
            st.success(f"Record {i+1} saved successfully! {result}")

def view_indicator_details_tab():
    """Tab for viewing detailed information about each indicator"""
    st.markdown('<div class="sub-header">Indicator Details View</div>', unsafe_allow_html=True)
    
    df = st.session_state.df
    
    # Check if dataframe is empty
    if len(df) == 0:
        st.error("No data found. Please check your data file.")
        return
    
    # Find indicator name column
    name_col = None
    for col_name in ['Indicators', 'Name', 'indicator_name', 'IndicatorName']:
        if col_name in df.columns:
            name_col = col_name
            break
    
    if name_col is None:
        st.error("Could not find indicator name column in the dataset")
        return
    
        # Track if any changes are made for download button activation
    if 'details_page_changes' not in st.session_state:
        st.session_state.details_page_changes = False
    
    # FILTER: Get only the selected indicators (either global or contextual)
    selected_df = df[(df['selected_global'] == 1) | (df['selected_contextual'] == 1)].copy()
    
    if len(selected_df) == 0:
        st.warning("No indicators have been selected yet. Please go to the 'Select Indicators' tab to select indicators first.")
        return
    

    # Create a dropdown to select an indicator from the SELECTED ones only
    indicators = selected_df[name_col].tolist()
    st.write(f"**Select an indicator to view details:** (Showing {len(indicators)} selected indicators)")
    selected_indicator = st.selectbox("Select an indicator to view details:", indicators)
    
    # Get the selected indicator's row
    selected_row = df[df[name_col] == selected_indicator].iloc[0]
    idx = df[df[name_col] == selected_indicator].index[0]
    
    st.markdown("### Indicator Details")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Basic information
        st.markdown("#### Basic Information")
        st.markdown(f"**Name:** {selected_indicator}")
        
        # Try to find ID column
        id_col = None
        for col_name in ['ID', 'Id', 'id', 'identifier']:
            if col_name in df.columns:
                id_col = col_name
                break
        
        if id_col and id_col in selected_row:
            st.markdown(f"**ID:** {selected_row[id_col]}")
        
        # Selection status
        global_status = bool(selected_row.get('selected_global', 0))
        contextual_status = bool(selected_row.get('selected_contextual', 0))
        
        if global_status:
            st.markdown("<span class='status-badge-selected'>Selected as Global Indicator</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span class='status-badge-unselected'>Not Selected as Global</span>", unsafe_allow_html=True)
            
        if contextual_status:
            st.markdown("<span class='status-badge-selected'>Selected as Contextual Indicator</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span class='status-badge-unselected'>Not Selected as Contextual</span>", unsafe_allow_html=True)
        
        # Try to find description column
        desc_col = None
        for col_name in ['Description', 'description', 'Desc', 'desc']:
            if col_name in df.columns:
                desc_col = col_name
                break
        
        if desc_col and desc_col in selected_row:
            st.markdown("#### Description")
            st.write(selected_row[desc_col])
    
    with col2:
        st.markdown("#### Indicator Attributes")
        
        # Create tabs for different attribute types
        tag_tab1, tag_tab2 = st.tabs(["Thematic Information", "Other Attributes"])
        
        with tag_tab1:
            # Thematic Area and Type
            thematic_area = selected_row.get('Thematic Area', 'Not specified')
            indicator_type = selected_row.get('Indicator Type', 'Not specified')
            reporting_status = selected_row.get('Already reported?', 'Not specified')
            
            st.markdown(f"**Thematic Area:** {thematic_area}")
            st.markdown(f"**Indicator Type:** {indicator_type}")
            st.markdown(f"**Reporting Status:** {reporting_status}")
        
        with tag_tab2:
            # Other attributes that might be in the dataset
            other_attributes = []
            for col in df.columns:
                if col not in [name_col, 'Thematic Area', 'Indicator Type', 'Already reported?', 
                              'selected_global', 'selected_contextual']:
                    if pd.notna(selected_row.get(col)):
                        other_attributes.append((col, selected_row[col]))
            
            if other_attributes:
                st.markdown("**Other Attributes:**")
                for attr_name, attr_value in other_attributes:
                    st.markdown(f"- **{attr_name}:** {attr_value}")
            else:
                st.info("No additional attributes found")
    
    # Additional information or actions
    st.divider()
    st.markdown("### Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Edit How this Indicator was Tagged", key="edit_indicator"):
            # Find the index in the dataframe
            idx = df[df[name_col] == selected_indicator].index[0]
            st.session_state.current_index = idx
            st.session_state.current_tab = "Tag"
            st.rerun()
    
    with col2:
        global_status = bool(selected_row.get('selected_global', 0))
            
        if global_status:
            if st.button("Remove from Global", key="remove_global"):
                idx = df[df[name_col] == selected_indicator].index[0]
                st.session_state.df.at[idx, 'selected_global'] = 0
                st.success(f"Removed {selected_indicator} from Global indicators")
                st.rerun()
        else:
            if st.button("Add to Global", key="add_global"):
                idx = df[df[name_col] == selected_indicator].index[0]
                st.session_state.df.at[idx, 'selected_global'] = 1
                st.success(f"Added {selected_indicator} to Global indicators")
                st.rerun()
    
    with col3:
        contextual_status = bool(selected_row.get('selected_contextual', 0))

        if contextual_status:
            if st.button("Remove from Contextual", key="remove_contextual"):
                idx = df[df[name_col] == selected_indicator].index[0]
                st.session_state.df.at[idx, 'selected_contextual'] = 0
                st.success(f"Removed {selected_indicator} from Contextual indicators")
                st.rerun()
        else:
            if st.button("Add to Contextual", key="add_contextual"):
                idx = df[df[name_col] == selected_indicator].index[0]
                st.session_state.df.at[idx, 'selected_contextual'] = 1
                st.success(f"Added {selected_indicator} to Contextual indicators")
                st.rerun()

        # Add a fourth column for the download button
    st.divider()
    
    # Get the updated selection count after any changes
    updated_selected_df = df[(df['selected_global'] == 1) | (df['selected_contextual'] == 1)].copy()
    
    # Create download button with conditional styling
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Save All Changes"):
            user_file = f'updated_{st.session_state.username}.xlsx'
            result = save_user_data(df=st.session_state.df, filename=user_file, drive_folder_id=DRIVE_FOLDER_ID)
            st.success(f"All changes saved! {result}")
            st.session_state.details_page_changes = False
    
    with col2:
        button_label = "Download Updated Indicators" if st.session_state.details_page_changes else "Download Selected Indicators"
        button_help = "Download indicators with recent changes" if st.session_state.details_page_changes else ""
        
        # Prepare download buffer
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            updated_selected_df.to_excel(writer, index=False)
        output.seek(0)
        
        st.download_button(
            label=button_label,
            data=output,
            file_name=f"selected_indicators_{st.session_state.username}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help=button_help
        )

# --- ADMIN FUNCTIONS ---
def admin_panel():
    """Additional admin functions"""
    if st.session_state.username != 'admin':
        return
    
    st.markdown('<div class="sub-header">Administrator Panel</div>', unsafe_allow_html=True)
    
    st.markdown("### Admin Functions")
    
    tab1, tab2 = st.tabs(["Download Options", "User Management"])
    
    with tab1:
        st.markdown("#### Download Options")
        
        if st.button("Download All User Files as ZIP"):
            # Create a temporary ZIP file
            with tempfile.TemporaryDirectory() as tmpdirname:
                zip_path = os.path.join(tmpdirname, "all_user_updates.zip")
                with zipfile.ZipFile(zip_path, "w") as zipf:
                    for file in os.listdir():
                        if file.startswith("updated_") and file.endswith(".xlsx"):
                            zipf.write(file, arcname=file)

                # Read the ZIP file as bytes and provide a download button
                with open(zip_path, "rb") as f:
                    zip_bytes = f.read()
                st.download_button(
                    label="Click here to download all user Excel files",
                    data=zip_bytes,
                    file_name="all_user_updates.zip",
                    mime="application/zip"
                )
        
        st.markdown("#### Generate Excel Files from Template")
        if st.button("Generate Excel files from template"):
            df = st.session_state.df

            # Check if template file exists
            if not os.path.exists(TEMPLATE_FILE):
                st.error(f"Template file '{TEMPLATE_FILE}' not found.")
                return

            # Output directory
            output_folder = "generated_indicators"
            os.makedirs(output_folder, exist_ok=True)

            count = 0
            count_global = 0
            count_contextual = 0
            for i, row in df.iterrows():
                if row.get('selected_global', 0) == 1 or row.get('selected_contextual', 0) == 1:
                    if row.get('selected_global', 0) == 1:
                        count_global += 1
                    if row.get('selected_contextual', 0) == 1:
                        count_contextual += 1
                    prefix = "global" if row.get('selected_global') == 1 else "contextual"
                    numero = count_global if row.get('selected_global') == 1 else count_contextual
                    filename = f"{prefix}_indicator_{numero}.xlsx"
                    filepath = os.path.join(output_folder, filename)

                    # Copy the Excel template
                    try:
                        copyfile(TEMPLATE_FILE, filepath)

                        # Open and edit the copied workbook
                        wb = load_workbook(filepath)
                        ws = wb.active

                        # Find ID column
                        id_col = None
                        for col_name in ['ID', 'Id', 'id', 'identifier']:
                            if col_name in df.columns:
                                id_col = col_name
                                break

                        # Find name column
                        name_col = None
                        for col_name in ['Indicators', 'Name', 'indicator_name', 'IndicatorName']:
                            if col_name in df.columns:
                                name_col = col_name
                                break

                        # Find type column
                        type_col = 'Indicator Type'

                        if id_col and id_col in df.columns:
                            ws["A2"] = row.get(id_col, "")
                        if name_col and name_col in df.columns:
                            ws["B2"] = row.get(name_col, "")
                        
                        # Thematic area
                        theme_col = 'Thematic Area'
                        if theme_col in df.columns:
                            ws["C2"] = row.get(theme_col, "")
                        
                        if type_col and type_col in df.columns:
                            ws["D2"] = row.get(type_col, "")
                        
                        # Reporting status
                        report_col = 'Already reported?'
                        if report_col in df.columns:
                            ws["E2"] = row.get(report_col, "")

                        wb.save(filepath)
                        count += 1
                    except Exception as e:
                        st.error(f"Error creating file {filepath}: {e}")

            st.success(f"{count} Excel files generated in folder: {output_folder}")
    
    with tab2:
        st.markdown("#### User Management")
        
        st.markdown("Viewing files from all users:")
        
        user_files = [f for f in os.listdir() if f.startswith("updated_") and f.endswith(".xlsx")]
        
        if user_files:
            for file in user_files:
                username = file.replace("updated_", "").replace(".xlsx", "")
                st.markdown(f"- {username}: {file}")
        else:
            st.info("No user files found")
        
        if drive_enabled:
            st.markdown("#### Drive Files")
            try:
                query = f"'{DRIVE_FOLDER_ID}' in parents and name contains 'updated_' and name contains '.xlsx'"
                response = drive_service.files().list(
                    q=query, 
                    fields="files(id, name, modifiedTime)", 
                    orderBy="modifiedTime desc"
                ).execute()
                
                files = response.get('files', [])
                
                if files:
                    st.markdown("Files on Google Drive:")
                    for file in files:
                        st.markdown(f"- {file['name']} (ID: {file['id']}, Modified: {file['modifiedTime']})")
                else:
                    st.info("No matching files found on Google Drive")
                    
            except Exception as e:
                st.error(f"Error listing Drive files: {e}")

# --- MAIN APP FUNCTION ---
def main():
    """Main application function"""
    # Check authentication
    if not st.session_state.get('authenticated', False):
        login_page()
        return
    
    # Initialize session state
    setup_session_state()
    
    # Render app header with tabs
    app_header()
    
    # Display appropriate tab content
    current_tab = st.session_state.get('current_tab', 'Select')
    
    if current_tab == "Select":
        select_indicators_tab()
    elif current_tab == "Tag":
        tag_indicators_tab()
    elif current_tab == "Details":
        view_indicator_details_tab()
    
    # Show admin panel if admin user
    if st.session_state.username == 'admin':
        st.divider()
        admin_panel()

# --- RUN THE APP ---
if __name__ == "__main__":
    main()