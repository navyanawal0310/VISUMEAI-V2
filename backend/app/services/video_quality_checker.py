import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class VideoQualityChecker:
    """Check video quality before processing to prevent evaluation issues"""
    
    def __init__(self):
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    
    def check_video_quality(self, video_path: str) -> Dict[str, Any]:
        """Check if video meets minimum quality requirements"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return {
                    'can_proceed': False,
                    'issues': ['Cannot open video file'],
                    'warnings': [],
                    'recommendations': ['Check file format and permissions']
                }
            
            issues = []
            warnings = []
            recommendations = []
            
            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            logger.info(f"Video properties: {width}x{height}, {fps}fps, {duration:.1f}s")
            
            # Check resolution
            if width < 640 or height < 480:
                issues.append("Resolution too low (minimum 640x480 required)")
                recommendations.append("Record at 720p or higher for best results")
            elif width < 1280 or height < 720:
                warnings.append("720p or higher recommended for optimal analysis")
            
            # Check duration
            if duration < 10:
                issues.append("Video too short (minimum 10 seconds required)")
                recommendations.append("Record at least 30-60 seconds for meaningful analysis")
            elif duration < 30:
                warnings.append("30+ seconds recommended for comprehensive evaluation")
            
            # Check FPS
            if fps < 15:
                warnings.append("Low frame rate may affect analysis accuracy")
                recommendations.append("Record at 24fps or higher if possible")
            
            # Sample frames for quality checks
            frame_samples = self._sample_frames(cap, 5)
            
            if not frame_samples:
                issues.append("No valid frames found in video")
                return {
                    'can_proceed': False,
                    'issues': issues,
                    'warnings': warnings,
                    'recommendations': recommendations
                }
            
            # Check lighting and face detection
            lighting_issues = self._check_lighting(frame_samples)
            face_issues = self._check_face_detection(frame_samples)
            
            issues.extend(lighting_issues)
            issues.extend(face_issues)
            
            # Check for movement (too much or too little)
            movement_analysis = self._check_movement(frame_samples)
            if movement_analysis['too_static']:
                warnings.append("Very little movement detected - consider being more expressive")
            elif movement_analysis['too_much']:
                warnings.append("Excessive movement detected - try to maintain steady position")
            
            # Generate recommendations
            if not issues:
                recommendations.append("Video quality looks good! Ready for evaluation.")
            else:
                recommendations.extend([
                    "Ensure good lighting on your face",
                    "Look directly at the camera",
                    "Maintain steady position",
                    "Speak clearly and confidently"
                ])
            
            cap.release()
            
            return {
                'can_proceed': len(issues) == 0,
                'issues': issues,
                'warnings': warnings,
                'recommendations': recommendations,
                'video_stats': {
                    'resolution': f"{width}x{height}",
                    'fps': round(fps, 1),
                    'duration': round(duration, 1),
                    'frame_count': frame_count
                }
            }
            
        except Exception as e:
            logger.error(f"Error checking video quality: {str(e)}")
            return {
                'can_proceed': False,
                'issues': [f"Error analyzing video: {str(e)}"],
                'warnings': [],
                'recommendations': ['Try uploading a different video file']
            }
    
    def _sample_frames(self, cap, num_samples: int) -> List[np.ndarray]:
        """Sample frames evenly throughout the video"""
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_count <= 0:
            return []
        
        sample_indices = np.linspace(0, frame_count - 1, num_samples, dtype=int)
        frames = []
        
        for idx in sample_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
        
        return frames
    
    def _check_lighting(self, frames: List[np.ndarray]) -> List[str]:
        """Check if lighting is adequate for face detection"""
        issues = []
        
        brightness_values = []
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            brightness_values.append(brightness)
        
        avg_brightness = np.mean(brightness_values)
        
        if avg_brightness < 50:
            issues.append("Video too dark - face may not be detected properly")
        elif avg_brightness > 200:
            issues.append("Video very bright - may affect face detection accuracy")
        
        # Check for consistent lighting
        brightness_std = np.std(brightness_values)
        if brightness_std > 30:
            issues.append("Inconsistent lighting throughout video")
        
        return issues
    
    def _check_face_detection(self, frames: List[np.ndarray]) -> List[str]:
        """Check if face is detectable in video frames"""
        issues = []
        face_detected_count = 0
        
        for frame in frames:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                face_detected_count += 1
        
        face_detection_rate = face_detected_count / len(frames)
        
        if face_detection_rate == 0:
            issues.append("No face detected - ensure you're visible and well-lit")
        elif face_detection_rate < 0.5:
            issues.append("Face not consistently detected - check lighting and positioning")
        elif face_detection_rate < 0.8:
            issues.append("Face detection intermittent - ensure steady positioning")
        
        return issues
    
    def _check_movement(self, frames: List[np.ndarray]) -> Dict[str, bool]:
        """Check for appropriate amount of movement"""
        if len(frames) < 2:
            return {'too_static': False, 'too_much': False}
        
        # Calculate optical flow between consecutive frames
        movement_scores = []
        
        for i in range(1, len(frames)):
            prev_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
            curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            
            # Calculate frame difference
            diff = cv2.absdiff(prev_gray, curr_gray)
            movement_score = np.mean(diff)
            movement_scores.append(movement_score)
        
        avg_movement = np.mean(movement_scores)
        
        return {
            'too_static': avg_movement < 5,  # Very little movement
            'too_much': avg_movement > 50    # Excessive movement
        }
