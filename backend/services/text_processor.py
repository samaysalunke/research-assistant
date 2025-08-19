"""
Advanced Text Processing Service
Handles text chunking, language detection, content analysis, and quality validation
"""

import re
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# Language detection
try:
    import langdetect
    from langdetect import detect, detect_langs
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logging.warning("langdetect not available, language detection will be disabled")

# Text processing
try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("nltk not available, advanced text processing will be limited")

from core.config import get_settings

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Content type classification"""
    ARTICLE = "article"
    DOCUMENTATION = "documentation"
    NEWS = "news"
    BLOG_POST = "blog_post"
    TECHNICAL = "technical"
    ACADEMIC = "academic"
    GENERAL = "general"

class ContentQuality(Enum):
    """Content quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

@dataclass
class TextChunk:
    """Represents a processed text chunk"""
    index: int
    text: str
    start_char: int
    end_char: int
    word_count: int
    sentence_count: int
    language: Optional[str] = None
    quality_score: float = 0.0
    topics: List[str] = None
    key_phrases: List[str] = None

@dataclass
class ContentAnalysis:
    """Content analysis results"""
    content_type: ContentType
    quality: ContentQuality
    language: str
    word_count: int
    sentence_count: int
    paragraph_count: int
    reading_time_minutes: int
    complexity_score: float
    topics: List[str]
    key_phrases: List[str]
    summary: str
    structure: Dict[str, Any]

