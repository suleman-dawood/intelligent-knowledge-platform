#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sentiment analyzer module for detecting sentiment and emotions in text.
"""

import logging
import asyncio
import time
import re
from typing import Dict, List, Any, Optional
import nltk
from nltk.tokenize import sent_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Import DeepSeek LLM client
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from coordinator.llm_client import get_llm_client

# Configure logging
logger = logging.getLogger(__name__)

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('vader_lexicon', quiet=True)


class SentimentAnalyzer:
    """Analyzer for detecting sentiment and emotions in text."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the sentiment analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Initialize the VADER sentiment analyzer
        self.vader = SentimentIntensityAnalyzer()
        
        # Initialize LLM client if available
        self.llm_client = None
        try:
            if config.get('llm', {}).get('deepseek_api_key'):
                self.llm_client = get_llm_client(config)
                logger.info("DeepSeek LLM client initialized for sentiment analysis")
        except Exception as e:
            logger.warning(f"Could not initialize LLM client: {e}")
        
        # Emotion lexicon (simplified version)
        # In a real implementation, this would be loaded from a comprehensive emotion lexicon
        self.emotion_lexicon = {
            "joy": ["happy", "joyful", "delighted", "excited", "glad", "pleased", "thrilled", "cheerful"],
            "sadness": ["sad", "unhappy", "depressed", "miserable", "gloomy", "heartbroken", "sorrowful"],
            "anger": ["angry", "furious", "enraged", "mad", "annoyed", "irritated", "outraged"],
            "fear": ["afraid", "scared", "frightened", "terrified", "anxious", "worried", "nervous"],
            "surprise": ["surprised", "amazed", "astonished", "shocked", "stunned", "unexpected"],
            "disgust": ["disgusted", "revolted", "repulsed", "nauseated", "appalled", "horrified"]
        }
        
        # Flatten the emotion lexicon for faster lookup
        self.emotion_words = {}
        for emotion, words in self.emotion_lexicon.items():
            for word in words:
                self.emotion_words[word] = emotion
                
        logger.info("Sentiment analyzer initialized")
    
    async def analyze(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment in text.
        
        Args:
            task_data: Task data containing text to analyze
            
        Returns:
            Sentiment analysis results
        """
        text = task_data.get('text')
        analyze_by_sentence = task_data.get('analyze_by_sentence', True)
        detect_emotions = task_data.get('detect_emotions', True)
        use_llm = task_data.get('use_llm', True)
        
        if not text:
            raise ValueError("Text content is required")
            
        logger.info("Analyzing sentiment in text")
        
        # Prepare result structure
        result = {
            "processed_at": time.time(),
            "text_length": len(text)
        }
        
        # Analyze overall document sentiment using VADER
        doc_sentiment = self._analyze_sentiment(text)
        result["document_sentiment"] = doc_sentiment
        
        # Get LLM sentiment analysis if available
        llm_sentiment = None
        if use_llm and self.llm_client:
            try:
                llm_sentiment = await self._analyze_sentiment_llm(text)
                result["llm_sentiment"] = llm_sentiment
            except Exception as e:
                logger.warning(f"LLM sentiment analysis failed: {e}")
        
        # Combine VADER and LLM results for final sentiment
        final_sentiment = self._combine_sentiment_results(doc_sentiment, llm_sentiment)
        result["sentiment"] = final_sentiment["label"]
        result["confidence"] = final_sentiment["confidence"]
        
        # Analyze by sentence if requested
        if analyze_by_sentence:
            sentences = sent_tokenize(text)
            sentence_sentiments = []
            
            for sentence in sentences:
                sentiment = self._analyze_sentiment(sentence)
                
                # Get LLM sentiment for sentence if available
                llm_sent = None
                if use_llm and self.llm_client and len(sentence) > 10:  # Only for substantial sentences
                    try:
                        llm_sent = await self._analyze_sentiment_llm(sentence)
                    except Exception:
                        pass
                
                # Combine results
                combined = self._combine_sentiment_results(sentiment, llm_sent)
                
                sentence_sentiments.append({
                    "text": sentence,
                    "sentiment": combined["label"],
                    "confidence": combined["confidence"],
                    "scores": sentiment,
                    "llm_scores": llm_sent
                })
                
            result["sentence_sentiments"] = sentence_sentiments
            
            # Calculate sentiment distribution
            sentiment_counts = {
                "positive": sum(1 for s in sentence_sentiments if s["sentiment"] == "positive"),
                "neutral": sum(1 for s in sentence_sentiments if s["sentiment"] == "neutral"),
                "negative": sum(1 for s in sentence_sentiments if s["sentiment"] == "negative")
            }
            
            total_sentences = len(sentences)
            sentiment_distribution = {
                label: count / total_sentences if total_sentences > 0 else 0
                for label, count in sentiment_counts.items()
            }
            
            result["sentiment_distribution"] = sentiment_distribution
        
        # Detect emotions if requested
        if detect_emotions:
            emotions = await self._detect_emotions(text)
            result["emotions"] = emotions
            
            # Add the dominant emotion
            if emotions:
                dominant_emotion = max(emotions.items(), key=lambda x: x[1])
                result["dominant_emotion"] = {
                    "emotion": dominant_emotion[0],
                    "score": dominant_emotion[1]
                }
            
        return result
    
    async def _analyze_sentiment_llm(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using DeepSeek LLM.
        
        Args:
            text: Text to analyze
            
        Returns:
            LLM sentiment analysis result
        """
        if not self.llm_client:
            return None
        
        try:
            # Limit text length for LLM processing
            if len(text) > 2000:
                text = text[:2000] + "..."
            
            sentiment_result = await self.llm_client.classify_sentiment(text)
            return sentiment_result
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment with LLM: {e}")
            return None
    
    def _combine_sentiment_results(self, vader_result: Dict[str, float], llm_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine VADER and LLM sentiment results.
        
        Args:
            vader_result: VADER sentiment scores
            llm_result: LLM sentiment result
            
        Returns:
            Combined sentiment result
        """
        # Determine VADER sentiment
        if vader_result["compound"] >= 0.05:
            vader_sentiment = "positive"
        elif vader_result["compound"] <= -0.05:
            vader_sentiment = "negative"
        else:
            vader_sentiment = "neutral"
        
        # If no LLM result, use VADER only
        if not llm_result:
            return {
                "label": vader_sentiment,
                "confidence": abs(vader_result["compound"])
            }
        
        # Get LLM sentiment
        llm_sentiment = llm_result.get("sentiment", "neutral")
        llm_confidence = llm_result.get("confidence", 0.5)
        
        # Combine results - if both agree, higher confidence; if they disagree, lower confidence
        if vader_sentiment == llm_sentiment:
            # Both agree - high confidence
            final_sentiment = vader_sentiment
            final_confidence = min(0.95, (abs(vader_result["compound"]) + llm_confidence) / 2 + 0.2)
        else:
            # Disagree - use the one with higher confidence but lower overall confidence
            vader_conf = abs(vader_result["compound"])
            if llm_confidence > vader_conf:
                final_sentiment = llm_sentiment
                final_confidence = llm_confidence * 0.7  # Reduce confidence due to disagreement
            else:
                final_sentiment = vader_sentiment
                final_confidence = vader_conf * 0.7
        
        return {
            "label": final_sentiment,
            "confidence": final_confidence
        }
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using VADER.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of sentiment scores
        """
        return self.vader.polarity_scores(text)
    
    async def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of emotion scores
        """
        # Tokenize and normalize text
        words = nltk.word_tokenize(text.lower())
        
        # Count emotion words
        emotion_counts = {emotion: 0 for emotion in self.emotion_lexicon.keys()}
        
        for word in words:
            if word in self.emotion_words:
                emotion = self.emotion_words[word]
                emotion_counts[emotion] += 1
                
        # Calculate emotion scores (normalized by text length)
        total_words = len(words) or 1  # Avoid division by zero
        emotion_scores = {
            emotion: count / total_words
            for emotion, count in emotion_counts.items()
        }
        
        # Filter out emotions with zero score
        emotions = {k: v for k, v in emotion_scores.items() if v > 0}
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        return emotions 