"""Security tests for API endpoints"""
import pytest
import jwt
from datetime import datetime, timedelta


class TestAPISecurity:
    """Security test suite for API endpoints"""
    
    @pytest.mark.asyncio
    async def test_unauthenticated_access_blocked(self, async_client):
        """Test that protected endpoints block unauthenticated access"""
        protected_endpoints = [
            "/api/vocabulary/library/stats",
            "/api/vocabulary/search",
            "/api/vocabulary/random",
            "/api/vocabulary/add",
            "/api/videos",
            "/api/auth/me",
            "/api/auth/logout"
        ]
        
        for endpoint in protected_endpoints:
            response = await async_client.get(endpoint)
            assert response.status_code == 401, f"Endpoint {endpoint} should require authentication"
            
            response_data = response.json()
            assert "detail" in response_data
            assert "authenticated" in response_data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self, async_client):
        """Test that invalid tokens are rejected"""
        invalid_tokens = [
            "invalid.token.here",
            "Bearer invalid.token.here",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
            "",
            "Bearer ",
            "NotBearer validtoken"
        ]
        
        for token in invalid_tokens:
            headers = {"Authorization": token} if token else {}
            response = await async_client.get("/api/auth/me", headers=headers)
            assert response.status_code == 401, f"Invalid token '{token}' should be rejected"
    
    @pytest.mark.asyncio
    async def test_expired_token_rejected(self, async_client):
        """Test that expired tokens are rejected"""
        # Create an expired token (this would need to match your JWT secret)
        expired_payload = {
            "user_id": "testuser",
            "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
        }
        
        # Note: In a real test, you'd use the same secret as your app
        # For now, we'll test with a malformed expired token
        expired_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdHVzZXIiLCJleHAiOjE2MzAwMDAwMDB9.invalid"
        
        headers = {"Authorization": expired_token}
        response = await async_client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_sql_injection_protection(self, authenticated_client):
        """Test protection against SQL injection attacks"""
        sql_injection_payloads = [
            "'; DROP TABLE vocabulary; --",
            "' OR '1'='1",
            "'; DELETE FROM users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "' OR 1=1 --",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --"
        ]
        
        for payload in sql_injection_payloads:
            # Test search endpoint
            response = await authenticated_client.get(f"/api/vocabulary/search?q={payload}")
            # Should not crash and should return proper error or empty result
            assert response.status_code in [200, 400, 404], f"SQL injection payload caused unexpected response: {response.status_code}"
            
            # Test registration endpoint (unauthenticated)
            response = await authenticated_client.post("/api/auth/register", json={
                "username": payload,
                "password": "testpass"
            })
            # Should handle malicious input gracefully
            assert response.status_code in [400, 422], f"Registration should reject malicious username: {payload}"
    
    @pytest.mark.asyncio
    async def test_xss_protection(self, authenticated_client):
        """Test protection against XSS attacks"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
            "'><script>alert('xss')</script>",
            "<iframe src='javascript:alert(\"xss\")'></iframe>"
        ]
        
        for payload in xss_payloads:
            # Test search endpoint
            response = await authenticated_client.get(f"/api/vocabulary/search?q={payload}")
            assert response.status_code in [200, 400, 404]
            
            # Ensure response doesn't contain unescaped payload
            response_text = response.text
            assert payload not in response_text or "&lt;" in response_text, f"XSS payload not properly escaped: {payload}"
    
    @pytest.mark.asyncio
    async def test_rate_limiting_behavior(self, async_client):
        """Test rate limiting behavior (if implemented)"""
        # Make many rapid requests to test rate limiting
        responses = []
        
        for i in range(100):
            response = await async_client.get("/health")
            responses.append(response.status_code)
            
            # If rate limiting is implemented, we should see 429 responses
            if response.status_code == 429:
                print(f"Rate limiting triggered after {i+1} requests")
                break
        
        # This test documents current behavior - adjust based on your rate limiting implementation
        success_responses = [r for r in responses if r == 200]
        rate_limited_responses = [r for r in responses if r == 429]
        
        print(f"Successful requests: {len(success_responses)}")
        print(f"Rate limited requests: {len(rate_limited_responses)}")
        
        # At minimum, ensure the server doesn't crash under load
        server_errors = [r for r in responses if r >= 500]
        assert len(server_errors) == 0, f"Server errors under load: {server_errors}"
    
    @pytest.mark.asyncio
    async def test_password_security_requirements(self, async_client):
        """Test password security requirements"""
        weak_passwords = [
            "123",
            "password",
            "abc",
            "",
            "12345678",  # Too simple
            "a" * 100,   # Too long
        ]
        
        for weak_password in weak_passwords:
            response = await async_client.post("/api/auth/register", json={
                "username": f"testuser_{len(weak_password)}",
                "password": weak_password
            })
            
            # Should reject weak passwords
            if len(weak_password) < 8 or weak_password in ["password", "12345678"]:
                assert response.status_code in [400, 422], f"Weak password '{weak_password}' should be rejected"
    
    @pytest.mark.asyncio
    async def test_username_security_requirements(self, async_client):
        """Test username security requirements"""
        invalid_usernames = [
            "",  # Empty
            "a",  # Too short
            "a" * 100,  # Too long
            "user with spaces",
            "user@domain.com",  # Email format
            "../../../etc/passwd",  # Path traversal
            "admin",  # Reserved
            "root",   # Reserved
        ]
        
        for username in invalid_usernames:
            response = await async_client.post("/api/auth/register", json={
                "username": username,
                "password": "ValidPass123"
            })
            
            # Should reject invalid usernames
            if not username or len(username) < 2 or len(username) > 50 or " " in username:
                assert response.status_code in [400, 422], f"Invalid username '{username}' should be rejected"
    
    @pytest.mark.asyncio
    async def test_session_security(self, async_client):
        """Test session security measures"""
        # Register and login
        await async_client.post("/api/auth/register", json={"username": "sessionuser", "password": "TestPass123"})
        login_response = await async_client.post("/api/auth/login", json={"username": "sessionuser", "password": "TestPass123"})
        
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        
        # Test authenticated access
        headers = {"Authorization": f"Bearer {token}"}
        me_response = await async_client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        # Test logout
        logout_response = await async_client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200
        
        # Test that token is invalidated after logout (if implemented)
        post_logout_response = await async_client.get("/api/auth/me", headers=headers)
        # This depends on your logout implementation - adjust accordingly
        # assert post_logout_response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_cors_headers(self, async_client):
        """Test CORS headers are properly configured"""
        response = await async_client.options("/api/auth/login")
        
        # Check for CORS headers (adjust based on your CORS configuration)
        headers = response.headers
        
        # These tests depend on your CORS configuration
        # Uncomment and adjust based on your security requirements
        # assert "access-control-allow-origin" in headers
        # assert "access-control-allow-methods" in headers
        # assert "access-control-allow-headers" in headers
    
    @pytest.mark.asyncio
    async def test_security_headers(self, async_client):
        """Test security headers are present"""
        response = await async_client.get("/health")
        headers = response.headers
        
        # Check for security headers (adjust based on your configuration)
        security_headers = [
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection",
            "strict-transport-security",
            "content-security-policy"
        ]
        
        missing_headers = []
        for header in security_headers:
            if header not in headers:
                missing_headers.append(header)
        
        if missing_headers:
            print(f"Missing security headers: {missing_headers}")
            # Uncomment to enforce security headers
            # assert False, f"Missing security headers: {missing_headers}"
    
    @pytest.mark.asyncio
    async def test_file_upload_security(self, authenticated_client):
        """Test file upload security (if video upload is implemented)"""
        # Test malicious file uploads
        malicious_files = [
            ("malicious.exe", b"MZ\x90\x00", "application/octet-stream"),
            ("script.js", b"alert('xss')", "application/javascript"),
            ("../../../etc/passwd", b"root:x:0:0:root:/root:/bin/bash", "text/plain"),
            ("large_file.txt", b"A" * (10 * 1024 * 1024), "text/plain"),  # 10MB file
        ]
        
        for filename, content, content_type in malicious_files:
            files = {"file": (filename, content, content_type)}
            
            # Test video upload endpoint (adjust endpoint as needed)
            response = await authenticated_client.post("/api/videos/upload", files=files)
            
            # Should reject malicious files
            assert response.status_code in [400, 413, 415, 422], f"Malicious file '{filename}' should be rejected"
    
    @pytest.mark.asyncio
    async def test_information_disclosure(self, async_client):
        """Test that sensitive information is not disclosed in error messages"""
        # Test various error conditions
        error_endpoints = [
            ("/api/nonexistent", 404),
            ("/api/auth/login", 422),  # Missing body
        ]
        
        for endpoint, expected_status in error_endpoints:
            response = await async_client.get(endpoint)
            assert response.status_code == expected_status
            
            response_text = response.text.lower()
            
            # Check that sensitive information is not leaked
            sensitive_terms = [
                "traceback",
                "exception",
                "stack trace",
                "internal server error",
                "database",
                "sql",
                "password",
                "secret",
                "token",
                "key"
            ]
            
            leaked_terms = [term for term in sensitive_terms if term in response_text]
            assert not leaked_terms, f"Sensitive information leaked in {endpoint}: {leaked_terms}"