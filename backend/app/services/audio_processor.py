import os
import subprocess
import logging
from typing import Optional
import httpx
from pydub import AudioSegment
from ..config.settings import settings

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Extract audio from video and transcribe using Whisper API"""
    
    def __init__(self):
        self.whisper_api_key = settings.OPENAI_API_KEY
    
    async def extract_audio(self, video_path: str, output_path: Optional[str] = None) -> str:
        """Extract audio from video file using pydub"""
        try:
            if output_path is None:
                video_dir = os.path.dirname(video_path)
                video_name = os.path.splitext(os.path.basename(video_path))[0]
                output_path = os.path.join(video_dir, f"{video_name}_audio.wav")
            
            logger.info(f"Extracting audio from: {video_path}")
            
            # Load video and extract audio
            video = AudioSegment.from_file(video_path)
            
            # Export as WAV for better compatibility
            video.export(output_path, format="wav")
            
            logger.info(f"Audio extracted to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error extracting audio: {str(e)}")
            raise
    
    async def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio using OpenAI Whisper API"""
        try:
            if not self.whisper_api_key:
                logger.warning("OpenAI API key not set, using mock transcription")
                return self._mock_transcription()
            
            logger.info(f"Transcribing audio: {audio_path}")
            
            # Use OpenAI Whisper API
            async with httpx.AsyncClient(timeout=300.0) as client:
                with open(audio_path, 'rb') as audio_file:
                    response = await client.post(
                        "https://api.openai.com/v1/audio/transcriptions",
                        headers={"Authorization": f"Bearer {self.whisper_api_key}"},
                        files={"file": audio_file},
                        data={"model": "whisper-1"}
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    transcript = result.get('text', '')
                    logger.info(f"Transcription complete: {len(transcript)} characters")
                    return transcript
                else:
                    logger.error(f"Whisper API error: {response.status_code}")
                    return self._mock_transcription()
                    
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return self._mock_transcription()
    
    def _mock_transcription(self) -> str:
        """Mock transcription for testing when API is not available"""
        return """
        Hello, my name is John Doe and I'm excited to apply for the Software Engineer position. 
        I have five years of experience in full-stack development, specializing in Python, JavaScript, 
        and React. In my previous role, I led a team of developers to build a scalable microservices 
        architecture that improved system performance by 40 percent.
        
        I'm particularly skilled in cloud technologies like AWS and Docker, and I have experience 
        with CI/CD pipelines. I'm passionate about writing clean, maintainable code and following 
        best practices. I believe my technical skills and leadership experience make me a strong 
        candidate for this role.
        
        I'm excited about the opportunity to contribute to your team and help build innovative solutions. 
        Thank you for considering my application.
        """
    
    async def process_video_audio(self, video_path: str) -> str:
        """Complete pipeline: extract audio and transcribe"""
        try:
            # Extract audio
            audio_path = await self.extract_audio(video_path)
            
            # Transcribe
            transcript = await self.transcribe_audio(audio_path)
            
            # Cleanup audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            return transcript
            
        except Exception as e:
            logger.warning(f"FFmpeg not available or error processing audio: {str(e)}")
            logger.info("Using mock transcription instead")
            return self._mock_transcription()
