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
# --- NEW CODE: Helper functions to calculate individual score components ---
def calculate_score_global_contextual(row):
    """Calculate score component for Global/Contextual Status (0-1 points)"""
    global_status = str(row.get('Global/Contextual Status', '')).strip()
    if global_status == 'Both':
        return 1.0  # Both global and contextual
    elif global_status == 'Global':
        return 0.75  # Global only
    return 0.0  # Contextual only gets 0 points

def calculate_score_thematic(row):
    """Calculate score component for Thematic Interlinkages (0-1 points)"""
    thematic_area = str(row.get('Thematic Area', '')).strip()
    thematic_areas = thematic_area.split(',')
    covered_areas = len(thematic_areas)
    
    if covered_areas >= 3:
        return 1.0
    elif covered_areas == 2:
        return 0.5
    return 0.0

def calculate_score_moi(row):
    """Calculate score component for Means of Implementation Coverage (0-1 points)"""
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
        return 1.0
    elif moi_count == 2:
        return 0.6
    elif moi_count == 1:
        return 0.3
    return 0.0

def calculate_score_indicator_type(row):
    """Calculate score component for Indicator Type (0-1 point)"""
    indicator_type = str(row.get('Indicator Type', '')).strip().lower()
    if indicator_type in ['input', 'process', 'output', 'outcome']:
        return 1.0  # Give full point if valid indicator type
    return 0.0

def calculate_score_reporting(row):
    """Calculate score component for Reporting Status (0-1 point)"""
    reporting_status = str(row.get('Already reported?', '')).strip().lower()
    
    if reporting_status == "never reported":
        # Not reported
        return 0.0
    elif "unknown" in reporting_status or "reporting status unknown" in reporting_status:
        # New indicator with unknown status
        return 1.0
    elif any(framework in reporting_status for framework in ["sdg", "international", "sendai"]):
        # Reported in established frameworks
        return 1.0
    else:
        # Default case for other types
        return 0.5

# --- NEW CODE: Function to reorganize columns for export ---
def reorganize_columns_for_export(df):
    """
    Reorganizes dataframe columns in the specified order for downloads.
    
    Args:
        df (pandas.DataFrame): The dataframe to reorganize
    
    Returns:
        pandas.DataFrame: A copy of the dataframe with reorganized columns
    """
    # Create a copy of the dataframe to avoid modifying the original
    export_df = df.copy()
    
    # Define the preferred column order
    preferred_order = [
        'Thematic Area',           # Column 1: Thematic Area
        'Indicator Type',          # Column 2: Indicator Type
        'Global/Contextual Status', # Column 3: Global/Contextual Status
        'Indicators',              # Column 4: Indicators
        'Already reported?',       # Column 5: Already reported?
        'Means of Implementation'  # Column 6: Means of Implementation
    ]
    
    # Find score component columns - these are individual scores calculated during scoring
    score_component_cols = []
    
    # Create columns for individual score components if they don't exist
    if 'score_global_contextual' not in export_df.columns:
        # Add individual score components (extracted from calculate_indicator_score function)
        export_df['score_global_contextual'] = export_df.apply(
            lambda row: calculate_score_global_contextual(row), axis=1
        )
        
    if 'score_thematic' not in export_df.columns:
        export_df['score_thematic'] = export_df.apply(
            lambda row: calculate_score_thematic(row), axis=1
        )
        
    if 'score_moi' not in export_df.columns:
        export_df['score_moi'] = export_df.apply(
            lambda row: calculate_score_moi(row), axis=1
        )
        
    if 'score_indicator_type' not in export_df.columns:
        export_df['score_indicator_type'] = export_df.apply(
            lambda row: calculate_score_indicator_type(row), axis=1
        )
        
    if 'score_reporting' not in export_df.columns:
        export_df['score_reporting'] = export_df.apply(
            lambda row: calculate_score_reporting(row), axis=1
        )
    
    # Add all score component columns to our list
    score_component_cols = [
        'score_global_contextual',  # Individual score for global/contextual status
        'score_thematic',           # Individual score for thematic areas
        'score_moi',                # Individual score for means of implementation
        'score_indicator_type',     # Individual score for indicator type
        'score_reporting'           # Individual score for reporting status
    ]
    
    # Add score component columns to preferred order
    preferred_order.extend(score_component_cols)
    
    # Add total score column to preferred order
    preferred_order.append('score')  # Total score
    
    # Create the final column order by including:
    # 1. Columns in the preferred order (if they exist in the dataframe)
    # 2. Any remaining columns that aren't in the preferred order
    final_columns = []
    
    # Add preferred columns that exist in the dataframe
    for col in preferred_order:
        if col in export_df.columns:
            final_columns.append(col)
    
    # Add any remaining columns not specified in the preferred order
    remaining_columns = [col for col in export_df.columns if col not in final_columns]
    final_columns.extend(remaining_columns)
    
    # Reorder the columns
    export_df = export_df[final_columns]
    
    return export_df

