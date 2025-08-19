"""
Enhanced AI Processing Service
Content-aware AI processing with improved prompts and strategies
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import logging

import anthropic
from core.config import get_settings

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Content type for AI processing strategies"""
    ARTICLE = "article"
    DOCUMENTATION = "documentation"
    NEWS = "news"
    BLOG_POST = "blog_post"
    TECHNICAL = "technical"
    ACADEMIC = "academic"
    GENERAL = "general"

class ProcessingStrategy(Enum):
    """Processing strategies based on content type and quality"""
    COMPREHENSIVE = "comprehensive"  # High-quality, important content
    STANDARD = "standard"           # Regular content
    LIGHT = "light"                 # Low-quality or short content
    TECHNICAL = "technical"         # Technical documentation
    ACADEMIC = "academic"           # Academic/research content

class EnhancedAIProcessor:
    """Enhanced AI processor with content-aware strategies"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)
        
    async def process_content(self, content: str, content_type: str, quality: str, 
                            language: str = "en", word_count: int = 0) -> Dict[str, Any]:
        """Process content using enhanced AI strategies"""
        try:
            # Determine processing strategy
            strategy = self._determine_strategy(content_type, quality, word_count)
            
            # Get content-aware prompts
            prompts = self._get_content_aware_prompts(content_type, strategy, language)
            
            # Process content with enhanced prompts
            results = await self._process_with_strategy(content, prompts, strategy)
            
            return results
            
        except Exception as e:
            logger.error(f"Enhanced AI processing failed: {str(e)}")
            raise Exception(f"Failed to process content with AI: {str(e)}")
            
    def _determine_strategy(self, content_type: str, quality: str, word_count: int) -> ProcessingStrategy:
        """Determine processing strategy based on content characteristics"""
        
        # Quality-based strategy selection
        if quality == "excellent" and word_count > 1000:
            return ProcessingStrategy.COMPREHENSIVE
        elif quality == "poor" or word_count < 200:
            return ProcessingStrategy.LIGHT
        elif content_type in ["technical", "documentation"]:
            return ProcessingStrategy.TECHNICAL
        elif content_type == "academic":
            return ProcessingStrategy.ACADEMIC
        else:
            return ProcessingStrategy.STANDARD
            
    def _get_content_aware_prompts(self, content_type: str, strategy: ProcessingStrategy, 
                                 language: str) -> Dict[str, str]:
        """Get content-aware prompts based on type and strategy"""
        
        base_prompts = {
            "title": self._get_title_prompt(content_type, language),
            "summary": self._get_summary_prompt(content_type, strategy, language),
            "insights": self._get_insights_prompt(content_type, strategy, language),
            "tags": self._get_tags_prompt(content_type, language),
            "action_items": self._get_action_items_prompt(content_type, language),
            "quotable_snippets": self._get_quotable_prompt(content_type, language)
        }
        
        return base_prompts
        
    def _get_title_prompt(self, content_type: str, language: str) -> str:
        """Get title extraction prompt based on content type"""
        
        prompts = {
            "technical": f"""Extract a clear, descriptive title from this technical content. 
            The title should be concise (under 100 characters) and accurately reflect the main topic.
            Focus on the primary technical concept or functionality described.
            Language: {language}
            
            Content:
            {{content}}""",
            
            "documentation": f"""Extract a clear, descriptive title from this documentation.
            The title should follow documentation naming conventions and clearly indicate the topic.
            Keep it concise and professional.
            Language: {language}
            
            Content:
            {{content}}""",
            
            "academic": f"""Extract a scholarly title from this academic content.
            The title should reflect the research topic, methodology, or findings.
            Use academic language and be specific about the subject matter.
            Language: {language}
            
            Content:
            {{content}}""",
            
            "news": f"""Extract a news-style headline from this content.
            The title should be engaging, accurate, and follow journalistic standards.
            Include key facts or outcomes if relevant.
            Language: {language}
            
            Content:
            {{content}}""",
            
            "blog_post": f"""Extract an engaging blog post title from this content.
            The title should be compelling and accurately represent the main message.
            Balance between being catchy and informative.
            Language: {language}
            
            Content:
            {{content}}""",
            
            "article": f"""Extract a clear, descriptive title from this article.
            The title should capture the main topic and be engaging for readers.
            Keep it concise and informative.
            Language: {language}
            
            Content:
            {{content}}"""
        }
        
        return prompts.get(content_type, prompts["article"])
        
    def _get_summary_prompt(self, content_type: str, strategy: ProcessingStrategy, 
                           language: str) -> str:
        """Get summary generation prompt based on content type and strategy"""
        
        length_guidance = {
            ProcessingStrategy.COMPREHENSIVE: "Create a comprehensive summary (200-300 words) covering all major points, key findings, and important details.",
            ProcessingStrategy.STANDARD: "Create a balanced summary (150-200 words) covering the main points and key insights.",
            ProcessingStrategy.LIGHT: "Create a concise summary (100-150 words) focusing on the most important points.",
            ProcessingStrategy.TECHNICAL: "Create a technical summary (150-250 words) focusing on functionality, features, and implementation details.",
            ProcessingStrategy.ACADEMIC: "Create an academic summary (200-300 words) covering methodology, findings, and implications."
        }
        
        type_guidance = {
            "technical": "Focus on technical concepts, features, and practical applications.",
            "documentation": "Emphasize functionality, usage, and key information for users.",
            "academic": "Include methodology, findings, significance, and potential implications.",
            "news": "Highlight key facts, outcomes, and newsworthy elements.",
            "blog_post": "Capture the main message, insights, and value for readers.",
            "article": "Cover the main topic, key points, and important takeaways."
        }
        
        return f"""Generate a summary of the following content.

