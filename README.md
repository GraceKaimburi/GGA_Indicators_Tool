 Combined Water Indicators Management System

This application combines the functionalities of indicator tagging and selection for water indicators management. It provides a unified interface for managing water indicators with features for both tagging and selection phases.

 Features

- User Authentication: Multi-user system with different access levels
- Selection Interface: Filter and select indicators as global or contextual
- Tagging Interface: Tag indicators with GGA targets, water components, and other attributes
- Detailed View: Examine all details and tags for each indicator
- Admin Panel: Download user files, generate indicator templates, and manage users
- Google Drive Integration: Save and load files from Google Drive

Setup
A. Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/water-indicators.git
cd water-indicators
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate   On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

B. Configuration

1. Create a `.env` file based on the template:
```bash
cp .env.template .env
```

2. Edit the `.env` file with your user credentials

3. Set up Google Drive API (optional):
   - Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Google Drive API
   - Create a service account and download the credentials JSON file
   - Save the JSON file as `credentials.json` in the project directory

 3. Data Preparation

1. Ensure your indicator data is in an Excel file named `data_to_update_filled.xlsx`
2. If you want to generate individual indicator sheets, create a template file named `Indicator_sheet.xlsx`

 Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Access the application in your web browser (typically http://localhost:8501)

3. Log in with your credentials

4. Use the application:
   - Select Indicators: Filter indicators by water component or indicator type, then select them as global or contextual
   - Tag Indicators: Navigate through indicators to tag them with relevant attributes
   - View Indicator Details: Get detailed information about each indicator and its tags

 Administrator Functions

If logged in as an admin, you can:

1. Download all user files as a ZIP archive
2. Generate individual Excel files for each selected indicator
3. View information about user files
4. View Drive files (if Drive integration is enabled)

 Folder Structure

```
water-indicators/
├── app.py                Main application file
├── requirements.txt      Python dependencies
├── .env                  Environment variables (user credentials)
├── .env.template         Template for environment variables
├── credentials.json      Google Drive API credentials (optional)
├── data_to_update_filled.xlsx   Main indicator data file
├── Indicator_sheet.xlsx  Template for individual indicator files
└── generated_indicators/   Generated individual indicator files
```

 Customization

- Modify the column mappings in the code to match your Excel file structure
- Add or remove GGA targets and MOI fields as needed
- Customize the UI by editing the CSS in the `app.py` file

 Troubleshooting

- If you encounter issues with Google Drive integration, ensure your credentials file is correctly set up
- If your Excel file has different column names, update the column mapping functions in the code