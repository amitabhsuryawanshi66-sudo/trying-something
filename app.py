import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from PIL import Image

# Fix Pillow/MoviePy compatibility issue
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from content_gen import ContentGenerator
from video_gen import VideoGenerator, VoiceoverGenerator
from video_editor import ReelEditor
from library_manager import LibraryManager
from footage_manager import FootageSearcher
from gameplay_processor import GameplayProcessor
from social_manager import InstagramManager
from dotenv import load_dotenv

# Page config
st.set_page_config(page_title="InstaViral - Instagram Reel Automator", page_icon="📸", layout="wide")

# Load environment variables
load_dotenv()

# Initialize managers
lib_mgr = LibraryManager()
gp = GameplayProcessor()
searcher = FootageSearcher()
editor = ReelEditor()

# Sidebar
st.sidebar.title("📸 Master Settings")
provider_choice = st.sidebar.selectbox(
    "AI Engine",
    ["Pollinations (Free)", "Groq (Fast)", "OpenAI (Premium)"]
)

provider = "pollinations"
if "Groq" in provider_choice: provider = "groq"
if "OpenAI" in provider_choice: provider = "openai"

openai_key = st.sidebar.text_input("OpenAI Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
groq_key = st.sidebar.text_input("Groq Key", value=os.getenv("GROQ_API_KEY", ""), type="password")

st.sidebar.divider()
st.sidebar.subheader("Social Config")
ig_user = st.sidebar.text_input("IG Username", value=os.getenv("INSTAGRAM_USERNAME", ""))
ig_pass = st.sidebar.text_input("IG Password", value=os.getenv("INSTAGRAM_PASSWORD", ""), type="password")

# Tabs
tab_workflow, tab_library, tab_ideas, tab_manual = st.tabs([
    "🔥 One-Click Reel Workflow",
    "📁 Gameplay Library",
    "💡 Idea Dashboard",
    "🛠 Individual Tools"
])

content_gen = ContentGenerator(api_key=openai_key, provider=provider, groq_key=groq_key)

with tab_workflow:
    st.header("Step-by-Step Instagram Reel Generator")

    st.info("💡 **How it works:** 1. Process a gameplay pack. 2. Generate a script. 3. Export your Reel.")

    col_flow_in, col_flow_out = st.columns([1, 1])

    with col_flow_in:
        # Phase 1: Script
        st.subheader("1. Script Content")
        niche = st.selectbox("Channel Niche", [
            "Minecraft Brainrot", "Self-Improvement", "Side Hustles",
            "AI Tools", "Discipline", "Productivity"
        ], key="wf_niche")
        topic = st.text_input("Topic", placeholder="e.g., Why you're addicted to scrolling", key="wf_topic")

        if st.button("📝 Generate Viral Script"):
            if topic:
                with st.spinner("Writing script..."):
                    ideas = content_gen.generate_ideas(niche, count=1)
                    idea = ideas[0]
                    script_text = content_gen.generate_script(idea['title'], niche)
                    st.session_state['wf_script'] = script_text
                    st.session_state['wf_idea'] = idea
                    st.success("Script ready!")
            else:
                st.error("Enter a topic first.")

        if 'wf_script' in st.session_state:
            st.text_area("Review Script", st.session_state['wf_script'], height=200)

        st.divider()

        # Phase 2: Generation
        st.subheader("2. Final Assembly")
        st.warning("Only use footage you own or have permission to use.")
        rights_confirmed = st.checkbox("I confirm I have usage rights.")

        music_file = st.file_uploader("Optional: Add Background Music", type=['mp3', 'wav'])

        if st.button("🚀 GENERATE FINISHED REEL"):
            if 'wf_script' not in st.session_state:
                st.error("Generate a script first.")
            elif not rights_confirmed:
                st.error("Confirm usage rights.")
            else:
                with st.spinner("🎬 Assembling Reel..."):
                    try:
                        script_text = st.session_state['wf_script']

                        # 1. Select clips from library
                        st.write("Selecting clips from library...")
                        gameplay_paths = lib_mgr.auto_select_clips(script_text)

                        if not gameplay_paths:
                            st.error("No processed clips found. Upload and process a video in the Library tab first.")
                            st.stop()

                        # 2. VO
                        st.write("Generating voiceover...")
                        vo_gen = VoiceoverGenerator(provider="gtts")
                        vo_path = vo_gen.generate_vo(script_text, output_path="wf_vo.mp3")

                        # 3. Captions Data
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

                        # 4. Music
                        m_path = None
                        if music_file:
                            m_path = "wf_music.mp3"
                            with open(m_path, "wb") as f: f.write(music_file.read())

                        # 5. Assemble
                        st.write("Processing final video (1080x1920)...")
                        final_path = editor.create_reel(gameplay_paths, vo_path, script_data, music_path=m_path)

                        st.session_state['wf_final_reel'] = final_path
                        st.session_state['wf_meta'] = content_gen.generate_metadata(st.session_state['wf_idea']['title'], niche)
                        st.success("Reel generated!")
                    except Exception as e:
                        st.error(f"Failed: {e}")

    with col_flow_out:
        st.subheader("Preview & Export")
        if 'wf_final_reel' in st.session_state and os.path.exists(st.session_state['wf_final_reel']):
            with open(st.session_state['wf_final_reel'], 'rb') as f:
                st.video(f.read())

            with open(st.session_state['wf_final_reel'], 'rb') as f:
                st.download_button("📥 Download Final Reel (MP4)", f, file_name="insta_reel.mp4")

            st.divider()
            st.subheader("Instagram Meta")
            st.text_area("Caption & Tags", st.session_state['wf_meta'], height=200)

            if st.button("📤 Upload to Instagram"):
                if not ig_user or not ig_pass:
                    st.error("Enter IG credentials in sidebar.")
                else:
                    with st.spinner("Uploading..."):
                        im = InstagramManager(ig_user, ig_pass)
                        status = im.upload_reel(st.session_state['wf_final_reel'], st.session_state['wf_meta'])
                        st.success(status)
        else:
            st.info("Your finished Reel will appear here.")

with tab_library:
    st.header("Gameplay Pack Manager")

    col_up, col_lib = st.columns([1, 1])

    with col_up:
        st.subheader("Upload & Process New Pack")
        up_file = st.file_uploader("Upload Long Gameplay (MP4/MOV)", type=['mp4', 'mov'])
        default_tag = st.selectbox("Default Tag for this pack", [
            "parkour", "speedrun", "lava", "fail", "chest", "neutral"
        ])

        if up_file:
            path = os.path.join(lib_mgr.library_dir, up_file.name)
            if not os.path.exists(path):
                with open(path, "wb") as f: f.write(up_file.read())
                st.success(f"Uploaded {up_file.name}")

            if st.button("⚙️ Process Gameplay Pack"):
                with st.spinner("Splitting video into micro-clips..."):
                    new_clips = gp.process_long_video(path, default_tags=[default_tag, "high_energy"])
                    st.success(f"Created {len(new_clips)} micro-clips!")
                    lib_mgr.add_original_upload(up_file.name, tags=[default_tag], confirmed_rights=True)

    with col_lib:
        st.subheader("Processed Clips")
        p_clips = lib_mgr.list_processed_clips()
        if p_clips:
            st.write(f"Total micro-clips: {len(p_clips)}")
            # Show small list
            for i, c in enumerate(p_clips[:15]):
                st.write(f"- {c['filename']} ({', '.join(c['tags'])})")
            if len(p_clips) > 15:
                st.write("...and more.")
        else:
            st.info("No micro-clips yet.")

with tab_ideas:
    st.header("Viral Idea Dashboard")
    id_niche = st.selectbox("Select Niche", ["Minecraft", "Self-Improvement", "Money"], key="id_niche")
    if st.button("💡 Generate Ideas", key="id_btn"):
        ideas = content_gen.generate_ideas(id_niche, count=3)
        st.session_state['id_list'] = ideas

    if 'id_list' in st.session_state:
        for idea in st.session_state['id_list']:
            with st.expander(idea.get('title', 'Idea')):
                st.write(idea)

with tab_manual:
    st.header("Manual Tools")
    st.subheader("Voiceover Generator")
    manual_vo_text = st.text_area("Text for VO")
    if st.button("Generate VO"):
        v = VoiceoverGenerator()
        p = v.generate_vo(manual_vo_text, "manual_vo.mp3")
        with open(p, "rb") as f: st.audio(f.read())

st.divider()
st.caption("InstaViral Automator - High Watchtime Engine")
