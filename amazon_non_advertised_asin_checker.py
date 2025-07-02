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

    This file contains all ASINs you're currently selling.

    #### 🟢 Step 2: Export a List of ASINs Being Advertised
    - Go to: **Advertising Console** → **Campaign Manager**
    - Select **Sponsored Products**
    - Download a **Campaign Performance Report**:
        - Go to **Reports > Campaign Reports**
        - Choose **Sponsored Products**
        - Select either **Targeting Report** or **Advertised Products Report**
        - Pick a relevant date range (e.g., last 30 days)
        - Download the file

    This report includes ASINs you're currently advertising.

    ---

    ### ✅ Upload both files on the next tab
    Just upload your **Active Listings** and **Advertised ASINs** files, and we’ll instantly show you the ASINs that are **not being advertised**.
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

    # Upload files
    active_file = st.file_uploader("📤 Upload Active ASINs file", type=['csv', 'xlsx', 'tsv'])
    ads_file = st.file_uploader("📤 Upload Advertised ASINs file", type=['csv', 'xlsx', 'tsv'])

    if active_file and ads_file:
        df_active = read_file(active_file)
        df_ads = read_file(ads_file)

        if df_active is not None and df_ads is not None:
            # Detect ASIN columns
            def find_asin_column(df):
                for col in df.columns:
                    if 'asin' in col.lower():
                        return col
                return None

            active_col = find_asin_column(df_active)
            ads_col = find_asin_column(df_ads)

            if not active_col or not ads_col:
                st.error("Could not find an 'ASIN' column in one of the files. Please check your uploads.")
            else:
                active_asins = df_active[active_col].dropna().drop_duplicates().astype(str).str.strip()
                advertised_asins = df_ads[ads_col].dropna().astype(str).str.strip()

                non_advertised_asins = active_asins[~active_asins.isin(advertised_asins)].reset_index(drop=True)
                non_advertised_df = pd.DataFrame(non_advertised_asins, columns=["Non-Advertised ASINs"])
                non_advertised_df.index = non_advertised_df.index + 1  # Start index from 1

                st.success(f"Found {len(non_advertised_df)} non-advertised ASIN(s).")
                st.dataframe(non_advertised_df, use_container_width=True)

                # Download button
                csv = non_advertised_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Non-Advertised ASINs CSV",
                    data=csv,
                    file_name="non_advertised_asins.csv",
                    mime="text/csv"
                )

    st.markdown("---")
    st.caption("Non-Advertised ASIN Checker | Built for Amazon Sellers | Nikita Jain")