{length_guidance[strategy]}

{type_guidance.get(content_type, type_guidance['article'])}

Language: {language}

Content:
{{content}}

Summary:"""
        
    def _get_insights_prompt(self, content_type: str, strategy: ProcessingStrategy, 
                            language: str) -> str:
        """Get insights extraction prompt based on content type and strategy"""
        
        insight_count = {
            ProcessingStrategy.COMPREHENSIVE: "5-8",
            ProcessingStrategy.STANDARD: "3-5", 
            ProcessingStrategy.LIGHT: "2-3",
            ProcessingStrategy.TECHNICAL: "4-6",
            ProcessingStrategy.ACADEMIC: "5-7"
        }
        
        type_guidance = {
            "technical": "Focus on technical insights, best practices, implementation considerations, and technical implications.",
            "documentation": "Extract insights about usability, common issues, best practices, and user experience considerations.",
            "academic": "Focus on research insights, methodological implications, theoretical contributions, and practical applications.",
            "news": "Extract insights about implications, trends, impact, and broader context.",
            "blog_post": "Focus on actionable insights, personal takeaways, and value for readers.",
            "article": "Extract insights about key learnings, implications, and important takeaways."
        }
        
        return f"""Extract {insight_count[strategy]} key insights from the following content.

{type_guidance.get(content_type, type_guidance['article'])}

For each insight, provide:
- A clear, actionable insight
- Brief explanation of why it's important
- Relevance score (0-1)

Language: {language}

Content:
{{content}}

Insights:"""
        
    def _get_tags_prompt(self, content_type: str, language: str) -> str:
        """Get tag extraction prompt based on content type"""
        
        tag_guidance = {
            "technical": "Include technical terms, programming languages, frameworks, methodologies, and technical concepts.",
            "documentation": "Focus on functionality, features, user scenarios, and technical topics.",
            "academic": "Include research areas, methodologies, key concepts, and academic disciplines.",
            "news": "Include relevant topics, entities, locations, and current events.",
            "blog_post": "Include topics, themes, personal insights, and relevant categories.",
            "article": "Include main topics, themes, and relevant categories."
        }
        
        return f"""Extract 10-15 relevant tags from the following content.

{tag_guidance.get(content_type, tag_guidance['article'])}

Tags should be:
- Single words or short phrases
- Relevant to the content
- Useful for categorization and search
- Include both broad and specific terms

Language: {language}

Content:
{{content}}

Tags:"""
        
    def _get_action_items_prompt(self, content_type: str, language: str) -> str:
        """Get action items extraction prompt based on content type"""
        
        action_guidance = {
            "technical": "Focus on implementation steps, technical tasks, and development actions.",
            "documentation": "Extract user actions, setup steps, and usage instructions.",
            "academic": "Focus on research actions, follow-up studies, and academic tasks.",
            "news": "Extract potential actions, responses, or next steps related to the news.",
            "blog_post": "Focus on actionable takeaways and personal actions readers can take.",
            "article": "Extract actionable insights and next steps for readers."
        }
        
        return f"""Extract actionable items from the following content.

{action_guidance.get(content_type, action_guidance['article'])}

For each action item, provide:
- Clear, specific action
- Priority level (high/medium/low)
- Brief context

Language: {language}

Content:
{{content}}

