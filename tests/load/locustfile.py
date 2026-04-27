import random
import uuid
import logging
from locust import HttpUser, task, between, events

logger = logging.getLogger(__name__)

# SLA Thresholds in milliseconds
SLA_TARGETS = {
    "/chat/message": 5000,
    "/analysis/image": 3000,
    "/analysis/history": 500
}

@events.request.add_listener
def assert_sla(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    """Event hook to validate SLA targets for specific endpoints."""
    if exception:
        return

    # Normalize name to match SLA keys
    endpoint = name
    for key, threshold in SLA_TARGETS.items():
        if key in endpoint:
            if response_time > threshold:
                logger.warning(
                    f"SLA VIOLATION: {endpoint} took {response_time:.2f}ms "
                    f"(Target: < {threshold}ms)"
                )
            break

class HealthAPIUser(HttpUser):
    # Set the target API host URL
    host = "http://localhost:8000"
    
    # Wait between 1 and 3 seconds between tasks to simulate real user behavior
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a Locust user starts before any tasks are scheduled."""
        self.email = f"loadtest_{uuid.uuid4().hex[:8]}@example.com"
        self.password = "LoadTest123!"
        
        # 1. Register
        self.client.post("/api/v1/auth/register", json={
            "email": self.email,
            "password": self.password,
            "first_name": "Load",
            "last_name": "Tester"
        }, name="/api/v1/auth/register")
        
        # 2. Login to get JWT
        response = self.client.post("/api/v1/auth/login", data={
            "username": self.email,
            "password": self.password
        }, name="/api/v1/auth/login")
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {token}"}
        else:
            self.headers = {}
            logger.error(f"Failed to login user {self.email}")

    @task(3)
    def send_chat_message(self):
        """Most frequent task: Chatting with LLM"""
        questions = [
            "I have a headache, what should I do?",
            "What is a good diet for clear skin?",
            "How many calories are in an apple?",
            "Why are my eyes red after looking at the screen?"
        ]
        self.client.post(
            "/api/v1/chat/message", 
            headers=self.headers,
            json={"message": random.choice(questions)},
            name="/api/v1/chat/message"
        )

    @task(2)
    def analyze_image(self):
        """Image analysis requires heavier backend processing."""
        # Create a tiny dummy image
        dummy_jpeg = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\xff\xdb\x00C\x01\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x03\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02\w\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&\'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xfd\xfc\xa8\xa2\x8a(\x00\xff\xd9'
        files = {"file": ("test.jpg", dummy_jpeg, "image/jpeg")}
        data = {"analysis_type": random.choice(["skin", "eye", "food", "emotion"])}
        
        self.client.post(
            "/api/v1/analysis/image", 
            headers=self.headers,
            files=files,
            data=data,
            name="/api/v1/analysis/image"
        )

    @task(1)
    def get_history(self):
        """Database read operation, should be very fast."""
        self.client.get(
            "/api/v1/analysis/history?limit=10", 
            headers=self.headers,
            name="/api/v1/analysis/history"
        )
