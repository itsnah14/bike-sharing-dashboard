# 🚲 Bike Sharing Analytics Dashboard

🌐 **[Click here to view the live dashboard](https://bike-sharing-dashboard-nahdah.streamlit.app/)**
<br>
<br>
## 📌 Project Overview
This repository contains a comprehensive data analytics project and an interactive dashboard built with **Streamlit**. The project aims to analyze and visualize the operational patterns, user behaviors, and environmental factors influencing a bike-sharing system. 

## ✨ Key Features
The dashboard is highly interactive and divided into three main analytical pages:

1. **Daily Overview & Key Factors**
   - Displays macro-level metrics (Total Rentals, Average Daily Rentals, Busiest Day).
   - Visualizes overall daily trends, weekly performance, and monthly seasonality to identify peak and low periods.

2. **24-Hour Pattern Analysis**
   - Explores micro-level trends focusing on hourly behaviors.
   - Highlights the absolute busiest and quietest hours.
   - Compares user composition (Registered vs. Casual) across different time segments (Morning, Afternoon, Evening, Night).

3. **Rental Factors by Time Period**
   - An advanced interactive analysis page.
   - Utilizes dynamic grid layouts and multiple selections to compare how environmental factors (Temperature, Humidity, Windspeed, Weather Situation, etc.) impact rental demand across different times of the day.

## 📂 Project Structure
```text
📦 bike-sharing-analytics
 ┣ 📂 raw data/              # Original, uncleaned dataset (day.csv, hour.csv)
 ┣ 📂 .streamlit/            # Streamlit configuration for custom UI themes
 ┣ 📜 dashboard_revisi.py    # Main Streamlit application script
 ┣ 📜 main_data_day.csv      # Cleaned daily data used for the dashboard
 ┣ 📜 main_data_hour.csv     # Cleaned hourly data used for the dashboard
 ┣ 📜 notebook_revisi.ipynb  # Data analysis script
 ┣ 📜 requirements.txt       # List of Python dependencies
 ┗ 📜 README.md              # Project documentation
```

## 🛠️ How to Run Locally
If you want to run this dashboard on your local machine, follow these steps:

1. **Clone this repository:**
   ```bash
   git clone https://github.com/itsnah14/bike-sharing-dashboard.git
   ```
2. **Navigate to the project directory:**
   ```bash
   cd bike-sharing-dashboard
   ```
3. **Create and activate a virtual environment:**
   ```bash
   # Windows
   py -m venv venv
   .\venv\Scripts\activate

   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
   
4. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Run the Streamlit app:**
   ```bash
   streamlit run dashboard_revisi.py
   ```

## 👨‍💻 Author
**Nahdah Tsamarah Hasan**
- Feel free to connect and provide feedback!
