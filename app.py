import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from image_gen import ImageGenerator
from content_gen import ContentGenerator
from video_gen import VideoGenerator
from social_manager import InstagramManager
from automation import run_reel_automation, download_file
from dotenv import load_dotenv

# Page config
st.set_page_config(page_title="Faceless Content Automator", page_icon="🎬", layout="wide")

# Load environment variables
load_dotenv()

# Utility functions for persistence
def load_tracker():
    if os.path.exists("content_tracker.json"):
        with open("content_tracker.json", "r") as f:
            return json.load(f)
    return []

def save_tracker(data):
    with open("content_tracker.json", "w") as f:
        json.dump(data, f, indent=4)

# Sidebar
st.sidebar.title("🎬 Settings")
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
tab_dash, tab_tracker, tab_manual = st.tabs(["🚀 Generator Dashboard", "📅 Content Tracker", "🛠 Individual Tools"])

content_gen = ContentGenerator(api_key=openai_key, provider=provider, groq_key=groq_key)

with tab_dash:
    st.header("Faceless Content Generator")
    col1, col2 = st.columns([1, 2])

    with col1:
        niche = st.selectbox("Select Niche", [
            "Minecraft Brainrot",
            "Self-Improvement",
            "Student Money Lessons",
            "AI Tools",
            "Discipline",
            "Side Hustles"
        ])
        count = st.slider("Ideas to generate", 1, 10, 3)

        if st.button("💡 Generate Ideas"):
            with st.spinner("Thinking of viral hits..."):
                ideas = content_gen.generate_ideas(niche, count)
                st.session_state['generated_ideas'] = ideas
                st.session_state['current_niche'] = niche

    if 'generated_ideas' in st.session_state:
        st.subheader(f"Top {len(st.session_state['generated_ideas'])} Ideas for {st.session_state['current_niche']}")
        for i, idea in enumerate(st.session_state['generated_ideas']):
            with st.expander(f"Idea {i+1}: {idea.get('title', 'Untitled')}"):
                st.write(f"**Hook:** {idea.get('hook')}")
                st.write(f"**Angle:** {idea.get('angle')}")
                st.write(f"**Trigger:** {idea.get('trigger')}")
                st.write(f"**Visuals:** {idea.get('visuals')}")

                if st.button(f"📝 Select & Generate Script for Idea {i+1}", key=f"sel_{i}"):
                    st.session_state['selected_idea'] = idea
                    with st.spinner("Writing script..."):
                        script = content_gen.generate_script(idea.get('title'), niche)
                        metadata = content_gen.generate_metadata(idea.get('title'), niche)
                        prompts = content_gen.generate_visual_prompts(idea.get('visuals'))

                        st.session_state['full_package'] = {
                            "idea": idea,
                            "script": script,
                            "metadata": metadata,
                            "visual_prompts": prompts,
                            "niche": niche,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }

    if 'full_package' in st.session_state:
        pkg = st.session_state['full_package']
        st.divider()
        st.header(f"📦 Content Package: {pkg['idea']['title']}")

        p_col1, p_col2 = st.columns(2)
        with p_col1:
            st.subheader("📜 Retention Script")
            st.text_area("Script", pkg['script'], height=300)

            st.subheader("🏷 Metadata & Captions")
            st.text_area("Captions", pkg['metadata'], height=200)

        with p_col2:
            st.subheader("🖼 Visual Prompts")
            st.text_area("AI Prompts", pkg['visual_prompts'], height=150)

            st.subheader("⚙️ Actions")
            if st.button("➕ Add to Tracker"):
                tracker = load_tracker()
                tracker.append({
                    "title": pkg['idea']['title'],
                    "niche": pkg['niche'],
                    "status": "Idea",
                    "created_at": pkg['timestamp']
                })
                save_tracker(tracker)
                st.success("Added to Tracker!")

            # Export logic
            export_data = f"# {pkg['idea']['title']}\n\n## Niche: {pkg['niche']}\n\n## Idea\n{pkg['idea']}\n\n## Script\n{pkg['script']}\n\n## Metadata\n{pkg['metadata']}\n\n## Visual Prompts\n{pkg['visual_prompts']}"
            st.download_button("📥 Export Markdown", export_data, file_name=f"{pkg['idea']['title'].replace(' ', '_')}.md")

            csv_data = pd.DataFrame([pkg['idea']]).to_csv(index=False)
            st.download_button("📥 Export CSV", csv_data, file_name=f"{pkg['idea']['title'].replace(' ', '_')}.csv")

with tab_tracker:
    st.header("📅 Content Management")
    st.write("Recommended IST Posting Times: **12:30 PM, 5:30 PM, 9:30 PM**")

    tracker = load_tracker()
    if tracker:
        df = pd.DataFrame(tracker)
        for i, row in df.iterrows():
            col_t, col_s, col_a = st.columns([2, 1, 1])
            col_t.write(f"**{row['title']}** ({row['niche']})")

            new_status = col_s.selectbox("Status", ["Idea", "Scripted", "Edited", "Posted"], index=["Idea", "Scripted", "Edited", "Posted"].index(row['status']), key=f"status_{i}")
            if new_status != row['status']:
                tracker[i]['status'] = new_status
                save_tracker(tracker)
                st.rerun()

            if col_a.button("🗑️ Delete", key=f"del_{i}"):
                tracker.pop(i)
                save_tracker(tracker)
                st.rerun()

        if st.button("🧹 Clear All"):
            save_tracker([])
            st.rerun()
    else:
        st.info("No content in tracker yet. Generate some ideas first!")

with tab_manual:
    st.header("Individual Creation Tools")
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
                        st.download_button("⬇️ Download Video", video_bytes, file_name="generated.mp4")
                else:
                    st.video(url)

st.divider()
st.caption("Faceless Content Automator - Powered by AI & Persistence")
