import streamlit as st
import os
import requests
from image_gen import ImageGenerator
from content_gen import ContentGenerator
from video_gen import VideoGenerator
from social_manager import SocialManager, InstagramManager
from automation import run_reel_automation, download_file
from dotenv import load_dotenv

# Page config
st.set_page_config(page_title="AI Influencer Automation", page_icon="🤖", layout="wide")

st.title("🤖 AI Influencer Automation System")

# Load environment variables
load_dotenv()

# Sidebar
st.sidebar.header("Global Settings")
mode = st.sidebar.radio("Operation Mode", ["Free (No API Key)", "OpenAI (Paid API Key)"], index=0)
provider = "free" if "Free" in mode else "openai"

api_key = os.getenv("OPENAI_API_KEY")
if provider == "openai" and not api_key:
    st.sidebar.warning("⚠️ OpenAI API Key missing.")
    api_key = st.sidebar.text_input("Enter OpenAI Key:", type="password")

st.sidebar.divider()
st.sidebar.header("Instagram Credentials")
ig_user = st.sidebar.text_input("Username", value=os.getenv("INSTAGRAM_USERNAME", ""))
ig_pass = st.sidebar.text_input("Password", value=os.getenv("INSTAGRAM_PASSWORD", ""), type="password")

# Tabs
tab_auto, tab_manual = st.tabs(["🚀 Full Automation (Topic to Reel)", "🛠 Manual Tools"])

with tab_auto:
    st.header("One-Click AI Reel Creator")
    st.write("Enter a topic and let the AI do everything: brainstorm the idea, write the script, generate the video, and post it.")

    topic = st.text_input("Topic for your Reel", placeholder="e.g., A day in the life of a digital artist")

    if st.button("🌟 Start Full Automation"):
        if not topic:
            st.error("Please enter a topic.")
        else:
            with st.spinner("Brainstorming, generating, and preparing..."):
                try:
                    results = run_reel_automation(topic, provider=provider)
                    st.session_state['auto_results'] = results
                    st.success("Automation sequence complete!")
                except Exception as e:
                    st.error(f"Automation failed: {e}")

    if 'auto_results' in st.session_state:
        res = st.session_state['auto_results']
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("The AI Plan")
            st.info(f"**Idea:** {res['plan'].get('idea')}")
            st.write(f"**Script:** {res['plan'].get('script')}")
            st.write(f"**Visual Prompt:** {res['plan'].get('visual')}")

        with col2:
            st.subheader("Generated Visuals")
            if os.path.exists(res['video_url']):
                with open(res['video_url'], 'rb') as v:
                    video_bytes = v.read()
                    st.video(video_bytes)
                    st.download_button(
                        label="⬇️ Download Reel (MP4)",
                        data=video_bytes,
                        file_name=os.path.basename(res['video_url']),
                        mime="video/mp4"
                    )
            else:
                st.video(res['video_url'])
            st.write(f"Video ready for upload.")

        st.divider()
        st.subheader("Post to Social Media")
        if st.button("📤 Upload as Instagram Reel"):
            if not ig_user or not ig_pass:
                st.error("Please provide Instagram credentials in the sidebar.")
            else:
                with st.spinner("Uploading to Instagram..."):
                    try:
                        # 1. Download
                        local_path = download_file(res['video_url'], res['local_video'])
                        # 2. Upload
                        im = InstagramManager(ig_user, ig_pass)
                        caption = f"{res['plan'].get('idea')}\n\n{res['plan'].get('script')}\n\n#AI #Influencer #Reel"
                        status = im.upload_reel(local_path, caption)
                        st.success(status)
                    except Exception as e:
                        st.error(f"Upload failed: {e}")

with tab_manual:
    st.header("Individual Generation Tools")

    col_img, col_vid = st.columns(2)

    with col_img:
        st.subheader("Image Generator")
        img_prompt = st.text_area("Image Prompt")
        if st.button("🖼 Generate Image"):
            with st.spinner("Generating..."):
                igen = ImageGenerator(api_key=api_key, provider=provider)
                url = igen.generate_image(img_prompt)
                st.image(url)
                st.write(url)

    with col_vid:
        st.subheader("Video Generator")
        vid_prompt = st.text_area("Video Prompt")
        if st.button("🎬 Generate Video"):
            with st.spinner("Generating..."):
                vgen = VideoGenerator(provider=provider)
                url = vgen.generate_video(vid_prompt)
                if os.path.exists(url):
                    with open(url, 'rb') as v:
                        video_bytes = v.read()
                        st.video(video_bytes)
                        st.download_button(
                            label="⬇️ Download Video (MP4)",
                            data=video_bytes,
                            file_name=os.path.basename(url),
                            mime="video/mp4"
                        )
                else:
                    st.video(url)
                st.write(url)

st.divider()
st.caption("AI Influencer Automation System - One-Click Creator")