# --- NEW CODE: Function to prepare detailed indicator data for download ---
def prepare_indicator_details_for_download(df, indicator_name, name_col):
    """
    Prepares a complete dataset with all visible information for a selected indicator.
    Includes basic info, score components, and selection status.
    
    Args:
        df (pandas.DataFrame): The main dataframe
        indicator_name (str): The name of the selected indicator
        name_col (str): The name of the column containing indicator names
    
    Returns:
        pandas.DataFrame: A detailed dataframe for the specified indicator
    """
    # Get the selected indicator's row
    matching_rows = df[df[name_col] == indicator_name]
    
    if matching_rows.empty:
        return pd.DataFrame()  # Return empty dataframe if indicator not found
    
    # Check for unique identifiers to distinguish between duplicates
    if 'Indicator Type' in df.columns and len(matching_rows) > 1:
        # If we have multiple indicators with same name but different types, 
        # use the currently displayed one (which should be the first one found by .iloc[0])
        single_df = matching_rows.iloc[[0]].copy()
    else:
        # Just use the first match
        single_df = matching_rows.iloc[[0]].copy()
    
    # Create a detailed version with explanations
    detailed_df = single_df.copy()
    
    # Add score component columns if they don't exist
    if 'score_global_contextual' not in detailed_df.columns:
        detailed_df['score_global_contextual'] = detailed_df.apply(
            lambda row: calculate_score_global_contextual(row), axis=1
        )
        
    if 'score_thematic' not in detailed_df.columns:
        detailed_df['score_thematic'] = detailed_df.apply(
            lambda row: calculate_score_thematic(row), axis=1
        )
        
    if 'score_moi' not in detailed_df.columns:
        detailed_df['score_moi'] = detailed_df.apply(
            lambda row: calculate_score_moi(row), axis=1
        )
        
    if 'score_indicator_type' not in detailed_df.columns:
        detailed_df['score_indicator_type'] = detailed_df.apply(
            lambda row: calculate_score_indicator_type(row), axis=1
        )
        
    if 'score_reporting' not in detailed_df.columns:
        detailed_df['score_reporting'] = detailed_df.apply(
            lambda row: calculate_score_reporting(row), axis=1
        )
    
    # Add textual explanations for each score component
    row = single_df.iloc[0]
    
    # Global/Contextual Status explanation
    gc_status = str(row.get('Global/Contextual Status', '')).strip()
    if gc_status == 'Both':
        gc_explanation = "Both Global and Contextual (+1 point)"
    elif gc_status == 'Global':
        gc_explanation = "Global indicator only (+0.75 points)"
    else:
        gc_explanation = "Contextual indicator only (0 points)"
    detailed_df['global_contextual_explanation'] = gc_explanation
    
    # The rest of the function remains unchanged...
    # [...]
    
    # Reorganize columns for better readability in exported file
    return reorganize_columns_for_download(detailed_df)
# --- NEW CODE: Function to reorganize columns for details download ---
def reorganize_columns_for_download(df):
    """
    Reorganizes columns for indicator details download to provide a logical reading order.
    
    Args:
        df (pandas.DataFrame): The dataframe to reorganize
    
    Returns:
        pandas.DataFrame: A copy of the dataframe with reorganized columns
    """
    # Create a copy to avoid modifying the original
    download_df = df.copy()
    
    # Define column groups for organized layout
    basic_info_cols = [
        'Indicators',  # Indicator name
        'ID', 'Id', 'id', 'identifier',  # Possible ID column names
        'Description', 'description', 'Desc', 'desc',  # Possible description column names
    ]
    
    classification_cols = [
        'Thematic Area',
        'Indicator Type',
        'Already reported?',
        'Global/Contextual Status',
        'Means of Implementation'
    ]
    
    score_cols = [
        'score',  # Total score
        'score_global_contextual',
        'score_thematic',
        'score_moi',
        'score_indicator_type',
        'score_reporting'
    ]
    
    explanation_cols = [
        'global_contextual_explanation',
        'thematic_explanation',
        'moi_explanation',
        'indicator_type_explanation',
        'reporting_explanation'
    ]
    
    selection_cols = [
        'selected_global',
        'selected_contextual',
        'global_selection_status',
        'contextual_selection_status'
    ]
    
    # Combine all preferred column groups
    all_preferred_cols = (
        basic_info_cols + 
        classification_cols + 
        score_cols + 
        explanation_cols + 
        selection_cols
    )
    
    # Create the final column order
    final_columns = []
    
    # Add columns that exist in the dataframe in the preferred order
    for col in all_preferred_cols:
        if col in download_df.columns:
            final_columns.append(col)
    
    # Add any remaining columns not in the preferred lists
    remaining_columns = [col for col in download_df.columns if col not in final_columns]
    final_columns.extend(remaining_columns)
    
    # Return the dataframe with reorganized columns
    return download_df[final_columns]

