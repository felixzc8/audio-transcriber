# Public S3 Audio Transcription API

This is a RESTful API service that transcribes a publicly accessible audio file (`.wav` or `.mp3`) from an S3 URL using OpenAI's Speech-to-Text (Whisper) API.

## Prerequisites

-   Python 3.8+
-   [FFmpeg](https://ffmpeg.org/download.html)
-   An OpenAI API key.

## Setup & Installation

1.  **Clone the repository...** (same as before)

2.  **Create and activate a virtual environment...** (same as before)

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure your environment variables:**
    Copy the example environment file. It now only requires your OpenAI key.
    ```bash
    cp .env.example .env
    ```
    Now, edit the `.env` file with your OpenAI key.

## API Usage

### Example Request

To transcribe an audio file, send a `POST` request to the `/transcribe` endpoint with a **public S3 HTTP URL**.

**Using `curl`:**
```bash
curl -X POST "[http://127.0.0.1:8000/transcribe](http://127.0.0.1:8000/transcribe)" \
-H "Content-Type: application/json" \
-d '{"public_url": "[https://your-bucket.s3.your-region.amazonaws.com/your-public-audio.mp3](https://your-bucket.s3.your-region.amazonaws.com/your-public-audio.mp3)"}'