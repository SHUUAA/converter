import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import zipfile

st.title("📄 Libre convert uwu")

uploaded_files = st.file_uploader("Upload multiple PDF files", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    try:
        zip_buffer = io.BytesIO()  # Create a ZIP buffer

        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            stored_files = {}  # Dictionary to store file content for reuse

            # Read and store uploaded files in memory (fixes "Cannot open empty stream" issue)
            for uploaded_file in uploaded_files:
                stored_files[uploaded_file.name] = uploaded_file.read()

            # Convert and save images
            for file_name, file_content in stored_files.items():
                pdf_document = fitz.open(stream=file_content, filetype="pdf")
                total_pages = len(pdf_document)

                for i in range(total_pages):
                    page = pdf_document[i]
                    
                    # High-quality rendering (216 DPI)
                    zoom = 3.0  # Adjust zoom for higher quality
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                    # Save image to buffer
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format="PNG", quality=100)
                    img_bytes = img_buffer.getvalue()

                    # Save each PNG inside the ZIP file
                    zipf.writestr(f"{file_name.replace('.pdf', '')}_page_{i+1}.png", img_bytes)

        # Display the download button at the top
        st.download_button(
            label="📥 Download All HD PNGs as ZIP",
            data=zip_buffer.getvalue(),
            file_name="converted_hd_images.zip",
            mime="application/zip"
        )

        # Display images below the download button
        for file_name, file_content in stored_files.items():
            pdf_document = fitz.open(stream=file_content, filetype="pdf")
            total_pages = len(pdf_document)

            st.write(f"📘 **Processing:** {file_name} ({total_pages} pages)")

            for i in range(total_pages):
                page = pdf_document[i]
                pix = page.get_pixmap(matrix=fitz.Matrix(3.0, 3.0))  # 216 DPI
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                # Convert to byte stream for Streamlit display
                img_buffer = io.BytesIO()
                img.save(img_buffer, format="PNG")
                img_bytes = img_buffer.getvalue()

                # Show the image with the updated parameter
                st.image(img_bytes, caption=f"{file_name} - Page {i+1} (HD)", use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
