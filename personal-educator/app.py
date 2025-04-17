import streamlit as st

# Streamlit page configuration
st.set_page_config(page_title="Documentation Uploader", layout="centered")

# Page title
st.title("Upload Documentation")

# File uploader
uploaded_file = st.file_uploader("Upload your documentation file", type=["txt", "pdf", "docx"])

if uploaded_file is not None:
    # Display file details
    st.write("File uploaded successfully!")
    st.write("Filename:", uploaded_file.name)
    st.write("File type:", uploaded_file.type)
    st.write("File size:", uploaded_file.size, "bytes")

    # Process the file content
    if uploaded_file.type == "text/plain":
        content = uploaded_file.read().decode("utf-8")
        st.text_area("File Content", content, height=300)
    else:
        st.write("File preview is not supported for this file type.")
else:
    st.write("Please upload a file to proceed.")