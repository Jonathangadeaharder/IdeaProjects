"""Contract tests for vocabulary endpoints.

These tests verify that the vocabulary API contract is maintained:
- Request/response schemas match expectations
- HTTP status codes are correct
- Required fields are present
- Data types are correct
"""
import pytest
from unittest.mock import patch, Mock
from api.models.vocabulary import (
    VocabularyWord, MarkKnownRequest, VocabularyLibraryWord,
    VocabularyLevel, BulkMarkRequest, VocabularyStats
)


@pytest.mark.asyncio
class TestVocabularyContract:
    """Contract tests for vocabulary API endpoints."""

    def setup_authenticated_client(self, client):
        """Helper to create an authenticated client."""
        # Register and login
        client.post("/auth/register", json={
            "username": "vocabtest",
            "password": "SecurePass123!"
        })
        
        login_response = client.post("/auth/login", json={
            "username": "vocabtest",
            "password": "SecurePass123!"
        })
        token = login_response.json()["token"]
        return {"Authorization": f"Bearer {token}"}

    def test_get_blocking_words_endpoint_contract(self, client):
        """Test /vocabulary/blocking-words endpoint contract."""
        headers = self.setup_authenticated_client(client)
        
        with patch('os.path.exists', return_value=True):
            response = client.get(
                "/vocabulary/blocking-words",
                params={"video_path": "test_series/S01E01.mp4"},
                headers=headers
            )
            
            # Contract assertions
            assert response.status_code in [200, 404]  # OK or video not found
            
            if response.status_code == 200:
                data = response.json()
                # Should return a list of vocabulary words
                assert isinstance(data, list)
                
                # If words exist, verify structure
                if data:
                    word = data[0]
                    # Verify response structure matches VocabularyWord model
                    assert "word" in word
                    assert "translation" in word
                    assert "difficulty_level" in word
                    assert "frequency" in word
                    assert "context" in word
                    
                    # Verify data types
                    assert isinstance(word["word"], str)
                    assert isinstance(word["translation"], str)
                    assert isinstance(word["difficulty_level"], str)
                    assert isinstance(word["frequency"], int)
                    assert isinstance(word["context"], str)

    def test_get_blocking_words_validation_contract(self, client):
        """Test blocking words endpoint validation contract."""
        headers = self.setup_authenticated_client(client)
        
        # Test without video_path parameter
        response = client.get("/vocabulary/blocking-words", headers=headers)
        assert response.status_code == 422
        
        # Test with invalid video_path
        response = client.get(
            "/vocabulary/blocking-words",
            params={"video_path": ""},
            headers=headers
        )
        assert response.status_code == 422

    def test_get_blocking_words_with_segments_contract(self, client):
        """Test blocking words with segment parameters contract."""
        headers = self.setup_authenticated_client(client)
        
        with patch('os.path.exists', return_value=True):
            response = client.get(
                "/vocabulary/blocking-words",
                params={
                    "video_path": "test_series/S01E01.mp4",
                    "segment_start": 10,
                    "segment_duration": 30
                },
                headers=headers
            )
            
            # Contract assertions
            assert response.status_code in [200, 404]
            
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, list)

    def test_mark_word_known_endpoint_contract(self, client):
        """Test /vocabulary/mark-known endpoint contract."""
        headers = self.setup_authenticated_client(client)
        
        payload = {
            "word": "example",
            "known": True
        }
        
        response = client.post("/vocabulary/mark-known", json=payload, headers=headers)
        
        # Contract assertions
        assert response.status_code == 200
        data = response.json()
        
        # Should return success response
        assert isinstance(data, dict)
        # Common success response patterns
        assert "message" in data or "success" in data or "status" in data

    def test_mark_word_known_validation_contract(self, client):
        """Test mark word known validation contract."""
        headers = self.setup_authenticated_client(client)
        
        # Test without word
        response = client.post("/vocabulary/mark-known", json={"known": True}, headers=headers)
        assert response.status_code == 422
        
        # Test without known flag
        response = client.post("/vocabulary/mark-known", json={"word": "test"}, headers=headers)
        assert response.status_code == 422
        
        # Test with invalid word (empty string)
        response = client.post("/vocabulary/mark-known", json={
            "word": "",
            "known": True
        }, headers=headers)
        assert response.status_code == 422
        
        # Test with invalid word (too long)
        response = client.post("/vocabulary/mark-known", json={
            "word": "a" * 101,  # Assuming max length is 100
            "known": True
        }, headers=headers)
        assert response.status_code == 422

    def test_preload_vocabulary_endpoint_contract(self, client):
        """Test /vocabulary/preload endpoint contract."""
        headers = self.setup_authenticated_client(client)
        
        with patch('core.database.get_async_session'):
            response = client.post("/vocabulary/preload", headers=headers)
            
            # Contract assertions
            assert response.status_code == 200
            data = response.json()
            
            # Should return success response
            assert isinstance(data, dict)

    def test_get_vocabulary_stats_endpoint_contract(self, client):
        """Test /vocabulary/library/stats endpoint contract."""
        headers = self.setup_authenticated_client(client)
        
        with patch('core.database.get_async_session'):
            response = client.get("/vocabulary/library/stats", headers=headers)
            
            # Contract assertions
            assert response.status_code == 200
            data = response.json()
            
            # Should return vocabulary stats structure
            assert isinstance(data, dict)
            # Common stats fields
            expected_fields = ["total_words", "known_words", "learning_words", "levels"]
            # At least some stats fields should be present
            assert any(field in data for field in expected_fields)

    def test_get_vocabulary_level_endpoint_contract(self, client):
        """Test /vocabulary/library/{level} endpoint contract."""
        headers = self.setup_authenticated_client(client)
        
        with patch('core.database.get_async_session'):
            response = client.get("/vocabulary/library/A1", headers=headers)
            
            # Contract assertions
            assert response.status_code in [200, 404]  # OK or level not found
            
            if response.status_code == 200:
                data = response.json()
                # Should return a list of vocabulary level words
                assert isinstance(data, list)
                
                # If words exist, verify structure
                if data:
                    word = data[0]
                    # Verify response structure matches VocabularyLibraryWord model
                    assert "word" in word
                    assert "translation" in word
                    assert "difficulty_level" in word
                    assert "frequency" in word
                    assert "known" in word
                    
                    # Verify data types
                    assert isinstance(word["word"], str)
                    assert isinstance(word["translation"], str)
                    assert isinstance(word["difficulty_level"], str)
                    assert isinstance(word["frequency"], int)
                    assert isinstance(word["known"], bool)

    def test_get_vocabulary_level_validation_contract(self, client):
        """Test vocabulary level endpoint validation contract."""
        headers = self.setup_authenticated_client(client)
        
        # Test with invalid level
        response = client.get("/vocabulary/library/INVALID", headers=headers)
        assert response.status_code in [400, 404, 422]
        
        # Test with empty level
        response = client.get("/vocabulary/library/", headers=headers)
        assert response.status_code == 404  # Should be treated as missing path

    def test_bulk_mark_level_known_endpoint_contract(self, client):
        """Test /vocabulary/library/bulk-mark endpoint contract."""
        headers = self.setup_authenticated_client(client)
        
        payload = {
            "level": "A1",
            "known": True
        }
        
        with patch('core.database.get_async_session'):
            response = client.post("/vocabulary/library/bulk-mark", json=payload, headers=headers)
            
            # Contract assertions
            assert response.status_code == 200
            data = response.json()
            
            # Should return success response
            assert isinstance(data, dict)

    def test_bulk_mark_validation_contract(self, client):
        """Test bulk mark validation contract."""
        headers = self.setup_authenticated_client(client)
        
        # Test without level
        response = client.post("/vocabulary/library/bulk-mark", json={"known": True}, headers=headers)
        assert response.status_code == 422
        
        # Test without known flag
        response = client.post("/vocabulary/library/bulk-mark", json={"level": "A1"}, headers=headers)
        assert response.status_code == 422
        
        # Test with invalid level
        response = client.post("/vocabulary/library/bulk-mark", json={
            "level": "INVALID",
            "known": True
        }, headers=headers)
        assert response.status_code == 422

    def test_vocabulary_endpoints_authentication_contract(self, client):
        """Test that vocabulary endpoints require authentication."""
        # Test without authentication
        endpoints_methods = [
            ("/vocabulary/blocking-words?video_path=test.mp4", "get"),
            ("/vocabulary/mark-known", "post"),
            ("/vocabulary/preload", "post"),
            ("/vocabulary/library/stats", "get"),
            ("/vocabulary/library/A1", "get"),
            ("/vocabulary/library/bulk-mark", "post"),
        ]
        
        for endpoint, method in endpoints_methods:
            if method == "get":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            
            # Should require authentication
            assert response.status_code == 401

    @pytest.mark.parametrize("endpoint,method", [
        ("/vocabulary/blocking-words", "get"),
        ("/vocabulary/mark-known", "post"),
        ("/vocabulary/preload", "post"),
        ("/vocabulary/library/stats", "get"),
        ("/vocabulary/library/A1", "get"),
        ("/vocabulary/library/bulk-mark", "post"),
    ])
    def test_vocabulary_endpoints_content_type_contract(self, client, endpoint, method):
        """Test that vocabulary endpoints return JSON content type."""
        headers = self.setup_authenticated_client(client)
        
        with patch('os.path.exists', return_value=True), \
             patch('core.database.get_async_session'):
            
            if method == "get":
                if "blocking-words" in endpoint:
                    response = client.get(f"{endpoint}?video_path=test.mp4", headers=headers)
                else:
                    response = client.get(endpoint, headers=headers)
            else:
                if "mark-known" in endpoint:
                    response = client.post(endpoint, json={"word": "test", "known": True}, headers=headers)
                elif "bulk-mark" in endpoint:
                    response = client.post(endpoint, json={"level": "A1", "known": True}, headers=headers)
                else:
                    response = client.post(endpoint, headers=headers)
            
            # Should return JSON content type (even for errors)
            assert "application/json" in response.headers.get("content-type", "")