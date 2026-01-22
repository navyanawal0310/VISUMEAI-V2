import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List, Tuple
import logging
from ..models.schemas import VideoAnalysisResult
from ..config.evaluation_config import config

logger = logging.getLogger(__name__)

class VideoProcessor:
    """Process video files and extract visual features using MediaPipe"""
    
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands
        
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5
        )
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5
        )
    
    async def process_video(self, video_path: str, video_id: str) -> VideoAnalysisResult:
        """Main entry point for video processing"""
        try:
            logger.info(f"Processing video: {video_path}")
            
            # Extract frames and analyze
            frames_data = self._extract_and_analyze_frames(video_path)
            
            # Compute metrics with improvements
            metrics = self._compute_metrics(frames_data)
            
            # Get video metadata
            metadata = self._get_video_metadata(video_path)
            
            # Apply duration-based adjustments
            adjusted_metrics = self._apply_duration_adjustments(metrics, metadata['duration'])
            
            result = VideoAnalysisResult(
                video_id=video_id,
                confidence_score=adjusted_metrics['confidence'],
                eye_contact_score=adjusted_metrics['eye_contact'],
                posture_score=adjusted_metrics['posture'],
                gesture_score=adjusted_metrics['gestures'],
                expressiveness_score=adjusted_metrics['expressiveness'],
                engagement_score=adjusted_metrics['engagement'],
                frame_count=metadata['frame_count'],
                duration_seconds=metadata['duration'],
                eye_contact_confidence=adjusted_metrics.get('eye_contact_confidence'),
                posture_confidence=adjusted_metrics.get('posture_confidence'),
                measurement_notes=adjusted_metrics.get('notes', [])
            )
            
            logger.info(f"Video analysis complete: {video_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing video {video_id}: {str(e)}")
            raise
    
    def _extract_and_analyze_frames(self, video_path: str, sample_rate: int = 5) -> List[Dict]:
        """Extract frames and analyze with MediaPipe"""
        cap = cv2.VideoCapture(video_path)
        frames_data = []
        frame_idx = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Sample frames to reduce processing time
            if frame_idx % sample_rate == 0:
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Analyze frame
                frame_analysis = self._analyze_frame(rgb_frame)
                frames_data.append(frame_analysis)
            
            frame_idx += 1
        
        cap.release()
        return frames_data
    
    def _analyze_frame(self, rgb_frame: np.ndarray) -> Dict:
        """Analyze a single frame with MediaPipe"""
        frame_data = {
            'has_face': False,
            'has_pose': False,
            'has_hands': False,
            'eye_gaze_center': 0.0,
            'head_pose': None,
            'posture_alignment': 0.0,
            'hand_gestures': 0
        }
        
        # Face mesh analysis
        face_results = self.face_mesh.process(rgb_frame)
        if face_results.multi_face_landmarks:
            frame_data['has_face'] = True
            face_landmarks = face_results.multi_face_landmarks[0]
            frame_data['eye_gaze_center'] = self._compute_eye_gaze(face_landmarks)
            frame_data['head_pose'] = self._compute_head_pose(face_landmarks)
        
        # Pose analysis
        pose_results = self.pose.process(rgb_frame)
        if pose_results.pose_landmarks:
            frame_data['has_pose'] = True
            frame_data['posture_alignment'] = self._compute_posture_alignment(
                pose_results.pose_landmarks
            )
        
        # Hand gesture analysis
        hands_results = self.hands.process(rgb_frame)
        if hands_results.multi_hand_landmarks:
            frame_data['has_hands'] = True
            frame_data['hand_gestures'] = len(hands_results.multi_hand_landmarks)
        
        return frame_data
    
    def _compute_eye_gaze(self, face_landmarks) -> float:
        """Compute eye gaze direction with relaxed thresholds (0-1, higher = better eye contact)"""
        # Simplified: check if eyes are centered
        # IMPROVED: More forgiving range and gentler penalties
        left_eye_idx = 33
        right_eye_idx = 263
        
        left_eye = face_landmarks.landmark[left_eye_idx]
        right_eye = face_landmarks.landmark[right_eye_idx]
        
        # Use configurable eye contact range
        avg_x = (left_eye.x + right_eye.x) / 2
        if config.eye_contact_range_min < avg_x < config.eye_contact_range_max:
            return 1.0
        else:
            # GENTLER penalty: linear decay (was deviation * 2)
            # Looking away isn't automatically bad - could be thinking
            center = (config.eye_contact_range_min + config.eye_contact_range_max) / 2
            deviation = abs(avg_x - center)
            return max(0, 1 - deviation * config.eye_contact_penalty_rate)
    
    def _compute_head_pose(self, face_landmarks) -> Dict[str, float]:
        """Compute head rotation angles"""
        # Simplified head pose estimation
        nose_tip = face_landmarks.landmark[1]
        chin = face_landmarks.landmark[152]
        
        return {
            'pitch': (nose_tip.y - chin.y) * 100,
            'yaw': (nose_tip.x - 0.5) * 100,
        }
    
    def _compute_posture_alignment(self, pose_landmarks) -> float:
        """Compute posture alignment score with relaxed expectations (0-1)"""
        # Check shoulder alignment and spine straightness
        # IMPROVED: More forgiving for natural movement and body diversity
        left_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        
        # Check if shoulders are level
        shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
        
        # REDUCED multiplier: 5x instead of 10x
        # Allows ~20% shoulder height difference without major penalty
        # Natural to lean, gesture, or shift position during long responses
        alignment_score = max(0, 1 - shoulder_diff * config.posture_shoulder_multiplier)
        
        return alignment_score
    
    def _compute_metrics(self, frames_data: List[Dict]) -> Dict[str, float]:
        """Compute aggregate metrics with temporal smoothing and confidence intervals"""
        if not frames_data:
            return {
                'confidence': 0.0,
                'eye_contact': 0.0,
                'posture': 0.0,
                'gestures': 0.0,
                'expressiveness': 0.0,
                'engagement': 0.0,
                'eye_contact_confidence': {'lower': 0.0, 'upper': 0.0},
                'posture_confidence': {'lower': 0.0, 'upper': 0.0},
                'notes': []
            }
        
        # TEMPORAL SMOOTHING: Use configurable window size
        window_size = config.window_size_frames
        windowed_scores = self._compute_windowed_scores(frames_data, window_size)
        
        # Eye contact score with confidence interval
        eye_contact_scores = [w['eye_contact'] for w in windowed_scores]
        eye_contact_score = np.mean(eye_contact_scores) if eye_contact_scores else 0.0
        eye_contact_conf = self._compute_confidence_interval(eye_contact_scores)
        
        # Posture score with confidence interval (use median for robustness)
        posture_scores = [w['posture'] for w in windowed_scores]
        posture_score = np.median(posture_scores) if posture_scores else 0.0
        posture_conf = self._compute_confidence_interval(posture_scores)
        
        # Gesture score (presence and variety)
        gesture_frames = [f['hand_gestures'] for f in frames_data]
        gesture_ratio = sum(1 for g in gesture_frames if g > 0) / len(gesture_frames)
        gesture_score = min(1.0, gesture_ratio * 1.5)  # Encourage some gestures
        
        # Expressiveness (variation in facial landmarks)
        face_detection_ratio = sum(1 for f in frames_data if f['has_face']) / len(frames_data)
        expressiveness_score = face_detection_ratio * 0.8 + gesture_score * 0.2
        
        # NEW: Engagement score (holistic measure)
        engagement_score = self._compute_engagement_score(frames_data)
        
        # Overall confidence (composite) - use configurable weights
        confidence_score = (
            eye_contact_score * config.confidence_weights['eye_contact'] +
            posture_score * config.confidence_weights['posture'] +
            gesture_score * config.confidence_weights['gestures'] +
            expressiveness_score * config.confidence_weights['expressiveness'] +
            engagement_score * config.confidence_weights['engagement']
        )
        
        # Generate contextual notes
        notes = self._generate_measurement_notes(frames_data, windowed_scores)
        
        return {
            'confidence': float(confidence_score),
            'eye_contact': float(eye_contact_score),
            'posture': float(posture_score),
            'gestures': float(gesture_score),
            'expressiveness': float(expressiveness_score),
            'engagement': float(engagement_score),
            'eye_contact_confidence': eye_contact_conf,
            'posture_confidence': posture_conf,
            'notes': notes
        }
    
    def _compute_windowed_scores(self, frames_data: List[Dict], window_size: int) -> List[Dict]:
        """Compute scores over sliding windows for temporal smoothing"""
        windowed_scores = []
        
        overlap_frames = int(window_size * config.window_overlap_ratio)
        for i in range(0, len(frames_data), overlap_frames):
            window = frames_data[i:i+window_size]
            if not window:
                continue
            
            # Eye contact: Use configurable threshold
            eye_contacts = [f['eye_gaze_center'] for f in window if f['has_face']]
            if eye_contacts:
                good_eye_contact_ratio = sum(1 for ec in eye_contacts if ec > config.good_eye_contact_threshold) / len(eye_contacts)
                window_eye_score = good_eye_contact_ratio
            else:
                window_eye_score = 0.5
            
            # Posture: Use median for robustness to outliers
            postures = [f['posture_alignment'] for f in window if f['has_pose']]
            window_posture_score = np.median(postures) if postures else 0.5
            
            windowed_scores.append({
                'eye_contact': window_eye_score,
                'posture': window_posture_score
            })
        
        return windowed_scores
    
    def _compute_confidence_interval(self, scores: List[float]) -> Dict[str, float]:
        """Compute 95% confidence interval for transparency"""
        if not scores or len(scores) < 2:
            return {'lower': 0.0, 'upper': 0.0}
        
        mean = np.mean(scores)
        std = np.std(scores)
        n = len(scores)
        
        # 95% confidence interval
        margin = 1.96 * std / np.sqrt(n)
        
        return {
            'lower': float(max(0, mean - margin)),
            'upper': float(min(1, mean + margin))
        }
    
    def _compute_engagement_score(self, frames_data: List[Dict]) -> float:
        """Holistic engagement: presence + expressiveness + natural movement"""
        if not frames_data:
            return 0.0
        
        # Face presence (are they in frame and visible?)
        face_presence = sum(1 for f in frames_data if f['has_face']) / len(frames_data)
        
        # Expressiveness variation (animated vs. static)
        # Look at variance in eye positions as proxy for facial animation
        eye_positions = [f['eye_gaze_center'] for f in frames_data if f['has_face']]
        expressiveness = min(1.0, np.std(eye_positions) * 5) if eye_positions else 0.0
        
        # Head movement naturalness (some movement is good, too much or too little is bad)
        head_movements = []
        for i in range(1, len(frames_data)):
            if frames_data[i]['head_pose'] and frames_data[i-1]['head_pose']:
                yaw_diff = abs(frames_data[i]['head_pose']['yaw'] - frames_data[i-1]['head_pose']['yaw'])
                head_movements.append(yaw_diff)
        
        if head_movements:
            avg_movement = np.mean(head_movements)
            # Optimal movement is in middle range (not static, not erratic)
            movement_score = 1.0 - abs(avg_movement - 2.0) / 2.0
            movement_score = max(0, min(1, movement_score))
        else:
            movement_score = 0.5
        
        engagement = (
            face_presence * 0.5 +           # Present in frame
            expressiveness * 0.3 +          # Animated/expressive
            movement_score * 0.2            # Natural movement
        )
        
        return float(max(0, min(1, engagement)))
    
    def _generate_measurement_notes(self, frames_data: List[Dict], windowed_scores: List[Dict]) -> List[str]:
        """Generate contextual notes about the measurement"""
        notes = []
        
        # Note about video length
        duration = len(frames_data) / 5  # Approximate seconds (5fps sampling)
        if duration > 120:
            notes.append("Long video: Natural movement and posture shifts expected and accounted for")
        
        # Note about eye contact variability
        if windowed_scores:
            eye_variance = np.std([w['eye_contact'] for w in windowed_scores])
            if eye_variance > 0.2:
                notes.append("Variable eye contact detected: May indicate thoughtful pauses (normal)")
        
        # Note about face detection
        face_ratio = sum(1 for f in frames_data if f['has_face']) / len(frames_data)
        if face_ratio < 0.9:
            notes.append("Occasional face occlusion detected: May affect eye contact measurement")
        
        return notes
    
    def _apply_duration_adjustments(self, metrics: Dict, duration: float) -> Dict:
        """Adjust scores based on video duration - longer videos get slight bonuses"""
        # Longer videos make it harder to maintain perfect posture/eye contact
        # Give a small bonus for longer videos
        duration_factor = min(1.0, 60 / max(duration, 30))  # Normalize to 1 minute
        
        adjusted = metrics.copy()
        
        for metric in ['posture', 'eye_contact']:
            if metric in adjusted:
                # Give up to 10% bonus for videos over 2 minutes
                bonus = (1 - duration_factor) * 0.1
                adjusted[metric] = min(1.0, metrics[metric] * (1 + bonus))
        
        # Recalculate confidence with adjusted scores
        adjusted['confidence'] = (
            adjusted['eye_contact'] * 0.25 +
            adjusted['posture'] * 0.25 +
            adjusted['gestures'] * 0.15 +
            adjusted['expressiveness'] * 0.15 +
            adjusted['engagement'] * 0.20
        )
        
        return adjusted
    
    def _get_video_metadata(self, video_path: str) -> Dict:
        """Extract video metadata"""
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = frame_count / fps if fps > 0 else 0
        cap.release()
        
        return {
            'frame_count': frame_count,
            'fps': fps,
            'duration': duration
        }
    
    def __del__(self):
        """Cleanup MediaPipe resources"""
        if hasattr(self, 'pose'):
            self.pose.close()
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()
        if hasattr(self, 'hands'):
            self.hands.close()
