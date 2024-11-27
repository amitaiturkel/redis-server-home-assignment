import pytest
import requests
import time
from datetime import datetime, timedelta
import json
import redis
from unittest.mock import patch
import threading

# Test configuration
BASE_URL = 'http://localhost:3000'
REDIS_HOST = 'localhost'

@pytest.fixture
def redis_client():
    client = redis.StrictRedis(host=REDIS_HOST)
    # Clear relevant keys before each test
    client.delete('scheduled_messages')
    keys = client.keys('message:*')
    if keys:
        client.delete(*keys)
    keys = client.keys('lock:*')
    if keys:
        client.delete(*keys)
    return client

class TestEchoAtTimeAPI:
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        assert response.text == "Server is running!"

    def test_schedule_message_success(self, redis_client):
        """Test scheduling a message for the future"""
        future_time = datetime.now() + timedelta(seconds=10)
        payload = {
            "time": future_time.isoformat(),
            "message": "Test message"
        }
        
        response = requests.post(f"{BASE_URL}/echoAtTime", json=payload)
        assert response.status_code == 200
        
        # Verify message is stored in Redis
        messages = redis_client.zrange('scheduled_messages', 0, -1)
        assert len(messages) == 1
        
        message_id = messages[0].decode('utf-8')
        stored_message = redis_client.hgetall(f'message:{message_id}')
        assert stored_message[b'message'].decode('utf-8') == "Test message"

    def test_schedule_message_past_time(self):
        """Test scheduling a message for a past time"""
        past_time = datetime.now() - timedelta(minutes=5)
        payload = {
            "time": past_time.isoformat(),
            "message": "Past message"
        }
        
        response = requests.post(f"{BASE_URL}/echoAtTime", json=payload)
        assert response.status_code == 400
        assert "Scheduled time must be in the future" in response.text

    def test_schedule_multiple_messages(self, redis_client):
        """Test scheduling multiple messages"""
        base_time = datetime.now() + timedelta(seconds=5)
        messages = []
        
        # Schedule 5 messages
        for i in range(5):
            payload = {
                "time": (base_time + timedelta(seconds=i*5)).isoformat(),
                "message": f"Message {i}"
            }
            response = requests.post(f"{BASE_URL}/echoAtTime", json=payload)
            assert response.status_code == 200
            messages.append(payload)
        
        # Verify all messages are stored
        stored_count = redis_client.zcount('scheduled_messages', '-inf', '+inf')
        assert stored_count == 5

    def test_message_format_validation(self):
        """Test input validation"""
        invalid_payloads = [
            # Missing time
            {"message": "Test"},
            # Missing message
            {"time": datetime.now().isoformat()},
            # Invalid time format
            {"time": "invalid-time", "message": "Test"},
            # Empty message
            {"time": datetime.now().isoformat(), "message": ""},
            # None values
            {"time": None, "message": None}
        ]
        
        for payload in invalid_payloads:
            response = requests.post(f"{BASE_URL}/echoAtTime", json=payload)
            assert response.status_code in [400, 422,], f"Payload {payload} should be rejected"

    @pytest.mark.slow
    def test_message_execution(self, redis_client):
        """Test that messages are actually executed at the scheduled time"""
        # Schedule a message for 5 seconds from now
        future_time = datetime.now() + timedelta(seconds=5)
        payload = {
            "time": future_time.isoformat(),
            "message": "Execution test message"
        }
        
        response = requests.post(f"{BASE_URL}/echoAtTime", json=payload)
        assert response.status_code == 200
        
        # Wait for 6 seconds to ensure message is processed
        time.sleep(6)
        
        # Verify message was removed from Redis
        messages = redis_client.zrange('scheduled_messages', 0, -1)
        assert len(messages) == 0

    def test_concurrent_message_scheduling(self, redis_client):
        """Test concurrent message scheduling"""
        def schedule_message(i):
            payload = {
                "time": (datetime.now() + timedelta(seconds=5)).isoformat(),
                "message": f"Concurrent message {i}"
            }
            return requests.post(f"{BASE_URL}/echoAtTime", json=payload)
        
        # Create and start threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=lambda: threads.append(schedule_message(i)))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all messages were stored
        stored_count = redis_client.zcount('scheduled_messages', '-inf', '+inf')
        assert stored_count == 10

    def test_server_restart_recovery(self, redis_client):
        """Test message persistence across server restarts doesnt work"""
        # Schedule messages
        future_time = datetime.now() + timedelta(minutes=5)
        payload = {
            "time": future_time.isoformat(),
            "message": "Persistence test message"
        }
        
        response = requests.post(f"{BASE_URL}/echoAtTime", json=payload)
        assert response.status_code == 200
        
        # Verify message exists in Redis before restart
        messages_before = redis_client.zrange('scheduled_messages', 0, -1)
        assert len(messages_before) == 1
        
        # Simulate server restart (would need to be implemented in actual test environment)
        # Here we're just verifying the data persists in Redis
        
        messages_after = redis_client.zrange('scheduled_messages', 0, -1)
        assert len(messages_after) == 1
        assert messages_after == messages_before

if __name__ == '__main__':
    pytest.main(['-v', __file__])
