from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import os
import logging
from datetime import datetime, timezone
import pandas as pd
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import shutil
import isodate
from typing import Optional


load_dotenv() 

def collect_youtube_channel_data(channel_id: str, output_path: str) -> None:
    """
    Collects all video data from a YouTube channel and saves to specified path.
    
    Parameters:
    channel_id (str): The YouTube channel ID to collect data from
    output_path (str): Full path where the output CSV should be saved
    
    Raises:
    ValueError: If API key is missing or invalid
    HttpError: If YouTube API request fails
    Exception: For other unexpected errors
    """
    try:
        # Setup logging
        logger = logging.getLogger(__name__)
        
        # Get API key from environment variable
        api_key = os.getenv('yt_api_key')
        if not api_key:
            raise ValueError("YouTube API key not found in environment variables")
        
        # Setup YouTube API
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=api_key,
            cache_discovery=False  # Recommended for production
        )
        
        # Get playlist ID (for uploads playlist)
        playlist_id = f'UU{channel_id[2:]}' if channel_id.startswith('UC') else channel_id
        
        # Get all video IDs
        video_ids = []
        next_page_token = None
        
        while True:
            try:
                request = youtube.playlistItems().list(
                    part='contentDetails',
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                )
                response = request.execute()
                
                video_ids.extend([
                    item['contentDetails']['videoId'] 
                    for item in response.get('items', [])
                ])
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                    
            except HttpError as e:
                logger.error(f"Error fetching playlist items: {str(e)}")
                raise
        
        if not video_ids:
            logger.warning(f"No videos found for channel {channel_id}")
            return
        
        # Get video details
        all_video_info = []
        stats_to_keep = {
            'snippet': ['channelTitle', 'title', 'description', 'tags', 'publishedAt'],
            'statistics': ['viewCount', 'likeCount', 'favouriteCount', 'commentCount'],
            'contentDetails': ['duration', 'definition', 'caption']
        }
        
        # Process videos in batches of 50
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i+50]
            try:
                request = youtube.videos().list(
                    part="snippet,contentDetails,statistics",
                    id=','.join(batch_ids)
                )
                response = request.execute()
                
                for video in response.get('items', []):
                    video_info = {'video_id': video['id']}
                    
                    for k, fields in stats_to_keep.items():
                        for field in fields:
                            try:
                                video_info[field] = video[k][field]
                            except KeyError:
                                video_info[field] = None
                    
                    # Add timestamp for when the data was collected
                    video_info['data_collected_at'] = datetime.utcnow().isoformat()
                    all_video_info.append(video_info)
                    
            except HttpError as e:
                logger.error(f"Error fetching video details for batch: {str(e)}")
                continue  # Continue with next batch instead of failing completely
        
        if not all_video_info:
            raise ValueError(f"No video data could be collected for channel {channel_id}")
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(all_video_info)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        logger.info(f"Successfully saved {len(df)} video records to {output_path}")
        
    except Exception as e:
        logger.error(f"Error in collect_youtube_channel_data: {str(e)}")
        raise