# --- NEW CODE: Function to create a detailed download for all selected indicators ---
def prepare_all_selected_indicators_for_download(df):
    """
    Prepares a complete dataset with all information for all selected indicators.
    
    Args:
        df (pandas.DataFrame): The main dataframe
    
    Returns:
        pandas.DataFrame: A detailed dataframe for all selected indicators
    """
    # Get only the selected indicators (either global or contextual)
    selected_df = df[(df['selected_global'] == 1) | (df['selected_contextual'] == 1)].copy()
    
    if selected_df.empty:
        return pd.DataFrame()  # Return empty dataframe if no indicators selected
    
    # Add score component columns if they don't exist
    if 'score_global_contextual' not in selected_df.columns:
        selected_df['score_global_contextual'] = selected_df.apply(
            lambda row: calculate_score_global_contextual(row), axis=1
        )
        
    if 'score_thematic' not in selected_df.columns:
        selected_df['score_thematic'] = selected_df.apply(
            lambda row: calculate_score_thematic(row), axis=1
        )
        
    if 'score_moi' not in selected_df.columns:
        selected_df['score_moi'] = selected_df.apply(
            lambda row: calculate_score_moi(row), axis=1
        )
        
    if 'score_indicator_type' not in selected_df.columns:
        selected_df['score_indicator_type'] = selected_df.apply(
            lambda row: calculate_score_indicator_type(row), axis=1
        )
        
    if 'score_reporting' not in selected_df.columns:
        selected_df['score_reporting'] = selected_df.apply(
            lambda row: calculate_score_reporting(row), axis=1
        )
    
    # Add textual explanations for global/contextual selection status
    selected_df['global_selection_status'] = selected_df['selected_global'].apply(
        lambda x: "Selected as Global Indicator" if x == 1 else "Not Selected as Global"
    )
    
    selected_df['contextual_selection_status'] = selected_df['selected_contextual'].apply(
        lambda x: "Selected as Contextual Indicator" if x == 1 else "Not Selected as Contextual"
    )
    
    # Reorganize columns for better readability in exported file
    return reorganize_columns_for_export(selected_df)

