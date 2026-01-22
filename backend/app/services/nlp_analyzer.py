import spacy
import logging
from typing import List, Dict, Set
from collections import Counter
import re
import math
from ..models.schemas import TranscriptAnalysisResult
from ..config.settings import settings

logger = logging.getLogger(__name__)

class NLPAnalyzer:
    """Analyze transcripts using NLP techniques"""
    
    def __init__(self):
        try:
            self.nlp = spacy.load(settings.SPACY_MODEL)
            logger.info(f"Loaded spaCy model: {settings.SPACY_MODEL}")
        except Exception as e:
            logger.warning(f"Could not load spaCy model: {e}. Using blank model.")
            self.nlp = spacy.blank("en")
        
        # Technical terms dictionary (expandable)
        self.technical_terms = {
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'nodejs', 'django', 'flask', 'fastapi', 'express', 'spring', 'docker',
            'kubernetes', 'aws', 'azure', 'gcp', 'sql', 'nosql', 'mongodb', 'postgresql',
            'mysql', 'redis', 'microservices', 'api', 'rest', 'graphql', 'git',
            'cicd', 'jenkins', 'agile', 'scrum', 'machine learning', 'deep learning',
            'tensorflow', 'pytorch', 'nlp', 'computer vision', 'devops', 'linux',
            'algorithm', 'data structure', 'optimization', 'scalability', 'architecture'
        }
    
    async def analyze_transcript(self, transcript: str) -> TranscriptAnalysisResult:
        """Analyze transcript for clarity, vocabulary, and technical content"""
        try:
            logger.info("Analyzing transcript with NLP")
            
            # Clean transcript
            cleaned_text = self._clean_text(transcript)
            
            # Process with spaCy
            doc = self.nlp(cleaned_text)
            
            # Compute metrics
            clarity_score = self._compute_clarity_score(doc, cleaned_text)
            vocabulary_diversity = self._compute_vocabulary_diversity(doc)
            coherence_score = self._compute_coherence_score(doc)
            technical_terms = self._extract_technical_terms(cleaned_text)
            word_count = len([token for token in doc if not token.is_punct and not token.is_space])
            sentiment = self._analyze_sentiment(doc)
            
            result = TranscriptAnalysisResult(
                transcript=transcript,
                clarity_score=clarity_score,
                vocabulary_diversity=vocabulary_diversity,
                coherence_score=coherence_score,
                technical_terms=technical_terms,
                word_count=word_count,
                sentiment=sentiment
            )
            
            logger.info("Transcript analysis complete")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing transcript: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()
    
    def _compute_clarity_score(self, doc, text: str) -> float:
        """Compute speech clarity score based on sentence structure and grammar"""
        if len(doc) == 0:
            return 0.0
        
        # Sentence length (not too short, not too long)
        sentences = list(doc.sents)
        if not sentences:
            return 0.3
        
        avg_sentence_length = len(doc) / len(sentences)
        optimal_length = 15  # words per sentence
        length_score = 1.0 - min(1.0, abs(avg_sentence_length - optimal_length) / optimal_length)
        
        # Proper punctuation
        punct_count = len([token for token in doc if token.is_punct])
        punct_score = min(1.0, punct_count / len(sentences))
        
        # Filler word detection
        filler_words = {'um', 'uh', 'like', 'you know', 'basically', 'actually', 'literally'}
        text_lower = text.lower()
        filler_count = sum(text_lower.count(word) for word in filler_words)
        filler_penalty = max(0, 1.0 - (filler_count * 0.05))
        
        # Weighted average
        clarity = (length_score * 0.4 + punct_score * 0.3 + filler_penalty * 0.3)
        return min(1.0, max(0.0, clarity))
    
    def _compute_vocabulary_diversity(self, doc) -> float:
        """Compute vocabulary diversity using Type-Token Ratio"""
        if len(doc) == 0:
            return 0.0
        
        # Get words (excluding punctuation and stopwords)
        words = [token.text.lower() for token in doc 
                if not token.is_punct and not token.is_space and token.is_alpha]
        
        if not words:
            return 0.0
        
        # Type-Token Ratio
        unique_words = set(words)
        ttr = len(unique_words) / len(words)
        
        # Normalize (TTR typically ranges from 0.4 to 0.8 for good speech)
        normalized_ttr = min(1.0, ttr / 0.6)
        
        return normalized_ttr
    
    def _compute_coherence_score(self, doc) -> float:
        """Compute coherence based on sentence transitions and topic consistency"""
        sentences = list(doc.sents)
        
        if len(sentences) < 2:
            return 0.5
        
        # Check for transition words
        transition_words = {
            'however', 'therefore', 'moreover', 'furthermore', 'additionally',
            'consequently', 'thus', 'hence', 'also', 'similarly', 'first',
            'second', 'finally', 'next', 'then', 'because', 'since', 'although'
        }
        
        transition_count = sum(
            1 for sent in sentences 
            for token in sent 
            if token.text.lower() in transition_words
        )
        
        transition_score = min(1.0, transition_count / len(sentences))
        
        # Check sentence connectivity (simplified)
        # In production, use sentence embeddings for semantic similarity
        coherence = transition_score * 0.6 + 0.4  # Base coherence
        
        return min(1.0, max(0.0, coherence))
    
    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terms from text"""
        text_lower = text.lower()
        found_terms = []
        
        for term in self.technical_terms:
            if term in text_lower:
                found_terms.append(term)
        
        return sorted(found_terms)
    
    def _analyze_sentiment(self, doc) -> str:
        """Analyze sentiment (simplified version)"""
        # Simplified sentiment based on positive/negative word counts
        positive_words = {'excited', 'passionate', 'excellent', 'great', 'strong', 
                         'confident', 'successful', 'innovative', 'effective'}
        negative_words = {'difficult', 'challenging', 'failed', 'problem', 'issue',
                         'weak', 'uncertain', 'limited'}
        
        text_lower = doc.text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"
    
    def extract_key_phrases(self, text: str, top_n: int = 10) -> List[str]:
        """Extract key phrases using noun chunks"""
        doc = self.nlp(text)
        
        # Extract noun chunks
        noun_chunks = [chunk.text.lower() for chunk in doc.noun_chunks 
                      if len(chunk.text.split()) >= 2]
        
        # Count frequency
        phrase_counts = Counter(noun_chunks)
        
        # Return top N
        return [phrase for phrase, _ in phrase_counts.most_common(top_n)]
