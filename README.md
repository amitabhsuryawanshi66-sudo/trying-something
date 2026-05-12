# AI Influencer Automation System 🤖

This project is a beginner-friendly, modular Python system for automating an AI influencer's workflow.

## 🌟 New Feature: Idea-to-Reel Automation
You can now enter a simple topic (e.g., "Why I love coding") and the system will:
1. **Brainstorm** a unique Reel idea.
2. **Write** a script for the post.
3. **Generate** a background video.
4. **Post** it directly to your Instagram account.

---

## 🚀 Beginner Setup Guide (No coding required!)

### 1. Prerequisites
- You need **Python** installed. Download from [python.org](https://www.python.org/downloads/). (Check "Add Python to PATH").

### 2. Installation
1. Download or clone this repository.
2. **Double-click `setup.bat`**. This installs everything needed (Streamlit, Instagrapi, etc.).

### 3. Running the App
1. **Double-click `run_app.bat`**.
2. The browser UI will open.
3. Enter your **Instagram Username** and **Password** in the sidebar if you want to use the automated posting feature.
4. Go to the **"Full Automation"** tab, enter a topic, and click **"Start Full Automation"**.

### 4. Configuration (API Keys)
- **Free Mode:** Default. No keys needed. Uses Pollinations.ai for everything.
- **Premium Mode:** Add your `OPENAI_API_KEY` to the `.env` file to use DALL-E 3 and GPT-4o.

---

## 🛠 Project Structure
- `app.py`: Streamlit Web UI.
- `automation.py`: Orchestrator for the "Idea to Post" pipeline.
- `social_manager.py`: Handles Instagram login and Reel uploads via `instagrapi`.
- `video_gen.py`: Generates videos using AI.
- `image_gen.py` / `content_gen.py`: Core generators.

---

## ⚠️ Important Note
Automating social media accounts can sometimes lead to temporary blocks or bans if used excessively. Use this tool responsibly and moderate the frequency of your automated posts.

## 📝 License
Open-source. Adapt it for your AI influencer journey!
