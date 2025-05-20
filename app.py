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

# ==========================================
# PART 1: SETUP AND CONFIGURATION
# ==========================================

# Force disable Google Drive integration (remove this line once you have credentials.json)
drive_enabled = False

# Load environment variables
load_dotenv(dotenv_path='.env')

# Your Google Drive Folder ID - Update this with your folder ID
DRIVE_FOLDER_ID = "1V9oik7onvQpvyl4y9mUh5MPOmom4GrkO"

# Set Streamlit page config to use full screen width
st.set_page_config(layout="wide", page_title="GGA Indicators - Tagging & Selection Management System")

# Default file paths
DEFAULT_EXCEL_FILE = 'Indicators_1000.xlsx'
TEMPLATE_FILE = 'Indicators_1000.xlsx'

# Apply custom CSS for improved UI
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
    /* Score display styling */
    .score-badge {
        background-color: #2a4c64; 
        color: #ffffff;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 12px;
        font-weight: bold;
        float: right;
    }
    .score-progress {
        width: 100%;
        height: 20px;
        background-color: #333; 
        border-radius: 10px; 
        overflow: hidden; 
        margin: 10px 0;
    }
    .score-progress-bar {
        height: 100%;
        background-color: #0078ff;
    }
    .score-breakdown {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
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
    /* Improve text contrast */
    p, li, label, .stCheckbox, .stRadio {
        color: white !important;
        font-weight: 500 !important;
    }
    
    /* Make section headers more prominent */
    .sub-header, h3, h4, h5 {
        color: #00bfff !important;
        font-weight: 600 !important;
        margin-top: 20px !important;
    }
    
    /* Improve checkbox visibility */
    .stCheckbox > label {
        color: white !important;
        font-weight: 500 !important;
        background-color: rgba(30, 30, 30, 0.7) !important;
        padding: 5px 10px !important;
        border-radius: 5px !important;
        margin-bottom: 5px !important;
    }
    
    /* Improve info icon visibility */
    [data-testid="stHelperIcon"] {
        color: #00bfff !important;
        background-color: rgba(0, 191, 255, 0.1) !important;
        border-radius: 50% !important;
        padding: 2px !important;
    }
    
    /* Improve non-editable field appearance */
    .stInfo {
        background-color: #1e3045 !important;
        color: white !important;
        border-color: #2a4c64 !important;
    }
    
    /* Make the progress bar more visible */
    .score-progress {
        height: 25px !important;
        background-color: #333344 !important;
    }
    
    .score-progress-bar {
        background-color: #0078ff !important;
        background-image: linear-gradient(45deg, 
                          rgba(255, 255, 255, 0.15) 25%, 
                          transparent 25%, 
                          transparent 50%, 
                          rgba(255, 255, 255, 0.15) 50%, 
                          rgba(255, 255, 255, 0.15) 75%, 
                          transparent 75%, 
                          transparent) !important;
        background-size: 1rem 1rem !important;
    }
    
    /* Improve indicator header visibility */
    .indicator-card strong {
        color: white !important;
        font-size: 16px !important;
    }
    
    /* Add subtle hover effect to buttons */
    .stButton > button:hover {
        border-color: #00bfff !important;
        box-shadow: 0 0 5px rgba(0, 191, 255, 0.5) !important;
    }
            
    /* Target hint text specifically */
    div[data-baseweb="tooltip"] {
        background-color: #1e3045 !important;
        color: white !important;
        border: 1px solid #2a4c64 !important;
        padding: 1px !important;
        border-radius: 1px !important;
        font-size: 1px !important;
    }
    
    /* Make checkbox container clearer */
    div.row-widget.stCheckbox {
        padding: 1px !important;
        margin: 1px 0 !important;
        background-color: rgba(30, 30, 30, 0.3) !important;
        border-radius: 1px !important;
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

# --- SCORING SYSTEM ---
def calculate_indicator_score(row):
    """
    Calculate a score for an indicator based on various attributes
    Max score is 5 points
    """
    score = 0
    
    # 1. Global/Contextual Status (0-1 points)
    global_status = str(row.get('Global/Contextual Status', '')).strip()
    if global_status == 'Both':
        score += 1.0  # Both global and contextual
    elif global_status == 'Global':
        score += 0.75  # Global only
    # Contextual only gets 0 points
    
    # 2. Thematic Interlinkages (0-1 points)
    # Count thematic areas by looking at the 'Thematic Area' column
    thematic_area = str(row.get('Thematic Area', '')).strip()
    # This checks if the thematic area contains commas (multiple entries)
    thematic_areas = thematic_area.split(',')
    covered_areas = len(thematic_areas)
    
    if covered_areas >= 3:
        score += 1.0
    elif covered_areas == 2:
        score += 0.5
    
    # 3. Means of Implementation Coverage (0-1 points)
    moi = str(row.get('Means of Implementation', '')).strip()
    moi_count = 0
    if 'Technology' in moi:
        moi_count += 1
    if 'Finance' in moi:
        moi_count += 1
    if 'Capacity Building' in moi:
        moi_count += 1
    if 'Enabling factor' in moi:
        moi_count += 1
    
    if moi_count >= 3:
        score += 1.0
    elif moi_count == 2:
        score += 0.6
    elif moi_count == 1:
        score += 0.3
    
    # 4. Indicator Type (0-1 point)
    indicator_type = str(row.get('Indicator Type', '')).strip().lower()
    if indicator_type in ['input', 'process', 'output', 'outcome']:
        score += 1.0  # Give full point if valid indicator type
    
    # 5. Reporting Status (0-1 point)
    reporting_status = str(row.get('Already reported?', '')).strip().lower()
    
    if reporting_status == "never reported":
        # Not reported
        score += 0.0
    elif "unknown" in reporting_status or "reporting status unknown" in reporting_status:
        # New indicator with unknown status
        score += 1.0
    elif any(framework in reporting_status for framework in ["sdg", "international", "sendai"]):
        # Reported in established frameworks
        score += 1.0
    else:
        # Default case for other types
        score += 0.5
    
    # Round to 2 decimal places for cleaner display
    return round(min(score, 5), 2)  # Cap at max 5 points

def calculate_scores_for_dataframe(df):
    """Calculate scores for all rows in the dataframe"""
    df['score'] = df.apply(calculate_indicator_score, axis=1)
    return df

# --- DATA LOADING FUNCTIONS ---
@st.cache_data(ttl=600)
def load_excel_data(file_path):
    try:
        if not os.path.exists(file_path):
            st.error(f"File not found: {file_path}")
            return pd.DataFrame()
        
        # Check if file is a text file (tab-delimited) or Excel
        if file_path.endswith('.txt'):
            df = pd.read_csv(file_path, sep='\t')
        else:
            df = pd.read_excel(file_path)
        
        # Calculate scores for the dataframe
        df = calculate_scores_for_dataframe(df)
        
        return df
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
            df = pd.read_excel(fh)
            # Calculate scores for the dataframe
            df = calculate_scores_for_dataframe(df)
            return df, user_filename
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
    
    # ==========================================
# PART 2: AUTHENTICATION AND APP STRUCTURE
# ==========================================

# --- CONSTANTS AND MAPPINGS ---
def get_column_mapping():
    """Define mappings for column names"""
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
    """Get list of GGA targets"""
    return [
        "Input",
        "Process",
        "Output",
        "Outcome"
    ]

def get_moi_fields():
    """Get Means of Implementation fields"""
    return ["Enabling factor", "MOI Technology", "MOI Finance", "MOI Capacity Building"]

# --- AUTHENTICATION SYSTEM ---
def setup_auth():
    """Initialize authentication system with user credentials"""
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
    """Render login page"""
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

# --- APP STRUCTURE FUNCTIONS ---
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
                
                # Calculate scores if they don't exist
                if 'score' not in st.session_state.df.columns:
                    st.session_state.df = calculate_scores_for_dataframe(st.session_state.df)
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

# --- UTILITY FUNCTIONS ---
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

# --- MAIN APP FUNCTION ---
def main():
    """Main application entry point"""
    setup_auth()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        setup_session_state()
        app_header()
        
        # Render the selected tab
        if st.session_state.current_tab == "Select":
            select_indicators_tab()
        elif st.session_state.current_tab == "Tag":
            tag_indicators_tab()
        elif st.session_state.current_tab == "Details":
            view_indicator_details_tab()
        
        

    # ==========================================
# PART 3: TAB FUNCTIONALITY
# ==========================================

# --- SELECT INDICATORS TAB ---
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
            
            # Add sorting by score
            sort_options = ["Score (high to low)", "Score (low to high)", "Alphabetical", "None"]
            sort_by = st.selectbox("Sort indicators by:", sort_options, index=0)
            
            show_full_list_checkbox = st.checkbox("Show full list of relevant components and targets", value=False)
            
            # Apply filters
            filtered_df = st.session_state.df.copy()
            
            # Apply thematic area filter
            if filter_by_theme != "All" and 'Thematic Area' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Thematic Area'] == filter_by_theme]
            
            # Apply indicator type filter  
            if selected_type != "All" and indicator_type_col in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[indicator_type_col] == selected_type]
            
            # Apply sorting based on selection
            if sort_by == "Score (high to low)":
                filtered_df = filtered_df.sort_values(by='score', ascending=False)
            elif sort_by == "Score (low to high)":
                filtered_df = filtered_df.sort_values(by='score', ascending=True)
            elif sort_by == "Alphabetical":
                if 'Indicators' in filtered_df.columns:
                    filtered_df = filtered_df.sort_values(by='Indicators')
            
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
                    score = row.get('score', 0)
                    
                    # Display indicator card with score
                    st.markdown(f"""
                    <div class="indicator-card">
                        <strong>{indicator_name}</strong>
                        <span class="score-badge">Score: {score}/5</span>
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
                        st.markdown(f"<div class='tag-pill'>MoI: {row.get('Means of Implementation', 'Not specified')}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='tag-pill'>Global/Contextual: {row.get('Global/Contextual Status', 'Not specified')}</div>", unsafe_allow_html=True)
                    
                    # Selection checkboxes
                    col1, col2 = st.columns(2)
                    with col1:
                        global_selected = st.checkbox(
                            "Select this Indicator (GLOBAL)", 
                            value=bool(row.get('selected_global', 0)), 
                            key=f"global_{idx}"
                        )
                    with col2:
                        contextual_selected = st.checkbox(
                            "Select this Indicator (CONTEXTUAL)", 
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
            
            # Show average score for selected indicators
            if len(global_selected) > 0 and 'score' in global_selected.columns:
                avg_score = global_selected['score'].mean()
                st.write(f"**Average Score: {avg_score:.2f}/5**")
            
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
                # Sort by score
                sorted_global = global_selected.sort_values(by='score', ascending=False)
                for i, (idx, row) in enumerate(sorted_global.iterrows()):
                    indicator_name = row['Indicators']
                    score = row.get('score', 0)
                    st.write(f"{i+1}. {indicator_name} (Score: {score:.2f}/5)")
            else:
                st.info("No global indicators selected yet")
        
        with tab2:
            st.write(f"**{len(contextual_selected)} Contextual Indicators Selected**")
            
            # Show average score for selected indicators
            if len(contextual_selected) > 0 and 'score' in contextual_selected.columns:
                avg_score = contextual_selected['score'].mean()
                st.write(f"**Average Score: {avg_score:.2f}/5**")
                
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
                # Sort by score
                sorted_contextual = contextual_selected.sort_values(by='score', ascending=False)
                for i, (idx, row) in enumerate(sorted_contextual.iterrows()):
                    indicator_name = row['Indicators']
                    score = row.get('score', 0)
                    st.write(f"{i+1}. {indicator_name} (Score: {score:.2f}/5)")
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

# --- TAG INDICATORS TAB ---
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
    indicator_type_col = 'Indicator Type'  
    report_col = 'Already reported?'       
    thematic_area_col = 'Thematic Area'
    global_contextual_col = 'Global/Contextual Status'
    moi_col = 'Means of Implementation'
    
    indicator_cols = []
    for col in [indicator_type_col, report_col, thematic_area_col, global_contextual_col, moi_col]:
        if col in df.columns:
            indicator_cols.append(col)
    
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
        
        # Show the indicator score
        score = row.get('score', 0)
        st.markdown(f"<h5>Indicator Score: {score:.2f}/5</h5>", unsafe_allow_html=True)
        
        # Progress bar for score visualization
        progress_percent = (score / 5) * 100
        st.markdown(f"""
            <div class="score-progress">
                <div class="score-progress-bar" style="width:{progress_percent}%"></div>
            </div>
        """, unsafe_allow_html=True)
        
        
        st.divider()
        
        # Thematic Interlinkages - editable
        st.markdown("##### 1. Thematic Interlinkages (Editable)")
        st.write("You can edit the thematic interlinkages for this indicator:")
        
        # Get all available thematic areas for checkboxes
        available_thematic_areas = []
        if 'Thematic Area' in df.columns:
            # Get unique thematic areas across all records
            all_thematic_areas = set()
            for area_str in df['Thematic Area'].dropna():
                areas = [a.strip() for a in area_str.split(',')]
                all_thematic_areas.update(areas)
            available_thematic_areas = sorted(list(all_thematic_areas))
        
        # Current thematic areas
        current_thematic_areas = []
        if thematic_area_col in df.columns and pd.notna(row.get(thematic_area_col)):
            current_thematic_areas = [area.strip() for area in row.get(thematic_area_col, "").split(',')]
        
        # Create thematic area checkboxes in a grid layout
        num_cols = 3  # Number of columns in the grid
        cols = st.columns(num_cols)
        
        selected_thematic_areas = []
        
        for idx, area in enumerate(available_thematic_areas):
            with cols[idx % num_cols]:
                is_selected = area in current_thematic_areas
                checkbox_key = f"thematic_area_{area}_{i}"
                area_selected = st.checkbox(
                    area, 
                    value=is_selected,
                    key=checkbox_key,
                    help=f"Check to indicate this indicator relates to the '{area}' thematic area"
                )
                
                if area_selected:
                    selected_thematic_areas.append(area)
                    
        # If any thematic areas were selected/deselected, mark as needing to be saved
        if set(selected_thematic_areas) != set(current_thematic_areas):
            updated_values[thematic_area_col] = ", ".join(selected_thematic_areas)
            st.session_state['unsaved_changes'] = True
        
        st.session_state['pending_values'] = updated_values

        # Show thematic area - non-editable
        if thematic_area_col in df.columns:
            st.markdown("##### 2. Thematic Area (Non-editable)")
            thematic_area = row.get(thematic_area_col, "Not specified")
            st.info(f"**Thematic Area:** {thematic_area}")
        
        # Show indicator type - non-editable
        if indicator_type_col in df.columns:
            st.markdown("##### 3. Indicator Type (Non-editable)")
            indicator_type = row.get(indicator_type_col, "Not specified")
            st.info(f"**Indicator Type:** {indicator_type}")
        
        # Show reporting status - non-editable
        if report_col in df.columns:
            st.markdown("##### 4. Reporting Status (Non-editable)")
            reporting_status = row.get(report_col, "Not specified")
            st.info(f"**Reporting Status:** {reporting_status}")
            
        # Show Global/Contextual status - non-editable
        if global_contextual_col in df.columns:
            st.markdown("##### 5. Global/Contextual Status (Non-editable)")
            gc_status = row.get(global_contextual_col, "Not specified")
            st.info(f"**Global/Contextual Status:** {gc_status}")
            
        # Show Means of Implementation - non-editable
        if moi_col in df.columns:
            st.markdown("##### 6. Means of Implementation (Non-editable)")
            moi_value = row.get(moi_col, "Not specified")
            st.info(f"**Means of Implementation:** {moi_value}")
            
        # Add Save button at the bottom
      
        
        if st.button(f"Save Record {i+1}"):
            for col, val in updated_values.items():
                df.at[i, col] = val
            
            # Recalculate the score after updates
            df.at[i, 'score'] = calculate_indicator_score(df.iloc[i])
            
            user_file = f'updated_{st.session_state.username}.xlsx'
            result = save_user_data(df=df, filename=user_file, drive_folder_id=DRIVE_FOLDER_ID)
            st.session_state['unsaved_changes'] = False
            st.session_state['pending_values'] = {}
            st.success(f"Record {i+1} saved successfully! {result}")

        # if st.button("Save All Changes to File"):
        #     user_file = f'updated_{st.session_state.username}.xlsx'
        #     result = save_user_data(df=st.session_state.df, filename=user_file, drive_folder_id=DRIVE_FOLDER_ID)
        #     st.success(f"All changes saved! {result}")

    # --- VIEW INDICATOR DETAILS TAB (continued) ---
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
    
    # Add sort options
    col1, col2 = st.columns([3, 1])
    
    with col1:
        sort_options = ["Score (high to low)", "Score (low to high)", "Alphabetical", "None"]
        sort_by = st.selectbox("Sort indicators by:", sort_options, index=0)
        
        # Apply sorting based on selection
        if sort_by == "Score (high to low)":
            selected_df = selected_df.sort_values(by='score', ascending=False)
        elif sort_by == "Score (low to high)":
            selected_df = selected_df.sort_values(by='score', ascending=True)
        elif sort_by == "Alphabetical":
            if name_col in selected_df.columns:
                selected_df = selected_df.sort_values(by=name_col)
    
    with col2:
        # Create download button for selected indicators
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            selected_df.to_excel(writer, index=False)
        output.seek(0)
        
        st.download_button(
            f"Download Selected ({len(selected_df)})",
            data=output,
            file_name=f"selected_indicators_{st.session_state.username}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download all currently selected indicators"
        )

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
        
        # Display Score
        score = selected_row.get('score', 0)
        st.markdown(f"#### Score: {score:.2f}/5")
        
        # Progress bar for score
        progress_percent = (score / 5) * 100
        st.markdown(f"""
            <div class="score-progress">
                <div class="score-progress-bar" style="width:{progress_percent}%"></div>
            </div>
        """, unsafe_allow_html=True)
        
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
        tab1, tab2 = st.tabs(["Basic Information", "Score Breakdown"])
        
        with tab1:
            # Thematic Area and Type
            thematic_area = selected_row.get('Thematic Area', 'Not specified')
            indicator_type = selected_row.get('Indicator Type', 'Not specified')
            reporting_status = selected_row.get('Already reported?', 'Not specified')
            global_contextual = selected_row.get('Global/Contextual Status', 'Not specified')
            means_implementation = selected_row.get('Means of Implementation', 'Not specified')
            
            st.markdown(f"**Thematic Area:** {thematic_area}")
            st.markdown(f"**Indicator Type:** {indicator_type}")
            st.markdown(f"**Reporting Status:** {reporting_status}")
            st.markdown(f"**Global/Contextual Status:** {global_contextual}")
            st.markdown(f"**Means of Implementation:** {means_implementation}")
        
        with tab2:
            # Show score breakdown
            st.markdown("##### Score Breakdown")
            
            # 1. Global/Contextual Status
            gc_status = str(selected_row.get('Global/Contextual Status', '')).strip()
            gc_points = 0
            if gc_status == 'Both':
                gc_points = 1.0
                gc_explanation = "Both Global and Contextual (+1 point)"
            elif gc_status == 'Global':
                gc_points = 0.75
                gc_explanation = "Global indicator only (+0.75 points)"
            else:
                gc_explanation = "Contextual indicator only (0 points)"
            
            st.markdown(f"**1. Global/Contextual Status:** {gc_explanation}")
            
            # 2. Thematic Interlinkages
            thematic_area = str(selected_row.get('Thematic Area', '')).strip()
            thematic_areas = thematic_area.split(',')
            covered_areas = len(thematic_areas)
            
            if covered_areas >= 3:
                tl_points = 1.0
                tl_explanation = f"Three or more thematic areas ({covered_areas}) (+1 point)"
            elif covered_areas == 2:
                tl_points = 0.5
                tl_explanation = "Two thematic areas (+0.5 points)"
            else:
                tl_points = 0
                tl_explanation = "Single thematic area (0 points)"
                
            st.markdown(f"**2. Thematic Interlinkages:** {tl_explanation}")
            
            # 3. Means of Implementation Coverage
            moi = str(selected_row.get('Means of Implementation', '')).strip()
            moi_count = 0
            if 'Technology' in moi:
                moi_count += 1
            if 'Finance' in moi:
                moi_count += 1
            if 'Capacity Building' in moi:
                moi_count += 1
            if 'Enabling factor' in moi:
                moi_count += 1
            
            if moi_count >= 3:
                moi_points = 1.0
                moi_explanation = f"{moi_count} MOI categories (+1 point)"
            elif moi_count == 2:
                moi_points = 0.6
                moi_explanation = "Two MOI categories (+0.6 points)"
            elif moi_count == 1:
                moi_points = 0.3
                moi_explanation = "One MOI category (+0.3 points)"
            else:
                moi_points = 0
                moi_explanation = "No MOI coverage (0 points)"
                
            st.markdown(f"**3. Means of Implementation Coverage:** {moi_explanation}")
            
            # 4. Indicator Type
            indicator_type = str(selected_row.get('Indicator Type', '')).strip().lower()
            if indicator_type in ['input', 'process', 'output', 'outcome']:
                it_points = 1.0
                it_explanation = f"{indicator_type.capitalize()} indicator type (+1 point)"
            else:
                it_points = 0
                it_explanation = "Unknown indicator type (0 points)"
                
            st.markdown(f"**4. Indicator Type:** {it_explanation}")
            
            # 5. Reporting Status
            reporting_status = str(selected_row.get('Already reported?', '')).strip().lower()
            
            if reporting_status == "never reported":
                rs_points = 0.0
                rs_explanation = "Never reported (0 points)"
            elif "unknown" in reporting_status or "reporting status unknown" in reporting_status:
                rs_points = 1.0
                rs_explanation = "New indicator with unknown reporting status (+1 point)"
            elif any(framework in reporting_status for framework in ["sdg", "international", "sendai"]):
                rs_points = 1.0
                rs_explanation = f"Reported in {reporting_status} (+1 point)"
            else:
                rs_points = 0.5
                rs_explanation = "Other reporting status (+0.5 points)"
                
            st.markdown(f"**5. Reporting Status:** {rs_explanation}")
            
            # Total score
            total_points = gc_points + tl_points + moi_points + it_points + rs_points
            st.markdown(f"**Total Score:** {total_points:.2f}/5")
            
            # Show this in a nice visual
            st.markdown("""
            <table style="width:100%; border-collapse: collapse; margin-top: 20px; background-color: #1e1e1e; border-radius: 10px;">
                <tr>
                    <th style="padding: 10px; text-align: left; border-bottom: 1px solid #444;">Score Component</th>
                    <th style="padding: 10px; text-align: right; border-bottom: 1px solid #444;">Points</th>
                </tr>
            """, unsafe_allow_html=True)
            
            components = [
                ("Global/Contextual Status", gc_points),
                ("Thematic Interlinkages", tl_points),
                ("Means of Implementation", moi_points),
                ("Indicator Type", it_points),
                ("Reporting Status", rs_points),
                ("Total", total_points)
            ]
            
            for name, points in components:
                bg_color = "#1e4620" if points > 0 else "#4e1c24"
                text_color = "#4caf50" if points > 0 else "#f44336"
                if name == "Total":
                    st.markdown(f"""
                    <tr style="background-color: #333;">
                        <td style="padding: 10px; font-weight: bold;">{name}</td>
                        <td style="padding: 10px; text-align: right; font-weight: bold;">{points:.2f}/5</td>
                    </tr>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <tr>
                        <td style="padding: 10px;">{name}</td>
                        <td style="padding: 10px; text-align: right; background-color: {bg_color}; color: {text_color}; border-radius: 5px;">{points:.2f}</td>
                    </tr>
                    """, unsafe_allow_html=True)
            
            st.markdown("</table>", unsafe_allow_html=True)
    

    # Additional information or actions
    st.divider()
    st.markdown("### Actions")

    # Create a 2-column layout for the buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Edit How this Indicator was Tagged", key="edit_indicator", use_container_width=True):
            # Find the index in the dataframe
            idx = df[df[name_col] == selected_indicator].index[0]
            st.session_state.current_index = idx
            st.session_state.current_tab = "Tag"
            st.rerun()

    with col2:
        # Prepare download buffer with only the current indicator's data
        single_df = df[df[name_col] == selected_indicator].copy()
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            single_df.to_excel(writer, index=False)
        output.seek(0)
        
        st.download_button(
            "Download Current Indicator Data",
            data=output,
            file_name=f"{selected_indicator.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
# --- EXECUTION POINT ---
if __name__ == '__main__':
    main()