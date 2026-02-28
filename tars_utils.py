import edge_tts
import asyncio
import pygame
import os
import whisper
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import requests
import re
import subprocess
import webbrowser
import psutil
import pyperclip
import feedparser

# --- INICIALIZAÇÃO DO SISTEMA ---
# Otimizado 
pygame.mixer.init(frequency=44100, size=-16, channels=1)

# Carregando o modelo Whisper 'small'
model = whisper.load_model("small")

def bip(inicio=True):
    """Feedback sonoro minimalista para início/fim de escuta."""
    try:
        duration = 0.1
        sample_rate = 44100
        f = 1046 if inicio else 784
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = 0.3 * np.sin(f * t * 2 * np.pi)
        fade_out = np.linspace(1, 0, len(t))
        tone = tone * fade_out
        audio_signal = (tone * 32767).astype(np.int16)
        sound = pygame.sndarray.make_sound(audio_signal)
        sound.play()
    except Exception as e:
        print(f"Erro no Bip: {e}")

def falar(texto: str):
    """Motor de Voz Neural: PT-BR, EN-US, ZH-CN."""
    # 1. Detecção de Mandarim
    if any('\u4e00' <= c <= '\u9fff' for c in texto):
        voz = "zh-CN-XiaoxiaoNeural"
    # 2. Detecção de Inglês (Apenas se não houver acentos e houver keywords)
    elif re.search(r'\b(the|is|you|what|hello|thanks|good|apple|code|open|start|how|search|system)\b', texto.lower()) and not re.search(r'[áéíóúçãõàêô]', texto.lower()):
        voz = "en-US-GuyNeural"
    # 3. Padrão: Português do Brasil
    else:
        voz = "pt-BR-AntonioNeural"

    async def _gerar():
        communicate = edge_tts.Communicate(texto, voz)
        await communicate.save("res.mp3")

    try:
        asyncio.run(_gerar())
        pygame.mixer.music.load("res.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        if os.path.exists("res.mp3"):
            os.remove("res.mp3")
    except Exception as e:
        print(f"Erro na saída de voz: {e}")

def gravar_audio(duracao=6):
    """Captura áudio com normalização para clareza fonética."""
    fs = 16000
    bip(inicio=True)
    try:
        audio = sd.rec(int(duracao * fs), samplerate=fs, channels=1, dtype='float32')
        sd.wait()
        
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))
            
        audio_int16 = (audio * 32767).astype(np.int16)
        bip(inicio=False)
        return audio_int16.flatten()
    except Exception as e:
        print(f"Erro no Microfone: {e}")
        return np.zeros(fs * duracao, dtype='int16')

def transcrever_audio(audio_data):
    """Transcrição estável para PT, EN e ZH."""
    wav.write("temp.wav", 16000, audio_data)
    try:
        result = model.transcribe(
            "temp.wav", 
            initial_prompt="Olá TARS. 你好. Hello. Eu falo português, inglês e chinês.",
            temperature=0
        )
        text = result.get("text", "").strip()
        return text if len(text) > 1 else ""
    finally:
        if os.path.exists("temp.wav"):
            os.remove("temp.wav")

def limpar_comando(texto: str):
    """Limpa gatilhos para isolar o termo de busca ou nome do app."""
    temp = texto.lower()
    temp = re.sub(r'^(tars|hey tars|ok tars|ei tars|escute tars|ouça tars)[^a-zA-Z0-9]*', '', temp)
    temp = re.sub(r'^(pesquise|procure|google|search|sobre|por|for|o que é|quem é|qual é|qual|quem|abra|abrir|open|start|inicie|run)[,\s]*', '', temp)
    return temp.strip()

def obter_clima():
    """Busca o clima de Curitiba com timeout estendido e fallback."""
    try:
        # Aumentamos o timeout para 8s e forçamos o lang=pt
        res = requests.get("https://wttr.in/Curitiba?format=%C+%t&lang=pt", timeout=8)
        if res.status_code == 200 and "Unknown" not in res.text:
            return res.text.replace("+", " ").strip()
        
        # Fallback caso o formato principal falhe
        res_alt = requests.get("https://wttr.in/Curitiba?format=3&lang=pt", timeout=8)
        return res_alt.text.strip() if res_alt.status_code == 200 else "indisponível"
    except:
        return "indisponível no momento"

def obter_noticias():
    """Busca as 3 principais notícias de tecnologia do G1."""
    try:
        feed = feedparser.parse("https://g1.globo.com/rss/g1/tecnologia/")
        return ". ".join([post.title for post in feed.entries[:3]])
    except:
        return "sem notícias agora"

