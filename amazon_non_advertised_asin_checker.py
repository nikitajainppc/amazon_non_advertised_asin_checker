import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Non-Advertised ASIN Finder", layout="centered")

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["📘 Instructions", "📤 Upload & Analyze"])

# --------------------- PAGE 1: INSTRUCTIONS ---------------------
if page == "📘 Instructions":
    st.title("📘 Non-Advertised ASIN Checker – Instructions")
    st.markdown("""
    This tool helps **Amazon sellers** identify ASINs in their inventory that are **not currently being advertised** via Sponsored Products.

    Identifying non-advertised ASINs allows you to find missed advertising opportunities and scale campaigns more effectively.

    ---  
    ### ✅ Step-by-Step: How to Find Non-Advertised ASINs on Amazon Seller Central

    #### 🟢 Step 1: Export Your Full Catalog of Active Listings
    - Log in to **Seller Central**
    - Go to: **Inventory > Inventory Reports**
    - From the drop-down, select: **“Active Listings Report”**
    - Click **“Request Report”** and download the CSV

    #### 🟢 Step 2: Export a List of ASINs Being Advertised
    - Go to: **Advertising Console > Campaign Manager**
    - Select **Sponsored Products**
    - Go to **Reports > Campaign Reports**
    - Select **Targeting Report** or **Advertised Products Report**
    - Choose a date range (e.g., last 30 days)
    - Generate and download the report

    ---  

    ### ✅ What to do next
    Upload both files on the next tab, and the app will instantly show you which ASINs are **not being advertised**.
    """)
    st.markdown("---")
    st.caption("© 2025 Non-Advertised ASIN Checker | Built for Amazon Sellers")

# --------------------- PAGE 2: FILE UPLOAD ---------------------
elif page == "📤 Upload & Analyze":
    st.title("📤 Upload Your Files to Find Non-Advertised ASINs")

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

    def find_asin_column(df, source='active'):
        candidates = ['ASIN', 'asin', 'ASIN1', 'Advertised ASIN']
        for col in df.columns:
            if col in candidates:
                if source == 'active' and col.lower().startswith('asin'):
                    return col
                if source == 'ads' and 'Advertised ASIN' in col:
                    return col
        for col in df.columns:
            if 'asin' in col.lower():
                return col
        return None

    active_file = st.file_uploader("📤 Upload Active ASINs file", type=['csv', 'xlsx', 'tsv'])
    ads_file = st.file_uploader("📤 Upload Advertised ASINs file", type=['csv', 'xlsx', 'tsv'])

    if active_file and ads_file:
        df_active = read_file(active_file)
        df_ads = read_file(ads_file)

        if df_active is not None and df_ads is not None:
            active_col = find_asin_column(df_active, source='active')
            ads_col = find_asin_column(df_ads, source='ads')

            if not active_col or not ads_col:
                st.error("ASIN column not found. Please ensure your files have 'ASIN', 'ASIN1', or 'Advertised ASIN'.")
            else:
                # Step 1: Clean and de-duplicate
                active_asins = pd.Series(df_active[active_col].dropna().astype(str).str.upper().str.strip().unique())
                advertised_asins = pd.Series(df_ads[ads_col].dropna().astype(str).str.upper().str.strip().unique())

                # Step 2: Compare
                non_advertised_asins = active_asins[~active_asins.isin(advertised_asins)].reset_index(drop=True)
                non_advertised_df = pd.DataFrame(non_advertised_asins, columns=["Non-Advertised ASINs"])
                non_advertised_df.index += 1

                st.success(f"✅ Found {len(non_advertised_df)} non-advertised ASIN(s).")
                st.dataframe(non_advertised_df, use_container_width=True)

                # Step 3: Download
                csv = non_advertised_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Non-Advertised ASINs CSV",
                    data=csv,
                    file_name="non_advertised_asins.csv",
                    mime="text/csv"
                )

    st.markdown("---")
    st.caption("© 2025 Non-Advertised ASIN Checker | Built by Nikita Jain")
