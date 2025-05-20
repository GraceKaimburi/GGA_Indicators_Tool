# GGA Indicators Selection System

A comprehensive system for selecting and analyzing Global Goal on Adaptation (GGA) indicators across multiple thematic areas: water, health, biodiversity, food, infrastructure, poverty, and cultural heritage.

## Features

- **Multi-Thematic Indicator Selection**: Select indicators across 7 different thematic areas
- **Interlinkage Analysis**: Prioritize indicators that link multiple thematic areas
- **Analytics Dashboard**: Visualize selection coverage and distribution
- **Google Drive Integration**: Save and load data from Google Drive (optional)
- **Dark Theme UI**: Optimized for readability and modern look
- **Multi-User Support**: Different logins with personalized selections

## Installation

1. Clone this repository
2. Install required packages:
```
pip install -r requirements.txt
```
3. Set up your environment variables by copying and modifying the template:
```
cp .env.template .env
```
4. Prepare your indicators database in Excel format (see format section below)

## Running the Application

```
streamlit run app.py
```

## Data Format

Your Excel indicators database should have the following columns:

- `Indicator`: Name of the indicator
- `ID`: Unique identifier (optional)
- `Description`: Brief description (optional)
- `Water`, `Health`, `Biodiversity`, `Food & Agriculture`, `Infrastructure`, `Poverty & Livelihoods`, `Cultural Heritage`: Mark with 'X' if the indicator is relevant to each thematic area
- `indicator_type`: Type of indicator (Input, Process, Output, Outcome)
- `reporting_status`: Current reporting framework (SDG, Sendai, etc.)

## Google Drive Integration

For Google Drive integration:

1. Create a Google Cloud project
2. Enable the Google Drive API
3. Create a service account and download credentials as `credentials.json`
4. Place this file in the same directory as the application
5. Share your Google Drive folder with the service account email

## User Management

Default credentials:
- Admin: username `admin`, password `admin123`
- User: username `user1`, password `pass123`

Modify these in the `.env` file for production use.

## Customization

You can customize the application by modifying these variables in `app.py`:

- `THEMATIC_AREAS`: List of thematic areas
- `WEIGHTS`: Weights for different scoring components
- `MAX_INDICATORS`: Maximum number of indicators that can be selected

## License

This project is licensed under the AGNES Business License.

© Grace Kaimburi
