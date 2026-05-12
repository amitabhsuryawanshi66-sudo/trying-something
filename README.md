# AI Influencer Automation System 🤖

This project is a beginner-friendly, modular Python system for automating an AI influencer's workflow. It includes image generation, caption generation, and social media automation structures.

## 🌟 Features
- **Free Mode (New!):** Use powerful AI generation for **FREE** without needing an OpenAI API key.
- **OpenAI Integration:** Optionally use OpenAI's DALL-E 3 and GPT-4o for premium quality.
- **Social Media Management:** Modular structure to simulate or automate posting to Instagram and Twitter.
- **Easy-to-use Web UI:** A simple clickable interface built with Streamlit.

---

## 🚀 Beginner Setup Guide (No coding required!)

### 1. Prerequisites
- You need **Python** installed on your Windows computer. If you don't have it, download and install it from [python.org](https://www.python.org/downloads/). (Make sure to check the box "Add Python to PATH" during installation).

### 2. Installation
1. Download or clone this repository to your computer.
2. Open the folder and find the file named `setup.bat`.
3. **Double-click `setup.bat`**. This will automatically:
   - Create a virtual environment (a private space for this project's dependencies).
   - Install all necessary libraries (Streamlit, OpenAI, etc.).
   - Create a `.env` file for your configuration.

### 3. Running the App (Free Mode)
1. Find the file named `run_app.bat`.
2. **Double-click `run_app.bat`**.
3. A terminal window will open, and shortly after, a new tab will open in your web browser with the app interface.
4. By default, the app is set to **"Free (No API Key)"**. You can start generating content immediately by entering a prompt!

### 4. Optional: Premium Mode (OpenAI)
If you want to use OpenAI's paid services:
1. Get an API key from [platform.openai.com](https://platform.openai.com/).
2. In the project folder, right-click the `.env` file and select **Open with > Notepad**.
3. Replace `your_openai_api_key_here` with your actual API key.
4. Save the file.
5. In the web app, switch the "Operation Mode" in the sidebar to **"OpenAI (Paid API Key)"**.

---

## 🛠 Project Structure (For Developers)

- `app.py`: The Streamlit web interface (Supports Free and OpenAI modes).
- `main.py`: Orchestrator for the generation pipeline.
- `image_gen.py`: Handles generation (Pollinations or DALL-E 3).
- `content_gen.py`: Handles text generation (Pollinations or GPT-4o).
- `social_manager.py`: Logic for social media posting.
- `requirements.txt`: List of Python dependencies.
- `setup.bat` / `run_app.bat`: Automation scripts for Windows.

---

## 📝 License
This project is open-source. Feel free to modify and adapt it for your own AI influencer projects!
