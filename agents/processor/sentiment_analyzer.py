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
        
        if not text:
            raise ValueError("Text content is required")
            
        logger.info("Analyzing sentiment in text")
        
        # Prepare result structure
        result = {
            "processed_at": time.time(),
            "text_length": len(text)
        }
        
        # Analyze overall document sentiment
        doc_sentiment = self._analyze_sentiment(text)
        result["document_sentiment"] = doc_sentiment
        
        # Determine the overall sentiment label
        if doc_sentiment["compound"] >= 0.05:
            result["sentiment"] = "positive"
        elif doc_sentiment["compound"] <= -0.05:
            result["sentiment"] = "negative"
        else:
            result["sentiment"] = "neutral"
            
        # Analyze by sentence if requested
        if analyze_by_sentence:
            sentences = sent_tokenize(text)
            sentence_sentiments = []
            
            for sentence in sentences:
                sentiment = self._analyze_sentiment(sentence)
                
                # Determine sentiment label
                if sentiment["compound"] >= 0.05:
                    sentiment_label = "positive"
                elif sentiment["compound"] <= -0.05:
                    sentiment_label = "negative"
                else:
                    sentiment_label = "neutral"
                    
                sentence_sentiments.append({
                    "text": sentence,
                    "sentiment": sentiment_label,
                    "scores": sentiment
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