import logging
import os
from typing import List, Dict
from datetime import datetime
import httpx
from jinja2 import Environment, FileSystemLoader, select_autoescape
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
from ..models.schemas import (
    CandidateEvaluation,
    FeedbackReport,
    SoftSkillIndex
)
from ..config.settings import settings
from .soft_skill_analyzer import SoftSkillAnalyzer

logger = logging.getLogger(__name__)

class FeedbackGenerator:
    """Generate personalized feedback reports using LLM and templates"""
    
    def __init__(self):
        self.soft_skill_analyzer = SoftSkillAnalyzer()
        
        # Setup Jinja2 for HTML reports
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        os.makedirs(template_dir, exist_ok=True)
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    async def generate_feedback(
        self,
        evaluation: CandidateEvaluation,
        job_title: str
    ) -> FeedbackReport:
        """Generate comprehensive feedback report"""
        try:
            logger.info(f"Generating feedback for: {evaluation.candidate_name}")
            
            # Calculate component scores
            technical_score = self._compute_technical_score(evaluation)
            soft_skill_score = evaluation.soft_skill_index.overall_score * 100 if evaluation.soft_skill_index else 50
            role_match_score = evaluation.role_match.match_percentage if evaluation.role_match else 50
            
            # Generate AI feedback
            detailed_feedback = await self._generate_ai_feedback(evaluation, job_title)
            
            # Identify strengths and improvements
            strengths = self._identify_strengths(evaluation)
            improvements = self._identify_improvements(evaluation)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(evaluation)
            
            # Create visualizations
            chart_data = self._create_charts(evaluation, technical_score, soft_skill_score, role_match_score)
            
            # Generate HTML report
            report_path = await self._create_html_report(
                evaluation,
                job_title,
                technical_score,
                soft_skill_score,
                role_match_score,
                strengths,
                improvements,
                detailed_feedback,
                recommendations,
                chart_data
            )
            
            report = FeedbackReport(
                evaluation_id=evaluation.evaluation_id,
                candidate_name=evaluation.candidate_name,
                role_title=job_title,
                overall_score=evaluation.overall_score,
                technical_score=technical_score,
                soft_skill_score=soft_skill_score,
                role_match_score=role_match_score,
                strengths=strengths,
                areas_for_improvement=improvements,
                detailed_feedback=detailed_feedback,
                recommendations=recommendations,
                report_url=report_path
            )
            
            logger.info(f"Feedback report generated: {report_path}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating feedback: {str(e)}")
            raise
    
    def _compute_technical_score(self, evaluation: CandidateEvaluation) -> float:
        """Compute technical skill score"""
        scores = []
        
        if evaluation.resume_analysis:
            # Skills count (normalize to 0-100)
            skill_count = len(evaluation.resume_analysis.skills)
            skill_score = min(100, skill_count * 5)
            scores.append(skill_score)
        
        if evaluation.transcript_analysis:
            # Technical terms mentioned
            tech_term_count = len(evaluation.transcript_analysis.technical_terms)
            tech_score = min(100, tech_term_count * 10)
            scores.append(tech_score)
        
        if evaluation.role_match:
            # Role match percentage
            scores.append(evaluation.role_match.match_percentage)
        
        return sum(scores) / len(scores) if scores else 50.0
    
    async def _generate_ai_feedback(
        self,
        evaluation: CandidateEvaluation,
        job_title: str
    ) -> Dict[str, str]:
        """Generate detailed feedback using LLM"""
        feedback = {}
        
        # Try to use Llama 3.2 API
        if settings.LLAMA_API_URL:
            llm_feedback = await self._generate_with_llama(evaluation, job_title)
            if llm_feedback:
                return llm_feedback
        
        # Fallback to template-based feedback
        feedback['summary'] = self._generate_summary_feedback(evaluation)
        feedback['technical'] = self._generate_technical_feedback(evaluation)
        feedback['soft_skills'] = self._generate_soft_skills_feedback(evaluation)
        feedback['role_fit'] = self._generate_role_fit_feedback(evaluation)
        
        return feedback
    
    async def _generate_with_llama(
        self,
        evaluation: CandidateEvaluation,
        job_title: str
    ) -> Dict[str, str]:
        """Generate feedback using Llama 3.2"""
        try:
            prompt = self._create_llama_prompt(evaluation, job_title)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    settings.LLAMA_API_URL,
                    json={
                        "model": "llama3.2",
                        "prompt": prompt,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    feedback_text = result.get('response', '')
                    return self._parse_llm_feedback(feedback_text)
            
            return {}
            
        except Exception as e:
            logger.warning(f"Could not generate with Llama: {e}")
            return {}
    
    def _create_llama_prompt(self, evaluation: CandidateEvaluation, job_title: str) -> str:
        """Create prompt for LLM"""
        return f"""
        As a professional recruiter, provide detailed feedback for a candidate applying for a {job_title} position.
        
        Candidate: {evaluation.candidate_name}
        Overall Score: {evaluation.overall_score}/100
        
        Technical Skills: {evaluation.resume_analysis.skills if evaluation.resume_analysis else 'N/A'}
        Communication Quality: {evaluation.transcript_analysis.clarity_score if evaluation.transcript_analysis else 'N/A'}
        Confidence Level: {evaluation.soft_skill_index.confidence if evaluation.soft_skill_index else 'N/A'}
        Role Match: {evaluation.role_match.match_percentage if evaluation.role_match else 'N/A'}%
        
        Provide feedback in the following categories:
        
        1. SUMMARY: Overall assessment (2-3 sentences)
        2. TECHNICAL: Technical skills evaluation
        3. SOFT_SKILLS: Communication and presentation skills
        4. ROLE_FIT: Fit for the role and recommendations
        
        Format each section starting with the category name in caps followed by a colon.
        """
    
    def _parse_llm_feedback(self, text: str) -> Dict[str, str]:
        """Parse LLM response into structured feedback"""
        sections = {
            'summary': '',
            'technical': '',
            'soft_skills': '',
            'role_fit': ''
        }
        
        current_section = None
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('SUMMARY:'):
                current_section = 'summary'
                line = line[8:].strip()
            elif line.startswith('TECHNICAL:'):
                current_section = 'technical'
                line = line[10:].strip()
            elif line.startswith('SOFT_SKILLS:'):
                current_section = 'soft_skills'
                line = line[12:].strip()
            elif line.startswith('ROLE_FIT:'):
                current_section = 'role_fit'
                line = line[9:].strip()
            
            if current_section and line:
                sections[current_section] += line + ' '
        
        return {k: v.strip() for k, v in sections.items()}
    
    def _generate_summary_feedback(self, evaluation: CandidateEvaluation) -> str:
        """Generate summary feedback"""
        score = evaluation.overall_score
        
        if score >= 80:
            return f"{evaluation.candidate_name} is an excellent candidate with strong technical skills and professional presentation. Highly recommended for the role."
        elif score >= 60:
            return f"{evaluation.candidate_name} is a good candidate with solid qualifications. Some areas for improvement identified, but overall a strong fit."
        else:
            return f"{evaluation.candidate_name} shows potential but needs development in several areas. Consider for entry-level positions or with additional training."
    
    def _generate_technical_feedback(self, evaluation: CandidateEvaluation) -> str:
        """Generate technical feedback"""
        if not evaluation.resume_analysis:
            return "Technical skills assessment unavailable."
        
        skill_count = len(evaluation.resume_analysis.skills)
        if skill_count > 10:
            return f"Strong technical profile with {skill_count} identified skills. Demonstrates broad technical knowledge."
        elif skill_count > 5:
            return f"Good technical foundation with {skill_count} relevant skills. Could expand skill set in emerging technologies."
        else:
            return f"Limited technical skills identified. Recommend additional training and certifications."
    
    def _generate_soft_skills_feedback(self, evaluation: CandidateEvaluation) -> str:
        """Generate soft skills feedback with transparency notes"""
        if not evaluation.soft_skill_index:
            return "Soft skills assessment unavailable."
        
        feedback_dict = self.soft_skill_analyzer.get_soft_skill_feedback(evaluation.soft_skill_index)
        feedback_text = " ".join(feedback_dict.values())
        
        # Add contextual notes if video analysis was performed
        if evaluation.video_analysis and evaluation.video_analysis.measurement_notes:
            notes = evaluation.video_analysis.measurement_notes
            feedback_text += f"\n\nMeasurement Context: {'; '.join(notes)}"
        
        # Add accessibility mode note if used
        if evaluation.accessibility_mode_used:
            feedback_text += "\n\nNote: Visual analysis was disabled at candidate's request (accessibility mode). Evaluation focused on communication skills and technical qualifications."
        
        return feedback_text
    
    def _generate_role_fit_feedback(self, evaluation: CandidateEvaluation) -> str:
        """Generate role fit feedback"""
        if not evaluation.role_match:
            return "Role matching analysis unavailable."
        
        match_pct = evaluation.role_match.match_percentage
        if match_pct >= 80:
            return f"Excellent fit for the role ({match_pct:.0f}% match). Strong alignment with job requirements."
        elif match_pct >= 60:
            return f"Good fit for the role ({match_pct:.0f}% match). Some skill gaps can be addressed through training."
        else:
            return f"Moderate fit for the role ({match_pct:.0f}% match). Consider alternative positions or additional preparation."
    
    def _identify_strengths(self, evaluation: CandidateEvaluation) -> List[str]:
        """Identify candidate strengths"""
        strengths = []
        
        if evaluation.role_match and evaluation.role_match.strengths:
            strengths.extend(evaluation.role_match.strengths)
        
        if evaluation.soft_skill_index:
            if evaluation.soft_skill_index.communication >= 0.8:
                strengths.append("Excellent communication skills")
            if evaluation.soft_skill_index.confidence >= 0.8:
                strengths.append("Strong confidence and presentation")
        
        if evaluation.transcript_analysis:
            if len(evaluation.transcript_analysis.technical_terms) > 5:
                strengths.append("Demonstrates technical vocabulary and knowledge")
        
        return strengths[:5]  # Top 5 strengths
    
    def _identify_improvements(self, evaluation: CandidateEvaluation) -> List[str]:
        """Identify areas for improvement"""
        improvements = []
        
        if evaluation.role_match and evaluation.role_match.gaps:
            improvements.extend(evaluation.role_match.gaps)
        
        if evaluation.soft_skill_index:
            if evaluation.soft_skill_index.communication < 0.6:
                improvements.append("Improve speech clarity and articulation")
            if evaluation.soft_skill_index.confidence < 0.6:
                improvements.append("Build confidence through practice and preparation")
            if evaluation.soft_skill_index.engagement < 0.6:
                improvements.append("Increase energy and expressiveness")
        
        if evaluation.video_analysis:
            if evaluation.video_analysis.eye_contact_score < 0.6:
                improvements.append("Maintain better eye contact with camera")
            if evaluation.video_analysis.posture_score < 0.6:
                improvements.append("Improve posture and body language")
        
        return improvements[:5]  # Top 5 improvements
    
    async def _generate_recommendations(self, evaluation: CandidateEvaluation) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if evaluation.role_match and evaluation.role_match.missing_skills:
            missing = evaluation.role_match.missing_skills[:3]
            recommendations.append(f"Develop skills in: {', '.join(missing)}")
        
        if evaluation.soft_skill_index and evaluation.soft_skill_index.overall_score < 0.7:
            recommendations.append("Practice video presentations to improve delivery")
        
        if evaluation.transcript_analysis and evaluation.transcript_analysis.word_count < 100:
            recommendations.append("Provide more detailed responses in interviews")
        
        recommendations.append("Review job description and align experience with requirements")
        recommendations.append("Prepare specific examples demonstrating key skills")
        
        return recommendations
    
    def _create_charts(
        self,
        evaluation: CandidateEvaluation,
        technical_score: float,
        soft_skill_score: float,
        role_match_score: float
    ) -> Dict[str, str]:
        """Create visualization charts as base64 encoded images"""
        charts = {}
        
        # Score breakdown chart
        fig, ax = plt.subplots(figsize=(8, 5))
        categories = ['Technical\nSkills', 'Soft\nSkills', 'Role\nMatch', 'Overall']
        scores = [technical_score, soft_skill_score, role_match_score, evaluation.overall_score]
        colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']
        
        bars = ax.bar(categories, scores, color=colors, alpha=0.7)
        ax.set_ylim(0, 100)
        ax.set_ylabel('Score')
        ax.set_title('Candidate Evaluation Scores')
        ax.axhline(y=70, color='r', linestyle='--', alpha=0.3, label='Target')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.0f}',
                   ha='center', va='bottom')
        
        charts['scores'] = self._fig_to_base64(fig)
        plt.close(fig)
        
        # Soft skills radar chart
        if evaluation.soft_skill_index:
            charts['soft_skills'] = self._create_radar_chart(evaluation.soft_skill_index)
        
        return charts
    
    def _create_radar_chart(self, soft_skills: SoftSkillIndex) -> str:
        """Create radar chart for soft skills"""
        categories = ['Communication', 'Confidence', 'Engagement', 'Professionalism']
        values = [
            soft_skills.communication * 100,
            soft_skills.confidence * 100,
            soft_skills.engagement * 100,
            soft_skills.professionalism * 100
        ]
        
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, projection='polar')
        
        angles = [n / float(len(categories)) * 2 * 3.14159 for n in range(len(categories))]
        values += values[:1]
        angles += angles[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, color='#3b82f6')
        ax.fill(angles, values, alpha=0.25, color='#3b82f6')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 100)
        ax.set_title('Soft Skills Profile', pad=20)
        
        return self._fig_to_base64(fig)
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        return f"data:image/png;base64,{img_base64}"
    
    async def _create_html_report(
        self,
        evaluation: CandidateEvaluation,
        job_title: str,
        technical_score: float,
        soft_skill_score: float,
        role_match_score: float,
        strengths: List[str],
        improvements: List[str],
        detailed_feedback: Dict[str, str],
        recommendations: List[str],
        chart_data: Dict[str, str]
    ) -> str:
        """Create HTML report file"""
        # Create simple HTML template inline since template file doesn't exist yet
        html_content = self._generate_html_template(
            evaluation,
            job_title,
            technical_score,
            soft_skill_score,
            role_match_score,
            strengths,
            improvements,
            detailed_feedback,
            recommendations,
            chart_data
        )
        
        # Save report
        report_filename = f"report_{evaluation.evaluation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        report_path = os.path.join(settings.UPLOAD_DIR, 'reports', report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_path
    
    def _format_confidence_interval(self, score: float, conf_interval: Dict[str, float]) -> str:
        """Format score with confidence interval"""
        if conf_interval and conf_interval.get('lower') and conf_interval.get('upper'):
            return f"{score*100:.1f}% (range: {conf_interval['lower']*100:.1f}%-{conf_interval['upper']*100:.1f}%)"
        return f"{score*100:.1f}%"
    
    def _generate_html_template(
        self,
        evaluation: CandidateEvaluation,
        job_title: str,
        technical_score: float,
        soft_skill_score: float,
        role_match_score: float,
        strengths: List[str],
        improvements: List[str],
        detailed_feedback: Dict[str, str],
        recommendations: List[str],
        chart_data: Dict[str, str]
    ) -> str:
        """Generate HTML report content with transparency and confidence intervals"""
        
        # Format scores with confidence intervals if available
        eye_contact_display = ""
        posture_display = ""
        
        if evaluation.video_analysis:
            eye_contact_display = self._format_confidence_interval(
                evaluation.video_analysis.eye_contact_score,
                evaluation.video_analysis.eye_contact_confidence or {}
            )
            posture_display = self._format_confidence_interval(
                evaluation.video_analysis.posture_score,
                evaluation.video_analysis.posture_confidence or {}
            )
        
        # Add accessibility badge if used
        accessibility_badge = ""
        if evaluation.accessibility_mode_used:
            accessibility_badge = '<span class="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">♿ Accessibility Mode</span>'
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>VisumeAI Evaluation Report - {evaluation.candidate_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #3b82f6; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }}
        h2 {{ color: #1e40af; margin-top: 30px; }}
        .score-box {{ background: #f0f9ff; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0; }}
        .chart {{ text-align: center; margin: 30px 0; }}
        .chart img {{ max-width: 100%; height: auto; }}
        .section {{ margin: 30px 0; }}
        .list-item {{ padding: 8px 0; border-bottom: 1px solid #e5e7eb; }}
        .strength {{ color: #059669; }}
        .improvement {{ color: #dc2626; }}
        .footer {{ text-align: center; color: #6b7280; margin-top: 50px; padding-top: 20px; border-top: 1px solid #e5e7eb; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>VisumeAI Evaluation Report</h1>
        
        <div class="score-box">
            <h2>Candidate Information</h2>
            <p><strong>Name:</strong> {evaluation.candidate_name} {accessibility_badge}</p>
            <p><strong>Position:</strong> {job_title}</p>
            <p><strong>Evaluation Date:</strong> {evaluation.created_at.strftime('%B %d, %Y')}</p>
            <p><strong>Overall Score:</strong> {evaluation.overall_score:.1f}/100</p>
        </div>
        
        <div class="section">
            <h2>Score Breakdown</h2>
            <p><strong>Technical Skills:</strong> {technical_score:.1f}/100</p>
            <p><strong>Soft Skills:</strong> {soft_skill_score:.1f}/100</p>
            <p><strong>Role Match:</strong> {role_match_score:.1f}/100</p>
            
            {f'''
            <div class="mt-4 p-4 bg-gray-50 rounded">
                <h3 class="font-semibold mb-2">📊 Detailed Metrics (with confidence intervals)</h3>
                <p><strong>Eye Contact:</strong> {eye_contact_display}</p>
                <p><strong>Posture:</strong> {posture_display}</p>
                <p><strong>Engagement:</strong> {evaluation.video_analysis.engagement_score*100:.1f}%</p>
                <p class="text-xs text-gray-600 mt-2">
                    <em>Confidence intervals show measurement uncertainty. Wider ranges indicate more variability in the video.</em>
                </p>
            </div>
            ''' if evaluation.video_analysis and not evaluation.accessibility_mode_used else ''}
            
            {f'''
            <div class="mt-4 p-4 bg-blue-50 rounded border border-blue-200">
                <p class="text-sm">
                    <strong>ℹ️ Accessibility Mode:</strong> Visual analysis was not performed at candidate's request. 
                    Evaluation focused on verbal communication and technical qualifications.
                </p>
            </div>
            ''' if evaluation.accessibility_mode_used else ''}
        </div>
        
        {f'<div class="chart"><img src="{chart_data["scores"]}" /></div>' if 'scores' in chart_data else ''}
        
        <div class="section">
            <h2>Summary</h2>
            <p>{detailed_feedback.get('summary', 'No summary available.')}</p>
        </div>
        
        <div class="section">
            <h2>Strengths</h2>
            <ul>
                {''.join(f'<li class="list-item strength">✓ {s}</li>' for s in strengths)}
            </ul>
        </div>
        
        <div class="section">
            <h2>Areas for Improvement</h2>
            <ul>
                {''.join(f'<li class="list-item improvement">⚠ {i}</li>' for i in improvements)}
            </ul>
        </div>
        
        <div class="section">
            <h2>Technical Skills Assessment</h2>
            <p>{detailed_feedback.get('technical', 'Assessment pending.')}</p>
        </div>
        
        <div class="section">
            <h2>Soft Skills Assessment</h2>
            <p>{detailed_feedback.get('soft_skills', 'Assessment pending.')}</p>
            {f'<div class="chart"><img src="{chart_data["soft_skills"]}" /></div>' if 'soft_skills' in chart_data else ''}
        </div>
        
        <div class="section">
            <h2>Role Fit Analysis</h2>
            <p>{detailed_feedback.get('role_fit', 'Analysis pending.')}</p>
        </div>
        
        <div class="section">
            <h2>Recommendations</h2>
            <ul>
                {''.join(f'<li class="list-item">{r}</li>' for r in recommendations)}
            </ul>
        </div>
        
        <div class="footer">
            <p>Generated by VisumeAI - AI-Powered Video Resume Evaluator</p>
            <p>Report ID: {evaluation.evaluation_id}</p>
        </div>
    </div>
</body>
</html>
        """
