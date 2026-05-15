import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from image_gen import ImageGenerator
from content_gen import ContentGenerator
from video_gen import VideoGenerator, VoiceoverGenerator
from video_editor import ReelEditor
from library_manager import LibraryManager
from footage_manager import FootageSearcher
from social_manager import InstagramManager
from dotenv import load_dotenv

# Page config
st.set_page_config(page_title="Instagram Reel Automator", page_icon="📸", layout="wide")

# Load environment variables
load_dotenv()

# Sidebar
st.sidebar.title("📸 Master Settings")
provider_choice = st.sidebar.selectbox(
    "AI Content Engine",
    ["Pollinations (Free, No Key)", "Groq (Free, Needs Key)", "OpenAI (Paid, Needs Key)"]
)

provider = "pollinations"
if "Groq" in provider_choice: provider = "groq"
if "OpenAI" in provider_choice: provider = "openai"

# API Keys
openai_key = st.sidebar.text_input("OpenAI Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
groq_key = st.sidebar.text_input("Groq Key", value=os.getenv("GROQ_API_KEY", ""), type="password")
pixabay_key = st.sidebar.text_input("Pixabay Key", value=os.getenv("PIXABAY_API_KEY", ""), type="password")
pexels_key = st.sidebar.text_input("Pexels Key", value=os.getenv("PEXELS_API_KEY", ""), type="password")

st.sidebar.divider()
st.sidebar.subheader("Instagram Login")
ig_user = st.sidebar.text_input("IG Username", value=os.getenv("INSTAGRAM_USERNAME", ""))
ig_pass = st.sidebar.text_input("IG Password", value=os.getenv("INSTAGRAM_PASSWORD", ""), type="password")

# Tabs
tab_reel, tab_dash, tab_tracker, tab_manual = st.tabs(["🔥 Generate Instagram Reel", "🚀 Idea Dashboard", "📅 Reel Tracker", "🛠 Individual Tools"])

content_gen = ContentGenerator(api_key=openai_key, provider=provider, groq_key=groq_key)
lib_mgr = LibraryManager()
searcher = FootageSearcher(pixabay_key=pixabay_key, pexels_key=pexels_key)
editor = ReelEditor(output_dir="exports/instagram_reels")

with tab_reel:
    st.header("One-Click Instagram Reel Pipeline")

    st.info("💡 **Instructions:** Enter a topic, confirm rights, and click generate. The app will script, search for footage, generate voiceover, and assemble the final Reel.")

    st.warning("⚠️ **Copyright Notice:** Only use royalty-free API footage, owned gameplay, or footage you have permission to use. No scraping from social media.")
    rights_confirmed = st.checkbox("I confirm I have the rights to use the footage/audio generated.")

    col_in, col_out = st.columns([1, 1])

    with col_in:
        st.subheader("1. Setup")
        niche = st.selectbox("Channel Niche", [
            "Minecraft Brainrot", "Self-Improvement", "Side Hustles",
            "AI Tools", "Discipline", "Productivity"
        ])
        topic = st.text_input("Specific Topic", placeholder="e.g., Why you're addicted to scrolling")

        st.divider()
        st.subheader("2. Footage Options")
        use_api = st.checkbox("Search Pixabay/Pexels for footage", value=True)
        use_library = st.checkbox("Include my uploaded library clips", value=True)

        st.divider()
        if st.button("🚀 GENERATE FINISHED INSTAGRAM REEL"):
            if not topic:
                st.error("Please enter a topic.")
            elif not rights_confirmed:
                st.error("Please confirm usage rights.")
            else:
                with st.spinner("🎬 Running Pipeline: Script -> Footage -> VO -> Edit..."):
                    try:
                        # 1. Script
                        st.write("Writing viral Instagram script...")
                        ideas = content_gen.generate_ideas(niche, count=1)
                        idea = ideas[0]
                        script_text = content_gen.generate_script(idea['title'], niche)
                        keywords = content_gen.extract_keywords(script_text)

                        # 2. Footage
                        gameplay_paths = []
                        if use_api:
                            st.write(f"Searching APIs for: {', '.join(keywords)}...")
                            gameplay_paths.extend(searcher.search_and_download(keywords, count=5))

                        if use_library:
                            st.write("Including library clips...")
                            gameplay_paths.extend(lib_mgr.auto_select_clips(script_text))

                        if not gameplay_paths:
                            st.error("No footage found. Please upload clips or check API keys.")
                            st.stop()

                        # 3. VO
                        st.write("Generating voiceover...")
                        vo_gen = VoiceoverGenerator(provider="gtts")
                        vo_path = vo_gen.generate_vo(script_text, output_path="reel_vo.mp3")

                        # 4. Meta
                        meta = content_gen.generate_metadata(idea['title'], niche)

                        # 5. Timing & Edit
                        words = script_text.split()
                        words_per_sec = 2.4
                        script_data = []
                        current_t = 0
                        chunk_size = 8
                        for i in range(0, len(words), chunk_size):
                            chunk = " ".join(words[i:i+chunk_size])
                            dur = len(chunk.split()) / words_per_sec
                            script_data.append({'start': current_t, 'end': current_t + dur, 'text': chunk})
                            current_t += dur

                        st.write("Assembling 9:16 Reel (1080x1920)...")
                        final_path = editor.create_reel(gameplay_paths, vo_path, script_data)

                        st.session_state['last_reel_path'] = final_path
                        st.session_state['last_reel_meta'] = meta
                        st.session_state['last_reel_script'] = script_text
                        st.success("Instagram Reel successfully exported!")

                    except Exception as e:
                        st.error(f"Generation error: {e}")

    with col_out:
        st.subheader("Final Reel Preview")
        if 'last_reel_path' in st.session_state and os.path.exists(st.session_state['last_reel_path']):
            with open(st.session_state['last_reel_path'], 'rb') as f:
                st.video(f.read())

            with open(st.session_state['last_reel_path'], 'rb') as f:
                st.download_button("📥 Download Reel (MP4)", f, file_name="instagram_reel.mp4", mime="video/mp4")

            st.divider()
            st.subheader("Instagram Caption & Tags")
            ig_caption = st.text_area("Caption", st.session_state['last_reel_meta'], height=200)

            if st.button("📤 Upload Finished Reel to Instagram"):
                if not ig_user or not ig_pass:
                    st.error("Please provide Instagram credentials in the sidebar.")
                else:
                    with st.spinner("Logging in and uploading..."):
                        im = InstagramManager(ig_user, ig_pass)
                        status = im.upload_reel(st.session_state['last_reel_path'], ig_caption)
                        if "Success" in status:
                            st.success(status)
                        else:
                            st.error(status)
        else:
            st.info("Your finished Reel will appear here.")

# --- Remaining tabs updated for Instagram focus ---
with tab_dash:
    st.header("Idea Generator")
    niche_d = st.selectbox("Niche", ["Minecraft", "Self-Improvement", "Money"], key="d_niche")
    if st.button("💡 Get Ideas"):
        ideas = content_gen.generate_ideas(niche_d, count=3)
        st.session_state['dash_ideas'] = ideas

    if 'dash_ideas' in st.session_state:
        for idea in st.session_state['dash_ideas']:
            with st.expander(idea.get('title', 'Idea')):
                st.write(idea)

with tab_tracker:
    st.header("Reel Content Tracker")
    st.write("Target IST: 12:30 PM, 5:30 PM, 9:30 PM")
    # Tracker logic simplified for Instagram
    if st.button("➕ Add Last Reel to Tracker"):
        if 'last_reel_path' in st.session_state:
            st.success("Added!")

with tab_manual:
    st.header("Media Library & Manual Tools")
    st.subheader("Upload Gameplay Footage")
    up = st.file_uploader("Select MP4", type=['mp4'])
    if up:
        path = os.path.join(lib_mgr.library_dir, up.name)
        with open(path, "wb") as f: f.write(up.read())
        if st.button("Save to Library"):
            lib_mgr.add_clip(up.name, tags=[])
            st.success("Saved!")

    st.divider()
    st.subheader("Library Clips")
    for clip in lib_mgr.list_clips():
        st.write(f"- {clip['filename']}")

st.divider()
st.caption("Instagram Reel Automator - Viral Generation Engine")
