from pydantic import BaseModel
from typing import Dict
import os

class VideoAnalysisConfig(BaseModel):
    """Configurable parameters for video analysis"""
    
    # Eye contact thresholds
    eye_contact_range_min: float = 0.25  # Acceptable horizontal position
    eye_contact_range_max: float = 0.75
    eye_contact_penalty_rate: float = 1.0  # Linear penalty rate
    
    # Posture thresholds
    posture_shoulder_multiplier: float = 5.0  # Reduced from 10
    posture_use_median: bool = True  # Use median instead of mean
    
    # Temporal smoothing
    window_size_frames: int = 30  # ~6 seconds at 5fps
    window_overlap_ratio: float = 0.5  # 50% overlap
    good_eye_contact_threshold: float = 0.7  # For windowed analysis
    
    # Duration adjustments
    duration_bonus_max: float = 0.10  # 10% max bonus
    duration_baseline_seconds: float = 60  # 1 minute baseline
    
    # Engagement scoring
    engagement_weight: float = 0.20  # In confidence calculation
    
    # Scoring weights
    confidence_weights: Dict[str, float] = {
        'eye_contact': 0.25,
        'posture': 0.25,
        'gestures': 0.15,
        'expressiveness': 0.15,
        'engagement': 0.20
    }
    
    # Accessibility mode settings
    accessibility_mode_weights: Dict[str, float] = {
        'role_match': 0.6,      # Increased from 0.4
        'soft_skills': 0.4      # Increased from 0.3
    }
    
    # Bias monitoring thresholds
    disparate_impact_threshold: float = 0.8  # Four-fifths rule
    min_evaluations_for_bias_check: int = 10

# Load config with environment variable override support
def load_config() -> VideoAnalysisConfig:
    """Load configuration with environment variable overrides"""
    config = VideoAnalysisConfig()
    
    # Override with environment variables if present
    if os.getenv('EYE_CONTACT_RANGE_MIN'):
        config.eye_contact_range_min = float(os.getenv('EYE_CONTACT_RANGE_MIN'))
    if os.getenv('EYE_CONTACT_RANGE_MAX'):
        config.eye_contact_range_max = float(os.getenv('EYE_CONTACT_RANGE_MAX'))
    if os.getenv('POSTURE_MULTIPLIER'):
        config.posture_shoulder_multiplier = float(os.getenv('POSTURE_MULTIPLIER'))
    if os.getenv('WINDOW_SIZE_FRAMES'):
        config.window_size_frames = int(os.getenv('WINDOW_SIZE_FRAMES'))
    
    return config

# Global config instance
config = load_config()
