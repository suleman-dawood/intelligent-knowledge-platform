#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Model trainer module for training and updating machine learning models.
"""

import logging
import asyncio
import time
import os
from typing import Dict, List, Any, Optional, Tuple
import json
import uuid
from datetime import datetime
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from pymongo import MongoClient

# Configure logging
logger = logging.getLogger(__name__)


class ModelTrainer:
    """Trainer for machine learning models used in the knowledge platform."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the model trainer.
        
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
        
        # Model types supported by the trainer
        self.model_types = {
            "sentiment": self._train_sentiment_model,
            "topic": self._train_topic_model,
            "relevance": self._train_relevance_model,
            "entity": self._train_entity_model
        }
        
        # Base path for model storage
        self.model_dir = config.get('models', {}).get('path', 'data/models')
        os.makedirs(self.model_dir, exist_ok=True)
        
        logger.info("Model trainer initialized")
    
    async def train(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Train or update a machine learning model.
        
        Args:
            task_data: Task data specifying training parameters
            
        Returns:
            Training results
        """
        model_type = task_data.get('model_type')
        training_data = task_data.get('training_data')
        model_id = task_data.get('model_id')  # Optional, for updating an existing model
        hyperparams = task_data.get('hyperparams', {})
        
        if not model_type or (not training_data and not model_id):
            raise ValueError("Model type and either training data or model ID are required")
            
        if model_type not in self.model_types:
            raise ValueError(f"Unsupported model type: {model_type}. Supported types: {', '.join(self.model_types.keys())}")
            
        logger.info(f"Training model of type {model_type}")
        
        # Connect to MongoDB
        self._connect()
        
        try:
            # Determine if we're training a new model or updating an existing one
            if model_id:
                # Load existing model
                existing_model = await self._load_model(model_id)
                
                if not existing_model:
                    raise ValueError(f"Model with ID {model_id} not found")
                    
                # Check model type consistency
                if existing_model.get('type') != model_type:
                    raise ValueError(f"Model type mismatch: requested {model_type}, found {existing_model.get('type')}")
                    
                # Get additional training data if not provided
                if not training_data:
                    # Use recent data since the model was last updated
                    last_updated = existing_model.get('updated_at', existing_model.get('created_at'))
                    training_data = await self._get_data_since(model_type, last_updated)
                    
                # Update the model
                model_info, evaluation = await self.model_types[model_type](
                    training_data, 
                    hyperparams, 
                    existing_model
                )
                
                # Update metadata
                model_info['id'] = model_id
                model_info['updated_at'] = datetime.now().isoformat()
                model_info['version'] += 1
                
                # Save the updated model
                await self._save_model(model_info)
                
                return {
                    "operation_id": str(uuid.uuid4()),
                    "timestamp": datetime.now().isoformat(),
                    "model_id": model_id,
                    "model_type": model_type,
                    "action": "update",
                    "data_points": len(training_data),
                    "evaluation": evaluation,
                    "version": model_info['version']
                }
                
            else:
                # Train a new model
                model_info, evaluation = await self.model_types[model_type](
                    training_data, 
                    hyperparams
                )
                
                # Generate a model ID and add metadata
                model_id = str(uuid.uuid4())
                model_info['id'] = model_id
                model_info['created_at'] = datetime.now().isoformat()
                model_info['version'] = 1
                
                # Save the new model
                await self._save_model(model_info)
                
                return {
                    "operation_id": str(uuid.uuid4()),
                    "timestamp": datetime.now().isoformat(),
                    "model_id": model_id,
                    "model_type": model_type,
                    "action": "create",
                    "data_points": len(training_data),
                    "evaluation": evaluation,
                    "version": 1
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
    
    async def _load_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Load a model by ID.
        
        Args:
            model_id: ID of the model to load
            
        Returns:
            Model information or None if not found
        """
        # Get model metadata from MongoDB
        model_meta = self.db.models.find_one({"id": model_id})
        
        if not model_meta:
            return None
            
        # Load the model file
        model_path = os.path.join(self.model_dir, f"{model_id}.pkl")
        
        if not os.path.exists(model_path):
            logger.warning(f"Model file not found: {model_path}")
            return model_meta
            
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
                
            model_meta['model'] = model_data
            return model_meta
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return None
    
    async def _save_model(self, model_info: Dict[str, Any]) -> bool:
        """Save a model.
        
        Args:
            model_info: Model information including the trained model
            
        Returns:
            True if saved successfully, False otherwise
        """
        model_id = model_info['id']
        model = model_info.pop('model', None)
        
        if not model:
            logger.error("No model to save")
            return False
            
        try:
            # Save model file
            model_path = os.path.join(self.model_dir, f"{model_id}.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
                
            # Save or update metadata in MongoDB
            self.db.models.update_one(
                {"id": model_id},
                {"$set": model_info},
                upsert=True
            )
            
            logger.info(f"Saved model {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    async def _get_data_since(self, model_type: str, timestamp: str) -> List[Dict[str, Any]]:
        """Get training data since a specific timestamp.
        
        Args:
            model_type: Type of model
            timestamp: Timestamp to filter data
            
        Returns:
            List of training data points
        """
        collection = self._get_collection_for_model(model_type)
        
        # Query for data newer than the timestamp
        query = {"timestamp": {"$gt": timestamp}}
        
        # Limit the result size to avoid memory issues
        max_results = 10000
        
        data = list(self.db[collection].find(query).limit(max_results))
        
        # Simulate async processing
        await asyncio.sleep(0.1)
        
        return data
    
    def _get_collection_for_model(self, model_type: str) -> str:
        """Get the MongoDB collection name for a model type.
        
        Args:
            model_type: Type of model
            
        Returns:
            Collection name
        """
        # Map model types to appropriate collections
        collections = {
            "sentiment": "feedback",
            "topic": "content",
            "relevance": "search_interactions",
            "entity": "entity_annotations"
        }
        
        return collections.get(model_type, model_type)
    
    async def _train_sentiment_model(self, training_data: List[Dict[str, Any]], 
                                  hyperparams: Dict[str, Any], 
                                  existing_model: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Train a sentiment analysis model.
        
        Args:
            training_data: Training data
            hyperparams: Hyperparameters for the model
            existing_model: Existing model information (for updates)
            
        Returns:
            Tuple of (model info, evaluation metrics)
        """
        # Extract features and labels
        texts = []
        labels = []
        
        for item in training_data:
            if 'content' in item and 'sentiment' in item:
                texts.append(item['content'])
                labels.append(item['sentiment'])
        
        if not texts:
            raise ValueError("No valid training data for sentiment model")
            
        # Convert labels to numerical values
        label_map = {"positive": 2, "neutral": 1, "negative": 0}
        y = np.array([label_map.get(label, 1) for label in labels])
        
        # Split into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(texts, y, test_size=0.2, random_state=42)
        
        # Set up the model pipeline
        clf_type = hyperparams.get('classifier', 'logistic_regression')
        
        if clf_type == 'random_forest':
            classifier = RandomForestClassifier(
                n_estimators=hyperparams.get('n_estimators', 100),
                max_depth=hyperparams.get('max_depth', 10),
                random_state=42
            )
        else:  # Default to logistic regression
            classifier = LogisticRegression(
                C=hyperparams.get('C', 1.0),
                max_iter=hyperparams.get('max_iter', 1000),
                random_state=42
            )
            
        pipeline = Pipeline([
            ('vectorizer', TfidfVectorizer(
                max_features=hyperparams.get('max_features', 5000),
                ngram_range=(1, hyperparams.get('ngram_max', 2))
            )),
            ('classifier', classifier)
        ])
        
        # Train the model
        pipeline.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = pipeline.predict(X_test)
        
        evaluation = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, average='weighted')),
            "recall": float(recall_score(y_test, y_pred, average='weighted')),
            "f1": float(f1_score(y_test, y_pred, average='weighted')),
            "samples": len(texts)
        }
        
        # Create model info
        model_info = {
            "type": "sentiment",
            "pipeline": pipeline,
            "label_map": label_map,
            "hyperparams": hyperparams,
            "model": pipeline
        }
        
        # Simulate longer processing time
        await asyncio.sleep(0.5)
        
        return model_info, evaluation
    
    async def _train_topic_model(self, training_data: List[Dict[str, Any]], 
                              hyperparams: Dict[str, Any], 
                              existing_model: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Train a topic classification model.
        
        Args:
            training_data: Training data
            hyperparams: Hyperparameters for the model
            existing_model: Existing model information (for updates)
            
        Returns:
            Tuple of (model info, evaluation metrics)
        """
        # Extract features and labels
        texts = []
        labels = []
        
        for item in training_data:
            if 'content' in item and 'topic' in item:
                texts.append(item['content'])
                labels.append(item['topic'])
        
        if not texts:
            raise ValueError("No valid training data for topic model")
            
        # Get unique labels and create a mapping
        unique_labels = list(set(labels))
        label_map = {label: i for i, label in enumerate(unique_labels)}
        reverse_map = {i: label for label, i in label_map.items()}
        
        # Convert labels to numerical values
        y = np.array([label_map[label] for label in labels])
        
        # Split into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(texts, y, test_size=0.2, random_state=42)
        
        # Set up the model pipeline
        clf_type = hyperparams.get('classifier', 'random_forest')
        
        if clf_type == 'random_forest':
            classifier = RandomForestClassifier(
                n_estimators=hyperparams.get('n_estimators', 100),
                max_depth=hyperparams.get('max_depth', 10),
                random_state=42
            )
        else:  # Default to logistic regression
            classifier = LogisticRegression(
                C=hyperparams.get('C', 1.0),
                max_iter=hyperparams.get('max_iter', 1000),
                random_state=42,
                multi_class='multinomial'
            )
            
        pipeline = Pipeline([
            ('vectorizer', TfidfVectorizer(
                max_features=hyperparams.get('max_features', 5000),
                ngram_range=(1, hyperparams.get('ngram_max', 2))
            )),
            ('classifier', classifier)
        ])
        
        # Train the model
        pipeline.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = pipeline.predict(X_test)
        
        evaluation = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, average='weighted')),
            "recall": float(recall_score(y_test, y_pred, average='weighted')),
            "f1": float(f1_score(y_test, y_pred, average='weighted')),
            "samples": len(texts),
            "classes": len(unique_labels)
        }
        
        # Create model info
        model_info = {
            "type": "topic",
            "label_map": label_map,
            "reverse_map": reverse_map,
            "hyperparams": hyperparams,
            "model": pipeline
        }
        
        # Simulate longer processing time
        await asyncio.sleep(0.5)
        
        return model_info, evaluation
    
    async def _train_relevance_model(self, training_data: List[Dict[str, Any]], 
                                  hyperparams: Dict[str, Any], 
                                  existing_model: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Train a relevance scoring model.
        
        Args:
            training_data: Training data
            hyperparams: Hyperparameters for the model
            existing_model: Existing model information (for updates)
            
        Returns:
            Tuple of (model info, evaluation metrics)
        """
        # Extract features and labels
        query_doc_pairs = []
        relevance_scores = []
        
        for item in training_data:
            if 'query' in item and 'document' in item and 'relevance' in item:
                # Combine query and document text as features
                query_doc_pairs.append(f"{item['query']} [SEP] {item['document']}")
                relevance_scores.append(float(item['relevance']))
        
        if not query_doc_pairs:
            raise ValueError("No valid training data for relevance model")
            
        # Convert to numpy array
        y = np.array(relevance_scores)
        
        # Split into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(query_doc_pairs, y, test_size=0.2, random_state=42)
        
        # Set up the model pipeline
        pipeline = Pipeline([
            ('vectorizer', TfidfVectorizer(
                max_features=hyperparams.get('max_features', 5000),
                ngram_range=(1, hyperparams.get('ngram_max', 2))
            )),
            ('regressor', RandomForestClassifier(
                n_estimators=hyperparams.get('n_estimators', 100),
                max_depth=hyperparams.get('max_depth', 10),
                random_state=42
            ))
        ])
        
        # Train the model
        pipeline.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = pipeline.predict(X_test)
        
        # Calculate Mean Squared Error
        mse = np.mean((y_test - y_pred) ** 2)
        
        evaluation = {
            "mse": float(mse),
            "rmse": float(np.sqrt(mse)),
            "samples": len(query_doc_pairs)
        }
        
        # Create model info
        model_info = {
            "type": "relevance",
            "hyperparams": hyperparams,
            "model": pipeline
        }
        
        # Simulate longer processing time
        await asyncio.sleep(0.5)
        
        return model_info, evaluation
    
    async def _train_entity_model(self, training_data: List[Dict[str, Any]], 
                               hyperparams: Dict[str, Any], 
                               existing_model: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Train an entity classification model.
        
        Args:
            training_data: Training data
            hyperparams: Hyperparameters for the model
            existing_model: Existing model information (for updates)
            
        Returns:
            Tuple of (model info, evaluation metrics)
        """
        # Extract features and labels
        entities = []
        entity_types = []
        
        for item in training_data:
            if 'entity' in item and 'type' in item:
                entities.append(item['entity'])
                entity_types.append(item['type'])
        
        if not entities:
            raise ValueError("No valid training data for entity model")
            
        # Get unique entity types and create a mapping
        unique_types = list(set(entity_types))
        type_map = {type_: i for i, type_ in enumerate(unique_types)}
        reverse_map = {i: type_ for type_, i in type_map.items()}
        
        # Convert labels to numerical values
        y = np.array([type_map[type_] for type_ in entity_types])
        
        # Split into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(entities, y, test_size=0.2, random_state=42)
        
        # Set up the model pipeline
        clf_type = hyperparams.get('classifier', 'random_forest')
        
        if clf_type == 'random_forest':
            classifier = RandomForestClassifier(
                n_estimators=hyperparams.get('n_estimators', 100),
                max_depth=hyperparams.get('max_depth', 10),
                random_state=42
            )
        else:  # Default to logistic regression
            classifier = LogisticRegression(
                C=hyperparams.get('C', 1.0),
                max_iter=hyperparams.get('max_iter', 1000),
                random_state=42,
                multi_class='multinomial'
            )
            
        pipeline = Pipeline([
            ('vectorizer', TfidfVectorizer(
                max_features=hyperparams.get('max_features', 5000),
                ngram_range=(1, hyperparams.get('ngram_max', 2))
            )),
            ('classifier', classifier)
        ])
        
        # Train the model
        pipeline.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = pipeline.predict(X_test)
        
        evaluation = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, average='weighted')),
            "recall": float(recall_score(y_test, y_pred, average='weighted')),
            "f1": float(f1_score(y_test, y_pred, average='weighted')),
            "samples": len(entities),
            "classes": len(unique_types)
        }
        
        # Create model info
        model_info = {
            "type": "entity",
            "type_map": type_map,
            "reverse_map": reverse_map,
            "hyperparams": hyperparams,
            "model": pipeline
        }
        
        # Simulate longer processing time
        await asyncio.sleep(0.5)
        
        return model_info, evaluation 