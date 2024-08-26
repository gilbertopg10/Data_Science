Job Data Dashboard
This Streamlit application creates an interactive dashboard to explore a dataset of job postings. It displays job locations on a map, analyzes salary distribution, and allows you to search for specific jobs.

Getting Started

Prerequisites:
Python 3.8 or later
Streamlit (pip install streamlit)
Pandas (pip install pandas)
Plotly (pip install plotly-express)
Folium (pip install folium)
Geopy (pip install geopy)
Streamlit-folium (pip install streamlit-folium)
Running the app:
Clone or download this repository.
Ensure you have the required libraries installed (see prerequisites).
Navigate to the project directory in your terminal.
Run the application using streamlit run app.py (replace app.py with your script name if different).
Usage

The dashboard opens in your web browser.
Select a view from the sidebar:
Location Map: Shows the geographical distribution of jobs.
Salary Distribution: Analyzes the overall salary range and displays a histogram.
Salary Distribution by Profile: Compares salaries across different job profiles.
Job Search: Lets you search for jobs by title or company name.
Interact with the elements based on the chosen view (e.g., zoom on the map, explore box plots in the salary distribution).
Features

Interactive map visualization of job locations.
Detailed salary distribution analysis with histogram and metrics.
Comparison of salaries by job profile.
Searchable interface to find specific jobs based on title or company.