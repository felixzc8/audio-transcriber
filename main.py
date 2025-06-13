from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, HttpUrl
from transcriber import transcribe_audio_from_public_url

app = FastAPI(
    title="Public Audio Transcription API",
    description="An API to transcribe audio files from public S3 URLs using OpenAI's Whisper.",
    version="1.1.0",
)

class TranscriptionRequest(BaseModel):
    # Use Pydantic's HttpUrl for automatic validation
    public_url: HttpUrl

class TranscriptionResponse(BaseModel):
    transcript: str

@app.post("/transcribe", response_model=TranscriptionResponse)
async def create_transcription(request: TranscriptionRequest):
    """
    Accepts a public S3 URL of an audio file and returns the transcription.
    """
    try:
        # Pass the URL as a string to the transcription function
        transcript_text = await transcribe_audio_from_public_url(str(request.public_url))
        return TranscriptionResponse(transcript=transcript_text)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ConnectionError as e:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.get("/")
def read_root():
    return {"message": "Welcome to the Public Audio Transcription API"}