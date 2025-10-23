import ray
from ray import serve
from starlette.requests import Request
import asyncio

# Initialize Ray cluster with 8 CPUs
# ray.init(num_cpus=8)

# serve.start()

@serve.deployment(
    num_replicas=8,
    max_ongoing_requests=5000,  # Maximum 5000 concurrent requests per replica
    ray_actor_options={"num_cpus": 1}
)
class SimpleDeployment:
    """Simple deployment that directly returns results"""
    
    def __init__(self):
        self.counter = 0
    
    async def __call__(self, request: Request):
        """Asynchronously process requests and return immediately"""
        self.counter += 1
        return {
            "status": "ok",
            "counter": self.counter,
            "message": "processed"
        }

# Deploy the application
app = SimpleDeployment.bind()
serve.run(app, route_prefix="/")

print("=" * 80)
print("Ray Serve is running!")
print("Visit http://localhost:8000/ to test")
print("Dashboard: http://localhost:8265")
print("=" * 80)

# Keep running
import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down...")
    serve.shutdown()
    ray.shutdown()
