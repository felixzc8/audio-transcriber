import os
import openai
import requests
from dotenv import load_dotenv
import ffmpeg
import tempfile
from urllib.parse import urlparse

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# OpenAI's Whisper API has a 25 MB file size limit
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB in bytes

# Supported audio file extensions
SUPPORTED_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac'}

def is_valid_audio_file(filename: str) -> bool:
    """Checks if the file has a supported audio extension."""
    _, ext = os.path.splitext(filename.lower())
    return ext in SUPPORTED_EXTENSIONS

def is_valid_s3_http_url(url: str) -> bool:
    """Checks if a URL is a valid S3 HTTP URL."""
    parsed_url = urlparse(url)
    return (
        parsed_url.scheme in ['http', 'https'] and
        '.s3.' in parsed_url.netloc and
        'amazonaws.com' in parsed_url.netloc
    )

async def transcribe_audio_from_public_url(public_url: str) -> str:
    """
    Downloads an audio file from a public URL, transcribes it,
    and handles large files by splitting them.
    """
    if not is_valid_s3_http_url(public_url):
        raise ValueError("URL must be a valid public S3 HTTP URL (e.g., https://bucket-name.s3.region.amazonaws.com/key)")

    # Get the filename from the URL path and validate extension
    file_name = os.path.basename(urlparse(public_url).path)
    if not is_valid_audio_file(file_name):
        raise ValueError(f"Unsupported file format. Supported formats are: {', '.join(SUPPORTED_EXTENSIONS)}")

    try:
        with requests.get(public_url, stream=True) as r:
            r.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            # Check file size from headers without downloading the whole file first
            file_size = int(r.headers.get('Content-Length', 0))

            with tempfile.TemporaryDirectory() as temp_dir:
                # Get the filename from the URL path
                local_file_path = os.path.join(temp_dir, file_name)

                # Download the file
                with open(local_file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

                if file_size > 0 and file_size <= MAX_FILE_SIZE:
                    # Transcribe the whole file if it's within the size limit
                    with open(local_file_path, "rb") as audio_file:
                        transcript = openai.Audio.transcribe("whisper-1", audio_file)
                    return transcript['text']
                else:
                    # If the file is large or size is unknown, split and transcribe
                    return await split_and_transcribe_audio(local_file_path, temp_dir)

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to download file from URL: {e}")
    except Exception as e:
        # Re-raise other exceptions to be handled by the FastAPI endpoint
        raise e

async def split_and_transcribe_audio(file_path: str, temp_dir: str) -> str:
    """
    Splits a large audio file into smaller chunks and transcribes each one.
    (This function remains unchanged)
    """
    probe = ffmpeg.probe(file_path)
    duration = float(probe['format']['duration'])

    # Aim for chunks of around 20 MB, assuming average audio compression
    # This logic may need tuning based on typical audio formats
    num_chunks = int(duration // 600) + 1
    chunk_duration = duration / num_chunks

    full_transcript = ""
    for i in range(num_chunks):
        chunk_path = os.path.join(temp_dir, f"chunk_{i}.mp3")
        start_time = i * chunk_duration

        (
            ffmpeg
            .input(file_path, ss=start_time, t=chunk_duration)
            .output(chunk_path, acodec='libmp3lame')
            .overwrite_output()
            .run(quiet=True)
        )

        with open(chunk_path, "rb") as audio_file:
            transcript_chunk = openai.Audio.transcribe("whisper-1", audio_file)
            full_transcript += transcript_chunk['text'] + " "

    return full_transcript.strip()