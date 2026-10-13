from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
PROJECT_DIR = Path(__file__).resolve().parent
TOKEN_PATH = PROJECT_DIR / "youtube_token.json"
VALID_PRIVACY_STATUSES = {"private", "unlisted", "public"}


def _get_credentials(client_secrets_file):
    client_secrets_path = Path(client_secrets_file).expanduser()
    if not client_secrets_path.is_absolute():
        client_secrets_path = PROJECT_DIR / client_secrets_path

    if not client_secrets_path.is_file():
        raise FileNotFoundError(
            f"YouTube OAuth client file not found: {client_secrets_path}. "
            "Download a Desktop app OAuth client JSON from Google Cloud."
        )

    credentials = None
    if TOKEN_PATH.is_file():
        credentials = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets_path), SCOPES)
        credentials = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(credentials.to_json(), encoding="utf-8")

    return credentials


def upload_video(
    video_path,
    title,
    description="",
    privacy_status="private",
    category_id="22",
    client_secrets_file="client_secret.json",
):
    video_file = Path(video_path).expanduser().resolve()
    if not video_file.is_file():
        raise FileNotFoundError(f"Video file not found: {video_file}")

    title = title.strip()
    if not title:
        raise ValueError("YouTube video title cannot be empty.")
    if len(title) > 100:
        raise ValueError("YouTube video titles must be 100 characters or fewer.")
    if privacy_status not in VALID_PRIVACY_STATUSES:
        raise ValueError("YOUTUBE_PRIVACY_STATUS must be private, unlisted, or public.")

    credentials = _get_credentials(client_secrets_file)
    youtube = build("youtube", "v3", credentials=credentials, cache_discovery=False)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": str(category_id),
            },
            "status": {"privacyStatus": privacy_status},
        },
        media_body=MediaFileUpload(
            str(video_file),
            mimetype="video/mp4",
            chunksize=8 * 1024 * 1024,
            resumable=True,
        ),
    )

    response = None
    while response is None:
        progress, response = request.next_chunk()
        if progress:
            print(f"Upload progress: {progress.progress():.0%}")

    if "id" not in response:
        raise RuntimeError("YouTube upload completed without returning a video ID.")
    return response["id"]
