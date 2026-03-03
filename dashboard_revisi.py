import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import base64
from io import BytesIO

# ==========================================
# 1. SETUP & KONFIGURASI WARNA
# ==========================================
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")

COLORS = {
    'sidebar': '#1665a0',       
    'main_bg': '#f6fafd',       
    'white': '#ffffff',         
    'card1': '#53cef4',         
    'card2': '#1668a3',         
    'card3': '#1aa9e2',         
    'text_main': '#333333',     
    'warning_bg': 'rgba(255, 75, 75, 0.15)', 
    'warning_text': '#d32f2f'   
}

# --- INJEKSI CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Nunito', sans-serif !important;
    }}

    [data-testid="stAppViewContainer"] {{
        background-color: {COLORS['main_bg']} !important;
    }}
    
    [data-testid="stSidebar"] > div:first-child {{
        background-color: {COLORS['sidebar']} !important;
        box-shadow: 4px 0 15px rgba(0,0,0,0.1);
    }}
    
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] label {{
        color: {COLORS['white']} !important;
    }}

    div[role="radiogroup"] > label > div:first-of-type {{
        display: none !important; 
    }}

    div[role="radiogroup"] > label {{
        background-color: transparent !important;
        padding: 12px 15px;
        border-radius: 12px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 0px solid rgba(255,255,255,0.3);
    }}
    
    div[role="radiogroup"] > label,
    div[role="radiogroup"] > label p,
    div[role="radiogroup"] > label span,
    div[role="radiogroup"] > label div {{
        color: {COLORS['white']} !important; 
        margin: 0;
        font-weight: 600;
    }}

    div[role="radiogroup"] > label:has(input:checked) {{
        background-color: {COLORS['white']} !important; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
        border: none !important;
    }}
    
    div[role="radiogroup"] > label:has(input:checked),
    div[role="radiogroup"] > label:has(input:checked) p,
    div[role="radiogroup"] > label:has(input:checked) span,
    div[role="radiogroup"] > label:has(input:checked) div {{
        color: {COLORS['sidebar']} !important; 
        font-weight: 800 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Fungsi Render Plot ke HTML Base64
def get_base64_of_figure(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', facecolor='#ffffff', transparent=False)
    return base64.b64encode(buf.getbuffer()).decode("ascii")

# ==========================================
# 2. LOAD DATA
# ==========================================
@st.cache_data
def load_data():
    df_day = pd.read_csv("main_data_day.csv")
    df_hour = pd.read_csv("main_data_hour.csv")
    
    df_day['dteday'] = pd.to_datetime(df_day['dteday'])
    df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])
    
    time_mapping = {
        'Pagi (05:00 - 11:59)': 'Morning (05:00 - 11:59)',
        'Siang (12:00 - 14:59)': 'Afternoon (12:00 - 14:59)',
        'Sore (15:00 - 17:59)': 'Evening (15:00 - 17:59)',
        'Malam (18:00 - 04:59)': 'Night (18:00 - 04:59)'
    }
    if 'time_segment' in df_hour.columns:
        df_hour['time_segment'] = df_hour['time_segment'].map(time_mapping).fillna(df_hour['time_segment'])
        
    return df_day, df_hour

df_day, df_hour = load_data()

# ==========================================
# 3. SIDEBAR & GLOBAL FILTER
# ==========================================
st.sidebar.title("🚲 Bike Analytics")

page = st.sidebar.radio(
    "Pages", 
    ["1. Daily Overview & Key Factors", 
     "2. 24-Hour Pattern Analysis", 
     "3. Rental Factors by Time Period"]
)

st.sidebar.markdown("<hr style='border-top: 1px solid rgba(255,255,255,0.4); margin-top: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)

min_date = df_day['dteday'].min().date()
max_date = df_day['dteday'].max().date()

st.sidebar.markdown("**Date Filter**")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date, format="DD/MM/YYYY")
with col2:
    end_date = st.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date, format="DD/MM/YYYY")

if start_date > end_date:
    st.sidebar.error("Error: End Date cannot be earlier than Start Date.")
    end_date = start_date

main_df_day = df_day[(df_day['dteday'].dt.date >= start_date) & (df_day['dteday'].dt.date <= end_date)]
main_df_hour = df_hour[(df_hour['dteday'].dt.date >= start_date) & (df_hour['dteday'].dt.date <= end_date)]

# FILTER KHUSUS PAGE 2 DI SIDEBAR
if page == "2. 24-Hour Pattern Analysis":
    st.sidebar.markdown("<br>**Day Type Filter**", unsafe_allow_html=True)
    day_type = st.sidebar.selectbox("Day Type", ["All Days", "Working Days", "Weekends/Holidays"], label_visibility="collapsed")

