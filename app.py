import streamlit as st
import os
import tempfile
from blockchain import Blockchain
from certificate_processor import process_certificate

# Page configuration
st.set_page_config(
    page_title="Blockchain Certificate Verification",
    page_icon="🔐",
    layout="wide"
)

# Initialize Blockchain
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = Blockchain()

# Main App UI
st.title("📜 Blockchain Certificate Verification System")
abc = "13 May 2025"

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Issue Certificate", "Verify Certificate", "Blockchain Explorer"])

if page == "Issue Certificate":
    st.header("Issue New Certificate")
    uploaded_file = st.file_uploader("Upload Certificate Image", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        # Create a temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name

        # Process certificate
        with st.spinner("Processing certificate..."):
            cert_data = process_certificate(temp_path)

        # Remove temporary file
        os.unlink(temp_path)

        # Display extracted data
        st.subheader("Extracted Certificate Data")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {cert_data['name']}")
            st.write(f"**Degree:** {cert_data['degree']}")
            st.write(f"**Passing Year:** {cert_data['passing_year']}")
            st.write(f"**CGPA:** {cert_data['cgpa']}")
        with col2:
            st.write(f"**Degree Serial:** {cert_data['degree_serial']}")
            st.write(f"**Enrollment No:** {cert_data['enrollment_no']}")
            st.write(f"**Roll No:** {cert_data['roll_no']}")
            st.write(f"**Issue Date:** {cert_data['issue_date']}")
            st.write(f"**Certificate Hash:** {cert_data['hash']}")

        if st.button("🔗 Add to Blockchain"):
            new_block = st.session_state.blockchain.add_block(cert_data['hash'])
            st.success(f"Certificate added to blockchain! Block #{new_block.index}")

elif page == "Verify Certificate":
    st.header("Verify Certificate")
    verify_method = st.radio("Verification Method", ["Upload Image", "Enter Certificate Hash"])
    if verify_method == "Upload Image":
        uploaded_file = st.file_uploader("Upload Certificate to Verify", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            # Create a temporary file to store the upload
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_path = tmp_file.name

            # Process certificate
            with st.spinner("Processing certificate..."):
                cert_data = process_certificate(temp_path)

            # Remove temporary file
            os.unlink(temp_path)

            # Display extracted hash
            st.write(f"**Certificate Hash:** {cert_data['hash']}")

            # Verify on blockchain
            if st.button("🛡️ Verify on Blockchain"):
                is_valid, block = st.session_state.blockchain.search_certificate(cert_data['hash'])
                if is_valid:
                    st.success(f"✅ Certificate verified on blockchain! Found in Block #{block.index}")
                    st.json(cert_data)
                else:
                    st.error("❌ Certificate not found on blockchain!")
    else:  # Enter Certificate Hash
        cert_hash = st.text_input("Enter Certificate Hash")
        if cert_hash and st.button("🛡️ Verify on Blockchain"):
            is_valid, block = st.session_state.blockchain.search_certificate(cert_hash)
            if is_valid:
                st.success(f"✅ Certificate verified on blockchain! Found in Block #{block.index}")
            else:
                st.error("❌ Certificate not found on blockchain!")

elif page == "Blockchain Explorer":
    st.header("🔍 Blockchain Explorer")
    if len(st.session_state.blockchain.chain) <= 1:
        st.info("Blockchain contains only the genesis block. Issue some certificates to see more blocks.")
    for block in st.session_state.blockchain.chain:
        with st.expander(f"Block #{block.index} - {block.timestamp}"):
            st.write(f"**Previous Hash:** {block.previous_hash}")
            st.write(f"**Data:** {block.data}")
            st.write(f"**Block Hash:** {block.hash}")

# Footer
st.markdown("---")
st.markdown("Blockchain Certificate Verification System - Built with Streamlit")
