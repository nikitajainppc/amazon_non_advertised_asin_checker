import streamlit as st
import pandas as pd
from amazon_non_advertised_asin_checker import find_non_advertised_asins

st.title(":bar_chart: Non-Advertised ASIN Finder")

active_file = st.file_uploader("Upload Active ASINs file", type=["csv", "xlsx"])
ads_file = st.file_uploader("Upload Advertised ASINs file", type=["csv", "xlsx"])

def load_file(uploaded_file):
    if uploaded_file.name.endswith('.csv'):
        return pd.read_csv(uploaded_file)
    else:
        return pd.read_excel(uploaded_file)

if active_file and ads_file:
    df_active = load_file(active_file)
    df_ads = load_file(ads_file)

    if 'ASIN' not in df_active.columns or 'ASIN' not in df_ads.columns:
        st.error("Both files must have a column named 'ASIN'")
    else:
        non_ad_asins = find_non_advertised_asins(df_active, df_ads)
        st.success(f"{len(non_ad_asins)} non-advertised ASIN(s) found.")
        st.dataframe(non_ad_asins)
        st.download_button("Download CSV", non_ad_asins.to_csv(index=False), "non_advertised_asins.csv", "text/csv")
