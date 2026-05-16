import streamlit as st
import os
import json
import asyncio
from PIL import Image
from dotenv import load_dotenv

# Fix Pillow/MoviePy compatibility
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from content_gen import ContentGenerator
from voiceover_agent import VoiceoverAgent
from video_editor import ReelEditor
from library_manager import LibraryManager
from gameplay_processor import GameplayProcessor
from social_manager import InstagramManager

# Load env
load_dotenv()

# Page config
st.set_page_config(page_title="InstaViral", page_icon="🚀", layout="wide")

# Init managers
lib_mgr = LibraryManager()
gp = GameplayProcessor()
editor = ReelEditor()
vo_agent = VoiceoverAgent()

# Sidebar Settings
st.sidebar.title("📸 InstaViral Settings")
provider_choice = st.sidebar.selectbox("AI Engine", ["Pollinations (Free)", "Groq (Fast)", "OpenAI (Premium)"])
provider = "pollinations"
if "Groq" in provider_choice: provider = "groq"
if "OpenAI" in provider_choice: provider = "openai"

groq_key = st.sidebar.text_input("Groq API Key", value=os.getenv("GROQ_API_KEY", ""), type="password")
openai_key = st.sidebar.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")

st.sidebar.divider()
st.sidebar.subheader("Voiceover Settings")
vo_preset = st.sidebar.selectbox("Voice Preset", list(vo_agent.presets.keys()))
vo_speed = st.sidebar.slider("Speed Boost", 1.0, 1.2, 1.08, step=0.01)

st.sidebar.divider()
debug_mode = st.sidebar.checkbox("Debug Mode")

# Helper for async VO
def run_vo_async(script, preset, filename):
    return asyncio.run(vo_agent.generate_voiceover(script, preset, filename))

# Main UI
st.title("🚀 InstaViral - One-Click Reel Generator")

# 1. Content Style & Idea Generation
col_idea, col_preview = st.columns([1, 1])

with col_idea:
    st.subheader("1. Generate Viral Idea")
    niche = st.selectbox("Channel Niche", ["Self-Improvement", "Side Hustles", "AI Tools", "Minecraft Money", "Discipline"])

    if st.button("💡 Generate Ideas"):
        with st.spinner("Brainstorming viral ideas..."):
            gen = ContentGenerator(provider=provider, groq_key=groq_key, api_key=openai_key)
            ideas = gen.generate_ideas(niche)
            st.session_state['ideas'] = ideas

    if 'ideas' in st.session_state:
        for i, idea in enumerate(st.session_state['ideas']):
            with st.container(border=True):
                st.write(f"**{idea['title']}**")
                st.caption(f"Hook: {idea['hook']}")
                st.write(f"Angle: {idea['angle']}")
                if st.button(f"Use This Idea", key=f"use_{i}"):
                    st.session_state['selected_idea'] = idea
                    st.success(f"Selected: {idea['title']}")

# 2. Selected Idea & Generation
if 'selected_idea' in st.session_state:
    st.divider()
    st.subheader(f"2. Generation Pipeline: {st.session_state['selected_idea']['title']}")

    col_pipe_left, col_pipe_right = st.columns([1, 1])

    with col_pipe_left:
        if st.button("🚀 GENERATE VIRAL REEL"):
            try:
                gen = ContentGenerator(provider=provider, groq_key=groq_key, api_key=openai_key)

                # Step 1: Script
                with st.status("Pipeline running...", expanded=True) as status:
                    st.write("Writing viral script...")
                    script = gen.generate_script(st.session_state['selected_idea'], niche)
                    st.session_state['current_script'] = script

                    if debug_mode:
                        st.json(script)

                    # Step 2: Voiceover
                    st.write("Generating Edge-TTS voiceover...")
                    vo_path = run_vo_async(script, vo_preset, "final_vo.mp3")
                    st.session_state['current_vo'] = vo_path

                    # Step 3: Edit Plan & Render
                    st.write("Selecting clips & rendering video...")
                    clips = lib_mgr.auto_select_clips(script.get('voiceover_full_text', ''))
                    if not clips:
                        st.error("No gameplay clips found! Go to 'Library' and process a video first.")
                        st.stop()

                    final_path = editor.create_reel(
                        gameplay_paths=clips,
                        vo_path=vo_path,
                        script_data=script.get('scenes', []),
                        output_filename="insta_viral_reel.mp4"
                    )
                    st.session_state['final_reel_path'] = final_path
                    status.update(label="Reel Generated!", state="complete")
                    st.success("Success!")
            except Exception as e:
                st.error(f"Pipeline failed: {e}")

    with col_pipe_right:
        if 'final_reel_path' in st.session_state:
            st.subheader("Preview & Download")
            st.video(st.session_state['final_reel_path'])
            with open(st.session_state['final_reel_path'], "rb") as f:
                st.download_button("📥 Download Final Reel (MP4)", f, "viral_reel.mp4")

            st.divider()
            st.subheader("Instagram Metadata")
            if 'current_script' in st.session_state:
                st.text_area("Caption", st.session_state['current_script'].get('instagram_caption', ''), height=100)
                st.text_area("Hashtags", " ".join(st.session_state['current_script'].get('hashtags', [])), height=50)

# Library & Advanced Tabs
st.divider()
with st.expander("📁 Library & Advanced Tools"):
    tab_lib, tab_manual = st.tabs(["Gameplay Library", "Manual Generation"])

    with tab_lib:
        st.subheader("Manage Gameplay Packs")
        up_file = st.file_uploader("Upload Long Gameplay (MP4)", type=['mp4'])
        if up_file:
            path = os.path.join(lib_mgr.library_dir, up_file.name)
            with open(path, "wb") as f: f.write(up_file.read())
            if st.button("⚙️ Process Pack"):
                with st.spinner("Splitting video..."):
                    gp.process_long_video(path)
                    st.success("Pack processed!")

    with tab_manual:
        st.write("Manual voiceover generation or script testing...")
        test_txt = st.text_area("Test Text")
        if st.button("Test VO"):
            p = run_vo_async({"voiceover_full_text": test_txt}, vo_preset, "test_vo.mp3")
            st.audio(p)

if debug_mode and 'selected_idea' in st.session_state:
    st.divider()
    st.subheader("Debug Info")
    st.write("Selected Idea:", st.session_state['selected_idea'])
    if 'current_script' in st.session_state:
        st.write("Current Script:", st.session_state['current_script'])
