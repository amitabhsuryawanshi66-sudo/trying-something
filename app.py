import streamlit as st
import os
from image_gen import ImageGenerator
from content_gen import ContentGenerator
from social_manager import SocialManager
from dotenv import load_dotenv

# Page config
st.set_page_config(page_title="AI Influencer Automation", page_icon="🤖")

st.title("🤖 AI Influencer Automation System")
st.markdown("""
This tool helps you generate AI influencer content and simulate social media posting.
1. Enter a prompt for the image.
2. Generate the image and caption.
3. Post to simulated social media platforms.
""")

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.warning("⚠️ OpenAI API Key not found. Please add it to your `.env` file.")
    api_key_input = st.text_input("Or enter your OpenAI API Key here:", type="password")
    if api_key_input:
        api_key = api_key_input

if api_key:
    # Sidebar for settings
    st.sidebar.header("Settings")
    img_model = st.sidebar.selectbox("Image Model", ["dall-e-3", "dall-e-2"], index=0)
    txt_model = st.sidebar.selectbox("Text Model", ["gpt-4o", "gpt-3.5-turbo"], index=0)

    # Main UI
    prompt = st.text_area("What is the influencer doing?", placeholder="e.g. A stylish AI influencer exploring Tokyo at night")

    col1, col2 = st.columns(2)

    if st.button("🚀 Generate Content"):
        if not prompt:
            st.error("Please enter a prompt first.")
        else:
            with st.spinner("Generating image and caption..."):
                try:
                    # Initialize generators
                    image_gen = ImageGenerator(api_key=api_key)
                    content_gen = ContentGenerator(api_key=api_key)

                    # Generate image
                    image_url = image_gen.generate_image(prompt, model=img_model)

                    # Generate caption
                    caption = content_gen.generate_caption(prompt)

                    # Display results
                    st.session_state['generated_image'] = image_url
                    st.session_state['generated_caption'] = caption

                    st.success("Content Generated!")
                except Exception as e:
                    st.error(f"Error: {e}")

    if 'generated_image' in st.session_state:
        st.subheader("Generated Image")
        if st.session_state['generated_image'].startswith("http"):
            st.image(st.session_state['generated_image'])
            st.write(f"[Open Image Link]({st.session_state['generated_image']})")
        else:
            st.error(st.session_state['generated_image'])

    if 'generated_caption' in st.session_state:
        st.subheader("Generated Caption")
        st.write(st.session_state['generated_caption'])

        # Social Media Actions
        st.subheader("Social Media Automation")
        social_mgr = SocialManager()

        col_ig, col_tw = st.columns(2)

        if col_ig.button("Post to Instagram"):
            status = social_mgr.post_to_instagram(st.session_state['generated_image'], st.session_state['generated_caption'])
            st.info(status)

        if col_tw.button("Post to Twitter"):
            status = social_mgr.post_to_twitter(st.session_state['generated_image'], st.session_state['generated_caption'])
            st.info(status)
else:
    st.info("Please provide an OpenAI API Key to start.")

st.divider()
st.caption("AI Influencer Automation System - Modular Python Architecture")
