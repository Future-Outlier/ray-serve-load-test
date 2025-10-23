#!/usr/bin/env python3
"""
Simplified extreme stress test
Fixed aiohttp parameter issues
"""

import asyncio
import aiohttp
import time

async def simple_extreme_test():
    """Simplified extreme stress test"""
    url = "http://localhost:8000/"
    
    print("🚀 Simplified Extreme Stress Test")
    print("Configuration: 8 replicas × 5000 max_ongoing_requests")
    print("=" * 60)
    
    # Test configurations
    test_configs = [
        {"rps": 800, "duration": 15, "name": "Test 800 RPS"},
        {"rps": 1200, "duration": 20, "name": "Test 1200 RPS"},
        {"rps": 1600, "duration": 20, "name": "Test 1600 RPS"},
    ]

    for config in test_configs:
        print(f"\n📊 {config['name']}")
        print("-" * 40)
        
        await run_simple_test(url, config['rps'], config['duration'])
        
        print("⏳ Waiting 3 seconds...")
        await asyncio.sleep(3)

async def run_simple_test(url: str, target_rps: int, duration: int):
    """Run simplified test"""
    # Simplified connector configuration
    connector = aiohttp.TCPConnector(
        limit=target_rps * 2,
        limit_per_host=target_rps * 2,
        ttl_dns_cache=300
    )
    
    async with aiohttp.ClientSession(connector=connector) as session:
        start_time = time.time()
        total_requests = 0
        successful_requests = 0
        latencies = []

        # Batch control
        batch_interval = 0.05  # 50ms
        batch_size = max(1, int(target_rps * batch_interval))
        
        print(f"📈 Batch size: {batch_size}, interval: {batch_interval}s")
        
        while (time.time() - start_time) < duration:
            batch_start = time.time()
            
            # Send a batch of requests
            tasks = []
            for i in range(batch_size):
                task = send_request(session, url)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Collect statistics
            for result in results:
                total_requests += 1
                if isinstance(result, dict) and result.get('success'):
                    successful_requests += 1
                    latencies.append(result.get('latency_ms', 0))
            
            # Rate control
            elapsed = time.time() - batch_start
            sleep_time = max(0, batch_interval - elapsed)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            
            # Display progress
            current_time = time.time() - start_time
            current_rps = total_requests / current_time if current_time > 0 else 0
            success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
            
            if total_requests % (target_rps // 2) == 0:
                print(f"  ⏱️  {current_time:.1f}s | Requests: {total_requests} | "
                      f"RPS: {current_rps:.1f} | Success rate: {success_rate:.1f}%")
        
        # Calculate results
        actual_duration = time.time() - start_time
        actual_rps = total_requests / actual_duration
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        print(f"\n📋 Results:")
        print(f"  ✅ Total requests: {total_requests}")
        print(f"  ✅ Successful: {successful_requests}")
        print(f"  ✅ Success rate: {success_rate:.2f}%")
        print(f"  ✅ Actual RPS: {actual_rps:.2f}")
        print(f"  ✅ Target achievement: {actual_rps/target_rps*100:.2f}%")
        
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)
            min_latency = min(latencies)
            
            sorted_latencies = sorted(latencies)
            p50_latency = sorted_latencies[len(sorted_latencies)//2]
            p95_latency = sorted_latencies[int(len(sorted_latencies)*0.95)]
            
            print(f"  ⏱️  Average latency: {avg_latency:.2f}ms")
            print(f"  ⏱️  P50 latency: {p50_latency:.2f}ms")
            print(f"  ⏱️  P95 latency: {p95_latency:.2f}ms")
            print(f"  ⏱️  Min latency: {min_latency:.2f}ms")
            print(f"  ⏱️  Max latency: {max_latency:.2f}ms")

async def send_request(session: aiohttp.ClientSession, url: str):
    """Send request"""
    start_time = time.time()
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=2)) as response:
            data = await response.json()
            latency = (time.time() - start_time) * 1000
            return {
                "success": True,
                "status_code": response.status,
                "latency_ms": latency,
                "data": data
            }
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        return {
            "success": False,
            "error": str(e),
            "latency_ms": latency
        }

if __name__ == "__main__":
    print("🎯 Simplified Extreme Stress Test Tool")
    print("Goal: Test performance at 800-1600 RPS")
    print()
    
    try:
        asyncio.run(simple_extreme_test())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
    
    print("\n🏁 Test completed!")