class AdvancedTextProcessor:
    """Advanced text processing with enhanced chunking and analysis"""
    
    def __init__(self):
        self.settings = get_settings()
        self._initialize_nltk()
        
    def _initialize_nltk(self):
        """Initialize NLTK resources"""
        if not NLTK_AVAILABLE:
            return
            
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('maxent_ne_chunker', quiet=True)
            nltk.download('words', quiet=True)
        except Exception as e:
            logger.warning(f"Failed to initialize NLTK: {str(e)}")
            
    async def process_text(self, text: str, source_url: Optional[str] = None) -> ContentAnalysis:
        """Process text with comprehensive analysis"""
        try:
            # Clean and normalize text
            cleaned_text = self._clean_text(text)
            
            # Detect language
            language = self._detect_language(cleaned_text)
            
            # Analyze content structure
            structure = self._analyze_structure(cleaned_text)
            
            # Classify content type
            content_type = self._classify_content_type(cleaned_text, source_url)
            
            # Assess quality
            quality = self._assess_quality(cleaned_text, structure)
            
            # Extract topics and key phrases
            topics = self._extract_topics(cleaned_text)
            key_phrases = self._extract_key_phrases(cleaned_text)
            
            # Calculate metrics
            word_count = len(cleaned_text.split())
            sentence_count = len(self._split_sentences(cleaned_text))
            paragraph_count = len([p for p in cleaned_text.split('\n\n') if p.strip()])
            reading_time = self._calculate_reading_time(word_count)
            complexity_score = self._calculate_complexity(cleaned_text)
            
            # Generate summary
            summary = self._generate_summary(cleaned_text)
            
            return ContentAnalysis(
                content_type=content_type,
                quality=quality,
                language=language,
                word_count=word_count,
                sentence_count=sentence_count,
                paragraph_count=paragraph_count,
                reading_time_minutes=reading_time,
                complexity_score=complexity_score,
                topics=topics,
                key_phrases=key_phrases,
                summary=summary,
                structure=structure
            )
            
        except Exception as e:
            logger.error(f"Text processing failed: {str(e)}")
            raise Exception(f"Failed to process text: {str(e)}")
            
    def create_enhanced_chunks(self, text: str, chunk_size: int = None, overlap: int = None) -> List[TextChunk]:
        """Create enhanced text chunks with semantic boundaries"""
        if chunk_size is None:
            chunk_size = self.settings.chunk_size
        if overlap is None:
            overlap = self.settings.chunk_overlap
            
        try:
            # Clean text first
            cleaned_text = self._clean_text(text)
            
            # Split into sentences
            sentences = self._split_sentences(cleaned_text)
            
            chunks = []
            current_chunk = []
            current_length = 0
            start_char = 0
            
            for i, sentence in enumerate(sentences):
                sentence_length = len(sentence)
                
                # If adding this sentence would exceed chunk size
                if current_length + sentence_length > chunk_size and current_chunk:
                    # Create chunk
                    chunk_text = ' '.join(current_chunk)
                    chunk = self._create_chunk_object(
                        len(chunks), chunk_text, start_char, 
                        start_char + len(chunk_text)
                    )
                    chunks.append(chunk)
                    
                    # Start new chunk with overlap
                    overlap_sentences = self._get_overlap_sentences(current_chunk, overlap)
                    current_chunk = overlap_sentences + [sentence]
                    current_length = sum(len(s) for s in current_chunk)
                    start_char = start_char + len(' '.join(overlap_sentences))
                else:
                    current_chunk.append(sentence)
                    current_length += sentence_length
                    
            # Add final chunk
            if current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunk = self._create_chunk_object(
                    len(chunks), chunk_text, start_char,
                    start_char + len(chunk_text)
                )
                chunks.append(chunk)
                
            return chunks
            
        except Exception as e:
            logger.error(f"Chunking failed: {str(e)}")
            # Fallback to simple chunking
            return self._simple_chunking(text, chunk_size, overlap)
            
    def _create_chunk_object(self, index: int, text: str, start_char: int, end_char: int) -> TextChunk:
        """Create a TextChunk object with analysis"""
        word_count = len(text.split())
        sentence_count = len(self._split_sentences(text))
        language = self._detect_language(text)
        quality_score = self._calculate_chunk_quality(text)
        topics = self._extract_topics(text)
        key_phrases = self._extract_key_phrases(text)
        
        return TextChunk(
            index=index,
            text=text,
            start_char=start_char,
            end_char=end_char,
            word_count=word_count,
            sentence_count=sentence_count,
            language=language,
            quality_score=quality_score,
            topics=topics,
            key_phrases=key_phrases
        )
        
    def _clean_text(self, text: str) -> str:
        """Advanced text cleaning and normalization"""
        if not text:
            return ""
            
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common unwanted patterns
        unwanted_patterns = [
            r'Cookie Policy',
            r'Privacy Policy', 
            r'Terms of Service',
            r'Subscribe',
            r'Newsletter',
            r'Follow us',
            r'Share this',
            r'Related articles',
            r'Advertisement',
            r'Advertise',
            r'© \d{4}',
            r'All rights reserved',
            r'Loading\.\.\.',
            r'Please wait\.\.\.',
            r'JavaScript is required',
            r'Enable JavaScript'
        ]
        
        for pattern in unwanted_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
        # Normalize quotes and dashes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        text = text.replace('–', '-').replace('—', '-')
        
        # Remove excessive punctuation
        text = re.sub(r'[.!?]{2,}', '.', text)
        text = re.sub(r'[,;]{2,}', ',', text)
        
        # Clean up paragraph breaks
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        return text.strip()
        
    def _detect_language(self, text: str) -> str:
        """Detect text language"""
        if not LANGDETECT_AVAILABLE or not text.strip():
            return "en"
            
        try:
            # Use first 1000 characters for detection
            sample = text[:1000]
            return detect(sample)
        except Exception as e:
            logger.warning(f"Language detection failed: {str(e)}")
            return "en"
            
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        if not NLTK_AVAILABLE:
            # Simple sentence splitting
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
            
        try:
            return sent_tokenize(text)
        except Exception as e:
            logger.warning(f"NLTK sentence tokenization failed: {str(e)}")
            # Fallback to simple splitting
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
            
    def _analyze_structure(self, text: str) -> Dict[str, Any]:
        """Analyze document structure"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        sentences = self._split_sentences(text)
        
        # Analyze paragraph lengths
        paragraph_lengths = [len(p.split()) for p in paragraphs]
        avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
        
        # Analyze sentence lengths
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        
        # Detect headers and sections
        headers = self._detect_headers(paragraphs)
        
        return {
            'paragraph_count': len(paragraphs),
            'sentence_count': len(sentences),
            'avg_paragraph_length': avg_paragraph_length,
            'avg_sentence_length': avg_sentence_length,
            'headers': headers,
            'has_lists': self._has_lists(text),
            'has_code_blocks': self._has_code_blocks(text),
            'has_links': self._has_links(text)
        }
        
    def _detect_headers(self, paragraphs: List[str]) -> List[str]:
        """Detect potential headers in text"""
        headers = []
        for para in paragraphs:
            # Simple header detection based on length and formatting
            if len(para.split()) <= 10 and para.isupper():
                headers.append(para)
            elif para.startswith('#') or para.startswith('*'):
                headers.append(para)
        return headers
        
    def _has_lists(self, text: str) -> bool:
        """Check if text contains lists"""
        list_patterns = [
            r'^\s*[-*+]\s+',  # Bullet points
            r'^\s*\d+\.\s+',  # Numbered lists
            r'^\s*[a-zA-Z]\.\s+'  # Lettered lists
        ]
        return any(re.search(pattern, text, re.MULTILINE) for pattern in list_patterns)
        
    def _has_code_blocks(self, text: str) -> bool:
        """Check if text contains code blocks"""
        code_patterns = [
            r'```[\s\S]*?```',  # Markdown code blocks
            r'`[^`]+`',  # Inline code
            r'<code>[\s\S]*?</code>'  # HTML code tags
        ]
        return any(re.search(pattern, text) for pattern in code_patterns)
        
    def _has_links(self, text: str) -> bool:
        """Check if text contains links"""
        link_patterns = [
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'\[([^\]]+)\]\(([^)]+)\)',  # Markdown links
            r'<a\s+href=[^>]+>.*?</a>'  # HTML links
        ]
        return any(re.search(pattern, text) for pattern in link_patterns)
        
    def _classify_content_type(self, text: str, source_url: Optional[str] = None) -> ContentType:
        """Classify content type based on text and URL"""
        text_lower = text.lower()
        url_lower = source_url.lower() if source_url else ""
        
        # Technical indicators
        technical_terms = ['api', 'function', 'method', 'class', 'interface', 'database', 'algorithm']
        if any(term in text_lower for term in technical_terms):
            return ContentType.TECHNICAL
            
        # Academic indicators
        academic_terms = ['research', 'study', 'analysis', 'methodology', 'conclusion', 'hypothesis']
        if any(term in text_lower for term in academic_terms):
            return ContentType.ACADEMIC
            
        # Documentation indicators
        doc_terms = ['documentation', 'guide', 'tutorial', 'manual', 'reference', 'docs']
        if any(term in url_lower for term in doc_terms):
            return ContentType.DOCUMENTATION
            
        # News indicators
        news_terms = ['news', 'report', 'announcement', 'press release', 'breaking']
        if any(term in text_lower for term in news_terms):
            return ContentType.NEWS
            
        # Blog indicators
        blog_terms = ['blog', 'post', 'article', 'opinion', 'thoughts']
        if any(term in url_lower for term in blog_terms):
            return ContentType.BLOG_POST
            
        # Default to article
        return ContentType.ARTICLE
        
    def _assess_quality(self, text: str, structure: Dict[str, Any]) -> ContentQuality:
        """Assess content quality based on various metrics"""
        score = 0.0
        
        # Length score (0-20 points)
        word_count = len(text.split())
        if word_count > 1000:
            score += 20
        elif word_count > 500:
            score += 15
        elif word_count > 200:
            score += 10
        elif word_count > 100:
            score += 5
            
        # Structure score (0-20 points)
        if structure['paragraph_count'] > 5:
            score += 10
        if structure['sentence_count'] > 10:
            score += 10
            
        # Readability score (0-20 points)
        avg_sentence_length = structure['avg_sentence_length']
        if 10 <= avg_sentence_length <= 25:
            score += 20
        elif 5 <= avg_sentence_length <= 30:
            score += 15
        elif avg_sentence_length > 0:
            score += 10
            
        # Content richness score (0-20 points)
        unique_words = len(set(text.lower().split()))
        if unique_words > 200:
            score += 20
        elif unique_words > 100:
            score += 15
        elif unique_words > 50:
            score += 10
            
        # Formatting score (0-20 points)
        if structure['has_lists']:
            score += 5
        if structure['has_links']:
            score += 5
        if structure['headers']:
            score += 10
            
        # Determine quality level
        if score >= 80:
            return ContentQuality.EXCELLENT
        elif score >= 60:
            return ContentQuality.GOOD
        elif score >= 40:
            return ContentQuality.FAIR
        else:
            return ContentQuality.POOR
            
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text"""
        if not NLTK_AVAILABLE:
            return self._simple_topic_extraction(text)
            
        try:
            # Simple topic extraction based on frequency
            words = word_tokenize(text.lower())
            stop_words = set(stopwords.words('english'))
            
            # Filter out stop words and short words
            filtered_words = [word for word in words if word.isalpha() and len(word) > 3 and word not in stop_words]
            
            # Count frequency
            word_freq = {}
            for word in filtered_words:
                word_freq[word] = word_freq.get(word, 0) + 1
                
            # Get top topics
            topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            return [topic[0] for topic in topics]
            
        except Exception as e:
            logger.warning(f"Topic extraction failed: {str(e)}")
            return self._simple_topic_extraction(text)
            
    def _simple_topic_extraction(self, text: str) -> List[str]:
        """Simple topic extraction without NLTK"""
        # Extract capitalized words and phrases
        topics = re.findall(r'\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\b', text)
        return list(set(topics))[:10]
        
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text"""
        if not NLTK_AVAILABLE:
            return self._simple_phrase_extraction(text)
            
        try:
            # Extract noun phrases using NLTK
            sentences = sent_tokenize(text)
            key_phrases = []
            
            for sentence in sentences[:10]:  # Limit to first 10 sentences
                words = word_tokenize(sentence)
                tagged = nltk.pos_tag(words)
                
                # Extract noun phrases
                grammar = r"""
                    NP: {<DT|PP\$>?<JJ.*>*<NN.*>+}
                    PP: {<IN><NP>}
                    VP: {<VB.*><NP|PP>}
                """
                cp = nltk.RegexpParser(grammar)
                result = cp.parse(tagged)
                
                for subtree in result.subtrees():
                    if subtree.label() == 'NP':
                        phrase = ' '.join(word for word, tag in subtree.leaves())
                        if len(phrase.split()) <= 4:  # Limit phrase length
                            key_phrases.append(phrase)
                            
            return list(set(key_phrases))[:15]
            
        except Exception as e:
            logger.warning(f"Key phrase extraction failed: {str(e)}")
            return self._simple_phrase_extraction(text)
            
    def _simple_phrase_extraction(self, text: str) -> List[str]:
        """Simple phrase extraction without NLTK"""
        # Extract phrases in quotes or parentheses
        phrases = re.findall(r'"([^"]+)"', text)
        phrases.extend(re.findall(r'\(([^)]+)\)', text))
        return phrases[:10]
        
    def _calculate_reading_time(self, word_count: int) -> int:
        """Calculate estimated reading time in minutes"""
        # Average reading speed: 200-250 words per minute
        return max(1, word_count // 225)
        
    def _calculate_complexity(self, text: str) -> float:
        """Calculate text complexity score (0-1)"""
        if not text:
            return 0.0
            
        sentences = self._split_sentences(text)
        words = text.split()
        
        if not sentences or not words:
            return 0.0
            
        # Average sentence length
        avg_sentence_length = len(words) / len(sentences)
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Unique word ratio
        unique_ratio = len(set(words)) / len(words)
        
        # Complexity score (0-1)
        complexity = (
            min(avg_sentence_length / 30, 1.0) * 0.4 +
            min(avg_word_length / 8, 1.0) * 0.3 +
            unique_ratio * 0.3
        )
        
        return min(complexity, 1.0)
        
    def _generate_summary(self, text: str) -> str:
        """Generate a brief summary of the text"""
        sentences = self._split_sentences(text)
        
        if len(sentences) <= 3:
            return text
            
        # Take first and last sentences for summary
        summary_sentences = sentences[:2]
        if len(sentences) > 4:
            summary_sentences.append(sentences[-1])
            
        return ' '.join(summary_sentences)
        
    def _calculate_chunk_quality(self, text: str) -> float:
        """Calculate quality score for a text chunk (0-1)"""
        if not text:
            return 0.0
            
        score = 0.0
        
        # Length score
        word_count = len(text.split())
        if word_count > 50:
            score += 0.3
        elif word_count > 20:
            score += 0.2
        elif word_count > 10:
            score += 0.1
            
        # Content richness
        unique_words = len(set(text.lower().split()))
        if unique_words > 20:
            score += 0.3
        elif unique_words > 10:
            score += 0.2
            
        # Sentence structure
        sentences = self._split_sentences(text)
        if len(sentences) > 2:
            score += 0.2
        elif len(sentences) > 1:
            score += 0.1
            
        # Readability
        avg_sentence_length = word_count / len(sentences) if sentences else 0
        if 10 <= avg_sentence_length <= 25:
            score += 0.2
        elif 5 <= avg_sentence_length <= 30:
            score += 0.1
            
        return min(score, 1.0)
        
    def _get_overlap_sentences(self, sentences: List[str], overlap_size: int) -> List[str]:
        """Get sentences for overlap between chunks"""
        if not sentences or overlap_size <= 0:
            return []
            
        overlap_text = ' '.join(sentences)
        if len(overlap_text) <= overlap_size:
            return sentences
            
        # Find sentence boundary within overlap size
        current_length = 0
        overlap_sentences = []
        
        for sentence in sentences:
            if current_length + len(sentence) <= overlap_size:
                overlap_sentences.append(sentence)
                current_length += len(sentence)
            else:
                break
                
        return overlap_sentences
        
    def _simple_chunking(self, text: str, chunk_size: int, overlap: int) -> List[TextChunk]:
        """Simple character-based chunking as fallback"""
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunk_text = text[i:i + chunk_size]
            if chunk_text.strip():
                chunk = self._create_chunk_object(
                    len(chunks), chunk_text.strip(), i, i + len(chunk_text)
                )
                chunks.append(chunk)
        return chunks
