import streamlit as st
from yt_dlp import YoutubeDL
import tempfile
import os
import glob

st.title("🎬 YouTube High-Quality Video Downloader")
st.write("Paste a YouTube link below to download in best available quality:")

url = st.text_input("🔗 YouTube URL")

# Session state setup
if "is_downloading" not in st.session_state:
    st.session_state.is_downloading = False
if "downloaded_file_data" not in st.session_state:
    st.session_state.downloaded_file_data = None
if "downloaded_file_name" not in st.session_state:
    st.session_state.downloaded_file_name = None

progress_bar = st.empty()
percent_text = st.empty()

def download_video_to_temp_folder(url):
    with tempfile.TemporaryDirectory() as tmpdir:
        def progress_hook(d):
            if d['status'] == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded_bytes = d.get('downloaded_bytes', 0)
                if total_bytes:
                    progress = downloaded_bytes / total_bytes
                    progress_bar.progress(min(progress, 1.0))
                    percent_text.markdown(f"📦 **Download Progress: {progress * 100:.2f}%**")
            elif d['status'] == 'finished':
                percent_text.markdown("✅ **Download complete. Preparing download...**")

        ydl_opts = {
            'format': 'bv*+ba/best',
            'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook],
            'quiet': True,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            downloaded_files = glob.glob(os.path.join(tmpdir, '*'))
            if not downloaded_files:
                return "ERROR::No file downloaded"

            latest_file = max(downloaded_files, key=os.path.getctime)
            with open(latest_file, 'rb') as f:
                file_data = f.read()
                file_name = os.path.basename(latest_file)
                return file_data, file_name

        except Exception as e:
            return f"ERROR::{e}"

def start_download():
    st.session_state.is_downloading = True
    st.session_state.downloaded_file_data = None
    st.session_state.downloaded_file_name = None

    result = download_video_to_temp_folder(url)
    st.session_state.is_downloading = False

    if isinstance(result, str) and result.startswith("ERROR::"):
        st.error(result.replace("ERROR::", "❌ "))
    else:
        file_data, file_name = result
        st.session_state.downloaded_file_data = file_data
        st.session_state.downloaded_file_name = file_name
        st.success("✅ Video downloaded successfully!")

# Trigger download button
if url:
    st.button("⬇️ Start Download", on_click=start_download, disabled=st.session_state.is_downloading)

# Show save file button after successful download
if st.session_state.downloaded_file_data:
    st.download_button(
        label="💾 Save Video to Your Device",
        data=st.session_state.downloaded_file_data,
        file_name=st.session_state.downloaded_file_name,
        mime="video/mp4"
    )
