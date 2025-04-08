import streamlit as st
import chardet
import io
import re
from datetime import datetime

st.set_page_config(page_title="Platby CSV Cleaner", layout="centered")
st.title("🧹 CSV Cleaner – Copy into Template")

# Load the fixed template file from disk (must exist in the repo)
TEMPLATE_PATH = "template.csv"

@st.cache_data
def load_template():
    with open(TEMPLATE_PATH, "rb") as f:
        template_bytes = f.read()
    has_bom = template_bytes.startswith(b'\xef\xbb\xbf')
    return template_bytes, has_bom

template_raw, has_bom = load_template()

# Upload the source file (to clean)
source_file = st.file_uploader("📤 Upload the RAW CSV file (to clean)", type=["csv", "txt"])

def transform_filename(original_name: str) -> str:
    match = re.search(r"(20\d{2})(\d{2})(\d{2})", original_name)
    if match:
        formatted_date = f"{match.group(1)}_{match.group(2)}_{match.group(3)}"
        new_name = re.sub(r"20\d{6}", formatted_date, original_name)
        return new_name.replace(" ", "_").replace(".csv", "").replace(".txt", "") + ".csv"
    return "platby_cleaned.csv"

if source_file:
    # Step 1: Read and clean the SOURCE file
    source_raw = source_file.read()
    detected = chardet.detect(source_raw)
    try:
        source_text = source_raw.decode(detected['encoding'])
        source_lines = source_text.splitlines()
        if len(source_lines) < 2:
            st.error("❌ Source file has fewer than 2 lines.")
            st.stop()
        cleaned_lines = source_lines[1:]  # Remove first line
        cleaned_lines = [line.replace(";", ",") for line in cleaned_lines]
        cleaned_csv = "\r\n".join(cleaned_lines)  # Use CRLF line endings
    except Exception as e:
        st.error(f"❌ Failed to clean source file: {e}")
        st.stop()

    # Step 2: Replace the template's content with the cleaned content
    final_string = cleaned_csv

    # Step 3: Encode with BOM (if the template has BOM) and prepare output
    if has_bom:
        output = io.BytesIO(b'\xef\xbb\xbf' + final_string.encode("utf-8"))
    else:
        output = io.BytesIO(final_string.encode("utf-8"))

    output_filename = transform_filename(source_file.name)

    st.success("✅ File cleaned and merged into template!")

    st.download_button(
        label="⬇️ Download Final CSV",
        data=output.getvalue(),
        file_name=output_filename,
        mime="text/csv"
    )
