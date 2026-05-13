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
provider_choice = st.sidebar.selectbox(
    "Text AI Provider",
    ["Pollinations (Free, No Key)", "Groq (Free, Needs Key)", "OpenAI (Paid, Needs Key)"]
)

provider = "pollinations"
if "Groq" in provider_choice: provider = "groq"
if "OpenAI" in provider_choice: provider = "openai"

# API Keys
openai_key = st.sidebar.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
groq_key = st.sidebar.text_input("Groq API Key", value=os.getenv("GROQ_API_KEY", ""), type="password")

st.sidebar.divider()
st.sidebar.header("Instagram Credentials")
ig_user = st.sidebar.text_input("Username", value=os.getenv("INSTAGRAM_USERNAME", ""))
ig_pass = st.sidebar.text_input("Password", value=os.getenv("INSTAGRAM_PASSWORD", ""), type="password")

# Tabs
tab_auto, tab_manual = st.tabs(["🚀 Full Automation (Topic to Reel)", "🛠 Manual Tools"])

with tab_auto:
    st.header("One-Click AI Reel Creator")
    st.write(f"Using **{provider_choice}** to generate ideas.")

    topic = st.text_input("Topic for your Reel", placeholder="e.g., A day in the life of a digital artist")

    if st.button("🌟 Start Full Automation"):
        if not topic:
            st.error("Please enter a topic.")
        elif provider == "openai" and not openai_key:
            st.error("Please provide an OpenAI API Key.")
        elif provider == "groq" and not groq_key:
            st.error("Please provide a Groq API Key.")
        else:
            with st.spinner(f"Brainstorming with {provider}..."):
                try:
                    results = run_reel_automation(
                        topic,
                        provider=provider,
                        openai_key=openai_key,
                        groq_key=groq_key
                    )
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
                        local_path = download_file(res['video_url'], res['local_video'])
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
        img_prov = "openai" if provider == "openai" else "free"
        if st.button("🖼 Generate Image"):
            with st.spinner("Generating..."):
                igen = ImageGenerator(api_key=openai_key, provider=img_prov)
                url = igen.generate_image(img_prompt)
                st.image(url)
                st.write(url)

    with col_vid:
        st.subheader("Video Generator")
        vid_prompt = st.text_area("Video Prompt")
        if st.button("🎬 Generate Video"):
            with st.spinner("Generating..."):
                vgen = VideoGenerator(provider="free")
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
