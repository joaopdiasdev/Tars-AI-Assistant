# 🤖 TARS - Autonomous Personal Assistant

[![Linux Mint](https://img.shields.io/badge/OS-Linux%20Mint-chbrightgreen?logo=linuxmint&logoColor=white)](https://linuxmint.com/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/LLM-Llama%203-orange)](https://ollama.ai/)
[![NVIDIA](https://img.shields.io/badge/GPU-NVIDIA%20CUDA-76B900?logo=nvidia&logoColor=white)](https://www.nvidia.com/)

TARS is a high-performance virtual assistant inspired by Interstellar, specifically tailored for the **Linux Mint** environment. It leverages local AI models for speech-to-text, natural language processing, and neural voice synthesis, running entirely on your local NVIDIA GPU.

![TARS Interface](./tars_interface.png)

---

## ✨ Core Features

- **🧠 Local Intelligence:** Integrated with **Ollama (Llama 3)** for 100% private and offline conversations.
- **🎙️ High-Fidelity Hearing:** Real-time transcription using **OpenAI Whisper (Small)**, optimized for NVIDIA CUDA cores.
- **🔊 Multilingual Neural Voice:** Realistic speech synthesis (PT-BR, EN-US, ZH-CN) via **Edge-TTS**.
- **🖥️ Linux Mint System Control:**
    - App Management: Launch VS Code, Discord, Spotify, and Terminal via voice.
    - Web Automation: Hands-free Google searches and clipboard translation.
- **📊 Smart Briefing:** Personalized morning reports including local weather and real-time news via RSS.

---

## 🛠️ System Requirements

### Hardware
- **GPU:** NVIDIA GPU with CUDA support (8GB+ VRAM recommended for low latency).
- **RAM:** 16GB+.

🧩 Software Dependencies

TARS requires specific Linux system libraries for audio and clipboard management:
```
sudo apt update && sudo apt install -y ffmpeg libportaudio2 xclip xsel
```
🚀 Quick Start

1️⃣ Clone the Repository
``` 
git clone https://github.com/joaopdiasdev/Tars-AI-Assistant.git
cd Tars-AI-Assistant
```

2️⃣ Set Up the Environment

Make sure you have Python 3 installed. Then create and activate a virtual environment:
```
python3 -m venv venv
source venv/bin/activate
```

Install the required dependencies:
```
pip install -r requirements.txt
```
3️⃣ Run TARS

Make the start script executable:
```
chmod +x tars_start.sh
```

Then run:
```
./tars_start.sh
```
---

## 📂 Project Structure

Here’s how the project is organized and what each file is responsible for:

- ### tars_gui.py
The main interface of TARS. It handles the application window, buttons, and the overall user interaction flow.

- ### tars_utils.py
The “brain” of the project. This is where voice processing, AI integration, system commands, and weather features are managed.

- ### requirements.txt
Contains all the Python dependencies required to run the project.

- ### tars_start.sh
A simple shell script that makes starting TARS quick and easy.

- ### .gitignore
Ensures unnecessary files (like cache, virtual environments, and temporary audio files) aren’t uploaded to GitHub.

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.
