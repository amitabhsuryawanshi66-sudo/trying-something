# 📸 InstaViral - Automated Instagram Reel Generator

Create viral faceless Instagram Reels (Minecraft, Self-Improvement, Side Hustles) without any editing or terminal knowledge. This tool automates the entire pipeline: **Scripting -> Voiceover -> Gameplay Selection -> Viral Editing -> Export.**

---

## 🚀 Beginner Quickstart (Windows)

1. **Setup:** Double-click `setup.bat`. This will install everything automatically. (Wait until it says "Setup Successful").
2. **Start:** Double-click `run_app.bat`. A browser window will open with the app.
3. **Usage:**
   - Go to the **📁 Gameplay Library** tab.
   - Upload a long gameplay video (10+ mins).
   - Click **⚙️ Process Gameplay Pack** (it will split it into viral 2-second clips).
   - Go to the **🔥 One-Click Reel Workflow** tab.
   - Click **📝 Generate Viral Script**.
   - Click **🚀 GENERATE FINISHED REEL**.

---

## 🔑 Adding API Keys (Optional)

You can use the app for **FREE** using the "Pollinations" engine. For higher quality, you can add keys in the **Sidebar** of the app or in the `.env` file:

1. Open the folder and find the file named `.env`.
2. Right-click it and "Open with Notepad".
3. Paste your keys:
   - `OPENAI_API_KEY`: Get from [OpenAI](https://platform.openai.com/)
   - `GROQ_API_KEY`: Get from [Groq](https://console.groq.com/) (Fast & Free)
   - `INSTAGRAM_USERNAME`: Your IG username for auto-posting.

---

## 🛠 Requirements for Viral Captions

To get the big, animated viral captions, you need **ImageMagick**:
1. Download it here: [ImageMagick Download](https://imagemagick.org/script/download.php) (Windows Binary).
2. **IMPORTANT:** During installation, you MUST check the box that says **"Install legacy utilities (e.g. convert)"**.

---

## 📁 Project Structure

- `app.py`: The main clickable browser UI.
- `gameplay_processor.py`: Splits long videos into micro-clips for the AI to pick.
- `video_editor.py`: Assembles the final 9:16 Reel with zooms and captions.
- `content_gen.py`: Writes the scripts using AI (GPT-4 or Groq).
- `library_manager.py`: Manages your collection of gameplay footage.

## ⚖️ Copyright & Safety
- **Footage:** Use only royalty-free footage or gameplay you recorded yourself.
- **Responsibility:** Use automation ethically. Do not spam.

## 📝 License
MIT - Build your Instagram empire!
