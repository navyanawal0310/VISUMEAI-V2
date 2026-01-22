import logging
from typing import List, Dict, Optional
from ..models.schemas import CandidateEvaluation, ImprovementComparison

logger = logging.getLogger(__name__)

class ImprovementTracker:
    """Track and compare candidate improvement across multiple submissions"""
    
    def compare_evaluations(
        self,
        previous: CandidateEvaluation,
        current: CandidateEvaluation,
        job_title: str
    ) -> ImprovementComparison:
        """Compare two evaluations and generate improvement statistics"""
        try:
            logger.info(f"Comparing evaluations for {current.candidate_name}")
            
            # Calculate overall score change
            score_change = current.overall_score - previous.overall_score
            score_change_pct = (score_change / previous.overall_score) * 100 if previous.overall_score > 0 else 0
            
            # Compare detailed metrics
            improvements = self._compare_detailed_metrics(previous, current)
            
            # Identify improved and declined areas
            areas_improved = []
            areas_declined = []
            
            for category, metrics in improvements.items():
                if metrics['change'] > 0:
                    areas_improved.append(f"{category}: +{metrics['change']:.1f} points")
                elif metrics['change'] < 0:
                    areas_declined.append(f"{category}: {metrics['change']:.1f} points")
            
            # Generate summary
            summary = self._generate_improvement_summary(score_change, improvements)
            
            # Compare recommendations
            rec_change = self._compare_recommendations(
                previous.recommendation,
                current.recommendation
            )
            
            comparison = ImprovementComparison(
                candidate_name=current.candidate_name,
                job_title=job_title,
                previous_version=previous.submission_version,
                current_version=current.submission_version,
                previous_score=previous.overall_score,
                current_score=current.overall_score,
                score_change=score_change,
                score_change_percentage=score_change_pct,
                improvements=improvements,
                areas_improved=areas_improved,
                areas_declined=areas_declined,
                overall_improvement_summary=summary,
                recommendation_change=rec_change
            )
            
            logger.info(f"Comparison complete: {score_change:+.1f} points change")
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing evaluations: {str(e)}")
            raise
    
    def _compare_detailed_metrics(
        self,
        previous: CandidateEvaluation,
        current: CandidateEvaluation
    ) -> Dict[str, Dict[str, float]]:
        """Compare all detailed metrics between two evaluations"""
        comparisons = {}
        
        # Compare video metrics
        if previous.video_analysis and current.video_analysis:
            comparisons['Video Confidence'] = {
                'old': previous.video_analysis.confidence_score * 100,
                'new': current.video_analysis.confidence_score * 100,
                'change': (current.video_analysis.confidence_score - previous.video_analysis.confidence_score) * 100
            }
            comparisons['Eye Contact'] = {
                'old': previous.video_analysis.eye_contact_score * 100,
                'new': current.video_analysis.eye_contact_score * 100,
                'change': (current.video_analysis.eye_contact_score - previous.video_analysis.eye_contact_score) * 100
            }
            comparisons['Posture'] = {
                'old': previous.video_analysis.posture_score * 100,
                'new': current.video_analysis.posture_score * 100,
                'change': (current.video_analysis.posture_score - previous.video_analysis.posture_score) * 100
            }
            comparisons['Engagement'] = {
                'old': previous.video_analysis.engagement_score * 100,
                'new': current.video_analysis.engagement_score * 100,
                'change': (current.video_analysis.engagement_score - previous.video_analysis.engagement_score) * 100
            }
        
        # Compare transcript metrics
        if previous.transcript_analysis and current.transcript_analysis:
            comparisons['Speech Clarity'] = {
                'old': previous.transcript_analysis.clarity_score * 100,
                'new': current.transcript_analysis.clarity_score * 100,
                'change': (current.transcript_analysis.clarity_score - previous.transcript_analysis.clarity_score) * 100
            }
            comparisons['Vocabulary'] = {
                'old': previous.transcript_analysis.vocabulary_diversity * 100,
                'new': current.transcript_analysis.vocabulary_diversity * 100,
                'change': (current.transcript_analysis.vocabulary_diversity - previous.transcript_analysis.vocabulary_diversity) * 100
            }
        
        # Compare soft skills
        if previous.soft_skill_index and current.soft_skill_index:
            comparisons['Communication'] = {
                'old': previous.soft_skill_index.communication * 100,
                'new': current.soft_skill_index.communication * 100,
                'change': (current.soft_skill_index.communication - previous.soft_skill_index.communication) * 100
            }
            comparisons['Confidence'] = {
                'old': previous.soft_skill_index.confidence * 100,
                'new': current.soft_skill_index.confidence * 100,
                'change': (current.soft_skill_index.confidence - previous.soft_skill_index.confidence) * 100
            }
            comparisons['Professionalism'] = {
                'old': previous.soft_skill_index.professionalism * 100,
                'new': current.soft_skill_index.professionalism * 100,
                'change': (current.soft_skill_index.professionalism - previous.soft_skill_index.professionalism) * 100
            }
        
        # Compare role match
        if previous.role_match and current.role_match:
            comparisons['Role Match'] = {
                'old': previous.role_match.match_percentage,
                'new': current.role_match.match_percentage,
                'change': current.role_match.match_percentage - previous.role_match.match_percentage
            }
            
            # Skills comparison
            prev_skills = set(previous.role_match.matching_skills)
            curr_skills = set(current.role_match.matching_skills)
            new_skills = curr_skills - prev_skills
            lost_skills = prev_skills - curr_skills
            
            comparisons['Skills Matched'] = {
                'old': len(prev_skills),
                'new': len(curr_skills),
                'change': len(curr_skills) - len(prev_skills),
                'new_skills': list(new_skills),
                'lost_skills': list(lost_skills)
            }
        
        return comparisons
    
    def _generate_improvement_summary(
        self,
        score_change: float,
        improvements: Dict[str, Dict[str, float]]
    ) -> str:
        """Generate human-readable improvement summary"""
        
        if score_change > 10:
            summary = f"🎉 Excellent improvement! You've increased your score by {score_change:.1f} points. "
        elif score_change > 5:
            summary = f"👍 Great progress! You've improved by {score_change:.1f} points. "
        elif score_change > 0:
            summary = f"📈 Good work! You've made a {score_change:.1f} point improvement. "
        elif score_change == 0:
            summary = "➡️ Your score remained the same. "
        elif score_change > -5:
            summary = f"📉 Slight decline of {abs(score_change):.1f} points. "
        else:
            summary = f"⚠️ Score decreased by {abs(score_change):.1f} points. "
        
        # Add top improvements
        positive_changes = [(k, v['change']) for k, v in improvements.items() if v['change'] > 2]
        positive_changes.sort(key=lambda x: x[1], reverse=True)
        
        if positive_changes:
            top_improvements = [k for k, _ in positive_changes[:3]]
            summary += f"Key improvements: {', '.join(top_improvements)}. "
        
        # Add areas needing work
        negative_changes = [(k, v['change']) for k, v in improvements.items() if v['change'] < -2]
        if negative_changes:
            negative_changes.sort(key=lambda x: x[1])
            areas_to_work = [k for k, _ in negative_changes[:2]]
            summary += f"Areas to focus on: {', '.join(areas_to_work)}."
        
        return summary
    
    def _compare_recommendations(self, previous: str, current: str) -> str:
        """Compare recommendation changes"""
        if previous == current:
            return f"Recommendation unchanged: '{current}'"
        
        # Map recommendations to levels
        rec_levels = {
            "Highly Recommended": 4,
            "Recommended": 3,
            "Consider with Reservations": 2,
            "Not Recommended": 1
        }
        
        prev_level = rec_levels.get(previous, 0)
        curr_level = rec_levels.get(current, 0)
        
        if curr_level > prev_level:
            return f"⬆️ Improved from '{previous}' to '{current}'"
        elif curr_level < prev_level:
            return f"⬇️ Changed from '{previous}' to '{current}'"
        else:
            return f"Maintained '{current}' status"
    
    def get_submission_history(
        self,
        candidate_name: str,
        job_id: str,
        evaluations: List[CandidateEvaluation]
    ) -> List[CandidateEvaluation]:
        """Get all submissions for a candidate-job combination"""
        history = [
            e for e in evaluations
            if e.candidate_name.lower() == candidate_name.lower() and e.job_id == job_id
        ]
        
        # Sort by submission version
        history.sort(key=lambda x: x.submission_version)
        
        return history
    
    def calculate_overall_improvement_stats(
        self,
        history: List[CandidateEvaluation]
    ) -> Dict:
        """Calculate overall improvement statistics across all submissions"""
        if len(history) < 2:
            return {
                'total_submissions': len(history),
                'improvement_trend': 'insufficient_data'
            }
        
        scores = [e.overall_score for e in history]
        
        return {
            'total_submissions': len(history),
            'first_score': scores[0],
            'latest_score': scores[-1],
            'best_score': max(scores),
            'worst_score': min(scores),
            'total_improvement': scores[-1] - scores[0],
            'average_score': sum(scores) / len(scores),
            'improvement_trend': 'improving' if scores[-1] > scores[0] else 'declining' if scores[-1] < scores[0] else 'stable',
            'attempts_to_highly_recommended': self._attempts_to_threshold(scores, 80),
            'consistency_score': 100 - (max(scores) - min(scores))  # Lower variance = more consistent
        }
    
    def _attempts_to_threshold(self, scores: List[float], threshold: float) -> Optional[int]:
        """Calculate how many attempts it took to reach a threshold"""
        for i, score in enumerate(scores, 1):
            if score >= threshold:
                return i
        return None