def executar_comando_sistema(texto: str):
    """Lógica para comandos de sistema, abertura de apps e buscas."""
    cmd = texto.lower()

    # 1. ABERTURA DE APLICATIVOS (Ação Real via Subprocess)
    if any(x in cmd for x in ["abra","abre", "abrir", "open", "start", "inicie"]):
        termo = limpar_comando(cmd)
        
        # VS CODE
        if any(v in cmd for v in ["code", "vsc", "vscode"]):
            subprocess.Popen(["code"], start_new_session=True)
            return "Abrindo Visual Studio Code."
        
        # DISCORD (Tenta binário padrão e depois Flatpak)
        elif "discord" in cmd:
            try:
                # Tenta o comando padrão
                subprocess.Popen(["discord"], start_new_session=True)
            except FileNotFoundError:
                try:
                    # Tenta via Flatpak (Comum no Mint)
                    subprocess.Popen(["flatpak", "run", "com.discordapp.Discord"], start_new_session=True)
                except:
                    return "Não encontrei o Discord instalado. Verifique se ele está no PATH ou no Flatpak."
            return "Iniciando o Discord."

        # SPOTIFY
        elif "spotify" in cmd:
            subprocess.Popen(["spotify"], start_new_session=True)
            return "Abrindo o Spotify."

        # NAVEGADOR (Firefox é padrão no Mint)
        elif any(x in cmd for x in ["firefox", "browser", "navegador", "internet"]):
            subprocess.Popen("nohup firefox > /dev/null 2>&1 &", shell=True)
            return "Opening Firefox." if "open" in cmd or "start" in cmd else "Iniciando o navegador Firefox."

        # GOOGLE CHROME
        elif "chrome" in cmd:
            subprocess.Popen("nohup google-chrome > /dev/null 2>&1 &", shell=True)
            return "Opening Google Chrome."
        
        # TERMINAL
        elif any(x in cmd for x in ["terminal", "console", "shell"]):
            subprocess.Popen("nohup x-terminal-emulator > /dev/null 2>&1 &", shell=True)
            return "Starting terminal."

    # 2. BUSCA WEB
    elif any(p in cmd for p in ["search", "google", "pesquise", "quem é", "o que é"]):
        termo = limpar_comando(texto)
        if termo: 
            webbrowser.open(f"https://www.google.com/search?q={termo}")
            return f"Pesquisando '{termo}' no Google."

    # 3. BRIEFING / BOM DIA
    elif any(x in cmd for x in ["bom dia", "briefing", "notícias", "notícias de hoje"]):
            clima = obter_clima()
            noticias = obter_noticias()
            
            # Resposta montada para o TARS falar
            resposta = (
                f"Bom dia! Em Curitiba o céu está {clima}. "
                f"As principais notícias de tecnologia são: {noticias}. "
                f"Estou pronto para as ordens, senhor."
            )
            return resposta

    # 4. STATUS TÉCNICO (Hardware)
    elif "status" in cmd:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        return f"Status do Sistema: CPU em {cpu}% e Memória RAM em {ram}%."

    # 5. TRADUÇÃO / CLIPBOARD
    elif any(x in cmd for x in ["traduza", "copiei", "translate"]):
        conteudo = pyperclip.paste()
        if not conteudo.strip(): return "O clipboard está vazio. Copie algo primeiro."
        return consultar_ollama(f"Traduza isso e se for Mandarim use Pinyin: '{conteudo}'")

    return None

def consultar_ollama(pergunta: str):
    """IA Llama 3 - Espelhamento de idioma e identidade de assistente pessoal."""
    url = "http://127.0.0.1:11434/api/generate"
    sys_prompt = (
        "Você é o TARS, meu assistente pessoal. Você fala Português, Inglês e Mandarim. "
        "REGRA CRÍTICA: Responda SEMPRE no mesmo idioma que o usuário usou. "
        "Não mencione o filme Interstellar. Seja direto e conciso."
    )
    try:
        response = requests.post(url, json={
            "model": "llama3", 
            "prompt": f"{sys_prompt}\nUsuário: {pergunta}\nTARS:", 
            "stream": False
        }, timeout=60)
        return response.json().get("response", "").strip()
    except:
        return "Desculpe, tive um erro de conexão com o meu núcleo de IA (Ollama)."

def processar_interacao_completa(pergunta: str):
    """Orquestrador principal com Auto-Copy."""
    if not pergunta or len(pergunta) < 2:
        return "Não consegui captar o áudio. Pode repetir, por favor?"

    # Tenta executar um comando local primeiro
    resposta = executar_comando_sistema(pergunta)
    
    # Se não for um comando local, envia para a inteligência artificial
    if not resposta:
        resposta = consultar_ollama(pergunta)
    
    # Copia a resposta para o clipboard (útil para o usuário)
    pyperclip.copy(resposta)
    return resposta
