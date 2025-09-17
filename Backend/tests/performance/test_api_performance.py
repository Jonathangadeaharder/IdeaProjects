"""Performance tests for API endpoints"""
import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from statistics import mean, median


class TestAPIPerformance:
    """Performance test suite for API endpoints"""
    
    @pytest.fixture
    async def authenticated_client(self, async_client):
        """Create authenticated client for performance tests"""
        # Register and login
        await async_client.post("/api/auth/register", json={"username": "perfuser", "password": "TestPass123"})
        login_resp = await async_client.post("/api/auth/login", json={"username": "perfuser", "password": "TestPass123"})
        token = login_resp.json()["token"]
        
        # Add auth header to client
        async_client.headers.update({"Authorization": f"Bearer {token}"})
        return async_client
    
    @pytest.mark.asyncio
    async def test_health_endpoint_performance(self, async_client):
        """Test health endpoint response time"""
        response_times = []
        
        # Perform multiple requests
        for _ in range(50):
            start_time = time.time()
            response = await async_client.get("/health")
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        # Analyze performance
        avg_time = mean(response_times)
        median_time = median(response_times)
        max_time = max(response_times)
        
        print(f"Health endpoint performance:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Median: {median_time:.3f}s")
        print(f"  Max: {max_time:.3f}s")
        
        # Assert performance requirements
        assert avg_time < 0.1, f"Average response time {avg_time:.3f}s exceeds 100ms"
        assert max_time < 0.5, f"Max response time {max_time:.3f}s exceeds 500ms"
    
    @pytest.mark.asyncio
    async def test_auth_endpoint_performance(self, async_client):
        """Test authentication endpoint performance"""
        login_times = []
        
        # Register a user first
        await async_client.post("/api/auth/register", json={"username": "speeduser", "password": "TestPass123"})
        
        # Perform multiple login requests
        for i in range(20):
            start_time = time.time()
            response = await async_client.post("/api/auth/login", json={"username": "speeduser", "password": "TestPass123"})
            end_time = time.time()
            
            assert response.status_code == 200
            login_times.append(end_time - start_time)
        
        # Analyze performance
        avg_time = mean(login_times)
        median_time = median(login_times)
        max_time = max(login_times)
        
        print(f"Login endpoint performance:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Median: {median_time:.3f}s")
        print(f"  Max: {max_time:.3f}s")
        
        # Assert performance requirements (auth can be slower due to bcrypt)
        assert avg_time < 1.0, f"Average login time {avg_time:.3f}s exceeds 1s"
        assert max_time < 2.0, f"Max login time {max_time:.3f}s exceeds 2s"
    
    @pytest.mark.asyncio
    async def test_vocabulary_stats_performance(self, authenticated_client):
        """Test vocabulary stats endpoint performance"""
        response_times = []
        
        # Perform multiple requests
        for _ in range(30):
            start_time = time.time()
            response = await authenticated_client.get("/api/vocabulary/library/stats")
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        # Analyze performance
        avg_time = mean(response_times)
        median_time = median(response_times)
        max_time = max(response_times)
        
        print(f"Vocabulary stats performance:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Median: {median_time:.3f}s")
        print(f"  Max: {max_time:.3f}s")
        
        # Assert performance requirements
        assert avg_time < 0.2, f"Average response time {avg_time:.3f}s exceeds 200ms"
        assert max_time < 1.0, f"Max response time {max_time:.3f}s exceeds 1s"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests_performance(self, async_client):
        """Test API performance under concurrent load"""
        # Register users for concurrent testing
        for i in range(10):
            await async_client.post("/api/auth/register", json={"username": f"concurrent{i}", "password": "TestPass123"})
        
        async def make_concurrent_request(user_id):
            """Make a concurrent request"""
            start_time = time.time()
            
            # Login
            login_resp = await async_client.post("/api/auth/login", json={"username": f"concurrent{user_id}", "password": "TestPass123"})
            assert login_resp.status_code == 200
            
            token = login_resp.json()["token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Make authenticated request
            response = await async_client.get("/api/vocabulary/library/stats", headers=headers)
            assert response.status_code == 200
            
            end_time = time.time()
            return end_time - start_time
        
        # Execute concurrent requests
        start_time = time.time()
        tasks = [make_concurrent_request(i) for i in range(10)]
        response_times = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Analyze performance
        avg_time = mean(response_times)
        max_time = max(response_times)
        
        print(f"Concurrent requests performance (10 users):")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Average per request: {avg_time:.3f}s")
        print(f"  Max per request: {max_time:.3f}s")
        print(f"  Requests per second: {10/total_time:.2f}")
        
        # Assert performance requirements
        assert total_time < 10.0, f"Total time {total_time:.3f}s for 10 concurrent requests exceeds 10s"
        assert avg_time < 2.0, f"Average request time {avg_time:.3f}s exceeds 2s under load"
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, authenticated_client):
        """Test that memory usage remains stable under repeated requests"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make many requests to test for memory leaks
        for i in range(100):
            response = await authenticated_client.get("/health")
            assert response.status_code == 200
            
            # Check memory every 20 requests
            if i % 20 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = current_memory - initial_memory
                
                print(f"Request {i}: Memory usage {current_memory:.1f}MB (+{memory_increase:.1f}MB)")
                
                # Assert memory doesn't grow excessively
                assert memory_increase < 50, f"Memory increased by {memory_increase:.1f}MB, possible leak"
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_increase = final_memory - initial_memory
        
        print(f"Final memory usage: {final_memory:.1f}MB (+{total_increase:.1f}MB)")
        assert total_increase < 100, f"Total memory increase {total_increase:.1f}MB exceeds threshold"
    
    @pytest.mark.asyncio
    async def test_database_query_performance(self, authenticated_client):
        """Test database query performance"""
        response_times = []
        
        # Test vocabulary search which involves database queries
        for _ in range(25):
            start_time = time.time()
            response = await authenticated_client.get("/api/vocabulary/search?q=test&level=A1")
            end_time = time.time()
            
            # Accept both 200 (found) and 404 (not found) as valid responses
            assert response.status_code in [200, 404]
            response_times.append(end_time - start_time)
        
        # Analyze performance
        avg_time = mean(response_times)
        median_time = median(response_times)
        max_time = max(response_times)
        
        print(f"Database query performance:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Median: {median_time:.3f}s")
        print(f"  Max: {max_time:.3f}s")
        
        # Assert performance requirements
        assert avg_time < 0.3, f"Average query time {avg_time:.3f}s exceeds 300ms"
        assert max_time < 1.0, f"Max query time {max_time:.3f}s exceeds 1s"
    
    @pytest.mark.asyncio
    async def test_error_handling_performance(self, async_client):
        """Test that error responses are also fast"""
        response_times = []
        
        # Test 404 errors
        for _ in range(30):
            start_time = time.time()
            response = await async_client.get("/api/nonexistent/endpoint")
            end_time = time.time()
            
            assert response.status_code == 404
            response_times.append(end_time - start_time)
        
        # Analyze performance
        avg_time = mean(response_times)
        max_time = max(response_times)
        
        print(f"Error response performance:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Max: {max_time:.3f}s")
        
        # Error responses should be even faster
        assert avg_time < 0.05, f"Average error response time {avg_time:.3f}s exceeds 50ms"
        assert max_time < 0.2, f"Max error response time {max_time:.3f}s exceeds 200ms"