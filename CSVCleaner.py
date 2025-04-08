import streamlit as st
import chardet
import io
import re
from datetime import datetime

st.set_page_config(page_title="Platby CSV Cleaner", layout="centered")
st.title("🧹CSV Cleaner")

uploaded_file = st.file_uploader("Upload your CSV or TXT file", type=["csv", "txt"])

def transform_filename(original_name: str) -> str:
    # Match 8-digit date pattern (e.g. 20250402)
    match = re.search(r"(20\d{2})(\d{2})(\d{2})", original_name)
    if match:
        formatted_date = f"{match.group(1)}_{match.group(2)}_{match.group(3)}"
        new_name = re.sub(r"20\d{6}", formatted_date, original_name)
        return new_name.replace(" ", "_").replace(".csv", "").replace(".txt", "") + ".csv"
    return "platby_cleaned.csv"

if uploaded_file is not None:
    raw_bytes = uploaded_file.read()
    result = chardet.detect(raw_bytes)
    encoding = result['encoding']

    try:
        raw_text = raw_bytes.decode(encoding)
        raw_lines = raw_text.splitlines()

        if len(raw_lines) < 2:
            st.error("The file doesn't contain enough lines to process.")
        else:
            # Remove the first line
            processed_lines = raw_lines[1:]
            # Replace ; with ,
            processed_lines = [line.replace(';', ',') for line in processed_lines]

            # Prepare output
            csv_string = "\r\n".join(processed_lines)
            output = io.BytesIO('\ufeff'.encode('utf-8') + csv_string.encode("utf-8"))

            # Use the original filename to generate a cleaner one
            output_filename = transform_filename(uploaded_file.name)

            st.success("✅ File processed successfully!")

            st.download_button(
                label="⬇️ Download cleaned CSV",
                data=output.getvalue(),
                file_name=output_filename,
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"❌ Could not decode the file: {str(e)}")