st.sidebar.markdown("<hr style='border-top: 1px solid rgba(255,255,255,0.4); margin-top: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
st.sidebar.caption("Created by: Nahdah Tsamarah Hasan")


# ==========================================
# PAGE 1: DAILY OVERVIEW & KEY FACTORS
# ==========================================
if page == "1. Daily Overview & Key Factors":
    
    st.markdown(f"<h2 style='color: {COLORS['sidebar']}; font-weight: 800;'>Daily Overview & Key Factors</h2>", unsafe_allow_html=True)
    
    # --- BARIS 1: SCORE CARDS ---
    total_sewa = main_df_day['cnt'].sum()
    rata_rata = main_df_day['cnt'].mean() if not main_df_day.empty else 0
    
    if not main_df_day.empty:
        busiest_date = main_df_day.loc[main_df_day['cnt'].idxmax(), 'dteday']
        hari_ramai = f"{busiest_date.day} {busiest_date.strftime('%B %Y')}"
        max_sewa = main_df_day['cnt'].max()
    else:
        hari_ramai = "-"
        max_sewa = 0

    st.markdown(f"""
    <div style="display: flex; gap: 20px; margin-bottom: 25px;">
        <div style="flex: 1; background-color: {COLORS['card1']}; padding: 25px; border-radius: 25px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); color: white; text-align: center;">
            <p style="margin: 0; font-size: 20px; font-weight: 600; opacity: 0.9;">Total Bike Rentals</p>
            <h2 style="margin: 0px 0 0 0; font-size: 50px; font-weight: 800; color: white;">{total_sewa:,}</h2>
        </div>
        <div style="flex: 1; background-color: {COLORS['card2']}; padding: 25px; border-radius: 25px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); color: white; text-align: center;">
            <p style="margin: 0; font-size: 20px; font-weight: 600; opacity: 0.9;">Average Daily Rentals</p>
            <h2 style="margin: 0px 0 0 0; font-size: 50px; font-weight: 800; color: white;">{rata_rata:,.0f}</h2>
        </div>
        <div style="flex: 1; background-color: {COLORS['card3']}; padding: 25px; border-radius: 25px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); color: white; text-align: center;">
            <p style="margin: 0; font-size: 20px; font-weight: 600; opacity: 0.9;">Busiest Day</p>
            <h2 style="margin: 0px 0 0 0; font-size: 32px; font-weight: 800; color: white;">{hari_ramai}</h2>
            <p style="margin: 0px 0 0 0; font-size: 17px; font-weight: 600; opacity: 0.9;">{max_sewa:,} rentals</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- BARIS 2: DAILY BIKE RENTAL TREND ---
    fig_trend, ax_trend = plt.subplots(figsize=(16, 5))
    fig_trend.patch.set_facecolor(COLORS['white'])
    ax_trend.set_facecolor(COLORS['white'])
    
    sns.lineplot(data=main_df_day, x='dteday', y='cnt', color=COLORS['card2'], linewidth=2.5, ax=ax_trend)
    
    if not main_df_day.empty:
        min_date_val = main_df_day['dteday'].min()
        max_date_val = main_df_day['dteday'].max()
        
        if len(main_df_day) <= 7:
            tick_dates = main_df_day['dteday']
        else:
            tick_dates = pd.date_range(start=min_date_val, end=max_date_val, periods=6)
            
        ax_trend.set_xticks(tick_dates)
        ax_trend.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y')) 
    
    plt.xticks(rotation=45)
    
    ax_trend.set_xlabel("") 
    ax_trend.set_ylabel("Total Rentals", fontweight='bold', color=COLORS['text_main'])
    
    ax_trend.spines['top'].set_visible(False)
    ax_trend.spines['right'].set_visible(False)
    ax_trend.spines['left'].set_color('#e0e0e0')
    ax_trend.spines['bottom'].set_color('#e0e0e0')
    ax_trend.grid(axis='y', linestyle='--', alpha=0.4, color='#a0a0a0')
    
    b64_trend = get_base64_of_figure(fig_trend)
    plt.close(fig_trend)
    
    st.markdown(f"""<div style="background-color: {COLORS['white']}; border-radius: 15px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); padding: 25px; margin-bottom: 25px;">
<h4 style="color: {COLORS['sidebar']}; font-weight: 700; margin-top: 0; margin-bottom: 15px;">Daily Bike Rental Trend</h4>
<img src="data:image/png;base64,{b64_trend}" style="width: 100%;">
</div>""", unsafe_allow_html=True)

    # --- BARIS 3: SIDE-BY-SIDE PLOTS ---
    plot_col1, plot_col2 = st.columns([1.5, 1.5], gap="small") 
    
    # KIRI: WEEKLY PERFORMANCE
    with plot_col1:
        delta_days = (end_date - start_date).days
        warning_html_bar = ""
        
        if delta_days < 6:
            warning_html_bar = f"""<details style="background-color: {COLORS['warning_bg']}; color: {COLORS['warning_text']}; padding: 12px; border-radius: 8px; border: 1px solid rgba(255, 75, 75, 0.4); margin-bottom: 15px;">
<summary style="cursor: pointer; font-weight: 800; font-size: 15px;">⚠️ WARNING!</summary>
<p style="margin-top: 10px; margin-bottom: 0; font-size: 14px; font-weight: 600;">Selected date range is &lt; 7 days. Only available days in this period are shown.</p>
</details>"""

        day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        day_stats = main_df_day.groupby('weekday')['cnt'].mean().reset_index()
        
        day_names = {0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat'}
        day_stats['weekday'] = day_stats['weekday'].map(day_names)
        
        day_order_present = [d for d in day_order if d in day_stats['weekday'].values]
        day_stats['weekday'] = pd.Categorical(day_stats['weekday'], categories=day_order_present, ordered=True)
        day_stats = day_stats.sort_values('weekday')
        
        day_stats['rank'] = day_stats['cnt'].rank(method='min', ascending=False)
        palette_colors = []
        for r in day_stats['rank']:
            if r == 1:
                palette_colors.append('#083054') 
            elif r in [2, 3]:
                palette_colors.append(COLORS['card2']) 
            else:
                palette_colors.append(COLORS['card1']) 
        
        fig_bar, ax_bar = plt.subplots(figsize=(8, 5.55))
        fig_bar.patch.set_facecolor(COLORS['white'])
        ax_bar.set_facecolor(COLORS['white'])
        
        sns.barplot(data=day_stats, x='weekday', y='cnt', palette=palette_colors, ax=ax_bar)
        
        ax_bar.set_xlabel("Day of the Week", fontweight='bold', color=COLORS['text_main'])
        ax_bar.set_ylabel("Average Rentals", fontweight='bold', color=COLORS['text_main'])
        
        ax_bar.spines['top'].set_visible(False)
        ax_bar.spines['right'].set_visible(False)
        ax_bar.spines['left'].set_color('#e0e0e0')
        ax_bar.spines['bottom'].set_color('#e0e0e0')
        ax_bar.grid(axis='y', linestyle='--', alpha=0.4, color='#a0a0a0')
        
        b64_bar = get_base64_of_figure(fig_bar)
        plt.close(fig_bar)
        
        st.markdown(f"""<div style="background-color: {COLORS['white']}; border-radius: 15px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); padding: 25px; height: 100%;">
<h4 style="color: {COLORS['sidebar']}; font-weight: 700; margin-top: 0; margin-bottom: 15px;">Weekly Performance</h4>
{warning_html_bar}
<img src="data:image/png;base64,{b64_bar}" style="width: 100%;">
</div>""", unsafe_allow_html=True)

    # KANAN: MONTHLY PERFORMANCE
    with plot_col2:
        # Cek jumlah bulan unik dalam data yang difilter
        unique_months = main_df_day['mnth'].nunique()
        warning_html_month = ""
        
        # Jika kurang dari 2 bulan, panggil data keseluruhan (df_day)
        if unique_months < 2:
            warning_html_month = f"""<details style="background-color: {COLORS['warning_bg']}; color: {COLORS['warning_text']}; padding: 12px; border-radius: 8px; border: 1px solid rgba(255, 75, 75, 0.4); margin-bottom: 15px;">
<summary style="cursor: pointer; font-weight: 800; font-size: 15px;">⚠️ WARNING!</summary>
<p style="margin-top: 10px; margin-bottom: 0; font-size: 14px; font-weight: 600;">Selected date range is too narrow (&lt; 2 months). Displaying monthly performance using the entire dataset.</p>
</details>"""
            month_df = df_day
        else:
            month_df = main_df_day
            
        month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_stats = month_df.groupby('mnth')['cnt'].mean().reset_index()
        
        # Mapping angka ke nama bulan
        month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
        month_stats['mnth'] = month_stats['mnth'].map(month_names)
        
        # Urutkan berdasarkan kalender dan buang bulan yang ga ada di data
        month_order_present = [m for m in month_order if m in month_stats['mnth'].values]
        month_stats['mnth'] = pd.Categorical(month_stats['mnth'], categories=month_order_present, ordered=True)
        month_stats = month_stats.sort_values('mnth')
        
        # Logika warna bar chart
        month_stats['rank'] = month_stats['cnt'].rank(method='min', ascending=False)
        palette_month = []
        for r in month_stats['rank']:
            if r == 1:
                palette_month.append('#083054') # Sangat gelap
            elif r in [2, 3]:
                palette_month.append(COLORS['card2']) # Sedang
            else:
                palette_month.append(COLORS['card1']) # Terang
                
        fig_month, ax_month = plt.subplots(figsize=(8, 5.55))
        fig_month.patch.set_facecolor(COLORS['white'])
        ax_month.set_facecolor(COLORS['white'])
        
        sns.barplot(data=month_stats, x='mnth', y='cnt', palette=palette_month, ax=ax_month)
        
        ax_month.set_xlabel("Month", fontweight='bold', color=COLORS['text_main'])
        ax_month.set_ylabel("Average Rentals", fontweight='bold', color=COLORS['text_main'])
        
        ax_month.spines['top'].set_visible(False)
        ax_month.spines['right'].set_visible(False)
        ax_month.spines['left'].set_color('#e0e0e0')
        ax_month.spines['bottom'].set_color('#e0e0e0')
        ax_month.grid(axis='y', linestyle='--', alpha=0.4, color='#a0a0a0')
        
        b64_month = get_base64_of_figure(fig_month)
        plt.close(fig_month)

        html_month = f"""<div style="background-color: {COLORS['white']}; border-radius: 15px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); padding: 25px; height: 100%;">
<h4 style="color: {COLORS['sidebar']}; font-weight: 700; margin-top: 0; margin-bottom: 15px;">Monthly Performance</h4>
{warning_html_month}
<img src="data:image/png;base64,{b64_month}" style="width: 100%;">
</div>"""
        st.markdown(html_month, unsafe_allow_html=True)

# ==========================================
# PAGE 2: 24-HOUR PATTERN ANALYSIS
# ==========================================
elif page == "2. 24-Hour Pattern Analysis":
    
    st.markdown(f"<h2 style='color: {COLORS['sidebar']}; font-weight: 800;'>24-Hour Pattern Analysis</h2>", unsafe_allow_html=True)
    
    filtered_hour = main_df_hour.copy()
    if day_type == "Working Days":
        filtered_hour = filtered_hour[filtered_hour['workingday'] == 1]
    elif day_type == "Weekends/Holidays":
        filtered_hour = filtered_hour[filtered_hour['workingday'] == 0]
        
    if filtered_hour.empty:
        st.warning("No data available for the selected filters.")
    else:
        # --- BARIS 1: SCORE CARDS KHUSUS JAM ---
        hourly_stats = filtered_hour.groupby('hr')['cnt'].mean()
        busiest_hr = hourly_stats.idxmax()
        quietest_hr = hourly_stats.idxmin()
        avg_hourly = hourly_stats.mean()
        
        str_busiest = f"{int(busiest_hr):02d}:00"
        str_quietest = f"{int(quietest_hr):02d}:00"

        st.markdown(f"""
        <div style="display: flex; gap: 30px; margin-bottom: 25px;">
            <div style="flex: 1; background-color: {COLORS['card1']}; padding: 15px 20px; border-radius: 25px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); color: white; text-align: center;">
                <p style="margin: 0; font-size: 20px; font-weight: 600; opacity: 0.9;">Busiest Hour</p>
                <h2 style="margin: 0px 0 0 0; font-size: 52px; font-weight: 800; color: white;">{str_busiest}</h2>
                <p style="margin: 0px 0 0 0; font-size: 17px; font-weight: 600; opacity: 0.9;">{hourly_stats.max():.0f} avg rentals</p>
            </div>
            <div style="flex: 1; background-color: {COLORS['card2']}; padding: 15px 20px; border-radius: 25px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); color: white; text-align: center;">
                <p style="margin: 0; font-size: 20px; font-weight: 600; opacity: 0.9;">Quietest Hour</p>
                <h2 style="margin: 0px 0 0 0; font-size: 52px; font-weight: 800; color: white;">{str_quietest}</h2>
                <p style="margin: 0px 0 0 0; font-size: 17px; font-weight: 600; opacity: 0.9;">{hourly_stats.min():.0f} avg rentals</p>
            </div>
            <div style="flex: 1; background-color: {COLORS['card3']}; padding: 15px 20px; border-radius: 25px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); color: white; text-align: center;">
                <p style="margin: 0; font-size: 20px; font-weight: 600; opacity: 0.9;">Average Hourly Rentals</p>
                <h2 style="margin: 0px 0 0 0; font-size: 52px; font-weight: 800; color: white;">{avg_hourly:.0f}</h2>
                <p style="margin: 0px 0 0 0; font-size: 17px; font-weight: 600; opacity: 0.9;">rentals / hour</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ==========================================
        # BARIS 2: Hourly Pattern & Time Segment
        # ==========================================
        row2_col1, row2_col2 = st.columns([1.8, 1.2], gap="small") 
        
        with row2_col1:
            fig_hour, ax_hour = plt.subplots(figsize=(10, 5.2)) 
            fig_hour.patch.set_facecolor(COLORS['white'])
            ax_hour.set_facecolor(COLORS['white'])
            
            sns.lineplot(data=hourly_stats.reset_index(), x='hr', y='cnt', color=COLORS['card2'], linewidth=3, ax=ax_hour)
            
            ax_hour.axvspan(5, 12, color='#d0f0fd', alpha=0.5, label='Morning (05-11)')
            ax_hour.axvspan(12, 15, color='#fff2cc', alpha=0.5, label='Afternoon (12-14)')
            ax_hour.axvspan(15, 18, color='#ffe6cc', alpha=0.5, label='Evening (15-17)')
            ax_hour.axvspan(18, 23.5, color='#e6e6fa', alpha=0.5, label='Night (18-04)')
            ax_hour.axvspan(-0.5, 5, color='#e6e6fa', alpha=0.5)
            
            ax_hour.set_xlim(0, 23)
            ax_hour.set_ylim(bottom=0) 
            ax_hour.margins(x=0, y=0)
            
            yticks_hour = ax_hour.get_yticks()
            ax_hour.set_yticks([tick for tick in yticks_hour if tick != 0])
            
            ax_hour.set_xticks(range(0, 24))
            ax_hour.set_xlabel("Hour of the Day", fontweight='bold', color=COLORS['text_main'])
            ax_hour.set_ylabel("Average Rentals", fontweight='bold', color=COLORS['text_main'])
            
            ax_hour.spines['top'].set_visible(False)
            ax_hour.spines['right'].set_visible(False)
            ax_hour.spines['left'].set_color('#e0e0e0')
            ax_hour.spines['bottom'].set_color('#e0e0e0')
            ax_hour.grid(axis='y', linestyle='--', alpha=0.4, color='#a0a0a0')
            ax_hour.legend(loc='upper left', frameon=True, facecolor=COLORS['white'])
            
            b64_hour = get_base64_of_figure(fig_hour)
            plt.close(fig_hour)
            
            # Height dikembalikan ke 100%, biarkan CSS yang ngatur otomatis
            st.markdown(f"""<div style="background-color: {COLORS['white']}; border-radius: 15px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); padding: 25px; height: 100%; display: flex; flex-direction: column;">
<h4 style="color: {COLORS['sidebar']}; font-weight: 700; margin-top: 0; margin-bottom: 15px;">Hourly Rental Pattern</h4>
<div style="flex-grow: 1; display: flex; align-items: center; justify-content: center;">
    <img src="data:image/png;base64,{b64_hour}" style="width: 100%; height: auto;">
</div>
</div>""", unsafe_allow_html=True)


        with row2_col2:
            segment_order = ['Morning (05:00 - 11:59)', 'Afternoon (12:00 - 14:59)', 'Evening (15:00 - 17:59)', 'Night (18:00 - 04:59)']
            segment_data = filtered_hour.groupby('time_segment')['cnt'].sum().reindex(segment_order).reset_index()
            
            max_val = segment_data['cnt'].max()
            sorted_vals = segment_data['cnt'].sort_values(ascending=False).values
            second_max = sorted_vals[1] if len(sorted_vals) > 1 else 0
            is_close = (max_val - second_max) / max_val <= 0.20
            
            palette_colors = []
            for val in segment_data['cnt']:
                if val == max_val:
                    palette_colors.append('#083054') 
                elif val == second_max and is_close:
                    palette_colors.append(COLORS['card2']) 
                else:
                    palette_colors.append(COLORS['card1']) 
            
            fig_seg, ax_seg = plt.subplots(figsize=(7, 6.35)) 
            fig_seg.patch.set_facecolor(COLORS['white'])
            ax_seg.set_facecolor(COLORS['white'])
            
            sns.barplot(data=segment_data, x='time_segment', y='cnt', palette=palette_colors, hue='time_segment', legend=False, ax=ax_seg)
            
            ax_seg.ticklabel_format(style='plain', axis='y')
            ax_seg.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
            
            ax_seg.set_xlabel("Time Segment", fontweight='bold', color=COLORS['text_main'])
            ax_seg.set_ylabel("Total Rentals", fontweight='bold', color=COLORS['text_main'])
            ax_seg.set_xticklabels(['Morning', 'Afternoon', 'Evening', 'Night'])
            
            ax_seg.spines['top'].set_visible(False)
            ax_seg.spines['right'].set_visible(False)
            ax_seg.spines['left'].set_color('#e0e0e0')
            ax_seg.spines['bottom'].set_color('#e0e0e0')
            ax_seg.grid(axis='y', linestyle='--', alpha=0.4, color='#a0a0a0')
            
            b64_seg = get_base64_of_figure(fig_seg)
            plt.close(fig_seg)
            
            st.markdown(f"""<div style="background-color: {COLORS['white']}; border-radius: 15px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); padding: 25px; height: 100%; display: flex; flex-direction: column;">
<h4 style="color: {COLORS['sidebar']}; font-weight: 700; margin-top: 0; margin-bottom: 15px;">Rentals by Time Segment</h4>
<div style="flex-grow: 1; display: flex; align-items: center; justify-content: center;">
    <img src="data:image/png;base64,{b64_seg}" style="width: 100%; height: auto;">
</div>
</div>""", unsafe_allow_html=True)


        # ==========================================
        # BARIS 3: Donut & Proportion
        # ==========================================
        st.markdown("<br>", unsafe_allow_html=True)
        row3_col1, row3_col2 = st.columns([1, 2], gap="small") 
        
        with row3_col1:
            total_reg = filtered_hour['registered'].sum()
            total_cas = filtered_hour['casual'].sum()
            
            # Porsi kolom 1 -> rasio 1:1 -> (5, 5)
            fig_donut, ax_donut = plt.subplots(figsize=(7, 7)) 
            fig_donut.patch.set_facecolor(COLORS['white'])
            
            ax_donut.pie(
                [total_reg, total_cas], 
                labels=['Registered', 'Casual'], 
                colors=[COLORS['card2'], COLORS['card1']], 
                autopct='%1.1f%%', 
                startangle=90, 
                pctdistance=0.7,
                textprops={'fontsize': 14, 'fontweight': 'bold', 'color': COLORS['text_main']}
            )
            
            centre_circle = plt.Circle((0,0), 0.45, fc=COLORS['white'])
            fig_donut.gca().add_artist(centre_circle)
            ax_donut.axis('equal')
            
            b64_donut = get_base64_of_figure(fig_donut)
            plt.close(fig_donut)

            st.markdown(f"""<div style="background-color: {COLORS['white']}; border-radius: 15px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); padding: 25px; height: 100%; display: flex; flex-direction: column;">
<h4 style="color: {COLORS['sidebar']}; font-weight: 700; margin-top: 0; margin-bottom: 15px;">Overall User Ratio</h4>
<div style="flex-grow: 1; display: flex; align-items: center; justify-content: center;">
    <img src="data:image/png;base64,{b64_donut}" style="width: 100%; height: auto;">
</div>
</div>""", unsafe_allow_html=True)

        with row3_col2:
            comp_data = filtered_hour.groupby('hr')[['registered', 'casual']].mean().reset_index()
            comp_data['total'] = comp_data['registered'] + comp_data['casual']
            comp_data['reg_pct'] = (comp_data['registered'] / comp_data['total']) * 100
            comp_data['cas_pct'] = (comp_data['casual'] / comp_data['total']) * 100
            
            # Porsi kolom 2 -> rasio 2:1 -> (10, 5)
            fig_comp, ax_comp = plt.subplots(figsize=(10, 4.3)) 
            fig_comp.patch.set_facecolor(COLORS['white'])
            ax_comp.set_facecolor(COLORS['white'])
            
            sns.lineplot(data=comp_data, x='hr', y='reg_pct', color=COLORS['card2'], linewidth=2.5, label='Registered (%)', ax=ax_comp)
            sns.lineplot(data=comp_data, x='hr', y='cas_pct', color=COLORS['card1'], linewidth=2.5, label='Casual (%)', ax=ax_comp)
            
            ax_comp.set_xlim(0, 23)
            ax_comp.set_ylim(0, 105) 
            ax_comp.margins(x=0, y=0)
            
            yticks_comp = ax_comp.get_yticks()
            ax_comp.set_yticks([tick for tick in yticks_comp if tick != 0 and tick <= 100])
            ax_comp.set_yticklabels([f"{int(tick)}%" for tick in ax_comp.get_yticks()])
            
            ax_comp.set_xticks(range(0, 24))
            ax_comp.set_xlabel("Hour of the Day", fontweight='bold', color=COLORS['text_main'])
            ax_comp.set_ylabel("Proportion (%)", fontweight='bold', color=COLORS['text_main'])
            
            ax_comp.spines['top'].set_visible(False)
            ax_comp.spines['right'].set_visible(False)
            ax_comp.spines['left'].set_color('#e0e0e0')
            ax_comp.spines['bottom'].set_color('#e0e0e0')
            ax_comp.grid(axis='y', linestyle='--', alpha=0.4, color='#a0a0a0')
            ax_comp.legend(frameon=False, loc='center right')
            
            b64_comp = get_base64_of_figure(fig_comp)
            plt.close(fig_comp)

            st.markdown(f"""<div style="background-color: {COLORS['white']}; border-radius: 15px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); padding: 25px; height: 100%; display: flex; flex-direction: column;">
<h4 style="color: {COLORS['sidebar']}; font-weight: 700; margin-top: 0; margin-bottom: 15px;">User Composition Proportion</h4>
<div style="flex-grow: 1; display: flex; align-items: center; justify-content: center;">
    <img src="data:image/png;base64,{b64_comp}" style="width: 100%; height: auto;">
</div>
</div>""", unsafe_allow_html=True)


# ==========================================
# PAGE 3: RENTAL FACTORS BY TIME PERIOD
# ==========================================
elif page == "3. Rental Factors by Time Period":

    st.markdown(f"<h2 style='color: {COLORS['sidebar']}; font-weight: 800;'>Rental Factors by Time Period</h2>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # BAGIAN 1: FACTORS INFLUENCING BIKE RENTALS
    # ---------------------------------------------------------
    delta_days = (end_date - start_date).days
    warning_html = ""
    
    if delta_days < 6:
        warning_html = f"""<details style="background-color: {COLORS['warning_bg']}; color: {COLORS['warning_text']}; padding: 12px; border-radius: 8px; border: 1px solid rgba(255, 75, 75, 0.4); margin-bottom: 15px;">
<summary style="cursor: pointer; font-weight: 800; font-size: 15px;">⚠️ WARNING!</summary>
<p style="margin-top: 10px; margin-bottom: 0; font-size: 14px; font-weight: 600;">Selected date range is &lt; 7 days. Displaying correlation using the entire dataset to maintain statistical validity.</p>
</details>"""
        corr_df = df_day
    else:
        corr_df = main_df_day
        
    b64_corr = ""
        
    if not corr_df.empty and len(corr_df) > 1:
        corr_raw = corr_df[['temp', 'atemp', 'hum', 'windspeed', 'season', 'weathersit', 'holiday', 'workingday', 'cnt']].corr()['cnt']
        corr_raw = corr_raw.drop('cnt').fillna(0)
        
        corr_zero = corr_raw[corr_raw == 0]
        corr_non_zero = corr_raw[corr_raw != 0].sort_values(ascending=True)
        correlation_data = pd.concat([corr_zero, corr_non_zero])
        
        colors_corr = []
        for x in correlation_data:
            if x == 0:
                colors_corr.append('#e0e0e0') 
            elif x < 0:
                colors_corr.append(COLORS['card1']) 
            else:
                colors_corr.append(COLORS['card2']) 
        
        fig_corr, ax_corr = plt.subplots(figsize=(14, 5))
        fig_corr.patch.set_facecolor(COLORS['white'])
        ax_corr.set_facecolor(COLORS['white'])
        
        correlation_data.plot(kind='barh', color=colors_corr, ax=ax_corr, width=0.6)
        
        x_min, x_max = correlation_data.min(), correlation_data.max()
        padding = max(0.05, (x_max - x_min) * 0.15) 
        ax_corr.set_xlim(min(0, x_min - padding), max(0, x_max + padding))
        
        ax_corr.set_xlabel("Pearson Correlation Coefficient", fontweight='bold', color=COLORS['text_main'])
        ax_corr.set_ylabel("") 
        ax_corr.axvline(x=0, color='#333333', linestyle='-', linewidth=1.5)
        
        ax_corr.spines['top'].set_visible(False)
        ax_corr.spines['right'].set_visible(False)
        ax_corr.spines['left'].set_visible(True)
        ax_corr.grid(axis='x', linestyle='--', alpha=0.4, color='#a0a0a0')
        
        text_offset = max(0.02, (x_max - x_min) * 0.05)
        
        # Memunculkan angka di samping bar menggunakan text() loop
        for index, value in enumerate(correlation_data):
            if value >= 0:
                str_val = '0.00' if value == 0 else f'{value:.2f}'
                ax_corr.text(value + text_offset, index, str_val, va='center', ha='left', fontsize=10, fontweight='bold', color=COLORS['text_main'])
            else:
                ax_corr.text(value - text_offset, index, f'{value:.2f}', va='center', ha='right', fontsize=10, fontweight='bold', color=COLORS['text_main'])
                
        b64_corr = get_base64_of_figure(fig_corr)
        plt.close(fig_corr)

    html_corr = f"""<div style="background-color: {COLORS['white']}; border-radius: 15px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); padding: 25px; margin-bottom: 25px;">
<h4 style="color: {COLORS['sidebar']}; font-weight: 700; margin-top: 0; margin-bottom: 15px;">Factors Influencing Bike Rentals</h4>
{warning_html}
<img src="data:image/png;base64,{b64_corr}" style="width: 100%;">
</div>"""
    st.markdown(html_corr, unsafe_allow_html=True)


    # ---------------------------------------------------------
    # BAGIAN 2: INTERACTIVE FACTOR ANALYSIS
    # ---------------------------------------------------------
    st.markdown(f"<h4 style='color: {COLORS['sidebar']}; font-weight: 700; margin-top: 20px; margin-bottom: 10px;'>Factors to Analyze</h4>", unsafe_allow_html=True)
    
    all_factors = ["Temperature", "Apparent Temperature", "Humidity", "Windspeed", "Season", "Weather Situation", "Working Day", "Holiday"]
    
    select_all_text = "Select All"
    options = [select_all_text] + all_factors
    
    # EXCLUSIVE MULTI-SELECT ---
    # Menyimpan status pilihan sebelumnya di memori (Session State)
    if "pills_key" not in st.session_state:
        st.session_state.pills_key = ["Temperature"]
        st.session_state.previous_pills = ["Temperature"]

    def sync_pills():
        current = st.session_state.pills_key
        previous = st.session_state.previous_pills
        
        # Kondisi 1: Jika user mengklik "Select All", maka hapus centang faktor lainnya
        if select_all_text in current and select_all_text not in previous:
            st.session_state.pills_key = [select_all_text]
        # Kondisi 2: Jika "Select All" sedang aktif, lalu user memilih faktor lain, maka matikan "Select All"
        elif select_all_text in current and len(current) > 1:
            st.session_state.pills_key = [x for x in current if x != select_all_text]
            
        st.session_state.previous_pills = st.session_state.pills_key
    
    selected_pills = st.pills(
        "Factors", 
        options=options, 
        selection_mode="multi", 
        key="pills_key", # Menghubungkan tombol ke memori Session State
        on_change=sync_pills, # Menjalankan logika tiap kali diklik
        label_visibility="collapsed"
    )
    
    df_p3 = main_df_hour.copy()
    
    if df_p3.empty:
        st.warning("No data available for the selected dates.")
    elif not selected_pills:
        st.info("Please select at least one factor from the options above to view the analysis.")
    else:
        # Menentukan daftar faktor yang akan digambar
        if select_all_text in selected_pills:
            selected_factors = all_factors
        else:
            selected_factors = selected_pills
            
        # Logika DYNAMIC GRID LAYOUT
        num_factors = len(selected_factors)
        
        # Looping dengan lompatan 2 (memproses 2 faktor sekaligus tiap putaran)
        for i in range(0, num_factors, 2):
            
            # CEK: Apakah kita sedang berada di sisa 1 faktor terakhir?
            if i == num_factors - 1:
                # SISA 1 -> FULL WIDTH (Tidak pakai kolom)
                factor_choice = selected_factors[i]
                
                df_plot = df_p3.copy()
                season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
                weather_map = {1: 'Clear/Partly Cloudy', 2: 'Misty/Cloudy', 3: 'Light Snow/Rain', 4: 'Heavy Rain/Ice'}
                
                if factor_choice == "Temperature":
                    df_plot['Factor_Category'] = pd.qcut(df_plot['temp'], q=3, labels=['Low Temp', 'Medium Temp', 'High Temp'])
                elif factor_choice == "Apparent Temperature":
                    df_plot['Factor_Category'] = pd.qcut(df_plot['atemp'], q=3, labels=['Low Feels-like', 'Medium Feels-like', 'High Feels-like'])
                elif factor_choice == "Humidity":
                    df_plot['Factor_Category'] = pd.qcut(df_plot['hum'], q=3, labels=['Low Humidity', 'Medium Humidity', 'High Humidity'])
                elif factor_choice == "Windspeed":
                    df_plot['Factor_Category'] = pd.qcut(df_plot['windspeed'].rank(method='first'), q=3, labels=['Low Wind', 'Medium Wind', 'High Wind'])
                elif factor_choice == "Season":
                    df_plot['Factor_Category'] = df_plot['season'].map(season_map)
                elif factor_choice == "Weather Situation":
                    df_plot['Factor_Category'] = df_plot['weathersit'].map(weather_map)
                elif factor_choice == "Working Day":
                    df_plot['Factor_Category'] = df_plot['workingday'].map({1: 'Working Day', 0: 'Weekend/Holiday'})
                elif factor_choice == "Holiday":
                    df_plot['Factor_Category'] = df_plot['holiday'].map({1: 'Holiday', 0: 'Non-Holiday'})

                segment_order = ['Morning (05:00 - 11:59)', 'Afternoon (12:00 - 14:59)', 'Evening (15:00 - 17:59)', 'Night (18:00 - 04:59)']
                grouped_data = df_plot.groupby(['time_segment', 'Factor_Category'], observed=False)['cnt'].mean().reset_index()
                
                # Karena Full Width, Figsize dilebarkan (14, 5)
                fig_fact, ax_fact = plt.subplots(figsize=(14, 5.5))
                fig_fact.patch.set_facecolor(COLORS['white'])
                ax_fact.set_facecolor(COLORS['white'])
                
                custom_palette = [COLORS['card1'], COLORS['card2'], '#083054', '#81d4fa']
                
                sns.barplot(data=grouped_data, x='time_segment', y='cnt', hue='Factor_Category', palette=custom_palette, order=segment_order, ax=ax_fact)
                
                max_y = grouped_data['cnt'].max()
                ax_fact.set_ylim(0, max_y * 1.15) 
                ax_fact.margins(x=0, y=0)
                
                for container in ax_fact.containers:
                    ax_fact.bar_label(container, fmt='{:,.0f}', padding=4, fontsize=10, fontweight='bold', color=COLORS['text_main'])
                
                ax_fact.ticklabel_format(style='plain', axis='y')
                ax_fact.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
                
                yticks_fact = ax_fact.get_yticks()
                ax_fact.set_yticks([tick for tick in yticks_fact if tick != 0])
                
                ax_fact.set_xlabel("Time Segment", fontweight='bold', color=COLORS['text_main'])
                ax_fact.set_ylabel("Average Rentals", fontweight='bold', color=COLORS['text_main'])
                ax_fact.set_xticklabels(['Morning', 'Afternoon', 'Evening', 'Night'])
                
                ax_fact.spines['top'].set_visible(False)
                ax_fact.spines['right'].set_visible(False)
                ax_fact.spines['left'].set_color('#e0e0e0')
                ax_fact.spines['bottom'].set_color('#e0e0e0')
                ax_fact.grid(axis='y', linestyle='--', alpha=0.4, color='#a0a0a0')
                ax_fact.legend(title=factor_choice, frameon=True, facecolor=COLORS['white'])
                
                b64_fact = get_base64_of_figure(fig_fact)
                plt.close(fig_fact)

                st.markdown(f"""<div style="background-color: {COLORS['white']}; border-radius: 15px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); padding: 25px; margin-top: 15px; margin-bottom: 25px;">
<h4 style="color: {COLORS['sidebar']}; font-weight: 700; margin-top: 0; margin-bottom: 20px;">Average Rentals by {factor_choice} per Time Segment</h4>
<img src="data:image/png;base64,{b64_fact}" style="width: 100%; height: auto;">
</div>""", unsafe_allow_html=True)
                
            else:
                # ADA PASANGANNYA -> BUAT 2 KOLOM
                cols = st.columns(2, gap="small")
                
                # Memproses 2 faktor yang bersebelahan (i dan i+1)
                for j in range(2):
                    with cols[j]:
                        factor_choice = selected_factors[i + j]
                        
                        df_plot = df_p3.copy()
                        season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
                        weather_map = {1: 'Clear/Partly Cloudy', 2: 'Misty/Cloudy', 3: 'Light Snow/Rain', 4: 'Heavy Rain/Ice'}
                        
                        if factor_choice == "Temperature":
                            df_plot['Factor_Category'] = pd.qcut(df_plot['temp'], q=3, labels=['Low Temp', 'Medium Temp', 'High Temp'])
                        elif factor_choice == "Apparent Temperature":
                            df_plot['Factor_Category'] = pd.qcut(df_plot['atemp'], q=3, labels=['Low Feels-like', 'Medium Feels-like', 'High Feels-like'])
                        elif factor_choice == "Humidity":
                            df_plot['Factor_Category'] = pd.qcut(df_plot['hum'], q=3, labels=['Low Humidity', 'Medium Humidity', 'High Humidity'])
                        elif factor_choice == "Windspeed":
                            df_plot['Factor_Category'] = pd.qcut(df_plot['windspeed'].rank(method='first'), q=3, labels=['Low Wind', 'Medium Wind', 'High Wind'])
                        elif factor_choice == "Season":
                            df_plot['Factor_Category'] = df_plot['season'].map(season_map)
                        elif factor_choice == "Weather Situation":
                            df_plot['Factor_Category'] = df_plot['weathersit'].map(weather_map)
                        elif factor_choice == "Working Day":
                            df_plot['Factor_Category'] = df_plot['workingday'].map({1: 'Working Day', 0: 'Weekend/Holiday'})
                        elif factor_choice == "Holiday":
                            df_plot['Factor_Category'] = df_plot['holiday'].map({1: 'Holiday', 0: 'Non-Holiday'})

                        segment_order = ['Morning (05:00 - 11:59)', 'Afternoon (12:00 - 14:59)', 'Evening (15:00 - 17:59)', 'Night (18:00 - 04:59)']
                        grouped_data = df_plot.groupby(['time_segment', 'Factor_Category'], observed=False)['cnt'].mean().reset_index()
                        
                        # Karena 2 Kolom, Figsize dikecilkan (8, 5.5)
                        fig_fact, ax_fact = plt.subplots(figsize=(8, 5.5))
                        fig_fact.patch.set_facecolor(COLORS['white'])
                        ax_fact.set_facecolor(COLORS['white'])
                        
                        custom_palette = [COLORS['card1'], COLORS['card2'], '#083054', '#81d4fa']
                        
                        sns.barplot(data=grouped_data, x='time_segment', y='cnt', hue='Factor_Category', palette=custom_palette, order=segment_order, ax=ax_fact)
                        
                        max_y = grouped_data['cnt'].max()
                        ax_fact.set_ylim(0, max_y * 1.15) 
                        ax_fact.margins(x=0, y=0)
                        
                        for container in ax_fact.containers:
                            ax_fact.bar_label(container, fmt='{:,.0f}', padding=4, fontsize=10, fontweight='bold', color=COLORS['text_main'])
                        
                        ax_fact.ticklabel_format(style='plain', axis='y')
                        ax_fact.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
                        
                        yticks_fact = ax_fact.get_yticks()
                        ax_fact.set_yticks([tick for tick in yticks_fact if tick != 0])
                        
                        ax_fact.set_xlabel("Time Segment", fontweight='bold', color=COLORS['text_main'])
                        ax_fact.set_ylabel("Average Rentals", fontweight='bold', color=COLORS['text_main'])
                        ax_fact.set_xticklabels(['Morning', 'Afternoon', 'Evening', 'Night'])
                        
                        ax_fact.spines['top'].set_visible(False)
                        ax_fact.spines['right'].set_visible(False)
                        ax_fact.spines['left'].set_color('#e0e0e0')
                        ax_fact.spines['bottom'].set_color('#e0e0e0')
                        ax_fact.grid(axis='y', linestyle='--', alpha=0.4, color='#a0a0a0')
                        ax_fact.legend(title=factor_choice, frameon=True, facecolor=COLORS['white'])
                        
                        b64_fact = get_base64_of_figure(fig_fact)
                        plt.close(fig_fact)

                        st.markdown(f"""<div style="background-color: {COLORS['white']}; border-radius: 15px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); padding: 25px; margin-top: 15px; margin-bottom: 25px; height: 100%;">
<h4 style="color: {COLORS['sidebar']}; font-weight: 700; margin-top: 0; margin-bottom: 20px;">Average Rentals by {factor_choice} per Time Segment</h4>
<img src="data:image/png;base64,{b64_fact}" style="width: 100%; height: auto;">
</div>""", unsafe_allow_html=True)