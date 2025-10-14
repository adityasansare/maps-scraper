import streamlit as st
import pandas as pd
from scraper import run_scraper

st.set_page_config(page_title="Google Maps Scraper", layout="wide")
st.title("🗺️ Google Maps Scraper (Mumbai Places)")

st.markdown("Enter a query like `Doctors in Dadar East` or `Jewelers in Tardeo`")

query = st.text_input("Search query:")
run_button = st.button("Start Scraping")

if run_button:
    if not query:
        st.warning("Please enter a search query.")
    else:
        with st.spinner("Scraping in progress... please wait ⏳"):
            data = run_scraper(query)
            if not data:
                st.error("No results found or scraping failed.")
            else:
                df = pd.DataFrame(data)
                st.success(f"✅ Found {len(df)} listings!")
                st.dataframe(df)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Download CSV", csv, f"{query.replace(' ','_')}.csv", "text/csv")
