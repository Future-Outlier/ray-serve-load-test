# locustfile.py
"""
locust -f ./locust_example.py --host http://10.96.72.20:8000
"""
from locust import HttpUser, task, constant

class FruitAppUser(HttpUser):
    wait_time = constant(0)  # Each user has a constant wait time of 0
    
    def on_start(self):
        """Called when a user starts"""
        self.client.verify = False  # Disable SSL verification if needed
    
    @task
    def test_fruit_endpoint(self):
        """Test the main fruit endpoint"""
        response = self.client.get("/")
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
