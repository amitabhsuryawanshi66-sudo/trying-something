# AI Influencer Automation System 🤖

This project is a beginner-friendly, modular Python system for automating an AI influencer's workflow. It includes image generation, caption generation, and social media automation structures.

## 🌟 Features
- **Image Generation:** Uses OpenAI's DALL-E 3 to create high-quality influencer photos.
- **Content Generation:** Uses OpenAI's GPT-4o to write engaging social media captions.
- **Social Media Management:** Modular structure to simulate or automate posting to Instagram and Twitter.
- **Easy-to-use Web UI:** A simple clickable interface built with Streamlit.

---

## 🚀 Beginner Setup Guide (No coding required!)

### 1. Prerequisites
- You need **Python** installed on your Windows computer. If you don't have it, download and install it from [python.org](https://www.python.org/downloads/). (Make sure to check the box "Add Python to PATH" during installation).
- You need an **OpenAI API Key**. Get one from [platform.openai.com](https://platform.openai.com/).

### 2. Installation
1. Download or clone this repository to your computer.
2. Open the folder and find the file named `setup.bat`.
3. **Double-click `setup.bat`**. This will automatically:
   - Create a virtual environment (a private space for this project's dependencies).
   - Install all necessary libraries (Streamlit, OpenAI, etc.).
   - Create a `.env` file for your configuration.

### 3. Configuration (Adding your API Key)
1. In the same folder, look for a file named `.env`.
2. Right-click `.env` and select **Open with > Notepad**.
3. Find the line that says: `OPENAI_API_KEY=your_openai_api_key_here`.
4. Replace `your_openai_api_key_here` with your actual API key from OpenAI.
5. **Save** the file (Ctrl+S) and close Notepad.

### 4. Running the App
1. Find the file named `run_app.bat`.
2. **Double-click `run_app.bat`**.
3. A terminal window will open, and shortly after, a new tab will open in your web browser with the app interface.
4. If the browser doesn't open automatically, look for a URL like `http://localhost:8501` in the terminal and copy-paste it into your browser.

---

## 🛠 Project Structure (For Developers)

- `app.py`: The Streamlit web interface.
- `main.py`: Orchestrator for the generation pipeline.
- `image_gen.py`: Handles DALL-E 3 API calls.
- `content_gen.py`: Handles GPT-4o API calls.
- `social_manager.py`: Logic for social media posting.
- `requirements.txt`: List of Python dependencies.
- `.env.example`: Template for environment variables.
- `setup.bat` / `run_app.bat`: Automation scripts for Windows.

---

## 📝 License
This project is open-source. Feel free to modify and adapt it for your own AI influencer projects!