# --- NEW CODE: Function to create download buttons for both CSV and Excel ---
def create_download_buttons(df, filename_prefix, button_label, help_text=""):
    """
    Creates a pair of download buttons for CSV and Excel formats without nesting columns.
    
    Args:
        df (pandas.DataFrame): The dataframe to download
        filename_prefix (str): Prefix for the filename (without extension)
        button_label (str): Label for the download button group
        help_text (str, optional): Help text to display with the buttons
    
    Returns:
        None: Renders buttons directly to the Streamlit UI
    """
    if df.empty:
        st.warning("No data available to download.")
        return
    
    # Create a container for the download buttons
    download_container = st.container()
    
    with download_container:
        st.write(f"**{button_label}**")
        
        if help_text:
            st.write(help_text)
        
        # Generate CSV download
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        # Generate Excel download
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        excel_buffer.seek(0)
        
        # Place buttons side by side with columns at root level of the container
        download_cols = st.columns(2)
        
        with download_cols[0]:
            st.download_button(
                "Download as CSV",
                data=csv_data,
                file_name=f"{filename_prefix}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with download_cols[1]:
            st.download_button(
                "Download as Excel",
                data=excel_buffer,
                file_name=f"{filename_prefix}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# --- NEW CODE: Function to add download buttons for pivot tables ---
def add_pivot_table_download(pivot_table, title, filename_prefix):
    """
    Adds download buttons for a pivot table.
    
    Args:
        pivot_table (pandas.DataFrame): The pivot table to download
        title (str): Title for the download section
        filename_prefix (str): Prefix for the download filename
        
    Returns:
        None: Renders buttons directly to the Streamlit UI
    """
    if pivot_table.empty:
        return
    
    # Reset index to convert multi-index pivot table to regular dataframe
    download_df = pivot_table.reset_index()
    
    with st.expander("Download this table", expanded=False):
        create_download_buttons(
            download_df,
            filename_prefix,
            title,
            "Download this table in your preferred format."
        )

# --- NEW CODE: Function to generate a complete indicator report with multiple sheets ---
def generate_complete_report(df):
    """
    Generates a complete report with multiple sheets in Excel format.
    
    Args:
        df (pandas.DataFrame): The main dataframe
        
    Returns:
        bytes: Excel file as bytes object
    """
    # Get selected indicators for global and contextual
    global_selected = df[df['selected_global'] == 1].copy()
    contextual_selected = df[df['selected_contextual'] == 1].copy()
    all_selected = df[(df['selected_global'] == 1) | (df['selected_contextual'] == 1)].copy()
    
    # Prepare data for each sheet
    detailed_all = prepare_all_selected_indicators_for_download(all_selected)
    
    # Create Excel file with multiple sheets
    excel_buffer = io.BytesIO()
    
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        # Sheet 1: All selected indicators with details
        detailed_all.to_excel(writer, sheet_name='All Selected Indicators', index=False)
        
        # Sheet 2: Global indicators only
        if not global_selected.empty:
            global_selected = reorganize_columns_for_export(global_selected)
            global_selected.to_excel(writer, sheet_name='Global Indicators', index=False)
            
            # Add pivot tables for global indicators if data exists
            if 'Thematic Area' in global_selected.columns and 'Indicator Type' in global_selected.columns:
                pivot_global = pd.pivot_table(
                    global_selected,
                    values='selected_global',
                    index=['Thematic Area'],
                    columns=['Indicator Type'],
                    aggfunc='count',
                    fill_value=0
                ).reset_index()
                
                pivot_global.to_excel(writer, sheet_name='Global by Theme & Type', index=False)
        
        # Sheet 3: Contextual indicators only
        if not contextual_selected.empty:
            contextual_selected = reorganize_columns_for_export(contextual_selected)
            contextual_selected.to_excel(writer, sheet_name='Contextual Indicators', index=False)
            
            # Add pivot tables for contextual indicators if data exists
            if 'Thematic Area' in contextual_selected.columns and 'Indicator Type' in contextual_selected.columns:
                pivot_contextual = pd.pivot_table(
                    contextual_selected,
                    values='selected_contextual',
                    index=['Thematic Area'],
                    columns=['Indicator Type'],
                    aggfunc='count',
                    fill_value=0
                ).reset_index()
                
                pivot_contextual.to_excel(writer, sheet_name='Contextual by Theme & Type', index=False)
                
    excel_buffer.seek(0)
    return excel_buffer

# --- NEW CODE: Function to add a comprehensive report download button ---
def add_comprehensive_report_button():
    """
    Adds a button to download a comprehensive multi-sheet report.
    """
    st.divider()
    st.subheader("Comprehensive Report")
    
    report_buffer = generate_complete_report(st.session_state.df)
    
    # Create columns directly instead of within another container
    report_cols = st.columns([2, 1])
    
    with report_cols[0]:
        st.write("Download a comprehensive report with multiple sheets containing all selected indicators and analysis.")
    
    with report_cols[1]:
        st.download_button(
            "Download Complete Report",
            data=report_buffer,
            file_name=f"GGA_indicators_report_{st.session_state.username}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

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
    
    # Create the main layout with two columns - KEEP these as the ONLY nested columns
    left_panel, right_panel = st.columns([3, 5], gap="large")
    
    with left_panel:
        # Use a container to group elements without nesting columns
        filter_container = st.container()
        
        with filter_container:
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
            
            # NEW CODE: Pagination controls
            total_records = len(filtered_df)
            
            # Items per page selector
            items_per_page_options = [10, 20, 50, 100, "All"]
            items_per_page = st.selectbox(
                "Records per page:",
                options=items_per_page_options,
                index=0  # Default to 10
            )
            
            # Initialize current page in session state if not exists
            if 'current_page' not in st.session_state:
                st.session_state.current_page = 0
            
            # Calculate pagination
            if items_per_page == "All":
                pages = 1
                current_page_items = filtered_df
            else:
                # Calculate total pages
                pages = max(1, (total_records + items_per_page - 1) // items_per_page)
                
                # Ensure current page is valid
                if st.session_state.current_page >= pages:
                    st.session_state.current_page = max(0, pages - 1)
                
                # Get items for current page
                start_idx = st.session_state.current_page * items_per_page
                end_idx = min(start_idx + items_per_page, total_records)
                current_page_items = filtered_df.iloc[start_idx:end_idx].copy()
            
            # Display pagination info
            st.write(f"Displaying {len(current_page_items)} of {total_records} filtered records (Page {st.session_state.current_page + 1} of {pages}):")
            
        # Use another container for the indicators list
        indicators_container = st.container()
        with indicators_container:
            st.markdown('<div class="scrollable-content">', unsafe_allow_html=True)
            
            if len(current_page_items) == 0:
                st.info("No records match your filter criteria. Try changing the filters.")
            
            # Display only the indicators for the current page
            for idx, row in current_page_items.iterrows():
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
                
                # Selection checkboxes - Use two separate markdown+checkbox pairs instead of columns
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Place checkboxes side by side using HTML/CSS styling
                st.markdown("""
                <style>
                .checkbox-container {
                    display: flex;
                    gap: 20px;
                    margin-bottom: 10px;
                }
                .checkbox-item {
                    flex: 1;
                }
                </style>
                <div class="checkbox-container">
                    <div class="checkbox-item">
                """, unsafe_allow_html=True)
                
                # Use individual checkboxes without nesting in columns
                global_selected = st.checkbox(
                    "Select this Indicator (GLOBAL)", 
                    value=bool(row.get('selected_global', 0)), 
                    key=f"global_{idx}"
                )
                
                st.markdown('</div><div class="checkbox-item">', unsafe_allow_html=True)
                
                contextual_selected = st.checkbox(
                    "Select this Indicator (CONTEXTUAL)", 
                    value=bool(row.get('selected_contextual', 0)), 
                    key=f"contextual_{idx}"
                )
                
                st.markdown('</div></div>', unsafe_allow_html=True)
                
                # Update selection status in dataframe
                st.session_state.df.at[idx, 'selected_global'] = 1 if global_selected else 0
                st.session_state.df.at[idx, 'selected_contextual'] = 1 if contextual_selected else 0
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Add pagination navigation buttons without nesting columns
        if pages > 1:
            # Create a container for the pagination controls
            pagination_container = st.container()
            with pagination_container:
                # HTML/CSS for pagination buttons
                st.markdown("""
                <style>
                .pagination-container {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin: 10px 0;
                }
                .pagination-button {
                    flex: 1;
                    text-align: center;
                }
                .pagination-info {
                    flex: 3;
                    text-align: center;
                }
                </style>
                <div class="pagination-container">
                    <div class="pagination-button">
                """, unsafe_allow_html=True)
                
                # Previous button
                prev_disabled = st.session_state.current_page <= 0
                if st.button("← Previous", disabled=prev_disabled, key="prev_page"):
                    st.session_state.current_page -= 1
                    st.rerun()
                
                st.markdown('</div><div class="pagination-info">', unsafe_allow_html=True)
                st.write(f"Page {st.session_state.current_page + 1} of {pages}")
                st.markdown('</div><div class="pagination-button">', unsafe_allow_html=True)
                
                # Next button
                next_disabled = st.session_state.current_page >= pages - 1
                if st.button("Next →", disabled=next_disabled, key="next_page"):
                    st.session_state.current_page += 1
                    st.rerun()
                
                st.markdown('</div></div>', unsafe_allow_html=True)
    
    with right_panel:
        summary_container = st.container()
        with summary_container:
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
                        
                        # Add download buttons for pivot table - without nesting
                        add_pivot_table_download_simple(
                            pivot_table,
                            "Download Thematic Area by Indicator Type",
                            f"global_indicators_by_theme_type_{st.session_state.username}"
                        )
                
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
                        
                        # Add download buttons for pivot table
                        add_pivot_table_download_simple(
                            pivot_table,
                            "Download Thematic Area by Indicator Type",
                            f"contextual_indicators_by_theme_type_{st.session_state.username}"
                        )
                
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
        
        # Export buttons - using direct placement without nesting columns
        st.divider()
        
        # Display buttons using HTML/CSS for layout
        st.markdown("""
        <style>
        .buttons-container {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }
        .button-item {
            flex: 1;
        }
        </style>
        <div class="buttons-container">
            <div class="button-item">
        """, unsafe_allow_html=True)
        
        # Save button
        if st.button("Save Selections", use_container_width=True, key="save_selections"):
            user_file = f'updated_{st.session_state.username}.xlsx'
            result = save_user_data(df=st.session_state.df, filename=user_file, drive_folder_id=DRIVE_FOLDER_ID)
            st.success(f"Selections saved! {result}")
        
        st.markdown('</div><div class="button-item">', unsafe_allow_html=True)
        
        # Clear button
        if st.button("Clear All Selections", use_container_width=True, key="clear_selections"):
            st.session_state.df['selected_global'] = 0
            st.session_state.df['selected_contextual'] = 0
            st.success("All selections cleared!")
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        # Download section
        selected_df = st.session_state.df[
            (st.session_state.df['selected_global'] == 1) | 
            (st.session_state.df['selected_contextual'] == 1)
        ].copy()
        
        # Create reorganized dataframe with proper column order
        export_df = reorganize_columns_for_export(selected_df)
        
        if len(selected_df) > 0:
            st.subheader(f"Download Selection ({len(selected_df)} indicators)")
            st.write("Download selected indicators in your preferred format.")
            
            # Generate CSV download
            csv_buffer = io.StringIO()
            export_df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            # Generate Excel download
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                export_df.to_excel(writer, index=False)
            excel_buffer.seek(0)
            
            # Use HTML/CSS for button layout
            st.markdown("""
            <style>
            .download-buttons {
                display: flex;
                gap: 10px;
                margin: 10px 0 20px 0;
            }
            .download-button {
                flex: 1;
            }
            </style>
            <div class="download-buttons">
                <div class="download-button">
            """, unsafe_allow_html=True)
            
            # CSV download button
            st.download_button(
                "Download as CSV",
                data=csv_data,
                file_name=f"selected_indicators_{st.session_state.username}.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_csv"
            )
            
            st.markdown('</div><div class="download-button">', unsafe_allow_html=True)
            
            # Excel download button
            st.download_button(
                "Download as Excel",
                data=excel_buffer,
                file_name=f"selected_indicators_{st.session_state.username}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="download_excel"
            )
            
            st.markdown('</div></div>', unsafe_allow_html=True)
        else:
            st.warning("No indicators selected yet. Select indicators before downloading.")
        
        # Add comprehensive report button
        add_comprehensive_report_button_simple()

    # --- FIXED FUNCTIONS TO AVOID NESTED COLUMNS ---

def add_pivot_table_download_simple(pivot_table, title, filename_prefix):
    """
    Adds download buttons for a pivot table without nesting columns.
    
    Args:
        pivot_table (pandas.DataFrame): The pivot table to download
        title (str): Title for the download section
        filename_prefix (str): Prefix for the download filename
    """
    if pivot_table.empty:
        return
    
    # Reset index to convert multi-index pivot table to regular dataframe
    download_df = pivot_table.reset_index()
    
    with st.expander("Download this table", expanded=False):
        st.write(f"**{title}**")
        st.write("Download this table in your preferred format.")
        
        # Generate CSV download
        csv_buffer = io.StringIO()
        download_df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        # Generate Excel download
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            download_df.to_excel(writer, index=False)
        excel_buffer.seek(0)
        
        # Use HTML/CSS for button layout
        st.markdown("""
        <style>
        .pivot-download-buttons {
            display: flex;
            gap: 10px;
            margin: 10px 0;
        }
        .pivot-download-button {
            flex: 1;
        }
        </style>
        <div class="pivot-download-buttons">
            <div class="pivot-download-button">
        """, unsafe_allow_html=True)
        
        # CSV download button
        st.download_button(
            "Download as CSV",
            data=csv_data,
            file_name=f"{filename_prefix}.csv",
            mime="text/csv",
            use_container_width=True,
            key=f"pivot_csv_{filename_prefix}"
        )
        
        st.markdown('</div><div class="pivot-download-button">', unsafe_allow_html=True)
        
        # Excel download button
        st.download_button(
            "Download as Excel",
            data=excel_buffer,
            file_name=f"{filename_prefix}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key=f"pivot_excel_{filename_prefix}"
        )
        
        st.markdown('</div></div>', unsafe_allow_html=True)

def add_comprehensive_report_button_simple():
    """
    Adds a button to download a comprehensive multi-sheet report without nested columns.
    """
    st.divider()
    st.subheader("Comprehensive Report")
    st.write("Download a comprehensive report with multiple sheets containing all selected indicators and analysis.")
    
    report_buffer = generate_complete_report(st.session_state.df)
    
    st.download_button(
        "Download Complete Report",
        data=report_buffer,
        file_name=f"GGA_indicators_report_{st.session_state.username}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        key="download_complete_report"
    )

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
            
            # Use HTML/CSS layout for buttons
            st.markdown("""
            <style>
            .confirm-buttons {
                display: flex;
                gap: 20px;
                margin: 15px 0;
            }
            .confirm-button {
                flex: 1;
            }
            </style>
            <div class="confirm-buttons">
                <div class="confirm-button">
            """, unsafe_allow_html=True)
            
            target = st.session_state.get('pending_target', current_index)
            
            # Save and Continue button
            if st.button("Save and Continue", key="save_continue", use_container_width=True):
                for col, val in st.session_state.get('pending_values', {}).items():
                    df.at[current_index, col] = 'X' if val is True else (' ' if val is False else val)
                
                user_file = f'updated_{st.session_state.username}.xlsx'
                save_user_data(df=df, filename=user_file, drive_folder_id=DRIVE_FOLDER_ID)
                st.session_state['unsaved_changes'] = False
                st.session_state['pending_values'] = {}
                st.session_state['show_confirm'] = False
                rerun_to_record(target)
            
            st.markdown('</div><div class="confirm-button">', unsafe_allow_html=True)
            
            # Ignore and Continue button
            if st.button("Ignore and Continue", key="ignore_continue", use_container_width=True):
                st.session_state['unsaved_changes'] = False
                st.session_state['pending_values'] = {}
                st.session_state['show_confirm'] = False
                rerun_to_record(target)
            
            st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Navigation controls - use HTML/CSS layout
    st.markdown("""
    <style>
    .navigation-controls {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    .nav-button {
        flex: 1;
    }
    .nav-info {
        flex: 4;
        text-align: center;
    }
    </style>
    <div class="navigation-controls">
        <div class="nav-button">
    """, unsafe_allow_html=True)
    
    # Previous button
    prev_disabled = current_index <= 0
    if st.button("← Previous", disabled=prev_disabled, key="tag_prev"):
        if st.session_state.get('unsaved_changes', False):
            confirm_navigation(current_index - 1)
        else:
            rerun_to_record(current_index - 1)
    
    st.markdown('</div><div class="nav-info">', unsafe_allow_html=True)
    st.markdown(f"### Record {current_index + 1} of {total_records}")
    st.markdown('</div><div class="nav-button">', unsafe_allow_html=True)
    
    # Next button
    next_disabled = current_index >= total_records - 1
    if st.button("Next →", disabled=next_disabled, key="tag_next"):
        if st.session_state.get('unsaved_changes', False):
            confirm_navigation(current_index + 1)
        else:
            rerun_to_record(current_index + 1)
    
    st.markdown('</div><div class="nav-button">', unsafe_allow_html=True)
    
    # First button
    if st.button("Go to First", key="tag_first"):
        if st.session_state.get('unsaved_changes', False):
            confirm_navigation(0)
        else:
            rerun_to_record(0)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
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
        
        # Create thematic area checkboxes in a grid layout with CSS
        st.markdown("""
        <style>
        .thematic-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }
        .thematic-item {
            padding: 5px;
        }
        </style>
        <div class="thematic-grid">
        """, unsafe_allow_html=True)
        
        selected_thematic_areas = []
        
        # Create checkboxes without nesting columns
        for idx, area in enumerate(available_thematic_areas):
            st.markdown(f'<div class="thematic-item">', unsafe_allow_html=True)
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
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
                    
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
        if st.button(f"Save Record {i+1}", use_container_width=True, key="save_record"):
            for col, val in updated_values.items():
                df.at[i, col] = val
            
            # Recalculate the score after updates
            df.at[i, 'score'] = calculate_indicator_score(df.iloc[i])
            
            user_file = f'updated_{st.session_state.username}.xlsx'
            result = save_user_data(df=df, filename=user_file, drive_folder_id=DRIVE_FOLDER_ID)
            st.session_state['unsaved_changes'] = False
            st.session_state['pending_values'] = {}
            st.success(f"Record {i+1} saved successfully! {result}")
            
        # Add download button for current indicator without nesting columns
        st.divider()
        st.markdown("##### Download Current Indicator Data")
        
        # Prepare detailed data for the current indicator
        if name_col:
            single_df = prepare_indicator_details_for_download(df, indicator_name, name_col)
            
            # Generate files
            csv_buffer = io.StringIO()
            single_df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                single_df.to_excel(writer, index=False)
            excel_buffer.seek(0)
            
            # Use HTML/CSS for button layout
            st.markdown("""
            <style>
            .tag-download-buttons {
                display: flex;
                gap: 10px;
                margin: 10px 0;
            }
            .tag-download-button {
                flex: 1;
            }
            </style>
            <div class="tag-download-buttons">
                <div class="tag-download-button">
            """, unsafe_allow_html=True)
            
            # CSV button
            st.download_button(
                "Download as CSV",
                data=csv_data,
                file_name=f"{indicator_name.replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="tag_indicator_csv"
            )
            
            st.markdown('</div><div class="tag-download-button">', unsafe_allow_html=True)
            
            # Excel button
            st.download_button(
                "Download as Excel",
                data=excel_buffer,
                file_name=f"{indicator_name.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="tag_indicator_excel"
            )
            
            st.markdown('</div></div>', unsafe_allow_html=True)

        # --- VIEW INDICATOR DETAILS TAB ---
# --- FIX FOR VIEW_INDICATOR_DETAILS_TAB ---
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
    
    # Add sort options and download button - avoid nesting columns
    options_container = st.container()
    with options_container:
        st.markdown("""
          <style>
        .options-container {
            display: flex;
            gap: 20px;
            align-items: flex-start;
            margin-bottom: 20px;
        }
        .sort-options {
            flex: 3;
        }
        .download-options {
            flex: 1;
            text-align: right;
        }
        </style>
        <div class="options-container">
            <div class="sort-options">
        """, unsafe_allow_html=True)
        
        # Sort options
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
        
        st.markdown('</div><div class="download-options">', unsafe_allow_html=True)
        
        # Create reorganized dataframe with all details for selected indicators
        export_df = prepare_all_selected_indicators_for_download(selected_df)
        
        if not export_df.empty:
            st.write(f"**Download ({len(selected_df)})**")
            
            # Generate CSV download
            csv_buffer = io.StringIO()
            export_df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            # Generate Excel download
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                export_df.to_excel(writer, index=False)
            excel_buffer.seek(0)
            
            # Download buttons
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "CSV",
                    data=csv_data,
                    file_name=f"selected_indicators_{st.session_state.username}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="details_csv"
                )
            
            with col2:
                st.download_button(
                    "Excel",
                    data=excel_buffer,
                    file_name=f"selected_indicators_{st.session_state.username}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="details_excel"
                )
        
        st.markdown('</div></div>', unsafe_allow_html=True)

    # Create a dropdown to select an indicator from the SELECTED ones only
    indicators = selected_df[name_col].tolist()
    st.write(f"**Select an indicator to view details:** (Showing {len(indicators)} selected indicators)")
    selected_indicator = st.selectbox("Select an indicator to view details:", indicators, key="details_indicator_selector")
    
    # Get the selected indicator's row
    selected_row = df[df[name_col] == selected_indicator].iloc[0]
    idx = df[df[name_col] == selected_indicator].index[0]
    
    st.markdown("### Indicator Details")
    
    # Use container instead of columns to avoid nesting
    details_container = st.container()
    with details_container:
        st.markdown("""
        <style>
        .details-container {
            display: flex;
            gap: 30px;
            margin-bottom: 20px;
        }
        .details-left {
            flex: 1;
        }
        .details-right {
            flex: 2;
        }
        </style>
        <div class="details-container">
            <div class="details-left">
        """, unsafe_allow_html=True)
        
        # Left column content
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
        
        st.markdown('</div><div class="details-right">', unsafe_allow_html=True)
        
        # Right column content
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
        
        st.markdown('</div></div>', unsafe_allow_html=True)

    # Additional information or actions
    st.divider()
    st.markdown("### Actions")

    # Create buttons using HTML/CSS layout instead of columns
    st.markdown("""
   <style>
        .centered-button-container {
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }
        .fixed-width-button {
            width: 30px; /* Set a fixed width */
        }
        </style>
        <div class="centered-button-container">
        """, unsafe_allow_html=True)
    
    # Edit button
    if st.button("Edit How this Indicator was Tagged", key="edit_indicator", use_container_width=True):
        # Find the index in the dataframe
        idx = df[df[name_col] == selected_indicator].index[0]
        st.session_state.current_index = idx
        st.session_state.current_tab = "Tag"
        st.rerun()
    
    st.markdown('</div><div class="action-button">', unsafe_allow_html=True)
    
    # Create download buttons for the current indicator
    single_df = prepare_indicator_details_for_download(df, selected_indicator, name_col)
    
    # Generate files
    csv_buffer = io.StringIO()
    single_df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        single_df.to_excel(writer, index=False)
    excel_buffer.seek(0)
    
    # Use buttons instead of create_download_buttons to avoid nested columns
    download_container = st.container()
    with download_container:
        st.markdown("**Download Details for This Indicator**")
        
        # Use a container with CSS layout for download buttons
        st.markdown("""
        <style>
        .indicator-download-buttons {
            display: flex;
            gap: 10px;
            margin: 10px 0;
        }
        .indicator-download-button {
            flex: 1;
        }
        </style>
        <div class="indicator-download-buttons">
            <div class="indicator-download-button">
        """, unsafe_allow_html=True)
        
        # CSV button
        st.download_button(
            "Download as CSV",
            data=csv_data,
            file_name=f"{selected_indicator.replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="single_indicator_csv"
        )
        
        st.markdown('</div><div class="indicator-download-button">', unsafe_allow_html=True)
        
        # Excel button
        st.download_button(
            "Download as Excel",
            data=excel_buffer,
            file_name=f"{selected_indicator.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="single_indicator_excel"
        )
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Add comprehensive report button
    add_comprehensive_report_button_simple()

# --- EXECUTION POINT ---
if __name__ == '__main__':
    main()