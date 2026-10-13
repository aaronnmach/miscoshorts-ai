# Miscoshorts - AI-Powered YouTube Shorts Generator

Automatically creates viral YouTube Shorts from long-form videos using AI analysis and automatic subtitle generation.
🎥 **[WATCH YOUTUBE TUTORIAL](https://youtu.be/zukJLVUwMxA?si=_DQ2RG10uzXtt7yT)**

## Features

- 🎥 Downloads YouTube videos automatically
- 🔍 Transcribes audio using OpenAI Whisper
- 🤖 Analyzes content with Google Gemini to find viral segments
- ✂️ Crops videos to vertical 9:16 format for Shorts
- 📝 Generates automatic subtitles with styling
- 🎬 Creates ready-to-upload MP4 files

## Requirements

- Python 3.12+
- FFmpeg (required by moviepy)
- Google Gemini API key
- YouTube Data API v3 OAuth client (optional, for automatic uploads)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd miscoshorts
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install FFmpeg:
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

4. Set up your Google Gemini API key:
   - Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - If `.env` does not exist, copy `.env.example` to `.env`. If it already exists, keep it and add the required settings:
```bash
GEMINI_API_KEY=your-api-key
```

## Usage

1. Edit the `URL_VIDEO` variable in `maker.py` to point to your target YouTube video
2. Run the script:
```bash
python maker.py
```

3. The script will:
   - Download the video
   - Transcribe the audio
   - Ask Gemini to suggest the best viral segment
   - Show you the suggestion with title, timestamps, and reasoning
   - Ask for confirmation (press 'y' to accept or provide custom timestamps)
   - Generate the vertical Short with subtitles
   - Save as `short_con_subs.mp4`
   - Upload automatically if `YOUTUBE_AUTO_UPLOAD=true` is set in `.env`

### YouTube Upload Setup

1. In the [Google Cloud Console](https://console.cloud.google.com/), create or select a project and enable **YouTube Data API v3**.
2. Configure the OAuth consent screen (add your Google account as a test user if the app is in testing), then create an OAuth client ID with application type **Desktop app**.
3. Download the OAuth JSON file as `client_secret.json` in the project directory. This file and the saved `youtube_token.json` are ignored by Git.
4. In `.env`, set `YOUTUBE_AUTO_UPLOAD=true`. Upload privacy defaults to `private`; change `YOUTUBE_PRIVACY_STATUS` to `unlisted` or `public` only when you want that visibility.
5. Run the script. On the first upload, a browser window opens for YouTube authorization. The upload then uses the Gemini-generated title and the optional `YOUTUBE_DESCRIPTION`.

Set `YOUTUBE_AUTO_UPLOAD=false` to create videos without uploading. You can also configure `YOUTUBE_VIDEO_CATEGORY_ID` and `YOUTUBE_CLIENT_SECRETS_FILE` in `.env`.

## Configuration

### Video Settings
Edit these variables in `maker.py`:
- `URL_VIDEO`: YouTube video URL to process
- `NOMBRE_SALIDA`: Output filename (default: "short_con_subs.mp4")
- `YOUTUBE_AUTO_UPLOAD`: Automatically upload after rendering (default: `false`)
- `YOUTUBE_PRIVACY_STATUS`: Upload visibility: `private` (default), `unlisted`, or `public`
- `YOUTUBE_DESCRIPTION`: Optional YouTube description

### Subtitle Styling
Edit subtitle appearance in `subtitulos.py`:
- Font: `DejaVuSans-Bold` (change to any available system font)
- Font size: `70`
- Color: `yellow` with black stroke
- Position: Centered

### AI Analysis
Edit the prompt in `cerebro_gemini.py` to customize how Gemini analyzes videos for viral potential.

## Output Files

- `short_con_subs.mp4`: Final vertical Short with subtitles
- `transcripcion_completa.txt`: Full transcription with timestamps
- `video_temp.mp4`: Temporary downloaded video (auto-deleted)

## Troubleshooting

### Font Issues
If you encounter font errors, try these alternatives:
- `'LiberationSans-Bold'`
- `'Arial-Bold'` 
- `'Ubuntu-Bold'`

Or install fonts:
```bash
sudo apt install fonts-dejavu-core fonts-liberation
```

### MoviePy Issues
Ensure FFmpeg is installed and in your PATH:
```bash
ffmpeg -version
```

### Whisper Issues
The script uses `openai-whisper`. If you have the wrong whisper package:
```bash
pip uninstall whisper
pip install openai-whisper
```

### Gemini API Issues
- Make sure your API key is valid
- Check that you're using the correct model name (`gemini-2.5-flash`)
- Monitor your API usage to avoid rate limits

## File Structure

```
miscoshorts/
├── maker.py              # Main script
├── cerebro_gemini.py     # Gemini AI analysis
├── subtitulos.py         # Subtitle generation
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── .gitignore           # Git ignore rules
```

## Dependencies

- `yt-dlp`: YouTube video downloading
- `openai-whisper`: Audio transcription
- `moviepy`: Video editing and processing
- `google-genai`: Gemini AI API
- `google-api-python-client` and `google-auth-oauthlib`: Optional YouTube uploads
- `torch`: Deep learning (Whisper dependency)
- `PIL`: Image processing (MoviePy dependency)

## Author / Resources

If this project has been useful, explore the ideas behind the AI to deepen your engineering skills. Check out my books:

- 📖 Explora la Inteligencia Artificial: https://amzn.eu/d/dSwYhue
- 💻 Programar con Inteligencia Artificial: https://amzn.eu/d/eK4f73N
- YouTube channel: https://www.youtube.com/@jokioki?sub_confirmation=1


## License

MIT License - feel free to use and modify for your projects.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Tips for Best Results

1. **Choose videos with clear audio** - Whisper works best with clean speech
2. **Look for moments with strong reactions** - Gemini identifies these as viral potential
3. **Keep segments 30-60 seconds** - Ideal for Shorts attention spans
4. **Ensure good lighting and clear visuals** - Important for vertical format
5. **Test different subtitle styles** - Adjust colors and fonts for your brand
