# YouTube Analytics ETL Pipeline

A data pipeline project that extracts data from YouTube API, processes it, and visualizes channel statistics using Apache Airflow and Streamlit.

## Project Overview

This project implements an ETL (Extract, Transform, Load) pipeline to process YouTube channel data. The pipeline is orchestrated using Apache Airflow and consists of three main stages:
1. Data extraction from YouTube API
2. Data transformation
3. Loading processed data into a designated folder

Additionally, the project includes a Streamlit dashboard for visualizing channel statistics.

## Setup Instructions

1. First, ensure you have Python 3.10.12 installed:
```bash
python3 --version
```


2. Create and navigate to your project directory:
```bash
mkdir youtube-analytics-pipeline
cd youtube-analytics-pipeline
```

3. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

4. Follow the instructions in the quickstart of Apache Airflow homepage:

https://airflow.apache.org/docs/apache-airflow/stable/start.html

the airflow version used for developed was the 2.10.2



5. Create a requirements.txt file with the following dependencies:
```txt
google-api-python-client==2.148.0
python-dotenv==1.0.1
pandas==2.2.3
isodate==0.7.0
seaborn==0.13.2
matplotlib==3.9.2
streamlit==1.39.0
```

6. Install the requirements:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in your project root:
```bash
touch .env
```

2. Add your credentials to the `.env` file:
```env
yt_api_key=your_api_key
```

3. Initialize Airflow:
```bash
# Set the Airflow home directory
export AIRFLOW_HOME=$(pwd)

# Initialize the Airflow database
airflow db init

# Create an admin user
airflow users create \
    --username admin \
    --firstname YourName \
    --lastname YourLastName \
    --role Admin \
    --email your@email.com
```

## Running the Pipeline

1. Start the Airflow webserver (in a terminal):
```bash
airflow webserver --port 8080
```

2. Open a new terminal, activate the virtual environment, and start the scheduler:
```bash
source venv/bin/activate
airflow scheduler
```

3. Access the Airflow UI at `http://localhost:8080` and log in with your admin credentials.

## Running the Streamlit Dashboard

1. In a new terminal, activate the virtual environment and run:
```bash
cd streamlit
streamlit run app.py
```

2. The dashboard will be available at `http://localhost:8501`

## Pipeline Details

### Extract Stage
- Connects to YouTube Data API
- Retrieves channel statistics and video data
- Saves raw data to the raw_data directory

### Transform Stage
- Cleans and processes the raw data
- Performs necessary calculations and aggregations
- Prepares data for analysis

### Load Stage
- Saves processed data to the dataset directory
- Organizes data for efficient access by the Streamlit dashboard

## Dashboard Features

- Channel overview statistics
- Video performance metrics

## Dependencies Explanation

- `google-api-python-client`: Interface with YouTube Data API
- `python-dotenv`: Environment variable management
- `pandas`: Data manipulation and analysis
- `isodate`: ISO 8601 date/time parser
- `seaborn` & `matplotlib`: Data visualization
- `streamlit`: Interactive dashboard creation

