# YouTube Video Analytics Dashboard

## Description
This Streamlit application provides an interactive dashboard for analyzing YouTube video performance data, specifically for the MrBeast channel. It offers various visualizations to help understand the relationships between video attributes and performance metrics.

## Features
- Interactive selection of different analytics views
- Visualizations include:
  - Top N videos by view count
  - Likes vs. Views scatter plot
  - Video Length vs. Views scatter plot (for videos under 100 minutes)
  - Average Views by Day of Week
  - Average Likes by Day of Week
- User-friendly interface with Streamlit
- Custom color palette for improved readability
- Formatted axis labels for large numbers (K for thousands, M for millions)

## Installation

1. Clone this repository:

2. Install the required packages:
pip install -r requirements.txt
Copy
## Usage

1. Ensure you have the dataset file `mrbeast_channel.csv` in the `dataset` folder.

2. Run the Streamlit app:
streamlit run app.py
Copy
3. Open your web browser and go to the URL provided by Streamlit (typically `http://localhost:8501`).

4. Use the sidebar to select different metrics and interact with the visualizations.

## Data

The dashboard uses a CSV file named `mrbeast_channel.csv`, which should be placed in a `dataset` folder. The file is expected to contain the following columns:
- video_id
- channelTitle
- title
- description
- tags
- publishedAt
- viewCount
- likeCount
- commentCount
- duration
- definition
- caption
- day_of_week

## Dependencies
- Python 3.11.9
- Streamlit
- Pandas
- Matplotlib
- Seaborn
