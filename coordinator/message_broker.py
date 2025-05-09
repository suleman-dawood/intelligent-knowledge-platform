#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Message broker module for the Intelligent Knowledge Aggregation Platform.
Handles the communication between agents using RabbitMQ.
"""

import json
import logging
import asyncio
from typing import Dict, Any, Callable, Optional, List, Tuple
import aio_pika

logger = logging.getLogger(__name__)


class MessageBroker:
    """Handles communication between components using RabbitMQ."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the message broker.
        
        Args:
            config: RabbitMQ configuration
        """
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 5672)
        self.user = config.get('user', 'guest')
        self.password = config.get('password', 'guest')
        
        self.connection = None
        self.channel = None
        self.exchanges = {}
        self.queues = {}
        self.consumers = {}
        
        self._is_connected = False
        
        # Define standard queue and exchange names
        self.agent_queues = {
            'scraper': 'scraper_tasks',
            'processor': 'processor_tasks',
            'knowledge': 'knowledge_tasks',
            'learning': 'learning_tasks',
            'ui': 'ui_tasks'
        }
        
        self.system_exchange = 'system'
        
        logger.info("Message broker initialized")
    
    async def connect(self) -> None:
        """Connect to RabbitMQ."""
        if self._is_connected:
            return
            
        try:
            # Connect to RabbitMQ
            self.connection = await aio_pika.connect_robust(
                host=self.host,
                port=self.port,
                login=self.user,
                password=self.password
            )
            
            # Create channel
            self.channel = await self.connection.channel()
            
            # Set QoS
            await self.channel.set_qos(prefetch_count=10)
            
            # Declare system exchange
            self.exchanges[self.system_exchange] = await self.channel.declare_exchange(
                self.system_exchange,
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )
            
            # Declare standard queues
            for agent_type, queue_name in self.agent_queues.items():
                queue = await self.channel.declare_queue(
                    queue_name,
                    durable=True
                )
                self.queues[agent_type] = queue
            
            self._is_connected = True
            logger.info("Connected to RabbitMQ")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    async def close(self) -> None:
        """Close the connection to RabbitMQ."""
        if not self._is_connected:
            return
            
        try:
            # Cancel all consumers
            for consumer_tag in self.consumers:
                await self.channel.basic_cancel(consumer_tag)
            
            # Close the connection
            await self.connection.close()
            
            self._is_connected = False
            logger.info("Disconnected from RabbitMQ")
            
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")
    
    async def publish_task(self, agent_type: str, task_data: Dict[str, Any]) -> None:
        """Publish a task to the appropriate agent queue.
        
        Args:
            agent_type: Type of agent to send the task to
            task_data: Task data to send
        """
        if not self._is_connected:
            await self.connect()
            
        try:
            # Ensure agent type is valid
            if agent_type not in self.agent_queues:
                logger.error(f"Invalid agent type: {agent_type}")
                return
                
            queue_name = self.agent_queues[agent_type]
            
            # Create message
            message = aio_pika.Message(
                body=json.dumps(task_data).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            
            # Publish message
            await self.channel.default_exchange.publish(
                message, 
                routing_key=queue_name
            )
            
            logger.debug(f"Published task to {queue_name}")
            
        except Exception as e:
            logger.error(f"Error publishing task: {e}")
            raise
    
    async def publish_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Publish an event to the system exchange.
        
        Args:
            event_type: Type of event
            event_data: Event data
        """
        if not self._is_connected:
            await self.connect()
            
        try:
            # Create message
            message = aio_pika.Message(
                body=json.dumps(event_data).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            
            # Publish to system exchange
            await self.exchanges[self.system_exchange].publish(
                message,
                routing_key=event_type
            )
            
            logger.debug(f"Published event: {event_type}")
            
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            raise
    
    async def subscribe(
        self, 
        agent_type: str, 
        callback: Callable[[Dict[str, Any]], None]
    ) -> str:
        """Subscribe to tasks for a specific agent type.
        
        Args:
            agent_type: Type of agent to subscribe for
            callback: Function to call when a message is received
            
        Returns:
            Consumer tag
        """
        if not self._is_connected:
            await self.connect()
            
        try:
            # Ensure agent type is valid
            if agent_type not in self.agent_queues:
                logger.error(f"Invalid agent type: {agent_type}")
                return ""
                
            queue = self.queues[agent_type]
            
            # Define message handler
            async def on_message(message: aio_pika.IncomingMessage) -> None:
                async with message.process():
                    try:
                        # Parse message body
                        body = json.loads(message.body.decode())
                        
                        # Call the callback
                        await callback(body)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        # Requeue the message in case of error
                        await message.nack(requeue=True)
            
            # Start consuming
            consumer_tag = await queue.consume(on_message)
            self.consumers[consumer_tag] = agent_type
            
            logger.info(f"Subscribed to {agent_type} tasks")
            
            return consumer_tag
            
        except Exception as e:
            logger.error(f"Error subscribing to tasks: {e}")
            raise
    
    async def subscribe_to_events(
        self, 
        event_types: List[str], 
        callback: Callable[[str, Dict[str, Any]], None]
    ) -> str:
        """Subscribe to specific event types.
        
        Args:
            event_types: List of event types to subscribe to
            callback: Function to call when an event is received
            
        Returns:
            Consumer tag
        """
        if not self._is_connected:
            await self.connect()
            
        try:
            # Create a temporary exclusive queue for the subscriber
            queue = await self.channel.declare_queue(exclusive=True)
            
            # Bind to each event type
            for event_type in event_types:
                await queue.bind(
                    exchange=self.exchanges[self.system_exchange],
                    routing_key=event_type
                )
            
            # Define message handler
            async def on_message(message: aio_pika.IncomingMessage) -> None:
                async with message.process():
                    try:
                        # Parse message body
                        body = json.loads(message.body.decode())
                        
                        # Call the callback with the routing key (event type)
                        await callback(message.routing_key, body)
                    except Exception as e:
                        logger.error(f"Error processing event: {e}")
            
            # Start consuming
            consumer_tag = await queue.consume(on_message)
            self.consumers[consumer_tag] = "events"
            
            logger.info(f"Subscribed to events: {', '.join(event_types)}")
            
            return consumer_tag
            
        except Exception as e:
            logger.error(f"Error subscribing to events: {e}")
            raise
    
    async def unsubscribe(self, consumer_tag: str) -> None:
        """Unsubscribe from a queue or exchange.
        
        Args:
            consumer_tag: Consumer tag to cancel
        """
        if not self._is_connected or not consumer_tag:
            return
            
        try:
            await self.channel.basic_cancel(consumer_tag)
            if consumer_tag in self.consumers:
                del self.consumers[consumer_tag]
                
            logger.info(f"Unsubscribed consumer {consumer_tag}")
            
        except Exception as e:
            logger.error(f"Error unsubscribing consumer: {e}")
            raise 