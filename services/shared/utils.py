"""Shared utilities for all microservices"""
import os
import json
import logging
from typing import Optional, Dict, Any
import redis.asyncio as redis
from openai import AsyncOpenAI
import httpx
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceRegistry:
    """Service discovery and registry"""
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.services_key = "services:registry"
        
    async def register_service(self, service_name: str, host: str, port: int, health_endpoint: str = "/health"):
        """Register a service in the registry"""
        service_info = {
            "name": service_name,
            "host": host,
            "port": port,
            "health_endpoint": health_endpoint,
            "registered_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
        await self.redis.hset(self.services_key, service_name, json.dumps(service_info))
        logger.info(f"Service {service_name} registered at {host}:{port}")
        
    async def get_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get service information from registry"""
        service_data = await self.redis.hget(self.services_key, service_name)
        if service_data:
            return json.loads(service_data)
        return None
    
    async def get_service_url(self, service_name: str) -> Optional[str]:
        """Get the URL for a service"""
        service = await self.get_service(service_name)
        if service:
            return f"http://{service['host']}:{service['port']}"
        return None
    
    async def deregister_service(self, service_name: str):
        """Remove a service from registry"""
        await self.redis.hdel(self.services_key, service_name)
        logger.info(f"Service {service_name} deregistered")

class InterServiceClient:
    """Client for inter-service communication"""
    def __init__(self, service_registry: ServiceRegistry):
        self.registry = service_registry
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def call_service(
        self,
        service_name: str,
        endpoint: str,
        method: str = "POST",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Call another microservice"""
        service_url = await self.registry.get_service_url(service_name)
        if not service_url:
            raise ValueError(f"Service {service_name} not found in registry")
        
        url = f"{service_url}{endpoint}"
        
        try:
            if method == "GET":
                response = await self.client.get(url, params=params)
            elif method == "POST":
                response = await self.client.post(url, json=data)
            elif method == "PUT":
                response = await self.client.put(url, json=data)
            elif method == "DELETE":
                response = await self.client.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error calling service {service_name}: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

class EventPublisher:
    """Publish events to message broker (Redis Pub/Sub)"""
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    async def publish(self, channel: str, event: Dict[str, Any]):
        """Publish an event to a channel"""
        event_data = json.dumps(event)
        await self.redis.publish(channel, event_data)
        logger.info(f"Published event to {channel}: {event.get('event_type', 'unknown')}")

class EventSubscriber:
    """Subscribe to events from message broker"""
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.pubsub = self.redis.pubsub()
        
    async def subscribe(self, channels: list):
        """Subscribe to channels"""
        await self.pubsub.subscribe(*channels)
        logger.info(f"Subscribed to channels: {channels}")
        
    async def listen(self):
        """Listen for messages"""
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                yield data
    
    async def unsubscribe(self):
        """Unsubscribe from all channels"""
        await self.pubsub.unsubscribe()

class CacheManager:
    """Centralized cache management"""
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_ttl = 3600  # 1 hour
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        await self.redis.setex(key, ttl, json.dumps(value))
    
    async def delete(self, key: str):
        """Delete from cache"""
        await self.redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return await self.redis.exists(key) > 0

def get_openai_client() -> AsyncOpenAI:
    """Get OpenAI client instance"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")
    return AsyncOpenAI(api_key=api_key)

def get_redis_client(url: Optional[str] = None) -> redis.Redis:
    """Get Redis client instance"""
    redis_url = url or os.getenv("REDIS_URL", "redis://localhost:6379")
    return redis.from_url(redis_url, decode_responses=True)