Action Items:"""
        
    def _get_quotable_prompt(self, content_type: str, language: str) -> str:
        """Get quotable snippets extraction prompt based on content type"""
        
        quote_guidance = {
            "technical": "Focus on key technical statements, important definitions, and notable technical insights.",
            "documentation": "Extract important statements, key concepts, and essential information.",
            "academic": "Focus on key findings, important conclusions, and significant statements.",
            "news": "Extract newsworthy quotes, important statements, and key facts.",
            "blog_post": "Focus on insightful statements, personal insights, and memorable quotes.",
            "article": "Extract important statements, key insights, and notable quotes."
        }
        
        return f"""Extract 3-5 quotable snippets from the following content.

{quote_guidance.get(content_type, quote_guidance['article'])}

For each quote, provide:
- The exact quote
- Brief context
- Why it's quotable

Language: {language}

Content:
{{content}}

Quotable Snippets:"""
        
    async def _process_with_strategy(self, content: str, prompts: Dict[str, str], 
                                   strategy: ProcessingStrategy) -> Dict[str, Any]:
        """Process content using the determined strategy"""
        
        results = {}
        
        # Process based on strategy
        if strategy == ProcessingStrategy.LIGHT:
            # Light processing for short/low-quality content
            results.update(await self._light_processing(content, prompts))
        elif strategy == ProcessingStrategy.COMPREHENSIVE:
            # Comprehensive processing for high-quality content
            results.update(await self._comprehensive_processing(content, prompts))
        else:
            # Standard processing
            results.update(await self._standard_processing(content, prompts))
            
        return results
        
    async def _light_processing(self, content: str, prompts: Dict[str, str]) -> Dict[str, Any]:
        """Light processing for short or low-quality content"""
        
        # Focus on essential extraction only
        tasks = [
            ("title", self._extract_title(content, prompts["title"])),
            ("summary", self._extract_summary(content, prompts["summary"])),
            ("tags", self._extract_tags(content, prompts["tags"]))
        ]
        
        results = {}
        for name, task in tasks:
            try:
                results[name] = await task
            except Exception as e:
                logger.warning(f"Light processing failed for {name}: {str(e)}")
                results[name] = self._get_fallback_value(name)
                
        return results
        
    async def _standard_processing(self, content: str, prompts: Dict[str, str]) -> Dict[str, Any]:
        """Standard processing for regular content"""
        
        tasks = [
            ("title", self._extract_title(content, prompts["title"])),
            ("summary", self._extract_summary(content, prompts["summary"])),
            ("insights", self._extract_insights(content, prompts["insights"])),
            ("tags", self._extract_tags(content, prompts["tags"])),
            ("action_items", self._extract_action_items(content, prompts["action_items"])),
            ("quotable_snippets", self._extract_quotable_snippets(content, prompts["quotable_snippets"]))
        ]
        
        results = {}
        for name, task in tasks:
            try:
                results[name] = await task
            except Exception as e:
                logger.warning(f"Standard processing failed for {name}: {str(e)}")
                results[name] = self._get_fallback_value(name)
                
        return results
        
    async def _comprehensive_processing(self, content: str, prompts: Dict[str, str]) -> Dict[str, Any]:
        """Comprehensive processing for high-quality content"""
        
        # Process in parallel for better performance
        tasks = [
            ("title", self._extract_title(content, prompts["title"])),
            ("summary", self._extract_summary(content, prompts["summary"])),
            ("insights", self._extract_insights(content, prompts["insights"])),
            ("tags", self._extract_tags(content, prompts["tags"])),
            ("action_items", self._extract_action_items(content, prompts["action_items"])),
            ("quotable_snippets", self._extract_quotable_snippets(content, prompts["quotable_snippets"]))
        ]
        
        # Execute tasks concurrently
        task_results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        results = {}
        for i, (name, _) in enumerate(tasks):
            if isinstance(task_results[i], Exception):
                logger.warning(f"Comprehensive processing failed for {name}: {str(task_results[i])}")
                results[name] = self._get_fallback_value(name)
            else:
                results[name] = task_results[i]
                
        return results
        
    async def _extract_title(self, content: str, prompt: str) -> str:
        """Extract title using AI"""
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt.format(content=content[:2000])
                }]
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Title extraction failed: {str(e)}")
            return "Untitled"
            
    async def _extract_summary(self, content: str, prompt: str) -> str:
        """Extract summary using AI"""
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                temperature=0.4,
                messages=[{
                    "role": "user",
                    "content": prompt.format(content=content[:5000])
                }]
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Summary extraction failed: {str(e)}")
            return "Summary not available"
            
    async def _extract_insights(self, content: str, prompt: str) -> List[Dict[str, Any]]:
        """Extract insights using AI"""
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=800,
                temperature=0.4,
                messages=[{
                    "role": "user",
                    "content": prompt.format(content=content[:8000])
                }]
            )
            
            # Parse insights from response
            insights_text = response.content[0].text.strip()
            return self._parse_insights(insights_text)
            
        except Exception as e:
            logger.error(f"Insights extraction failed: {str(e)}")
            return []
            
    async def _extract_tags(self, content: str, prompt: str) -> List[str]:
        """Extract tags using AI"""
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt.format(content=content[:3000])
                }]
            )
            
            # Parse tags from response
            tags_text = response.content[0].text.strip()
            return self._parse_tags(tags_text)
            
        except Exception as e:
            logger.error(f"Tags extraction failed: {str(e)}")
            return []
            
    async def _extract_action_items(self, content: str, prompt: str) -> List[str]:
        """Extract action items using AI"""
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=400,
                temperature=0.4,
                messages=[{
                    "role": "user",
                    "content": prompt.format(content=content[:4000])
                }]
            )
            
            # Parse action items from response
            action_text = response.content[0].text.strip()
            return self._parse_action_items(action_text)
            
        except Exception as e:
            logger.error(f"Action items extraction failed: {str(e)}")
            return []
            
    async def _extract_quotable_snippets(self, content: str, prompt: str) -> List[Dict[str, Any]]:
        """Extract quotable snippets using AI"""
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=600,
                temperature=0.4,
                messages=[{
                    "role": "user",
                    "content": prompt.format(content=content[:6000])
                }]
            )
            
            # Parse quotable snippets from response
            quotes_text = response.content[0].text.strip()
            return self._parse_quotable_snippets(quotes_text)
            
        except Exception as e:
            logger.error(f"Quotable snippets extraction failed: {str(e)}")
            return []
            
    def _parse_insights(self, insights_text: str) -> List[Dict[str, Any]]:
        """Parse insights from AI response"""
        try:
            # Simple parsing - look for numbered or bulleted insights
            lines = insights_text.split('\n')
            insights = []
            
            for line in lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or 
                           line[0].isdigit() or line.startswith('Insight')):
                    # Extract insight text
                    insight_text = line.lstrip('-•0123456789. ')
                    if insight_text:
                        insights.append({
                            "text": insight_text,
                            "relevance_score": 0.8,  # Default score
                            "category": "general"
                        })
                        
            return insights[:8]  # Limit to 8 insights
            
        except Exception as e:
            logger.warning(f"Insights parsing failed: {str(e)}")
            return []
            
    def _parse_tags(self, tags_text: str) -> List[str]:
        """Parse tags from AI response"""
        try:
            # Extract tags from response
            tags = []
            lines = tags_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or 
                           line[0].isalpha()):
                    tag = line.lstrip('-• ').strip()
                    if tag and len(tag) < 50:  # Reasonable tag length
                        tags.append(tag)
                        
            return list(set(tags))[:15]  # Remove duplicates, limit to 15
            
        except Exception as e:
            logger.warning(f"Tags parsing failed: {str(e)}")
            return []
            
    def _parse_action_items(self, action_text: str) -> List[str]:
        """Parse action items from AI response"""
        try:
            # Extract action items from response
            actions = []
            lines = action_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or 
                           line[0].isdigit()):
                    action = line.lstrip('-•0123456789. ')
                    if action:
                        actions.append(action)
                        
            return actions[:10]  # Limit to 10 action items
            
        except Exception as e:
            logger.warning(f"Action items parsing failed: {str(e)}")
            return []
            
    def _parse_quotable_snippets(self, quotes_text: str) -> List[Dict[str, Any]]:
        """Parse quotable snippets from AI response"""
        try:
            # Simple parsing for quotable snippets
            lines = quotes_text.split('\n')
            snippets = []
            current_quote = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('Quote:') or line.startswith('"'):
                    if current_quote:
                        snippets.append(current_quote)
                    current_quote = {"quote": line.lstrip('Quote: "').rstrip('"')}
                elif line.startswith('Context:') and current_quote:
                    current_quote["context"] = line.lstrip('Context: ')
                    
            if current_quote:
                snippets.append(current_quote)
                
            return snippets[:5]  # Limit to 5 snippets
            
        except Exception as e:
            logger.warning(f"Quotable snippets parsing failed: {str(e)}")
            return []
            
    def _get_fallback_value(self, field_name: str) -> Any:
        """Get fallback values for failed processing"""
        fallbacks = {
            "title": "Untitled",
            "summary": "Summary not available",
            "insights": [],
            "tags": [],
            "action_items": [],
            "quotable_snippets": []
        }
        return fallbacks.get(field_name, "")
