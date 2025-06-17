#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Feedback analyzer module for analyzing user feedback and interactions.
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional
import json
import uuid
from datetime import datetime
from pymongo import MongoClient

# Configure logging
logger = logging.getLogger(__name__)


class FeedbackAnalyzer:
    """Analyzer for user feedback and interactions."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the feedback analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # MongoDB connection settings
        self.mongo_uri = config.get('databases', {}).get('mongodb', {}).get('uri', 'mongodb://localhost:27017')
        self.mongo_db = config.get('databases', {}).get('mongodb', {}).get('db', 'knowledge_platform')
        
        # Initialize MongoDB client
        self.client = None
        self.db = None
        
        # Feedback types
        self.feedback_types = ["rating", "like", "dislike", "correction", "addition", "comment"]
        
        logger.info("Feedback analyzer initialized")
    
    async def analyze(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user feedback and interactions.
        
        Args:
            task_data: Task data specifying feedback to analyze
            
        Returns:
            Analysis results
        """
        feedback_data = task_data.get('feedback_data')
        feedback_type = task_data.get('feedback_type')
        time_range = task_data.get('time_range', {})  # Start and end timestamps
        user_id = task_data.get('user_id')  # Optional filter by user
        content_id = task_data.get('content_id')  # Optional filter by content
        
        if not feedback_data and not (feedback_type and (time_range or user_id or content_id)):
            raise ValueError("No feedback data or filter criteria provided")
            
        logger.info(f"Analyzing feedback of type {feedback_type or 'all'}")
        
        # Connect to MongoDB
        self._connect()
        
        try:
            # Process feedback based on input type
            if feedback_data:
                # Analyze specific feedback data
                analysis = self._analyze_feedback_data(feedback_data)
                
                # Store the feedback in the database
                await self._store_feedback(feedback_data)
                
            else:
                # Analyze feedback based on filter criteria
                feedback_items = await self._get_feedback(
                    feedback_type, time_range, user_id, content_id
                )
                
                # Analyze the retrieved feedback
                analysis = self._analyze_feedback_data(feedback_items)
            
            # Generate insights from the analysis
            insights = self._generate_insights(analysis)
            
            # Determine actions based on insights
            recommended_actions = self._recommend_actions(insights)
            
            return {
                "operation_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "feedback_type": feedback_type,
                "feedback_count": analysis["feedback_count"],
                "analysis": analysis,
                "insights": insights,
                "recommended_actions": recommended_actions
            }
            
        finally:
            # Close the MongoDB connection
            self._close()
    
    def _connect(self) -> None:
        """Connect to MongoDB."""
        if self.client is None:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.mongo_db]
            logger.info("Connected to MongoDB")
    
    def _close(self) -> None:
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
    
    async def _store_feedback(self, feedback_data: Any) -> str:
        """Store feedback in the database.
        
        Args:
            feedback_data: Feedback data to store
            
        Returns:
            ID of the stored feedback
        """
        # Ensure we have a list of feedback items
        if not isinstance(feedback_data, list):
            feedback_data = [feedback_data]
            
        # Insert feedback items
        feedback_ids = []
        for item in feedback_data:
            # Add metadata
            if 'timestamp' not in item:
                item['timestamp'] = datetime.now().isoformat()
                
            if 'id' not in item:
                item['id'] = str(uuid.uuid4())
                
            # Insert into MongoDB
            try:
                self.db.feedback.insert_one(item)
                feedback_ids.append(item['id'])
                logger.debug(f"Stored feedback with ID {item['id']}")
            except Exception as e:
                logger.error(f"Error storing feedback: {e}")
                
        return feedback_ids
    
    async def _get_feedback(self, feedback_type: Optional[str], time_range: Dict[str, Any], 
                          user_id: Optional[str], content_id: Optional[str]) -> List[Dict[str, Any]]:
        """Get feedback from the database based on filter criteria.
        
        Args:
            feedback_type: Type of feedback to filter by
            time_range: Time range to filter by
            user_id: User ID to filter by
            content_id: Content ID to filter by
            
        Returns:
            List of feedback items
        """
        # Build query based on filter criteria
        query = {}
        
        if feedback_type:
            query['type'] = feedback_type
            
        if user_id:
            query['user_id'] = user_id
            
        if content_id:
            query['content_id'] = content_id
            
        if time_range:
            time_query = {}
            if 'start' in time_range:
                time_query['$gte'] = time_range['start']
            if 'end' in time_range:
                time_query['$lte'] = time_range['end']
                
            if time_query:
                query['timestamp'] = time_query
                
        # Query the database
        feedback_items = list(self.db.feedback.find(query))
        
        # Simulate async processing
        await asyncio.sleep(0.1)
        
        return feedback_items
    
    def _analyze_feedback_data(self, feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze feedback data.
        
        Args:
            feedback_data: List of feedback items to analyze
            
        Returns:
            Analysis results
        """
        # Initialize analysis structure
        analysis = {
            "feedback_count": len(feedback_data),
            "feedback_by_type": {},
            "sentiment_distribution": {
                "positive": 0,
                "neutral": 0,
                "negative": 0
            },
            "rating_distribution": {},
            "top_topics": {},
            "time_analysis": {
                "hourly": {},
                "daily": {},
                "weekly": {}
            }
        }
        
        # Process each feedback item
        for item in feedback_data:
            # Count by type
            feedback_type = item.get('type')
            if feedback_type:
                analysis["feedback_by_type"][feedback_type] = analysis["feedback_by_type"].get(feedback_type, 0) + 1
            
            # Analyze sentiment
            sentiment = self._determine_sentiment(item)
            if sentiment:
                analysis["sentiment_distribution"][sentiment] = analysis["sentiment_distribution"].get(sentiment, 0) + 1
                
            # Process ratings
            if feedback_type == 'rating' and 'value' in item:
                rating = item['value']
                analysis["rating_distribution"][rating] = analysis["rating_distribution"].get(rating, 0) + 1
                
            # Extract topics
            topics = self._extract_topics(item)
            for topic in topics:
                analysis["top_topics"][topic] = analysis["top_topics"].get(topic, 0) + 1
                
            # Analyze by time
            if 'timestamp' in item:
                try:
                    timestamp = datetime.fromisoformat(item['timestamp'])
                    
                    # Hourly analysis
                    hour = timestamp.hour
                    analysis["time_analysis"]["hourly"][hour] = analysis["time_analysis"]["hourly"].get(hour, 0) + 1
                    
                    # Daily analysis
                    day = timestamp.weekday()
                    analysis["time_analysis"]["daily"][day] = analysis["time_analysis"]["daily"].get(day, 0) + 1
                    
                    # Weekly analysis
                    week = timestamp.isocalendar()[1]
                    analysis["time_analysis"]["weekly"][week] = analysis["time_analysis"]["weekly"].get(week, 0) + 1
                    
                except (ValueError, TypeError):
                    # Skip time analysis if timestamp is invalid
                    pass
        
        # Sort top topics
        analysis["top_topics"] = dict(sorted(analysis["top_topics"].items(), key=lambda x: x[1], reverse=True)[:10])
        
        return analysis
    
    def _determine_sentiment(self, feedback_item: Dict[str, Any]) -> Optional[str]:
        """Determine sentiment of a feedback item.
        
        Args:
            feedback_item: Feedback item to analyze
            
        Returns:
            Sentiment category (positive, neutral, negative)
        """
        # Check if sentiment is explicitly provided
        if 'sentiment' in feedback_item:
            return feedback_item['sentiment']
            
        # Infer from feedback type and value
        feedback_type = feedback_item.get('type')
        
        if feedback_type == 'rating':
            rating = feedback_item.get('value')
            if rating is not None:
                if rating > 3:  # Assuming 5-point scale
                    return "positive"
                elif rating < 3:
                    return "negative"
                else:
                    return "neutral"
                    
        elif feedback_type == 'like':
            return "positive"
            
        elif feedback_type == 'dislike':
            return "negative"
            
        # For other types, check for sentiment indicators in the content
        if 'content' in feedback_item:
            content = feedback_item['content']
            
            # Simple keyword-based sentiment analysis
            # In a real implementation, this would use more sophisticated methods
            positive_words = ['good', 'great', 'excellent', 'helpful', 'useful', 'amazing', 'love']
            negative_words = ['bad', 'poor', 'terrible', 'unhelpful', 'useless', 'awful', 'hate']
            
            content_lower = content.lower()
            positive_count = sum(1 for word in positive_words if word in content_lower)
            negative_count = sum(1 for word in negative_words if word in content_lower)
            
            if positive_count > negative_count:
                return "positive"
            elif negative_count > positive_count:
                return "negative"
            else:
                return "neutral"
                
        return None
    
    def _extract_topics(self, feedback_item: Dict[str, Any]) -> List[str]:
        """Extract topics from a feedback item.
        
        Args:
            feedback_item: Feedback item to analyze
            
        Returns:
            List of topics
        """
        topics = []
        
        # Check if topics are explicitly provided
        if 'topics' in feedback_item:
            return feedback_item['topics']
            
        # Extract from content
        if 'content' in feedback_item:
            content = feedback_item['content']
            
            # Simple keyword-based topic extraction
            # In a real implementation, this would use more sophisticated methods
            topic_keywords = {
                "interface": ["ui", "interface", "design", "layout", "button", "menu"],
                "performance": ["speed", "fast", "slow", "performance", "loading"],
                "accuracy": ["accurate", "correct", "wrong", "accuracy", "error"],
                "content": ["information", "content", "article", "text", "data"],
                "search": ["search", "find", "query", "results"],
                "recommendations": ["recommend", "suggestion", "similar"]
            }
            
            content_lower = content.lower()
            for topic, keywords in topic_keywords.items():
                if any(keyword in content_lower for keyword in keywords):
                    topics.append(topic)
                    
        return topics
    
    def _generate_insights(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights from the analysis.
        
        Args:
            analysis: Analysis results
            
        Returns:
            List of insights
        """
        insights = []
        
        # Calculate overall sentiment
        sentiment_dist = analysis["sentiment_distribution"]
        total_sentiment = sum(sentiment_dist.values())
        
        if total_sentiment > 0:
            positive_ratio = sentiment_dist.get("positive", 0) / total_sentiment
            negative_ratio = sentiment_dist.get("negative", 0) / total_sentiment
            
            if positive_ratio > 0.7:
                insights.append({
                    "type": "sentiment",
                    "insight": "Overall sentiment is very positive",
                    "value": positive_ratio,
                    "importance": "high"
                })
            elif negative_ratio > 0.7:
                insights.append({
                    "type": "sentiment",
                    "insight": "Overall sentiment is very negative",
                    "value": negative_ratio,
                    "importance": "high"
                })
                
        # Analyze ratings
        rating_dist = analysis["rating_distribution"]
        if rating_dist:
            # Calculate average rating
            total_ratings = sum(rating_dist.values())
            rating_sum = sum(rating * count for rating, count in rating_dist.items())
            avg_rating = rating_sum / total_ratings if total_ratings > 0 else 0
            
            insights.append({
                "type": "rating",
                "insight": f"Average rating is {avg_rating:.1f} out of 5",
                "value": avg_rating,
                "importance": "medium"
            })
            
        # Identify prominent topics
        top_topics = analysis["top_topics"]
        if top_topics:
            top_topic = max(top_topics.items(), key=lambda x: x[1])
            
            insights.append({
                "type": "topic",
                "insight": f"Most discussed topic is '{top_topic[0]}'",
                "value": top_topic[1],
                "importance": "medium"
            })
            
        # Analyze time patterns
        hourly = analysis["time_analysis"]["hourly"]
        if hourly:
            peak_hour = max(hourly.items(), key=lambda x: x[1])
            
            insights.append({
                "type": "time",
                "insight": f"Peak interaction occurs at hour {peak_hour[0]}",
                "value": peak_hour[1],
                "importance": "low"
            })
            
        return insights
    
    def recommend_actions(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Recommend actions based on insights."""
        actions = []
        
        for insight in insights:
            try:
                # Validate required fields
                insight_type = insight.get("type")
                insight_text = insight.get("insight", "")
                importance = insight.get("importance", "low")
                
                if not insight_type:
                    continue
                    
                # Sentiment analysis
                if (insight_type == "sentiment" and 
                    importance == "high" and 
                    any(neg_word in insight_text.lower() for neg_word in ["negative", "poor", "bad"])):
                    actions.append({
                        "action": "investigate_negative_feedback",
                        "description": "Investigate causes of negative feedback",
                        "priority": "high"
                    })
                    
                # Rating analysis
                elif insight_type == "rating":
                    rating_value = insight.get("value")
                    if rating_value is not None and rating_value < 3.0:
                        actions.append({
                            "action": "improve_content_quality", 
                            "description": "Review and improve content quality",
                            "priority": "high"
                        })
                        
                # Topic analysis - safer extraction
                elif insight_type == "topic":
                    # Extract topic name more safely
                    topic_name = self._extract_topic_name(insight_text)
                    actions.append({
                        "action": "enhance_topic_coverage",
                        "description": f"Enhance coverage of topic: {topic_name}",
                        "priority": "medium"
                    })
                    
                # Time-based analysis
                elif insight_type == "time":
                    actions.append({
                        "action": "optimize_availability",
                        "description": "Optimize system availability during peak hours", 
                        "priority": "low"
                    })
                    
            except Exception as e:
                # Log error but continue processing other insights
                print(f"Error processing insight: {e}")
                continue
                
        return actions

    def _extract_topic_name(self, insight_text: str) -> str:
        """Safely extract topic name from insight text."""
        # Try multiple extraction methods
        if "'" in insight_text:
            parts = insight_text.split("'")
            if len(parts) >= 2:
                return parts[1]
        
        # Fallback to taking last word or returning generic
        words = insight_text.split()
        return words[-1] if words else "unknown topic"