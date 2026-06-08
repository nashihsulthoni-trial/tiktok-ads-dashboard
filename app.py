import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from data_processor import load_and_clean_data, generate_recommendations, evaluate_retention_ai

def update_dates_from_preset():
    preset = st.session_state.preset_selector
    today = datetime.now().date()
    if preset == "Hari Ini":
        st.session_state.date_picker = (today, today)
    elif preset == "Kemarin":
        st.session_state.date_picker = (today - timedelta(days=1), today - timedelta(days=1))
    elif preset == "7 Hari Terakhir":
        st.session_state.date_picker = (today - timedelta(days=7), today)
    elif preset == "30 Hari Terakhir":
        st.session_state.date_picker = (today - timedelta(days=30), today)
    elif preset == "Semua Waktu":
        if 'global_min_date' in st.session_state and 'global_max_date' in st.session_state:
            st.session_state.date_picker = (st.session_state.global_min_date, st.session_state.global_max_date)

def update_preset_from_dates():
    dates = st.session_state.date_picker
    today = datetime.now().date()
    if isinstance(dates, (tuple, list)) and len(dates) == 2:
        start, end = dates
        if start == today and end == today:
            st.session_state.preset_selector = "Hari Ini"
        elif start == today - timedelta(days=1) and end == today - timedelta(days=1):
            st.session_state.preset_selector = "Kemarin"
        elif start == today - timedelta(days=7) and end == today:
            st.session_state.preset_selector = "7 Hari Terakhir"
        elif start == today - timedelta(days=30) and end == today:
            st.session_state.preset_selector = "30 Hari Terakhir"
        else:
            st.session_state.preset_selector = "Kustom"
    else:
        st.session_state.preset_selector = "Kustom"

st.set_page_config(page_title="TikTok Ads Dashboard", layout="wide", page_icon="📈")

