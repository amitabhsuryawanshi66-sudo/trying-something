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
from social_manager import InstagramManager
from automation import run_reel_automation, download_file
from dotenv import load_dotenv

# Page config
st.set_page_config(page_title="Faceless Content Automator Pro", page_icon="🎬", layout="wide")

# Load environment variables
load_dotenv()

# Utility functions
def load_tracker():
    if os.path.exists("content_tracker.json"):
        with open("content_tracker.json", "r") as f:
            return json.load(f)
    return []

def save_tracker(data):
    with open("content_tracker.json", "w") as f:
        json.dump(data, f, indent=4)

# Sidebar
st.sidebar.title("🎬 Master Settings")
provider_choice = st.sidebar.selectbox(
    "AI Engine",
    ["Pollinations (Free, No Key)", "Groq (Free, Needs Key)", "OpenAI (Paid, Needs Key)", "Template (Offline Fallback)"]
)

provider = "pollinations"
if "Groq" in provider_choice: provider = "groq"
if "OpenAI" in provider_choice: provider = "openai"
if "Template" in provider_choice: provider = "template"

openai_key = st.sidebar.text_input("OpenAI Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
groq_key = st.sidebar.text_input("Groq Key", value=os.getenv("GROQ_API_KEY", ""), type="password")

st.sidebar.divider()
st.sidebar.subheader("Social Config")
ig_user = st.sidebar.text_input("IG Username", value=os.getenv("INSTAGRAM_USERNAME", ""))
ig_pass = st.sidebar.text_input("IG Password", value=os.getenv("INSTAGRAM_PASSWORD", ""), type="password")

# Tabs
tab_reel, tab_dash, tab_tracker, tab_manual = st.tabs(["🔥 Finished Reel Generator", "🚀 Generator Dashboard", "📅 Content Tracker", "🛠 Individual Tools"])

content_gen = ContentGenerator(api_key=openai_key, provider=provider, groq_key=groq_key)
lib_mgr = LibraryManager()
editor = ReelEditor()

with tab_reel:
    st.header("One-Click Finished Reel Generator")

    st.warning("⚠️ **Copyright Warning:** Only use footage you created, own, or have license to use. Do not use random YouTube/TikTok clips.")
    rights_confirmed = st.checkbox("I confirm I have rights to use this footage.")

    col_setup, col_preview = st.columns([1, 1])

    with col_setup:
        st.subheader("1. Video Settings")
        niche = st.selectbox("Niche for this Reel", [
            "Minecraft Brainrot", "Self-Improvement", "Student Money Lessons",
            "AI Tools", "Discipline", "Side Hustles"
        ], key="reel_niche")

        topic = st.text_input("Specific Topic", placeholder="e.g., Why you are broke at 20")

        st.divider()
        st.subheader("2. Gameplay Library")
        uploaded_file = st.file_uploader("Upload new gameplay clip", type=['mp4', 'mov', 'avi'])
        if uploaded_file:
            path = os.path.join(lib_mgr.library_dir, uploaded_file.name)
            with open(path, "wb") as f:
                f.write(uploaded_file.read())

            tags = st.multiselect("Tag this clip", ["parkour", "lava", "falling", "chest", "satisfying"], key="upload_tags")
            if st.button("Add to Library"):
                lib_mgr.add_clip(uploaded_file.name, tags=tags)
                st.success(f"Added {uploaded_file.name} to library!")

        clips = lib_mgr.list_clips()
        if clips:
            st.write(f"Library has {len(clips)} clips.")
            selected_clips = st.multiselect("Manually select clips (or leave empty for auto-selection)", [c['filename'] for c in clips])
        else:
            st.info("Your gameplay library is empty. Please upload some clips first.")

        st.divider()
        st.subheader("3. Voice & Captions")
        voice_provider = st.selectbox("TTS Provider", ["gTTS (Online)", "pyttsx3 (Offline)"])

        st.divider()
        if st.button("🎬 GENERATE FINISHED REEL"):
            if not topic:
                st.error("Please enter a topic.")
            elif not rights_confirmed:
                st.error("You must confirm you have the rights to the footage.")
            elif not clips:
                st.error("Please upload gameplay footage to the library first.")
            else:
                with st.spinner("🚀 Starting Pipeline: Idea -> Script -> VO -> Edit..."):
                    try:
                        # 1. Generate Idea & Script
                        st.write("Generating viral script...")
                        ideas = content_gen.generate_ideas(niche, count=1)
                        idea = ideas[0]
                        script_text = content_gen.generate_script(idea['title'], niche)

                        # 2. Select Clips
                        st.write("Selecting best gameplay...")
                        if selected_clips:
                            gameplay_paths = [os.path.join(lib_mgr.library_dir, f) for f in selected_clips]
                        else:
                            gameplay_paths = lib_mgr.auto_select_clips(script_text)

                        # 3. Generate VO
                        st.write("Generating voiceover...")
                        vo_gen = VoiceoverGenerator(provider="gtts" if "gTTS" in voice_provider else "pyttsx3")
                        vo_path = vo_gen.generate_vo(script_text, output_path="temp_vo.mp3")

                        # 4. Parse Script for Captions
                        # We'll use a simple heuristic for timing based on script length
                        # Real systems would use forced alignment or SRT generators
                        words = script_text.split()
                        words_per_sec = 2.5
                        script_data = []
                        current_t = 0
                        chunk_size = 10
                        for i in range(0, len(words), chunk_size):
                            chunk = " ".join(words[i:i+chunk_size])
                            duration = len(chunk.split()) / words_per_sec
                            script_data.append({
                                'start': current_t,
                                'end': current_t + duration,
                                'text': chunk
                            })
                            current_t += duration

                        # 5. Edit Video
                        st.write("Assembling and exporting final MP4 (this may take a minute)...")
                        final_path = editor.create_reel(gameplay_paths, vo_path, script_data)

                        st.session_state['last_reel'] = final_path
                        st.session_state['last_reel_script'] = script_text
                        st.success("Reel successfully exported!")
                    except Exception as e:
                        st.error(f"Generation failed: {e}")

    with col_preview:
        st.subheader("Final Preview & Download")
        if 'last_reel' in st.session_state and os.path.exists(st.session_state['last_reel']):
            with open(st.session_state['last_reel'], 'rb') as f:
                st.video(f.read())

            with open(st.session_state['last_reel'], 'rb') as f:
                st.download_button(
                    "📥 Download Final Reel (MP4)",
                    f,
                    file_name=f"reel_{datetime.now().strftime('%Y%m%d_%H%M')}.mp4",
                    mime="video/mp4"
                )

            st.divider()
            st.subheader("Script Used")
            st.write(st.session_state['last_reel_script'])
        else:
            st.info("Generated reel will appear here.")

with tab_dash:
    st.header("Faceless Content Generator")
    col1, col2 = st.columns([1, 2])

    with col1:
        niche_dash = st.selectbox("Select Niche", [
            "Minecraft Brainrot", "Self-Improvement", "Student Money Lessons",
            "AI Tools", "Discipline", "Side Hustles"
        ], key="dash_niche")
        count = st.slider("Ideas to generate", 1, 10, 3)

        if st.button("💡 Generate Ideas"):
            with st.spinner("Thinking of viral hits..."):
                try:
                    ideas = content_gen.generate_ideas(niche_dash, count)
                    st.session_state['generated_ideas'] = ideas
                    st.session_state['current_niche'] = niche_dash
                    st.session_state['raw_debug'] = content_gen.last_raw_response
                    st.session_state['parse_errors'] = content_gen.last_parse_errors
                except Exception as e:
                    st.error(f"Generation failed: {e}")

    # ... [Rest of tab_dash, tab_tracker, tab_manual remains same as previous version]
    # (Abbreviated here for brevity, but I will write the full file)
    if 'generated_ideas' in st.session_state:
        st.subheader(f"Top Ideas for {st.session_state['current_niche']}")
        for i, idea in enumerate(st.session_state['generated_ideas']):
            with st.expander(f"Idea {i+1}: {idea.get('title', 'Untitled')}"):
                st.write(f"**Hook:** {idea.get('hook')}")
                st.write(f"**Angle:** {idea.get('angle')}")
                st.write(f"**Trigger:** {idea.get('trigger')}")

                if st.button(f"📝 Select & Generate Package for Idea {i+1}", key=f"sel_{i}"):
                    st.session_state['selected_idea'] = idea
                    with st.spinner("Writing package..."):
                        script = content_gen.generate_script(idea.get('title'), niche_dash)
                        metadata = content_gen.generate_metadata(idea.get('title'), niche_dash)
                        prompts = content_gen.generate_visual_prompts(idea.get('visuals'))
                        st.session_state['full_package'] = {
                            "idea": idea, "script": script, "metadata": metadata,
                            "visual_prompts": prompts, "niche": niche_dash,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }

    if 'full_package' in st.session_state:
        pkg = st.session_state['full_package']
        st.divider()
        st.header(f"📦 Content Package: {pkg['idea']['title']}")
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            st.subheader("📜 Script")
            st.text_area("Script", pkg['script'], height=300)
            st.subheader("🏷 Metadata")
            st.text_area("Captions", pkg['metadata'], height=200)
        with p_col2:
            st.subheader("🖼 Visual Prompts")
            st.text_area("AI Prompts", pkg['visual_prompts'], height=150)
            if st.button("➕ Add to Tracker"):
                tracker = load_tracker()
                tracker.append({"title": pkg['idea']['title'], "niche": pkg['niche'], "status": "Idea", "created_at": pkg['timestamp']})
                save_tracker(tracker)
                st.success("Added to Tracker!")
            export_data = f"# {pkg['idea']['title']}\n\n{pkg['script']}"
            st.download_button("📥 Export Markdown", export_data, file_name="brief.md")

with tab_tracker:
    st.header("📅 Content Management")
    st.write("IST Posting: **12:30 PM, 5:30 PM, 9:30 PM**")
    tracker = load_tracker()
    if tracker:
        for i, row in pd.DataFrame(tracker).iterrows():
            col_t, col_s, col_a = st.columns([2, 1, 1])
            col_t.write(f"**{row['title']}**")
            new_status = col_s.selectbox("Status", ["Idea", "Scripted", "Edited", "Posted"], index=["Idea", "Scripted", "Edited", "Posted"].index(row['status']), key=f"status_{i}")
            if new_status != row['status']:
                tracker[i]['status'] = new_status
                save_tracker(tracker)
                st.rerun()
            if col_a.button("🗑️", key=f"del_{i}"):
                tracker.pop(i)
                save_tracker(tracker)
                st.rerun()

with tab_manual:
    st.header("Individual Creation Tools")
    col_img, col_vid = st.columns(2)
    with col_img:
        st.subheader("Image Generator")
        img_prompt = st.text_area("Image Prompt", key="man_img_prompt")
        if st.button("🖼 Generate"):
            igen = ImageGenerator(api_key=openai_key, provider="openai" if provider == "openai" else "free")
            st.image(igen.generate_image(img_prompt))
    with col_vid:
        st.subheader("Video Generator")
        vid_prompt = st.text_area("Video Prompt", key="man_vid_prompt")
        if st.button("🎬 Generate"):
            vgen = VideoGenerator(provider="free")
            st.video(vgen.generate_video(vid_prompt))

st.divider()
st.caption("Faceless Content Automator Pro - Powered by AI & MoviePy")
