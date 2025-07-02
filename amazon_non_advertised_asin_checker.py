import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Non-Advertised ASIN Finder", layout="centered")

st.title("🔍 Non-Advertised ASIN Checker")
st.markdown("""
Upload two files:
- **Active ASINs** (inventory)
- **Advertised ASINs** (may contain duplicates)

This app will show you the ASINs that are *not currently being advertised*.
""")

def read_file(file):
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        elif file.name.endswith('.xlsx'):
            return pd.read_excel(file)
        elif file.name.endswith('.tsv'):
            return pd.read_csv(file, sep='\t')
        else:
            st.warning("Unsupported file type. Please upload CSV, XLSX, or TSV.")
            return None
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        return None

# Upload files
active_file = st.file_uploader("📤 Upload Active ASINs file", type=['csv', 'xlsx', 'tsv'])
ads_file = st.file_uploader("📤 Upload Advertised ASINs file", type=['csv', 'xlsx', 'tsv'])

if active_file and ads_file:
    df_active = read_file(active_file)
    df_ads = read_file(ads_file)

    if df_active is not None and df_ads is not None:
        # Try to find ASIN column (case-insensitive)
        def find_asin_column(df):
            for col in df.columns:
                if 'asin' in col.lower():
                    return col
            return None

        active_col = find_asin_column(df_active)
        ads_col = find_asin_column(df_ads)

        if not active_col or not ads_col:
            st.error("Could not find ASIN column in one of the files. Please make sure at least one column is named 'ASIN'.")
        else:
            active_asins = df_active[active_col].dropna().drop_duplicates().astype(str).str.strip()
            advertised_asins = df_ads[ads_col].dropna().astype(str).str.strip()

            non_advertised_asins = active_asins[~active_asins.isin(advertised_asins)].reset_index(drop=True)

            st.success(f"Found {len(non_advertised_asins)} non-advertised ASIN(s).")
            st.dataframe(non_advertised_asins, use_container_width=True)

            # Download link
            csv = non_advertised_asins.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Non-Advertised ASINs CSV", csv, "non_advertised_asins.csv", "text/csv")
