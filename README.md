# Public S3 Audio Transcription API

This is a RESTful API service that transcribes publicly accessible audio files from S3 URLs using OpenAI's Speech-to-Text (Whisper) API. The service automatically handles large files by splitting them into manageable chunks.

## Supported Audio Formats

The service supports the following audio file formats:
- MP3 (`.mp3`)
- WAV (`.wav`)
- M4A (`.m4a`)
- OGG (`.ogg`)
- FLAC (`.flac`)
- AAC (`.aac`)

## Features

- Transcribes audio files from public S3 URLs
- Automatically handles files larger than 25MB by splitting them
- Supports multiple audio formats
- Streaming download for efficient memory usage
- Temporary file management for security

## Prerequisites

- Python 3.8+
- [FFmpeg](https://ffmpeg.org/download.html) (required for handling large files)
- An OpenAI API key

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd audio-transcriber
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Running the Service

Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

## API Usage

### Transcribe Audio

Send a POST request to the `/transcribe` endpoint with a public S3 HTTP URL.

**Endpoint:** `POST /transcribe`

**Request Body:**
```json
{
    "public_url": "https://your-bucket.s3.your-region.amazonaws.com/your-audio-file.mp3"
}
```

**Example using curl:**
```bash
curl -X POST "http://127.0.0.1:8000/transcribe" \
-H "Content-Type: application/json" \
-d '{"public_url": "https://your-bucket.s3.your-region.amazonaws.com/your-audio-file.mp3"}'
```

**Response:**
```json
{
    "transcript": "The transcribed text of your audio file..."
}
```

### Error Responses

The API may return the following error responses:

- `400 Bad Request`: Invalid S3 URL or unsupported file format
- `422 Unprocessable Entity`: Invalid request format
- `500 Internal Server Error`: Server-side errors (e.g., OpenAI API issues)

## Notes

- Maximum file size for direct transcription: 25MB
- Files larger than 25MB are automatically split and processed in chunks
- All files are processed securely using temporary storage
- The service requires a valid OpenAI API key with access to the Whisper API

## API Documentation

When the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`