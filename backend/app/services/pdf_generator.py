import os
import logging
from datetime import datetime
from typing import Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64

from ..models.schemas import CandidateEvaluation
from ..config.settings import settings

logger = logging.getLogger(__name__)

class PDFGenerator:
    """Generate professional PDF reports for candidate evaluations"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#7e22ce'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#6b21a8'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#374151'),
            spaceAfter=6,
            alignment=TA_LEFT
        ))
        
        self.styles.add(ParagraphStyle(
            name='ScoreText',
            parent=self.styles['Normal'],
            fontSize=36,
            textColor=colors.HexColor('#7e22ce'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
    
    def generate_evaluation_pdf(
        self,
        evaluation: CandidateEvaluation,
        job_title: str,
        output_path: Optional[str] = None
    ) -> str:
        """Generate PDF report for candidate evaluation"""
        try:
            if output_path is None:
                pdf_filename = f"evaluation_{evaluation.evaluation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                output_path = os.path.join(settings.UPLOAD_DIR, 'reports', pdf_filename)
            
            logger.info(f"Generating PDF report: {output_path}")
            
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
            )
            
            # Build content
            story = []
            
            # Header
            story.append(Paragraph("VisumeAI", self.styles['CustomTitle']))
            story.append(Paragraph("Candidate Evaluation Report", self.styles['CustomHeading']))
            story.append(Spacer(1, 0.2 * inch))
            
            # Candidate Information
            story.append(self._create_candidate_info_section(evaluation, job_title))
            story.append(Spacer(1, 0.3 * inch))
            
            # Overall Score - Big and Bold
            story.append(self._create_overall_score_section(evaluation))
            story.append(Spacer(1, 0.3 * inch))
            
            # Score Breakdown Table
            story.append(Paragraph("Score Breakdown", self.styles['CustomHeading']))
            story.append(self._create_score_breakdown_table(evaluation))
            story.append(Spacer(1, 0.3 * inch))
            
            # Detailed Metrics
            if evaluation.video_analysis:
                story.append(Paragraph("Video Analysis Metrics", self.styles['CustomHeading']))
                story.append(self._create_video_metrics_table(evaluation.video_analysis))
                story.append(Spacer(1, 0.3 * inch))
            
            if evaluation.soft_skill_index:
                story.append(Paragraph("Soft Skills Assessment", self.styles['CustomHeading']))
                story.append(self._create_soft_skills_table(evaluation.soft_skill_index))
                story.append(Spacer(1, 0.3 * inch))
            
            if evaluation.role_match:
                story.append(Paragraph("Role Match Analysis", self.styles['CustomHeading']))
                story.append(self._create_role_match_section(evaluation.role_match))
                story.append(Spacer(1, 0.3 * inch))
            
            # Page break before summary
            story.append(PageBreak())
            
            # Strengths and Areas for Improvement
            story.append(Paragraph("Evaluation Summary", self.styles['CustomHeading']))
            story.append(self._create_summary_section(evaluation))
            story.append(Spacer(1, 0.3 * inch))
            
            # NEW: Detailed Feedback Report
            story.append(Paragraph("Detailed Feedback Report", self.styles['CustomHeading']))
            story.append(self._create_detailed_feedback_section(evaluation))
            story.append(Spacer(1, 0.3 * inch))
            
            # Recommendations
            story.append(Paragraph("Actionable Recommendations", self.styles['CustomHeading']))
            story.append(self._create_recommendations_section(evaluation))
            
            # Footer
            story.append(Spacer(1, 0.5 * inch))
            story.append(self._create_footer(evaluation))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF report generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise
    
    def _create_candidate_info_section(self, evaluation: CandidateEvaluation, job_title: str):
        """Create candidate information section"""
        data = [
            ['Candidate Name:', evaluation.candidate_name],
            ['Position:', job_title],
            ['Evaluation Date:', evaluation.created_at.strftime('%B %d, %Y at %I:%M %p')],
            ['Evaluation ID:', evaluation.evaluation_id[:16] + '...'],
        ]
        
        if evaluation.submission_version > 1:
            data.append(['Submission Version:', f"#{evaluation.submission_version}"])
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b21a8')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#374151')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        return table
    
    def _create_overall_score_section(self, evaluation: CandidateEvaluation):
        """Create overall score display"""
        score_data = [
            [Paragraph(f"<font size=48 color='#7e22ce'><b>{evaluation.overall_score:.1f}</b></font><font size=24 color='#9ca3af'>/100</font>", self.styles['CustomBody'])],
            [Paragraph(f"<b>{evaluation.recommendation}</b>", self.styles['CustomHeading'])]
        ]
        
        table = Table(score_data, colWidths=[6.5*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3e8ff')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#9333ea')),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        return table
    
    def _create_score_breakdown_table(self, evaluation: CandidateEvaluation):
        """Create score breakdown table"""
        technical_score = evaluation.role_match.match_percentage if evaluation.role_match else 0
        soft_skill_score = evaluation.soft_skill_index.overall_score * 100 if evaluation.soft_skill_index else 0
        video_score = evaluation.video_analysis.confidence_score * 100 if evaluation.video_analysis else 0
        
        data = [
            ['Category', 'Score', 'Weight', 'Contribution'],
            ['Technical Skills (Role Match)', f"{technical_score:.1f}/100", '40%', f"{technical_score * 0.4:.1f}"],
            ['Soft Skills', f"{soft_skill_score:.1f}/100", '30%', f"{soft_skill_score * 0.3:.1f}"],
            ['Video Confidence', f"{video_score:.1f}/100", '30%', f"{video_score * 0.3:.1f}"],
            ['', '', 'Total:', f"{evaluation.overall_score:.1f}"],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7e22ce')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternating row colors
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#faf5ff')),
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#faf5ff')),
            
            # Total row
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e9d5ff')),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        return table
    
    def _create_video_metrics_table(self, video_analysis):
        """Create video analysis metrics table"""
        data = [
            ['Metric', 'Score', 'Confidence Interval'],
            ['Eye Contact', f"{video_analysis.eye_contact_score * 100:.1f}%", 
             self._format_confidence_interval(video_analysis.eye_contact_confidence)],
            ['Posture', f"{video_analysis.posture_score * 100:.1f}%",
             self._format_confidence_interval(video_analysis.posture_confidence)],
            ['Expressiveness', f"{video_analysis.expressiveness_score * 100:.1f}%", '-'],
            ['Engagement', f"{video_analysis.engagement_score * 100:.1f}%", '-'],
        ]
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#06b6d4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        return table
    
    def _create_soft_skills_table(self, soft_skill_index):
        """Create soft skills assessment table"""
        data = [
            ['Soft Skill', 'Score', 'Level'],
            ['Communication', f"{soft_skill_index.communication * 100:.1f}%", 
             self._get_level(soft_skill_index.communication)],
            ['Confidence', f"{soft_skill_index.confidence * 100:.1f}%",
             self._get_level(soft_skill_index.confidence)],
            ['Engagement', f"{soft_skill_index.engagement * 100:.1f}%",
             self._get_level(soft_skill_index.engagement)],
            ['Professionalism', f"{soft_skill_index.professionalism * 100:.1f}%",
             self._get_level(soft_skill_index.professionalism)],
        ]
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#22c55e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        return table
    
    def _create_role_match_section(self, role_match):
        """Create role match details section"""
        elements = []
        
        # Match percentage
        match_data = [
            ['Overall Match', f"{role_match.match_percentage:.1f}%"],
            ['Experience Match', '✓ Yes' if role_match.experience_match else '✗ No'],
            ['Semantic Similarity', f"{role_match.semantic_similarity * 100:.1f}%"],
        ]
        
        match_table = Table(match_data, colWidths=[2.5*inch, 2*inch])
        match_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b21a8')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#faf5ff')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#c084fc')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(match_table)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Matching Skills
        if role_match.matching_skills:
            elements.append(Paragraph(f"<b>✓ Matching Skills ({len(role_match.matching_skills)}):</b>", self.styles['CustomBody']))
            skills_text = ", ".join(role_match.matching_skills[:15])
            if len(role_match.matching_skills) > 15:
                skills_text += f", and {len(role_match.matching_skills) - 15} more"
            elements.append(Paragraph(skills_text, self.styles['CustomBody']))
            elements.append(Spacer(1, 0.1 * inch))
        
        # Missing Skills
        if role_match.missing_skills:
            elements.append(Paragraph(f"<b>⚠ Missing Skills ({len(role_match.missing_skills)}):</b>", self.styles['CustomBody']))
            missing_text = ", ".join(role_match.missing_skills[:10])
            if len(role_match.missing_skills) > 10:
                missing_text += f", and {len(role_match.missing_skills) - 10} more"
            elements.append(Paragraph(missing_text, self.styles['CustomBody']))
        
        # Create container table
        container = Table([[e] for e in elements], colWidths=[6.5*inch])
        container.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        return container
    
    def _create_summary_section(self, evaluation: CandidateEvaluation):
        """Create summary with strengths and improvements"""
        elements = []
        
        # Strengths
        strengths = []
        if evaluation.role_match and evaluation.role_match.strengths:
            strengths.extend(evaluation.role_match.strengths)
        
        if evaluation.soft_skill_index:
            if evaluation.soft_skill_index.communication >= 0.8:
                strengths.append("Excellent communication skills")
            if evaluation.soft_skill_index.confidence >= 0.8:
                strengths.append("Strong confidence and presentation")
        
        if strengths:
            elements.append(Paragraph("<b>Key Strengths:</b>", self.styles['CustomBody']))
            for strength in strengths[:5]:
                elements.append(Paragraph(f"• {strength}", self.styles['CustomBody']))
            elements.append(Spacer(1, 0.2 * inch))
        
        # Areas for Improvement
        improvements = []
        if evaluation.role_match and evaluation.role_match.gaps:
            improvements.extend(evaluation.role_match.gaps)
        
        if evaluation.soft_skill_index:
            if evaluation.soft_skill_index.communication < 0.6:
                improvements.append("Improve speech clarity and articulation")
            if evaluation.soft_skill_index.engagement < 0.6:
                improvements.append("Increase energy and expressiveness")
        
        if improvements:
            elements.append(Paragraph("<b>Areas for Improvement:</b>", self.styles['CustomBody']))
            for improvement in improvements[:5]:
                elements.append(Paragraph(f"• {improvement}", self.styles['CustomBody']))
        
        # Create container
        container = Table([[e] for e in elements], colWidths=[6.5*inch])
        container.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        return container
    
    def _create_footer(self, evaluation: CandidateEvaluation):
        """Create footer with disclaimers"""
        footer_text = """
        <para alignment='center' fontSize='9' textColor='#6b7280'>
        <b>VisumeAI - AI-Powered Video Resume Analysis</b><br/>
        This report was generated using AI and should be used as a supplementary tool in the hiring process.<br/>
        Final hiring decisions should involve human judgment and consider multiple factors.<br/>
        Generated on """ + datetime.now().strftime('%B %d, %Y') + """<br/>
        Report ID: """ + evaluation.evaluation_id + """
        </para>
        """
        
        return Paragraph(footer_text, self.styles['Normal'])
    
    def _format_confidence_interval(self, confidence: Optional[dict]) -> str:
        """Format confidence interval for display"""
        if not confidence or not confidence.get('lower') or not confidence.get('upper'):
            return '-'
        
        lower = confidence['lower'] * 100
        upper = confidence['upper'] * 100
        return f"({lower:.1f}% - {upper:.1f}%)"
    
    def _get_level(self, score: float) -> str:
        """Convert score to level description"""
        if score >= 0.8:
            return "⭐ Excellent"
        elif score >= 0.6:
            return "✓ Good"
        elif score >= 0.4:
            return "~ Average"
        else:
            return "↓ Needs Work"
    
    def _create_detailed_feedback_section(self, evaluation: CandidateEvaluation):
        """Create comprehensive feedback report section"""
        elements = []
        
        # Overall Assessment
        overall_feedback = self._generate_overall_feedback(evaluation)
        elements.append(Paragraph("<b>Overall Assessment:</b>", self.styles['CustomBody']))
        elements.append(Paragraph(overall_feedback, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.15 * inch))
        
        # Technical Skills Feedback
        if evaluation.resume_analysis or evaluation.role_match:
            technical_feedback = self._generate_technical_feedback(evaluation)
            elements.append(Paragraph("<b>Technical Skills:</b>", self.styles['CustomBody']))
            elements.append(Paragraph(technical_feedback, self.styles['CustomBody']))
            elements.append(Spacer(1, 0.15 * inch))
        
        # Communication & Soft Skills Feedback
        if evaluation.soft_skill_index or evaluation.transcript_analysis:
            soft_skills_feedback = self._generate_soft_skills_feedback(evaluation)
            elements.append(Paragraph("<b>Communication & Soft Skills:</b>", self.styles['CustomBody']))
            elements.append(Paragraph(soft_skills_feedback, self.styles['CustomBody']))
            elements.append(Spacer(1, 0.15 * inch))
        
        # Presentation & Video Feedback
        if evaluation.video_analysis:
            video_feedback = self._generate_video_feedback(evaluation)
            elements.append(Paragraph("<b>Presentation & Video Performance:</b>", self.styles['CustomBody']))
            elements.append(Paragraph(video_feedback, self.styles['CustomBody']))
            elements.append(Spacer(1, 0.15 * inch))
        
        # Role Fit Feedback
        if evaluation.role_match:
            role_fit_feedback = self._generate_role_fit_feedback(evaluation)
            elements.append(Paragraph("<b>Role Fit Analysis:</b>", self.styles['CustomBody']))
            elements.append(Paragraph(role_fit_feedback, self.styles['CustomBody']))
        
        # Create container
        container = Table([[e] for e in elements], colWidths=[6.5*inch])
        container.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#faf5ff')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#c084fc')),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        return container
    
    def _generate_overall_feedback(self, evaluation: CandidateEvaluation) -> str:
        """Generate overall assessment feedback"""
        score = evaluation.overall_score
        name = evaluation.candidate_name
        
        if score >= 80:
            return f"{name} is an excellent candidate with strong qualifications and professional presentation. " \
                   f"They demonstrate both technical competence and soft skills essential for success. " \
                   f"Highly recommended for advancing to the next stage of the hiring process."
        elif score >= 60:
            return f"{name} is a good candidate with solid qualifications and positive attributes. " \
                   f"They show competency in key areas with some opportunities for growth. " \
                   f"Recommended for further consideration and potentially moving forward in the process."
        else:
            return f"{name} shows potential but would benefit from additional development in several key areas. " \
                   f"Consider for entry-level positions, training programs, or with additional coaching. " \
                   f"May be a good fit with proper support and development."
    
    def _generate_technical_feedback(self, evaluation: CandidateEvaluation) -> str:
        """Generate technical skills feedback"""
        feedback_parts = []
        
        if evaluation.resume_analysis:
            skill_count = len(evaluation.resume_analysis.skills)
            if skill_count > 10:
                feedback_parts.append(f"Demonstrates a strong technical profile with {skill_count} identified skills across multiple domains.")
            elif skill_count > 5:
                feedback_parts.append(f"Shows good technical foundation with {skill_count} relevant skills.")
            else:
                feedback_parts.append(f"Has {skill_count} core technical skills. Consider expanding expertise in additional technologies.")
            
            if evaluation.resume_analysis.experience_years:
                feedback_parts.append(f"Brings {evaluation.resume_analysis.experience_years:.0f} years of professional experience.")
            
            if evaluation.resume_analysis.certifications:
                cert_count = len(evaluation.resume_analysis.certifications)
                feedback_parts.append(f"Holds {cert_count} professional certification(s), demonstrating commitment to continuous learning.")
        
        if evaluation.role_match:
            match_pct = evaluation.role_match.match_percentage
            if match_pct >= 80:
                feedback_parts.append(f"Excellent alignment with job requirements ({match_pct:.0f}% match).")
            elif match_pct >= 60:
                feedback_parts.append(f"Good fit for the role ({match_pct:.0f}% match) with some skill gaps that can be addressed.")
            else:
                feedback_parts.append(f"Moderate alignment with job requirements ({match_pct:.0f}% match). Additional training may be beneficial.")
        
        return " ".join(feedback_parts) if feedback_parts else "Technical assessment data limited."
    
    def _generate_soft_skills_feedback(self, evaluation: CandidateEvaluation) -> str:
        """Generate soft skills and communication feedback"""
        feedback_parts = []
        
        if evaluation.soft_skill_index:
            ss = evaluation.soft_skill_index
            
            # Communication
            if ss.communication >= 0.8:
                feedback_parts.append("Demonstrates excellent communication skills with clear articulation and well-structured responses.")
            elif ss.communication >= 0.6:
                feedback_parts.append("Shows good communication ability with some room for improvement in clarity or structure.")
            else:
                feedback_parts.append("Communication skills need development. Focus on speech clarity, vocabulary, and logical flow.")
            
            # Confidence
            if ss.confidence >= 0.8:
                feedback_parts.append("Presents with strong confidence and professional demeanor.")
            elif ss.confidence >= 0.6:
                feedback_parts.append("Shows moderate confidence with occasional uncertainty.")
            else:
                feedback_parts.append("Building confidence through practice and preparation would be beneficial.")
            
            # Engagement
            if ss.engagement >= 0.8:
                feedback_parts.append("Highly engaging and energetic presentation style that captures attention.")
            elif ss.engagement >= 0.6:
                feedback_parts.append("Good engagement level with opportunities to increase expressiveness.")
            else:
                feedback_parts.append("Consider increasing energy and expressiveness to better engage the audience.")
        
        if evaluation.transcript_analysis:
            word_count = evaluation.transcript_analysis.word_count
            if word_count > 150:
                feedback_parts.append(f"Provided detailed responses ({word_count} words), showing thorough preparation.")
            elif word_count < 80:
                feedback_parts.append("Responses were brief. Consider providing more detailed explanations in interviews.")
        
        return " ".join(feedback_parts) if feedback_parts else "Soft skills assessment data limited."
    
    def _generate_video_feedback(self, evaluation: CandidateEvaluation) -> str:
        """Generate video presentation feedback"""
        video = evaluation.video_analysis
        feedback_parts = []
        
        # Eye contact
        if video.eye_contact_score >= 0.75:
            feedback_parts.append("Maintains good eye contact, demonstrating engagement and connection.")
        elif video.eye_contact_score >= 0.6:
            feedback_parts.append("Eye contact is adequate but could be more consistent.")
        else:
            feedback_parts.append("Work on maintaining better eye contact with the camera to project confidence.")
        
        # Posture
        if video.posture_score >= 0.75:
            feedback_parts.append("Excellent posture and body language throughout the presentation.")
        elif video.posture_score >= 0.6:
            feedback_parts.append("Generally good posture with minor adjustments needed.")
        else:
            feedback_parts.append("Focus on improving posture and body positioning for a more professional appearance.")
        
        # Engagement
        if video.engagement_score >= 0.75:
            feedback_parts.append("Highly engaging presence with natural expressiveness.")
        elif video.engagement_score >= 0.6:
            feedback_parts.append("Good engagement with room for more expressiveness.")
        else:
            feedback_parts.append("Increase energy and use more facial expressions to enhance engagement.")
        
        # Duration context
        duration = video.duration_seconds
        if duration > 120:
            feedback_parts.append(f"Provided comprehensive response ({duration:.0f} seconds), showing thorough preparation.")
        elif duration < 30:
            feedback_parts.append("Consider providing longer, more detailed video responses in future applications.")
        
        return " ".join(feedback_parts)
    
    def _generate_role_fit_feedback(self, evaluation: CandidateEvaluation) -> str:
        """Generate role fit assessment"""
        role_match = evaluation.role_match
        feedback_parts = []
        
        match_pct = role_match.match_percentage
        
        if match_pct >= 80:
            feedback_parts.append(f"Excellent fit for the position with {match_pct:.0f}% alignment to job requirements.")
            feedback_parts.append("Possesses most critical skills and demonstrates strong potential for success in this role.")
        elif match_pct >= 60:
            feedback_parts.append(f"Good fit for the position with {match_pct:.0f}% alignment.")
            feedback_parts.append("Core competencies are present, with some skill gaps that can be addressed through training or on-the-job learning.")
        else:
            feedback_parts.append(f"Moderate alignment with the position ({match_pct:.0f}% match).")
            feedback_parts.append("Significant skill gaps exist. Consider alternative positions that better match current skill set, or provide substantial training.")
        
        # Highlight strengths
        if role_match.strengths:
            strengths_text = ". ".join(role_match.strengths[:2])
            feedback_parts.append(f"Key strengths: {strengths_text}.")
        
        return " ".join(feedback_parts)
    
    def _create_recommendations_section(self, evaluation: CandidateEvaluation):
        """Create actionable recommendations section"""
        elements = []
        recommendations = []
        
        # Skill-based recommendations
        if evaluation.role_match and evaluation.role_match.missing_skills:
            missing = evaluation.role_match.missing_skills[:5]
            if missing:
                recommendations.append(f"<b>Skill Development:</b> Focus on acquiring skills in {', '.join(missing)} to increase role alignment.")
        
        # Communication recommendations
        if evaluation.soft_skill_index:
            if evaluation.soft_skill_index.communication < 0.7:
                recommendations.append("<b>Communication:</b> Practice articulating thoughts clearly and concisely. Consider Toastmasters or public speaking courses.")
            
            if evaluation.soft_skill_index.confidence < 0.7:
                recommendations.append("<b>Confidence Building:</b> Record practice videos, review them, and iterate. Consider mock interviews to build comfort.")
            
            if evaluation.soft_skill_index.engagement < 0.7:
                recommendations.append("<b>Engagement:</b> Work on being more expressive. Vary your tone and pace to maintain interest.")
        
        # Video-specific recommendations
        if evaluation.video_analysis:
            if evaluation.video_analysis.eye_contact_score < 0.7:
                recommendations.append("<b>Eye Contact:</b> Practice looking directly at the camera lens. Mark the camera with a sticker as a focal point.")
            
            if evaluation.video_analysis.posture_score < 0.7:
                recommendations.append("<b>Posture:</b> Sit up straight and position yourself at eye level with the camera. Good lighting and framing are essential.")
        
        # Transcript recommendations
        if evaluation.transcript_analysis:
            if evaluation.transcript_analysis.word_count < 100:
                recommendations.append("<b>Response Length:</b> Provide more detailed answers. Aim for 1-2 minutes of content to fully demonstrate your capabilities.")
            
            if evaluation.transcript_analysis.clarity_score < 0.7:
                recommendations.append("<b>Speech Clarity:</b> Speak slowly and clearly. Reduce filler words (um, uh, like). Prepare talking points in advance.")
        
        # General recommendations
        recommendations.append("<b>Preparation:</b> Research the company thoroughly. Prepare specific examples demonstrating your key skills and achievements.")
        recommendations.append("<b>Technical Depth:</b> Be ready to discuss technical projects in detail. Have code samples or portfolio pieces ready to share.")
        
        # Add to story
        for i, rec in enumerate(recommendations[:8], 1):  # Limit to 8 recommendations
            elements.append(Paragraph(f"{i}. {rec}", self.styles['CustomBody']))
        
        # Create container
        container = Table([[e] for e in elements], colWidths=[6.5*inch])
        container.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecfeff')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#06b6d4')),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        return container

