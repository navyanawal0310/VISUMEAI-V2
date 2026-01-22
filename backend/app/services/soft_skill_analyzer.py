import logging
from typing import Optional
from ..models.schemas import (
    SoftSkillIndex,
    VideoAnalysisResult,
    TranscriptAnalysisResult
)

logger = logging.getLogger(__name__)

class SoftSkillAnalyzer:
    """Analyze soft skills from video and transcript data"""
    
    async def analyze_soft_skills(
        self,
        video_analysis: Optional[VideoAnalysisResult] = None,
        transcript_analysis: Optional[TranscriptAnalysisResult] = None
    ) -> SoftSkillIndex:
        """Compute overall soft skill index"""
        try:
            logger.info("Analyzing soft skills")
            
            # Communication score (from transcript)
            communication = self._compute_communication_score(transcript_analysis)
            
            # Confidence score (from video + transcript)
            confidence = self._compute_confidence_score(video_analysis, transcript_analysis)
            
            # Engagement score (from video)
            engagement = self._compute_engagement_score(video_analysis)
            
            # Professionalism score (combined)
            professionalism = self._compute_professionalism_score(
                video_analysis,
                transcript_analysis
            )
            
            # Overall score (weighted average)
            overall_score = (
                communication * 0.3 +
                confidence * 0.3 +
                engagement * 0.2 +
                professionalism * 0.2
            )
            
            result = SoftSkillIndex(
                communication=communication,
                confidence=confidence,
                engagement=engagement,
                professionalism=professionalism,
                overall_score=overall_score
            )
            
            logger.info(f"Soft skill analysis complete: {overall_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing soft skills: {str(e)}")
            raise
    
    def _compute_communication_score(
        self,
        transcript_analysis: Optional[TranscriptAnalysisResult]
    ) -> float:
        """Compute communication effectiveness score"""
        if not transcript_analysis:
            return 0.5  # Neutral if no data
        
        # Weight components
        clarity = transcript_analysis.clarity_score
        vocabulary = transcript_analysis.vocabulary_diversity
        coherence = transcript_analysis.coherence_score
        
        # Check for adequate word count (not too short)
        word_count_score = min(1.0, transcript_analysis.word_count / 100)
        
        communication_score = (
            clarity * 0.35 +
            vocabulary * 0.25 +
            coherence * 0.3 +
            word_count_score * 0.1
        )
        
        return min(1.0, max(0.0, communication_score))
    
    def _compute_confidence_score(
        self,
        video_analysis: Optional[VideoAnalysisResult],
        transcript_analysis: Optional[TranscriptAnalysisResult]
    ) -> float:
        """Compute confidence score"""
        scores = []
        
        # Video-based confidence
        if video_analysis:
            # Direct confidence score from video
            scores.append(video_analysis.confidence_score)
            
            # Eye contact contributes to confidence
            scores.append(video_analysis.eye_contact_score)
            
            # Posture contributes to confidence
            scores.append(video_analysis.posture_score)
        
        # Transcript-based confidence
        if transcript_analysis:
            # Positive sentiment indicates confidence
            sentiment_score = 0.7 if transcript_analysis.sentiment == 'positive' else 0.5
            scores.append(sentiment_score)
            
            # Clear communication indicates confidence
            scores.append(transcript_analysis.clarity_score)
        
        if not scores:
            return 0.5
        
        return sum(scores) / len(scores)
    
    def _compute_engagement_score(
        self,
        video_analysis: Optional[VideoAnalysisResult]
    ) -> float:
        """Compute engagement and energy level"""
        if not video_analysis:
            return 0.5
        
        # Expressiveness indicates engagement
        expressiveness = video_analysis.expressiveness_score
        
        # Gestures indicate engagement
        gestures = video_analysis.gesture_score
        
        # Eye contact indicates engagement
        eye_contact = video_analysis.eye_contact_score
        
        engagement_score = (
            expressiveness * 0.4 +
            gestures * 0.3 +
            eye_contact * 0.3
        )
        
        return min(1.0, max(0.0, engagement_score))
    
    def _compute_professionalism_score(
        self,
        video_analysis: Optional[VideoAnalysisResult],
        transcript_analysis: Optional[TranscriptAnalysisResult]
    ) -> float:
        """Compute professionalism score"""
        scores = []
        
        # Video professionalism
        if video_analysis:
            # Good posture indicates professionalism
            scores.append(video_analysis.posture_score)
            
            # Appropriate gestures
            # Not too few, not too many
            gesture_score = video_analysis.gesture_score
            if 0.3 <= gesture_score <= 0.8:
                scores.append(0.9)
            else:
                scores.append(0.6)
        
        # Transcript professionalism
        if transcript_analysis:
            # Technical terms indicate professional knowledge
            tech_term_score = min(1.0, len(transcript_analysis.technical_terms) / 5)
            scores.append(tech_term_score)
            
            # Coherent speech indicates professionalism
            scores.append(transcript_analysis.coherence_score)
            
            # Adequate length indicates preparation
            length_score = min(1.0, transcript_analysis.word_count / 150)
            scores.append(length_score)
        
        if not scores:
            return 0.5
        
        return sum(scores) / len(scores)
    
    def get_soft_skill_feedback(self, soft_skill_index: SoftSkillIndex) -> dict:
        """Generate human-readable feedback for soft skills"""
        feedback = {}
        
        # Communication feedback
        if soft_skill_index.communication >= 0.8:
            feedback['communication'] = "Excellent communication skills. Clear, articulate, and well-structured responses."
        elif soft_skill_index.communication >= 0.6:
            feedback['communication'] = "Good communication. Some minor improvements in clarity or structure could help."
        else:
            feedback['communication'] = "Consider improving speech clarity, vocabulary usage, and logical flow."
        
        # Confidence feedback
        if soft_skill_index.confidence >= 0.8:
            feedback['confidence'] = "Strong, confident presentation with good body language and eye contact."
        elif soft_skill_index.confidence >= 0.6:
            feedback['confidence'] = "Moderate confidence. Work on maintaining eye contact and posture."
        else:
            feedback['confidence'] = "Build confidence through practice. Focus on posture, eye contact, and tone."
        
        # Engagement feedback
        if soft_skill_index.engagement >= 0.8:
            feedback['engagement'] = "Highly engaging and energetic presentation."
        elif soft_skill_index.engagement >= 0.6:
            feedback['engagement'] = "Good engagement level. Could use more expressiveness or gestures."
        else:
            feedback['engagement'] = "Increase engagement through facial expressions and appropriate gestures."
        
        # Professionalism feedback
        if soft_skill_index.professionalism >= 0.8:
            feedback['professionalism'] = "Highly professional demeanor and technical competence demonstrated."
        elif soft_skill_index.professionalism >= 0.6:
            feedback['professionalism'] = "Professional presentation. Continue developing technical vocabulary."
        else:
            feedback['professionalism'] = "Focus on professional presentation and demonstrating technical knowledge."
        
        return feedback
