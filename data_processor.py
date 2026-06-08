import pandas as pd
import numpy as np

def clean_value(val):
    if pd.isna(val) or val == '-':
        return np.nan
    val = str(val).replace('="', '').replace('"', '').strip()
    if val == '-' or val == 'N/A' or val == '':
        return np.nan
    return val

def clean_percentage(val):
    if pd.isna(val) or val == '-':
        return 0.0
    val = str(val).replace('%', '')
    try:
        return float(val)
    except:
        return 0.0

def load_and_clean_data(file):
    filename = getattr(file, "name", "")
    try:
        if filename.endswith('.csv') or filename.endswith('.tsv') or not filename:
            df = pd.read_csv(file, sep='\t', dtype=str)
            if len(df.columns) < 5:
                file.seek(0)
                df = pd.read_csv(file, sep=',', dtype=str)
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(file, dtype=str)
        else:
            df = pd.read_csv(file, sep='\t', dtype=str)
    except Exception as e:
        return None, str(e)

    if df.empty:
        return df, None

    for col in df.columns:
        df[col] = df[col].apply(clean_value)

    col_mapping = {
        'Nama kampanye': 'Campaign Name',
        'ID Campaign': 'Campaign ID',
        'ID produk': 'Product ID',
        'Jenis materi iklan': 'Ad Type',
        'Judul video': 'Video Title',
        'ID video': 'Video ID',
        'Akun TikTok': 'TikTok Account',
        'Waktu posting': 'Post Time',
        'Status': 'Status',
        'Jenis otorisasi': 'Authorization Type',
        'Biaya': 'Cost',
        'Pesanan SKU': 'SKU Orders',
        'Biaya per pesanan': 'Cost Per Order',
        'Pendapatan kotor': 'Gross Revenue',
        'ROI': 'ROI',
        'Impresi iklan produk': 'Impressions',
        'Jumlah klik iklan produk': 'Clicks',
        'Tingkat klik iklan produk': 'CTR',
        'Rasio konversi iklan': 'Conversion Rate',
        'Rasio tayang video iklan 2 detik': 'View Rate 2s',
        'Rasio tayang video iklan 6 detik': 'View Rate 6s',
        'Rasio tayang video iklan 25%': 'View Rate 25%',
        'Rasio tayang video iklan 50%': 'View Rate 50%',
        'Rasio tayang video iklan 75%': 'View Rate 75%',
        'Rasio tayang video iklan 100%': 'View Rate 100%',
        'Mata uang': 'Currency'
    }
    
    df.rename(columns=col_mapping, inplace=True)

    numeric_cols = ['Cost', 'SKU Orders', 'Cost Per Order', 'Gross Revenue', 'ROI', 'Impressions', 'Clicks']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    pct_cols = ['CTR', 'Conversion Rate', 'View Rate 2s', 'View Rate 6s', 'View Rate 25%', 'View Rate 50%', 'View Rate 75%', 'View Rate 100%']
    for col in pct_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_percentage)

    if 'Post Time' in df.columns:
        df['Post Time'] = pd.to_datetime(df['Post Time'], errors='coerce')

    return df, None

def evaluate_retention_ai(row):
    """Memberikan umpan balik teks AI sederhana berdasarkan rasio retensi."""
    # Handle missing keys
    v2 = row.get('View Rate 2s', 0)
    v6 = row.get('View Rate 6s', 0)
    v100 = row.get('View Rate 100%', 0)
    
    if v2 == 0:
        return "Tidak cukup data views."
    
    drop_to_6 = 100 - ((v6 / v2) * 100) if v2 > 0 else 100
    
    if drop_to_6 > 60:
        return "⚠️ Hook Lemah: >60% audiens kabur sebelum detik ke-6. Buat 3 detik pertama lebih memancing rasa penasaran!"
    elif v6 > 40 and drop_to_6 <= 40:
        if v100 > 10:
            return "🔥 Sangat Kuat: Hook bagus dan banyak yang menonton hingga tuntas. Layak Scale!"
        return "✅ Hook Stabil: Audiens bertahan di awal, tapi pastikan ada Call-To-Action kuat di tengah."
    elif v100 > 5:
        return "💡 Niche Audience: Menarik bagi segmen tertentu yang bersedia menonton sampai habis."
    
    return "Pertengahan membosankan, evaluasi isi video."

def generate_recommendations(df):
    recommendations = []
    if df.empty: return "Belum ada data."

    if 'Campaign Name' in df.columns:
        campaigns = df.groupby('Campaign Name').agg({'Cost': 'sum', 'Gross Revenue': 'sum'}).reset_index()
        campaigns['ROI'] = campaigns['Gross Revenue'] / campaigns['Cost'].replace(0, 1)

        for _, row in campaigns.iterrows():
            camp_name = row['Campaign Name']
            roi = row['ROI']
            if pd.isna(camp_name): continue
            
            if row['Cost'] > 0:
                if roi < 1.0:
                    recommendations.append(f"🔴 **{camp_name}**: Rugi (ROI {roi:.2f}). Matikan iklan yang jelek (Pause), evaluasi audiens/kreatif.")
                elif roi < 3.0:
                    recommendations.append(f"🟡 **{camp_name}**: ROI standar ({roi:.2f}). Lakukan A/B testing materi baru untuk meningkatkan margin.")
                else:
                    recommendations.append(f"🟢 **{camp_name}**: ROI sangat baik ({roi:.2f}). Lakukan SCALING budget harian perlahan-lahan.")

    if not recommendations:
        return "Semua kampanye stabil."
    return "\n\n".join(recommendations)