# ─────────────────────────────────────────────────────────────
# LIGHT THEME CUSTOM CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    .stApp { background: #F8F9FA; color: #1F2937; font-family: 'Inter', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }
    section[data-testid="stSidebar"] { background: #FFFFFF !important; border-right: 1px solid #E5E7EB; }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 { color: #FE2C55 !important; font-weight: 700; }
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label { color: #4B5563 !important; }
    
    h1 {
        background: linear-gradient(90deg, #FE2C55 0%, #00E5FF 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 900 !important; font-size: 2.4rem !important; letter-spacing: -0.5px;
    }
    h2, h3 { color: #111827 !important; font-weight: 700 !important; }
    h4 { color: #6B7280 !important; font-weight: 700 !important; font-size: 0.95rem !important; text-transform: uppercase; letter-spacing: 1.2px; }
    p, span, div { color: #374151; }

    div[data-testid="stMetric"] {
        background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 16px; padding: 20px 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); border-color: #FE2C55;
    }
    div[data-testid="stMetricLabel"] { color: #6B7280 !important; font-size: 0.8rem !important; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; }
    div[data-testid="stMetricValue"] { color: #111827 !important; font-weight: 800 !important; font-size: 1.6rem !important; }

    .streamlit-expanderHeader {
        background: #FFFFFF !important; border: 1px solid #E5E7EB !important; border-radius: 12px !important;
        color: #111827 !important; font-weight: 600 !important; font-size: 0.95rem !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); transition: all 0.3s ease;
    }
    .streamlit-expanderHeader:hover { border-color: #00E5FF !important; background: #F9FAFB !important; }
    .streamlit-expanderContent { background: #FFFFFF !important; border: 1px solid #E5E7EB !important; border-top: none !important; border-radius: 0 0 12px 12px !important; }

    .stDataFrame { border-radius: 12px; overflow: hidden; border: 1px solid #E5E7EB; }
    [data-testid="stDataFrame"] div, [data-testid="stDataFrame"] span { color: #111827 !important; }

    .stSelectbox > div > div, .stMultiSelect > div > div { background-color: #FFFFFF !important; border: 1px solid #D1D5DB !important; border-radius: 10px !important; color: #111827 !important; }

    .stFileUploader section { border: 2px dashed #D1D5DB !important; border-radius: 16px !important; background: #FFFFFF !important; transition: border-color 0.3s ease; }
    .stFileUploader section:hover { border-color: #FE2C55 !important; background: #FFF5F7 !important; }

    .js-plotly-plot { border-radius: 16px; overflow: hidden; background: #FFFFFF; border: 1px solid #E5E7EB; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); padding: 10px; margin-bottom: 20px;}

    hr { border: none; height: 1px; background: linear-gradient(90deg, transparent 0%, #D1D5DB 30%, #D1D5DB 70%, transparent 100%); margin: 2.5rem 0; }

    .stAlert { border-radius: 12px !important; border: 1px solid #E5E7EB !important; background: #FFFFFF !important; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); }
    .stAlert p { color: #374151 !important; }

    .section-title { display: flex; align-items: center; gap: 12px; margin: 2.5rem 0 1.2rem 0; }
    .section-title .icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; flex-shrink: 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .section-title .icon.pink { background: linear-gradient(135deg, #FE2C55, #FF6B81); color: white;}
    .section-title .icon.cyan { background: linear-gradient(135deg, #00E5FF, #00B8D4); color: white;}
    .section-title .icon.purple { background: linear-gradient(135deg, #9C27B0, #CE93D8); color: white;}
    .section-title .text h3 { margin: 0 !important; font-size: 1.2rem !important; color: #111827 !important; }
    .section-title .text p { margin: 0; font-size: 0.85rem; color: #6B7280; }

    .rec-card { background: #FFFFFF; border-left: 5px solid; border-radius: 8px 12px 12px 8px; padding: 18px 24px; margin: 12px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: transform 0.2s ease, box-shadow 0.2s ease; }
    .rec-card:hover { transform: translateX(4px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .rec-card.danger { border-left-color: #FE2C55; }
    .rec-card.warning { border-left-color: #F59E0B; }
    .rec-card.success { border-left-color: #10B981; }
    .rec-card p { margin: 0; color: #374151; font-size: 0.95rem; line-height: 1.6; }
    .rec-card strong { color: #111827; }
</style>
""", unsafe_allow_html=True)

CHART_LAYOUT = dict(
    template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#4B5563", size=12),
    title_font=dict(size=15, color="#111827", family="Inter", weight="bold"),
    margin=dict(l=20, r=20, t=50, b=20),
    legend=dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="#E5E7EB", borderwidth=1, font=dict(size=11, color="#374151")),
    xaxis=dict(gridcolor="#F3F4F6", zerolinecolor="#E5E7EB", tickfont=dict(color="#6B7280")),
    yaxis=dict(gridcolor="#F3F4F6", zerolinecolor="#E5E7EB", tickfont=dict(color="#6B7280")),
)

PINK, CYAN, GREEN, PURPLE, ORANGE = "#FE2C55", "#00B8D4", "#10B981", "#8B5CF6", "#F59E0B"
COLORS = [PINK, CYAN, GREEN, PURPLE, ORANGE, "#EC4899", "#06B6D4", "#84CC16"]

def section_title(icon, title, subtitle, color_class="pink"):
    st.markdown(f'<div class="section-title"><div class="icon {color_class}">{icon}</div><div class="text"><h3>{title}</h3><p>{subtitle}</p></div></div>', unsafe_allow_html=True)

def rec_card(text, level="warning"):
    st.markdown(f'<div class="rec-card {level}"><p>{text}</p></div>', unsafe_allow_html=True)

# Helper function to group by Video ID
def aggregate_videos(df):
    if 'Video ID' not in df.columns: return df
    
    aggs = {
        'Video Title': 'first',
        'TikTok Account': 'first',
        'Cost': 'sum',
        'Gross Revenue': 'sum',
        'SKU Orders': 'sum'
    }
    
    retention_cols = ['View Rate 2s', 'View Rate 6s', 'View Rate 25%', 'View Rate 50%', 'View Rate 75%', 'View Rate 100%']
    for c in retention_cols:
        if c in df.columns: aggs[c] = 'mean'
    
    def join_campaigns(x):
        return ", ".join(sorted(list(set([str(i) for i in x.dropna()]))))
    
    aggs['Campaign Name'] = join_campaigns
    
    grouped = df.groupby('Video ID').agg(aggs).reset_index()
    
    grouped['ROI'] = grouped['Gross Revenue'] / grouped['Cost'].replace(0, 1)
    grouped['Cost Per Order'] = grouped['Cost'] / grouped['SKU Orders'].replace(0, 1)
    grouped.loc[grouped['SKU Orders'] == 0, 'Cost Per Order'] = 0
    
    if 'CTR' in df.columns:
        ctr_map = df.groupby('Video ID')['CTR'].mean().to_dict()
        grouped['CTR'] = grouped['Video ID'].map(ctr_map)
    if 'Conversion Rate' in df.columns:
        cr_map = df.groupby('Video ID')['Conversion Rate'].mean().to_dict()
        grouped['Conversion Rate'] = grouped['Video ID'].map(cr_map)
        
    return grouped


# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.markdown('<div style="text-align:center; padding: 1rem 0 0.5rem 0;"><h1 style="font-size:2.8rem !important; margin-bottom:8px;">📈 TikTok Ads Analytics</h1><p style="color:#6B7280; font-size:1.05rem; margin-top:0;">Visualisasi interaktif &amp; insight cerdas untuk memaksimalkan profit kampanye iklan Anda</p></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="text-align:center; padding:0.5rem 0 1rem 0;"><span style="font-size:2.5rem;">🎯</span><h2 style="margin:8px 0 0 0; font-size:1.3rem; color:#111827 !important;">Dashboard Control</h2><p style="color:#6B7280; font-size:0.85rem; margin:4px 0 0 0;">Upload &amp; filter data Anda</p></div>', unsafe_allow_html=True)
    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Upload File TikTok Ads", type=['csv', 'tsv', 'xlsx'])
    st.markdown("---")

if uploaded_file is not None:
    with st.spinner("⏳ Memproses & membersihkan data..."):
        df, error = load_and_clean_data(uploaded_file)
        
    if error:
        st.error(f"❌ Gagal memproses file: {error}")
    elif df is not None and not df.empty:
        if 'Video Title' not in df.columns:
            df['Video Title'] = df.get('Video ID', df.get('Campaign Name', 'Unknown'))
            
        st.sidebar.markdown('<p style="color:#4B5563; font-weight:700; font-size:0.85rem; letter-spacing:1px; text-transform:uppercase;">🔍 Filter Data</p>', unsafe_allow_html=True)
        
        # 1. Date Filter with Presets (Bidirectional Sync)
        if 'Post Time' in df.columns:
            valid_dates = pd.to_datetime(df['Post Time']).dropna()
            if not valid_dates.empty:
                min_date = valid_dates.min().date()
                max_date = valid_dates.max().date()
                today = datetime.now().date()
                
                st.session_state.global_min_date = min_date
                st.session_state.global_max_date = max_date
                
                # Initialize default state to 7 Hari Terakhir
                if 'preset_selector' not in st.session_state:
                    st.session_state.preset_selector = "7 Hari Terakhir"
                if 'date_picker' not in st.session_state:
                    st.session_state.date_picker = (today - timedelta(days=7), today)
                
                preset = st.sidebar.selectbox(
                    "Pilih Rentang Waktu", 
                    ["Hari Ini", "Kemarin", "7 Hari Terakhir", "30 Hari Terakhir", "Semua Waktu", "Kustom"], 
                    key='preset_selector',
                    on_change=update_dates_from_preset
                )
                
                date_range = st.sidebar.date_input(
                    "Interval Tanggal", 
                    key='date_picker',
                    on_change=update_preset_from_dates
                )
            else:
                date_range = []
        else:
            date_range = []
        
        # 2. Campaign Filter
        campaigns = df['Campaign Name'].dropna().unique().tolist()
        selected_campaigns = st.sidebar.multiselect("Kampanye", campaigns, default=campaigns)
        
        # 3. Status Filter
        statuses = df['Status'].dropna().unique().tolist() if 'Status' in df.columns else []
        selected_statuses = st.sidebar.multiselect("Status", statuses, default=statuses)

        # APPLY FILTERS
        filtered_df = df[df['Campaign Name'].isin(selected_campaigns)]
        if statuses:
            filtered_df = filtered_df[filtered_df['Status'].isin(selected_statuses)]
        
        if len(date_range) == 2 and 'Post Time' in filtered_df.columns:
            start_d, end_d = date_range
            filtered_df = filtered_df[
                (filtered_df['Post Time'].dt.date >= start_d) & 
                (filtered_df['Post Time'].dt.date <= end_d)
            ]
            
        agg_vids_df = aggregate_videos(filtered_df)

        # ─── KEY METRICS ──────────────────────
        section_title("📊", "Ringkasan Kinerja", f"{len(agg_vids_df)} materi unik dari {len(selected_campaigns)} kampanye", "cyan")
        
        col1, col2, col3, col4 = st.columns(4)
        total_cost = filtered_df['Cost'].sum()
        total_rev = filtered_df['Gross Revenue'].sum()
        total_orders = filtered_df['SKU Orders'].sum()
        avg_roi = total_rev / total_cost if total_cost > 0 else 0
        
        col1.metric("💸 Total Spend", f"Rp {total_cost:,.0f}")
        col2.metric("💰 Revenue", f"Rp {total_rev:,.0f}")
        col3.metric("📦 Pesanan", f"{total_orders:,.0f}")
        col4.metric("🚀 Global ROI", f"{avg_roi:.2f}x")

        st.markdown("---")

        # ═══════════════════════════════════════
        # SECTION A: ORDER & DAILY SPEND TABLE
        # ═══════════════════════════════════════
        section_title("🛒", "Analisis Kampanye & Pengeluaran", "Tinjauan mendalam performa per kampanye", "pink")

        # ── Chart 1: Order per Kampanye ──
        camp_order = filtered_df.groupby('Campaign Name').agg({
            'Cost':'sum', 'SKU Orders':'sum', 'Gross Revenue':'sum'
        }).reset_index()
        camp_order['Cost Per Order'] = camp_order['Cost'] / camp_order['SKU Orders'].replace(0, 1)
        camp_order = camp_order.sort_values('SKU Orders', ascending=False)

        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=camp_order['Campaign Name'], y=camp_order['SKU Orders'],
            marker=dict(color=CYAN, line=dict(width=0)),
            text=[f"{int(r)}" for r in camp_order['SKU Orders']],
            textposition='outside', textfont=dict(color="#111827", size=13, family="Inter", weight="bold"),
            hovertemplate="<b>%{x}</b><br>Pesanan: %{y}<extra></extra>"
        ))
        fig1.update_layout(**CHART_LAYOUT, title="Pesanan per Kampanye", showlegend=False, yaxis_title="Jumlah Pesanan (Order)", bargap=0.3)
        st.plotly_chart(fig1, use_container_width=True)
        
        with st.expander("📋 Lihat Detail Kampanye"):
            display_camp = camp_order.copy()
            display_camp.columns = ['Kampanye', 'Spend (Rp)', 'Pesanan', 'Revenue (Rp)', 'Biaya per Pesanan (Rp)']
            st.dataframe(display_camp.style.format({
                'Spend (Rp)': 'Rp {:,.0f}',
                'Revenue (Rp)': 'Rp {:,.0f}',
                'Biaya per Pesanan (Rp)': 'Rp {:,.0f}'
            }), use_container_width=True, hide_index=True)

        # ── Chart 1.5: Spend per Kampanye ──
        camp_spend = camp_order.sort_values('Cost', ascending=False)
        fig_spend = go.Figure()
        fig_spend.add_trace(go.Bar(
            x=camp_spend['Campaign Name'], y=camp_spend['Cost'],
            marker=dict(color=PINK, line=dict(width=0)),
            text=[f"Rp {v/1000:,.0f}K" if v > 1000 else f"Rp {v:,.0f}" for v in camp_spend['Cost']],
            textposition='outside', textfont=dict(color="#111827", size=11, family="Inter", weight="bold"),
            hovertemplate="<b>%{x}</b><br>Spend: Rp %{y:,.0f}<extra></extra>"
        ))
        fig_spend.update_layout(**CHART_LAYOUT, title="Total Spend per Kampanye", showlegend=False, yaxis_title="Biaya (IDR)", bargap=0.3)
        st.plotly_chart(fig_spend, use_container_width=True)

        with st.expander("📅 Tabel Detail Spend Harian (Pivot)"):
            if 'Post Time' in filtered_df.columns:
                daily_df = filtered_df.dropna(subset=['Post Time']).copy()
                daily_df['Date'] = daily_df['Post Time'].dt.date
                if not daily_df.empty:
                    pivot_spend = pd.pivot_table(daily_df, values='Cost', index='Date', columns='Campaign Name', aggfunc='sum', fill_value=0)
                    pivot_spend = pivot_spend.sort_index(ascending=True)
                    pivot_spend.loc['TOTAL SPEND'] = pivot_spend.sum()
                    st.dataframe(pivot_spend.style.format("Rp {:,.0f}"), use_container_width=True)
                else:
                    st.info("Data waktu posting (tanggal) tidak valid.")
            else:
                st.info("Kolom Post Time tidak ditemukan.")

        st.markdown("---")

        # ═══════════════════════════════════════
        # SECTION B: EFISIENSI & RETENSI
        # ═══════════════════════════════════════
        section_title("⚡", "Retensi Penonton & CPA", "Evaluasi AI per video dan metrik biaya akuisisi terendah", "cyan")
        
        # ── Chart 3: Funnel Retensi Penonton ──
        retention_cols = ['View Rate 2s', 'View Rate 6s', 'View Rate 25%', 'View Rate 50%', 'View Rate 75%', 'View Rate 100%']
        available_cols = [c for c in retention_cols if c in filtered_df.columns]
        if available_cols:
            stage_labels = ['👁️ 2 Detik', '⏱️ 6 Detik', '📊 25%', '📈 50%', '🎯 75%', '🏆 100%']
            ret_means = filtered_df[available_cols].mean()
            
            fig3 = go.Figure(go.Funnel(
                y=stage_labels[:len(available_cols)], x=ret_means.values,
                textposition="inside", textinfo="value+percent initial", textfont=dict(size=14, family="Inter", color="#ffffff", weight="bold"),
                marker=dict(color=[PINK, ORANGE, PURPLE, CYAN, GREEN, "#84CC16"][:len(available_cols)], line=dict(width=0)),
                connector=dict(line=dict(color="#E5E7EB", width=2)),
                hovertemplate="<b>%{y}</b><br>Rata-rata: %{x:.1f}%<extra></extra>"
            ))
            fig3.update_layout(**CHART_LAYOUT, title="Funnel Retensi Penonton (Rata-rata)")
            st.plotly_chart(fig3, use_container_width=True)
            
            with st.expander("🤖 Detail Evaluasi AI & Analisis Retensi per Video (Unik)"):
                if 'Video ID' in agg_vids_df.columns:
                    ret_detail = agg_vids_df[agg_vids_df['Cost'] > 0][['Video ID', 'Campaign Name', 'TikTok Account'] + available_cols].copy()
                    ret_detail['🤖 AI Feedback'] = ret_detail.apply(evaluate_retention_ai, axis=1)
                    
                    ret_detail['Tautan Video'] = "https://www.tiktok.com/@" + ret_detail['TikTok Account'].astype(str).str.replace(' ', '') + "/video/" + ret_detail['Video ID'].astype(str)
                    
                    if 'View Rate 6s' in ret_detail.columns:
                        ret_detail = ret_detail.sort_values('View Rate 6s', ascending=False)
                    
                    display_ret = ret_detail[['Video ID', 'Campaign Name', 'Tautan Video', '🤖 AI Feedback'] + available_cols]
                    
                    st.dataframe(
                        display_ret,
                        column_config={
                            "Tautan Video": st.column_config.LinkColumn("Tautan Video", display_text="Buka Video ↗")
                        },
                        use_container_width=True, hide_index=True
                    )
                else:
                    st.info("Video ID tidak ditemukan di dalam data.")
        else:
            st.info("Data rasio tayang tidak tersedia.")

        # ── Chart 4: Top 10 CPA ──
        if 'Cost Per Order' in agg_vids_df.columns:
            # Filter CPR > 0 and sort
            cpa_df = agg_vids_df[agg_vids_df['Cost Per Order'] > 0].sort_values('Cost Per Order', ascending=True).head(10)
            if not cpa_df.empty:
                # Better labels
                cpa_df['Label'] = "ID: " + cpa_df['Video ID'].astype(str).str[-6:] + " (" + cpa_df['TikTok Account'].astype(str) + ")"
                
                fig4 = go.Figure(go.Bar(
                    x=cpa_df['Cost Per Order'], y=cpa_df['Label'], orientation='h',
                    marker=dict(color=cpa_df['Cost Per Order'], colorscale=[[0, GREEN], [0.5, CYAN], [1, PINK]], line=dict(width=0)),
                    text=[f"Rp {v:,.0f}" for v in cpa_df['Cost Per Order']],
                    textposition='outside', textfont=dict(color="#111827", size=12, weight="bold"),
                    hovertemplate="<b>%{y}</b><br>CPA: Rp %{x:,.0f}<extra></extra>"
                ))
                fig4.update_layout(**CHART_LAYOUT, title="Top 10 CPA Termurah (Biaya / Pesanan per Video Unik)", xaxis_title="Rupiah")
                fig4.update_yaxes(categoryorder='total descending')
                st.plotly_chart(fig4, use_container_width=True)
                
                with st.expander("📋 Detail Top CPA Video"):
                    cpa_detail = cpa_df[['Video ID', 'Campaign Name', 'TikTok Account', 'Cost', 'Cost Per Order', 'Gross Revenue', 'SKU Orders']].copy()
                    cpa_detail['Tautan Video'] = "https://www.tiktok.com/@" + cpa_detail['TikTok Account'].astype(str).str.replace(' ', '') + "/video/" + cpa_detail['Video ID'].astype(str)
                    
                    cpa_detail = cpa_detail[['Video ID', 'Campaign Name', 'Tautan Video', 'Cost', 'Cost Per Order', 'Gross Revenue', 'SKU Orders']]
                    cpa_detail.columns = ['Video ID', 'Campaign Name', 'Tautan Video', 'Spend (Rp)', 'CPA (Rp)', 'Revenue (Rp)', 'Pesanan']
                    
                    st.dataframe(cpa_detail.style.format({
                        'Spend (Rp)': 'Rp {:,.0f}', 'CPA (Rp)': 'Rp {:,.0f}', 'Revenue (Rp)': 'Rp {:,.0f}'
                    }), column_config={
                        "Tautan Video": st.column_config.LinkColumn("Tautan Video", display_text="Buka ↗")
                    }, use_container_width=True, hide_index=True)
            else:
                st.info("Belum ada video dengan data CPA / Pesanan.")
        else:
            st.info("Kolom CPA tidak ditemukan.")

        st.markdown("---")

        # ═══════════════════════════════════════
        # SECTION C: KONVERSI, PENJUALAN, AKUN
        # ═══════════════════════════════════════
        section_title("🎯", "Konversi, Penjualan & Performa Kreator", "Analisis kuadran, top video, dan partner terbaik", "purple")
        
        # ── Chart 5: Kuadran CTR vs Conversion ──
        if 'CTR' in agg_vids_df.columns and 'Conversion Rate' in agg_vids_df.columns:
            valid_scatter = agg_vids_df[(agg_vids_df['CTR'] > 0) | (agg_vids_df['Conversion Rate'] > 0)].copy()
            if not valid_scatter.empty:
                med_ctr = valid_scatter['CTR'].median()
                med_cr = valid_scatter['Conversion Rate'].median()
                
                def classify(row):
                    if row['CTR'] >= med_ctr and row['Conversion Rate'] >= med_cr: return "⭐ Star (Winner)"
                    elif row['CTR'] >= med_ctr and row['Conversion Rate'] < med_cr: return "⚡ Clickbait"
                    elif row['CTR'] < med_ctr and row['Conversion Rate'] >= med_cr: return "💎 Niche"
                    else: return "❌ Underperformer"
                
                valid_scatter['Quadrant'] = valid_scatter.apply(classify, axis=1)
                q_colors = {"⭐ Star (Winner)": GREEN, "⚡ Clickbait": ORANGE, "💎 Niche": CYAN, "❌ Underperformer": PINK}
                
                fig5 = px.scatter(
                    valid_scatter, x='CTR', y='Conversion Rate', size='Cost', color='Quadrant',
                    color_discrete_map=q_colors, hover_name='Video ID', hover_data={'Campaign Name': True, 'Cost': ':,.0f'}
                )
                fig5.add_hline(y=med_cr, line_dash="dot", line_color="#9CA3AF")
                fig5.add_vline(x=med_ctr, line_dash="dot", line_color="#9CA3AF")
                
                fig5.add_annotation(x=valid_scatter['CTR'].max()*0.85, y=valid_scatter['Conversion Rate'].max()*0.9, text="⭐ STAR", showarrow=False, font=dict(color=GREEN, size=12, family="Inter", weight="bold"))
                fig5.add_annotation(x=valid_scatter['CTR'].max()*0.85, y=valid_scatter['Conversion Rate'].min(), text="⚡ CLICKBAIT", showarrow=False, font=dict(color=ORANGE, size=11, family="Inter", weight="bold"))
                fig5.add_annotation(x=valid_scatter['CTR'].min()*1.1, y=valid_scatter['Conversion Rate'].max()*0.9, text="💎 NICHE", showarrow=False, font=dict(color=CYAN, size=11, family="Inter", weight="bold"))
                fig5.add_annotation(x=valid_scatter['CTR'].min()*1.1, y=valid_scatter['Conversion Rate'].min(), text="❌ WEAK", showarrow=False, font=dict(color=PINK, size=11, family="Inter", weight="bold"))
                
                fig5.update_layout(**CHART_LAYOUT, title="Kuadran CTR vs Conversion Rate")
                st.plotly_chart(fig5, use_container_width=True)
                
                with st.expander("📋 Detail Video per Kuadran"):
                    tab1, tab2, tab3, tab4 = st.tabs(["⭐ Star", "⚡ Clickbait", "💎 Niche", "❌ Under"])
                    for tab, q_name in zip([tab1, tab2, tab3, tab4], q_colors.keys()):
                        with tab:
                            q_df = valid_scatter[valid_scatter['Quadrant'] == q_name][['Video ID', 'Campaign Name', 'CTR', 'Conversion Rate', 'Cost', 'SKU Orders']]
                            if q_df.empty: st.caption("Tidak ada video di kuadran ini.")
                            else: st.dataframe(q_df, use_container_width=True, hide_index=True)
            else: st.info("Tidak cukup data CTR/CR.")

        # ── Chart 6: Top Videos + Detail ──
        if 'Video ID' in agg_vids_df.columns:
            top5 = agg_vids_df.nlargest(5, 'SKU Orders')
            top5['Label'] = "ID: " + top5['Video ID'].astype(str).str[-6:]
            
            fig6 = go.Figure(go.Pie(
                labels=top5['Label'], values=top5['SKU Orders'], hole=0.55,
                marker=dict(colors=COLORS[:len(top5)], line=dict(color='#FFFFFF', width=2)),
                textfont=dict(size=12, family="Inter", color="#111827", weight="bold"),
                hovertemplate="<b>%{label}</b><br>Pesanan: %{value}<br>Share: %{percent}<extra></extra>"
            ))
            fig6.update_layout(**CHART_LAYOUT, title="Top 5 Video (Pesanan Terbanyak)", annotations=[dict(text=f"<b>{int(top5['SKU Orders'].sum())}</b><br>Total", x=0.5, y=0.5, font_size=18, font_color="#111827", showarrow=False, font_family="Inter")])
            st.plotly_chart(fig6, use_container_width=True)
            
            with st.expander("📋 Detail Seluruh Penjualan Video"):
                all_vids = agg_vids_df[['Video ID', 'Campaign Name', 'SKU Orders', 'Cost Per Order', 'Cost', 'ROI']].copy()
                all_vids = all_vids.sort_values('SKU Orders', ascending=False)
                all_vids.columns = ['Kode Video', 'Campaign Name', 'Pesanan', 'CPR (Rp)', 'Spend (Rp)', 'ROI']
                st.dataframe(all_vids.style.format({'CPR (Rp)': 'Rp {:,.0f}', 'Spend (Rp)': 'Rp {:,.0f}', 'ROI': '{:.2f}x'}), use_container_width=True, hide_index=True)

        st.markdown("---")

        # ── Chart 7: Kinerja Akun TikTok ──
        section_title("👥", "Kinerja Kreator / Afiliasi", "Akun TikTok mana yang mendatangkan GMV terbesar?", "pink")
        
        if 'TikTok Account' in filtered_df.columns:
            acc_perf = filtered_df.groupby('TikTok Account').agg({'Gross Revenue':'sum', 'Cost':'sum', 'SKU Orders':'sum'}).reset_index()
            acc_perf['ROI'] = acc_perf['Gross Revenue'] / acc_perf['Cost'].replace(0, 1)
            acc_perf = acc_perf[acc_perf['Gross Revenue'] > 0].sort_values('Gross Revenue', ascending=True)
            
            if not acc_perf.empty:
                # Combine creator metrics nicely inside the layout
                fig7 = go.Figure()
                fig7.add_trace(go.Bar(
                    x=acc_perf['Gross Revenue'], y=acc_perf['TikTok Account'], orientation='h', name='Revenue',
                    marker=dict(color=acc_perf['Gross Revenue'], colorscale=[[0, '#E0F2FE'], [1, CYAN]], line=dict(width=0)),
                    text=[f"Rp {v:,.0f}" for v in acc_perf['Gross Revenue']], textposition='outside', textfont=dict(color="#111827", size=12, weight="bold"),
                    hovertemplate="<b>%{y}</b><br>Revenue: Rp %{x:,.0f}<extra></extra>"
                ))
                fig7.update_layout(**CHART_LAYOUT, title="Revenue per Akun TikTok", xaxis_title="Gross Revenue (IDR)", height=max(300, len(acc_perf)*45))
                st.plotly_chart(fig7, use_container_width=True)
                
                best = acc_perf.iloc[-1]
                st.markdown(f"""
                <div style="background: #FFFFFF; border:2px solid {CYAN}; border-radius:16px; padding:24px; text-align:center; box-shadow: 0 4px 6px rgba(0, 184, 212, 0.1); max-width: 600px; margin: 0 auto;">
                    <p style="color:#6B7280; font-size:0.8rem; text-transform:uppercase; font-weight:700; letter-spacing:1.5px; margin:0;">🏆 Top Kreator Berdasarkan Revenue</p>
                    <h3 style="color:#111827 !important; margin:12px 0 8px 0; font-size:1.6rem;">{best['TikTok Account']}</h3>
                    <p style="color:#4B5563; font-size:1rem; margin:0;">Total Revenue: <strong style="color:{PINK}; font-size:1.2rem;">Rp {best['Gross Revenue']:,.0f}</strong></p>
                    <hr style="margin:16px 0;">
                    <p style="color:#4B5563; font-size:1rem; margin:0;">Pesanan: <strong>{int(best['SKU Orders'])}</strong> &nbsp;|&nbsp; ROI: <strong style="color:{GREEN};">{best['ROI']:.1f}x</strong></p>
                </div>
                """, unsafe_allow_html=True)
            else: st.info("Tidak ada data revenue berdasarkan akun.")

        st.markdown("---")

        # ═══════════════════════════════════════
        # SECTION D: KESIMPULAN & SARAN
        # ═══════════════════════════════════════
        section_title("💡", "Kesimpulan & Saran Optimasi", "Analisis cerdas otomatis berdasarkan metrik kampanye Anda", "cyan")
        
        recs = generate_recommendations(filtered_df)
        rec_lines = recs.split("\n\n")
        for line in rec_lines:
            if "🔴" in line: rec_card(line.replace("**", "<strong>").replace("**", "</strong>"), "danger")
            elif "🟡" in line: rec_card(line.replace("**", "<strong>").replace("**", "</strong>"), "warning")
            elif "🟢" in line: rec_card(line.replace("**", "<strong>").replace("**", "</strong>"), "success")
            else: st.markdown(f"<p style='color:#374151;'>{line}</p>", unsafe_allow_html=True)

        st.markdown('<div style="text-align:center; padding:3rem 0 1rem 0; color:#9CA3AF; font-size:0.8rem; font-weight:500;"><p>Built with ❤️ using Streamlit & Plotly · TikTok Ads Analytics Dashboard v3</p></div>', unsafe_allow_html=True)

else:
    # ── EMPTY STATE ──
    st.markdown("""
    <div style="text-align:center; padding: 5rem 2rem;">
        <div style="display:inline-block; width:120px; height:120px; border-radius:50%; 
                    background: #FFF5F7;
                    display:flex; align-items:center; justify-content:center; margin:0 auto 1.5rem auto;
                    border: 2px dashed #FECDD3;">
            <span style="font-size:3.5rem; display:block; text-align:center; line-height:120px;">📂</span>
        </div>
        <h2 style="color:#111827 !important; margin-bottom:8px;">Belum Ada Data</h2>
        <p style="color:#6B7280; max-width:480px; margin:0 auto; line-height:1.7; font-size:1rem;">
            Upload file ekspor TikTok Ads Anda melalui panel <strong style="color:#FE2C55;">sidebar di sebelah kiri</strong> 
            untuk melihat dashboard analitik lengkap.
        </p>
    </div>
    """, unsafe_allow_html=True)
