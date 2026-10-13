import re
from urllib.parse import urlparse, parse_qs

import yt_dlp
from moviepy import VideoFileClip
import os
import whisper
import warnings

# own modules
import cerebro_gemini as cerebro
import subtitulos
from youtube_uploader import upload_video

warnings.filterwarnings("ignore")

URL_VIDEO = "https://youtu.be/PxBx_ZgKJUQ?si=qbI8PYdVJbVYG_Dn"
NOMBRE_SALIDA = "short_con_subs.mp4"


def validar_url_youtube(url):
    if not url or not isinstance(url, str):
        return False

    url = url.strip()
    if not url:
        return False

    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if not host:
        return False

    valid_hosts = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"}
    if host not in valid_hosts and not host.endswith(".youtube.com"):
        return False

    if host == "youtu.be":
        return bool(parsed.path and parsed.path != "/")

    path = parsed.path.lower()
    if path.startswith("/watch"):
        query = parse_qs(parsed.query)
        return bool(query.get("v"))
    if path.startswith(("/shorts/", "/embed/", "/live/")):
        return bool(parsed.path.strip("/"))
    return False


def pedir_url_video():
    while True:
        url = input("Paste a YouTube video URL: ").strip() or URL_VIDEO
        if validar_url_youtube(url):
            return url
        print("❌ That doesn't look like a valid YouTube URL. Please try again.")
        print("Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ")


def descargar_video(url):
    print(f"📥 Downloading video: {url}...")
    ydl_opts = {'format': 'bestvideo*+bestaudio/best', 'outtmpl': 'video_temp.%(ext)s', 'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return info.get('filepath') or ydl.prepare_filename(info)

def parsear_respuesta_gemini(texto):
    """Extract structured fields from Gemini's text response."""
    datos = {}
    lines = texto.split('\n')
    for line in lines:
        if "TITLE:" in line: datos['title'] = line.split("TITLE:")[1].strip()
        if "START:" in line: datos['start'] = float(line.split("START:")[1].strip())
        if "END:" in line: datos['end'] = float(line.split("END:")[1].strip())
        if "REASON:" in line: datos['reason'] = line.split("REASON:")[1].strip()
    return datos

def main():
    url_video = pedir_url_video()
    video_path = descargar_video(url_video)
    
    print("🔍 Transcribing audio to get timestamps...")
    model = whisper.load_model("base")
    resultado = model.transcribe(video_path)
    with open("transcripcion_completa.txt", "w", encoding="utf-8") as f:
        f.write(f"URL: {url_video}\n")
        f.write(resultado['text'])  
    
    analisis = cerebro.encontrar_clip_viral(resultado['segments'])
    clip_data = parsear_respuesta_gemini(analisis)

    print("🤖 SHORT PROPOSAL:")
    print(f"📌 Title: {clip_data.get('title')}")
    print(f"⏱️ Time: {clip_data.get('start')}s --> {clip_data.get('end')}s")
    print(f"💡 Reason: {clip_data.get('reason')}")
    confirmacion = input("Create this Short? Enter 'y' to accept, or enter custom times (e.g. 120-140): ")
    
    start = 0
    end = 0
    if confirmacion.lower() in ('y', 'yes'):
        start = clip_data['start']
        end = clip_data['end']
    elif '-' in confirmacion:
        partes = confirmacion.split('-')
        start = float(partes[0])
        end = float(partes[1])
    else:
        print("Cancelled.")
        return

    print(f"🚀 Creating the Short ({start}s to {end}s)...")
    clip = VideoFileClip(video_path).subclipped(start, end)

    w, h = clip.size
    new_width = h * (9/16)
    clip_vertical = clip.cropped(x1=w/2 - new_width/2, y1=0, x2=w/2 + new_width/2, y2=h)
    
    clip_final = subtitulos.generar_subtitulos(clip_vertical, resultado['segments'], start)
    clip_final.write_videofile(NOMBRE_SALIDA, 
                               codec='libx264', 
                               audio_codec='aac', 
                               fps=24,
                               threads=4)
    
    clip.close()
    os.remove(video_path)
    print(f"🎉 Video ready: {NOMBRE_SALIDA}!")

    auto_upload = os.getenv("YOUTUBE_AUTO_UPLOAD", "false").strip().lower() in {"1", "true", "yes", "on"}
    if auto_upload:
        print("Uploading Short to YouTube...")
        video_id = upload_video(
            video_path=NOMBRE_SALIDA,
            title=clip_data.get("title") or "AI-generated Short",
            description=os.getenv("YOUTUBE_DESCRIPTION", "").strip(),
            privacy_status=os.getenv("YOUTUBE_PRIVACY_STATUS", "private").strip().lower(),
            category_id=os.getenv("YOUTUBE_VIDEO_CATEGORY_ID", "22").strip(),
            client_secrets_file=os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secret.json").strip(),
        )
        print(f"🎉 Uploaded: https://www.youtube.com/watch?v={video_id}")

if __name__ == "__main__":
    main()