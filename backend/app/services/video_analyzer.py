"""
app/services/video_analyzer.py
-------------------------------
Lightweight video analysis using OpenCV and moviepy.
Analyzes: duration, resolution, brightness, audio presence.
No emotion detection. No ML models. No external APIs.
"""

import os
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

_DURATION_IDEAL_MIN = 60
_DURATION_IDEAL_MAX = 300
_DURATION_HARD_MAX  = 600
_RESOLUTION_GOOD  = 720
_RESOLUTION_OK    = 480
_BRIGHTNESS_LOW   = 50
_BRIGHTNESS_HIGH  = 210
_BRIGHTNESS_OK_LO = 80
_BRIGHTNESS_OK_HI = 180
_W_DURATION    = 0.30
_W_RESOLUTION  = 0.25
_W_BRIGHTNESS  = 0.25
_W_AUDIO       = 0.20


def analyze(video_path: str) -> Dict:
    """
    Analyze the video at *video_path* and return:
      { "video_score": float, "video_feedback": List[str] }
    Falls back gracefully on import or processing errors.
    """
    try:
        import cv2
    except ImportError:
        logger.warning("OpenCV not installed")
        return _unavailable("OpenCV not installed; run: pip install opencv-python-headless")

    try:
        from moviepy.editor import VideoFileClip
    except ImportError:
        logger.warning("moviepy not installed")
        return _unavailable("moviepy not installed; run: pip install moviepy")

    if not os.path.exists(video_path):
        return _unavailable(f"Video file not found: {video_path}")

    feedback: List[str] = []

    try:
        duration_score, audio_score, duration, has_audio = _analyze_duration_audio(
            VideoFileClip, video_path, feedback
        )
        resolution_score, brightness_score = _analyze_frames(cv2, video_path, feedback)

        overall = round(min(100.0, max(0.0,
            duration_score   * _W_DURATION +
            resolution_score * _W_RESOLUTION +
            brightness_score * _W_BRIGHTNESS +
            audio_score      * _W_AUDIO
        )), 1)

        if not feedback:
            feedback.append("Good video clarity and quality overall.")

        logger.info(f"Video analysis — score:{overall} dur:{duration:.1f}s audio:{has_audio}")
        return {"video_score": overall, "video_feedback": feedback}

    except Exception as e:
        logger.error(f"Video analysis error: {e}")
        return _unavailable(f"Video could not be analyzed: {e}")


def _unavailable(reason: str) -> Dict:
    return {"video_score": 0.0, "video_feedback": [reason]}


def _analyze_duration_audio(VideoFileClip, path, feedback):
    try:
        clip = VideoFileClip(path)
        duration  = clip.duration or 0.0
        has_audio = clip.audio is not None
        clip.close()
    except Exception as e:
        feedback.append("Could not read video duration or audio track.")
        return 50.0, 50.0, 0.0, False

    if _DURATION_IDEAL_MIN <= duration <= _DURATION_IDEAL_MAX:
        dur_score = 100.0
    elif duration < _DURATION_IDEAL_MIN:
        dur_score = max(0.0, (duration / _DURATION_IDEAL_MIN) * 100)
        if duration < 20:
            feedback.append(f"Video duration is too short ({duration:.0f}s). Aim for 1–5 minutes.")
        else:
            feedback.append(f"Video is short ({duration:.0f}s). Ideal length is 1–5 minutes.")
    elif duration <= _DURATION_HARD_MAX:
        excess = duration - _DURATION_IDEAL_MAX
        dur_score = max(50.0, 100.0 - (excess / (_DURATION_HARD_MAX - _DURATION_IDEAL_MAX)) * 50)
        feedback.append(f"Video is slightly long ({duration:.0f}s). Aim for under 5 minutes.")
    else:
        dur_score = 20.0
        feedback.append(f"Video is too long ({duration:.0f}s). Keep it under 5 minutes.")

    if has_audio:
        aud_score = 100.0
    else:
        aud_score = 0.0
        feedback.append("No audio track detected. Check your microphone before recording.")

    return dur_score, aud_score, duration, has_audio


def _analyze_frames(cv2, path, feedback):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        feedback.append("Could not open video file for frame analysis.")
        return 50.0, 50.0

    try:
        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        short_edge = min(width, height)
        if short_edge >= _RESOLUTION_GOOD:
            res_score = 100.0
        elif short_edge >= _RESOLUTION_OK:
            res_score = 70.0
            feedback.append(f"Video resolution is {width}×{height}. 720p or higher is recommended.")
        else:
            res_score = 30.0
            feedback.append(f"Low video resolution ({width}×{height}). Use at least 480p.")

        brightness_score = _sample_brightness(cv2, cap, total_frames, feedback)
        return res_score, brightness_score

    finally:
        cap.release()


def _sample_brightness(cv2, cap, total_frames, feedback):
    n_samples = min(10, max(1, total_frames))
    step = max(1, total_frames // n_samples)
    values = []

    for i in range(n_samples):
        cap.set(1, i * step)
        ret, frame = cap.read()
        if not ret or frame is None:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        values.append(float(gray.mean()))

    if not values:
        return 50.0

    avg = sum(values) / len(values)

    if _BRIGHTNESS_OK_LO <= avg <= _BRIGHTNESS_OK_HI:
        return 100.0
    elif avg < _BRIGHTNESS_LOW:
        feedback.append("Lighting is dim. Record in a well-lit environment.")
        return 20.0
    elif avg < _BRIGHTNESS_OK_LO:
        score = 40.0 + ((avg - _BRIGHTNESS_LOW) / (_BRIGHTNESS_OK_LO - _BRIGHTNESS_LOW)) * 60
        feedback.append("Lighting is slightly dim. Try improving room brightness.")
        return round(score, 1)
    elif avg > _BRIGHTNESS_HIGH:
        feedback.append("Video is overexposed. Avoid strong backlighting or direct sunlight.")
        return 20.0
    else:
        score = 100.0 - ((avg - _BRIGHTNESS_OK_HI) / (_BRIGHTNESS_HIGH - _BRIGHTNESS_OK_HI)) * 60
        feedback.append("Video is slightly bright. Reduce background lighting if possible.")
        return round(score, 1)