def transform_youtube_data(input_path: str, output_path: str) -> None:
    """
    Transforms YouTube data from raw CSV file and saves the result to a new location.
    
    Parameters:
    input_path (str): Path to the input CSV file
    output_path (str): Path where the transformed CSV should be saved
    
    Raises:
    FileNotFoundError: If input file doesn't exist
    Exception: For other unexpected errors
    """
    try:
        # Setup logging
        logger = logging.getLogger(__name__)
        
        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Read the input CSV file
        logger.info(f"Reading data from {input_path}")
        df = pd.read_csv(input_path)
        
        # Create a copy for transformations
        df_transformed = df.copy()
        
        # Step 1: Convert columns to numeric types
        numeric_columns = ['viewCount', 'likeCount', 'commentCount']
        for col in numeric_columns:
            if col in df_transformed.columns:
                df_transformed[col] = pd.to_numeric(df_transformed[col], errors='coerce')
                logger.info(f"Converted {col} to numeric type")
        
        # Step 2: Drop the 'favouriteCount' column if it exists
        if 'favouriteCount' in df_transformed.columns:
            df_transformed.drop(columns=['favouriteCount'], inplace=True)
            logger.info("Dropped favouriteCount column")
        
        # Step 3: Convert 'publishedAt' to datetime format
        try:
            df_transformed['publishedAt'] = pd.to_datetime(df_transformed['publishedAt'])
            logger.info("Converted publishedAt to datetime format")
        except Exception as e:
            logger.warning(f"Error converting publishedAt to datetime: {str(e)}")
        
        # Step 4: Extract the day of the week from 'publishedAt'
        try:
            df_transformed['day_of_week'] = df_transformed['publishedAt'].dt.day_name()
            logger.info("Added day_of_week column")
        except Exception as e:
            logger.warning(f"Error creating day_of_week column: {str(e)}")
        
        # Step 5: Convert 'duration' to total seconds
        def safe_duration_convert(x: Optional[str]) -> Optional[float]:
            try:
                if pd.isna(x) or x == '':
                    return None
                return isodate.parse_duration(x).total_seconds()
            except Exception:
                return None
        
        df_transformed['duration'] = df_transformed['duration'].apply(safe_duration_convert)
        logger.info("Converted duration to seconds")
        
        # Step 6: Fill NaN values for specific columns (fixed warning)
        text_columns = ['tags', 'description']
        for col in text_columns:
            if col in df_transformed.columns:
                # Fixed the chained assignment warning by using loc
                df_transformed.loc[df_transformed[col].isna(), col] = ''
                logger.info(f"Filled NaN values in {col}")
        
        # Add transformation timestamp (fixed deprecation warning)
        df_transformed['transformed_at'] = datetime.now(timezone.utc).isoformat()
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save transformed data
        df_transformed.to_csv(output_path, index=False)
        logger.info(f"Successfully saved transformed data to {output_path}")
        
    except Exception as e:
        logger.error(f"Error in transform_youtube_data: {str(e)}")
        raise

def load_youtube_data(input_path: str, output_folder: str, channel_name: str) -> None:
    """
    Loads transformed YouTube data into the final dataset folder.
    The output folder will be cleaned before loading new data.
    
    Parameters:
    input_path (str): Path to the transformed CSV file
    output_folder (str): Path to the destination folder
    channel_name (str): Name of the channel (used in filename)
    
    Raises:
    FileNotFoundError: If input file doesn't exist
    Exception: For other unexpected errors
    """
    try:
        # Setup logging
        logger = logging.getLogger(__name__)
        
        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Read the transformed data
        logger.info(f"Reading transformed data from {input_path}")
        df = pd.read_csv(input_path)
        
        # Clean and recreate the output folder
        if os.path.exists(output_folder):
            logger.info(f"Cleaning existing output folder: {output_folder}")
            shutil.rmtree(output_folder)
        
        logger.info(f"Creating output folder: {output_folder}")
        os.makedirs(output_folder)
        
        # Create the output path
        output_path = os.path.join(output_folder, f"{channel_name}_channel.csv")
        
        # Save the data
        df.to_csv(output_path, index=False)
        logger.info(f"Successfully saved data to {output_path}")
        
        # Log some basic statistics
        logger.info(f"Loaded {len(df)} records with {len(df.columns)} columns")
        
    except Exception as e:
        logger.error(f"Error in load_youtube_data: {str(e)}")
        raise



# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 10, 6),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email_on_retry': False,
    'depends_on_past': False,
}

# Define the DAG
with DAG(
    'etl_with_streamlit_dashboard',
    default_args=default_args,
    schedule_interval='@weekly',
    catchup=False,
    description='ETL pipeline with Streamlit dashboard',
    tags=['etl', 'streamlit']
) as dag:

    # Task to run the extraction script
    extract_task = PythonOperator(
    task_id='extract_youtube_data',
    python_callable=collect_youtube_channel_data,
    op_kwargs={
            'channel_id': 'UC295-Dw_tDNtZXFeAPAW6Aw',
            'output_path': 'raw_data/youtube_videos.csv'
        }
    )

    # Task to run the transformation script
    trans_task = PythonOperator(
        task_id='transform_youtube_data',
        python_callable=transform_youtube_data,
        op_kwargs={
            'input_path': 'raw_data/youtube_videos.csv',
            'output_path': 'transformed_data/youtube_videos_transformed.csv'
        }
    )

     # Task to run the loading script
    loading_task = PythonOperator(
        task_id='loading_youtube_data',
        python_callable=load_youtube_data,
        op_kwargs={
            'input_path': 'transformed_data/youtube_videos_transformed.csv',
            'output_folder': 'dataset',
            'channel_name': '5mins_crafts'
        }
    )

    # Define the task dependencies
    extract_task >> trans_task >> loading_task