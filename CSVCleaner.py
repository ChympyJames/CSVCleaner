import streamlit as st
import chardet
import io

st.set_page_config(page_title="Platby CSV Cleaner", layout="centered")

st.title("🧹 Platby CSV Cleaner")

uploaded_file = st.file_uploader("Upload your CSV or TXT file", type=["csv", "txt"])

if uploaded_file is not None:
    # Detect encoding using chardet
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
            output = io.StringIO("\n".join(processed_lines))
            st.success("✅ File processed successfully!")

            st.download_button(
                label="⬇️ Download cleaned CSV",
                data=output.getvalue(),
                file_name="platby_cleaned.csv",
                mime="text/csv"
            )
    except Exception as e:
        st.error(f"❌ Could not decode the file: {str(e)}")
