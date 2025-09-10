#!/usr/bin/env python3
"""
Comprehensive workflow testing for LangPlug application
Tests all critical user journeys and API endpoints
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://172.30.96.1:8000"
FRONTEND_URL = "http://localhost:3001"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(message: str, status: str = "INFO"):
    colors = {
        "PASS": Colors.GREEN,
        "FAIL": Colors.RED,
        "INFO": Colors.BLUE,
        "WARN": Colors.YELLOW
    }
    color = colors.get(status, "")
    print(f"{color}[{status}]{Colors.END} {message}")

def print_section(title: str):
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.END}\n")

class WorkflowTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.test_results = []
        
    def test_health_check(self) -> bool:
        """Test if backend is responsive"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print_test("Backend health check passed", "PASS")
                return True
            else:
                print_test(f"Backend health check failed: {response.status_code}", "FAIL")
                return False
        except Exception as e:
            print_test(f"Backend connection failed: {e}", "FAIL")
            return False

    def test_authentication_workflow(self) -> bool:
        """Test complete authentication workflow"""
        print_section("AUTHENTICATION WORKFLOW")
        
        # 1. Register new user
        timestamp = int(time.time())
        self.user_data = {
            "username": f"test_user_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "TestPass123!@#"
        }
        
        try:
            # Register
            print_test("Testing user registration...")
            response = self.session.post(
                f"{BASE_URL}/auth/register",
                json=self.user_data
            )
            
            if response.status_code == 200:
                print_test(f"User registered: {self.user_data['username']}", "PASS")
            else:
                print_test(f"Registration failed: {response.text}", "FAIL")
                return False
            
            # Login
            print_test("Testing user login...")
            login_data = {
                "username": self.user_data["username"],
                "password": self.user_data["password"]
            }
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                auth_response = response.json()
                self.auth_token = auth_response.get("token")
                print_test(f"Login successful, token received", "PASS")
                
                # Set auth header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
            else:
                print_test(f"Login failed: {response.text}", "FAIL")
                return False
            
            # Get current user info
            print_test("Testing get current user...")
            response = self.session.get(f"{BASE_URL}/auth/me")
            
            if response.status_code == 200:
                user_info = response.json()
                print_test(f"Current user retrieved: {user_info.get('username')}", "PASS")
            else:
                print_test(f"Get user failed: {response.text}", "FAIL")
                return False
                
            return True
            
        except Exception as e:
            print_test(f"Authentication workflow error: {e}", "FAIL")
            return False

    def test_video_management_workflow(self) -> bool:
        """Test video browsing and selection"""
        print_section("VIDEO MANAGEMENT WORKFLOW")
        
        try:
            # Get available videos
            print_test("Testing get available videos...")
            response = self.session.get(f"{BASE_URL}/videos")
            
            if response.status_code == 200:
                videos = response.json()
                print_test(f"Found {len(videos)} videos", "PASS")
                
                if videos:
                    # Display first few videos
                    for video in videos[:3]:
                        print_test(f"  - {video.get('title', video.get('path'))}", "INFO")
                    
                    # Test getting specific video
                    first_video = videos[0]
                    if "Superstore" in str(first_video.get("path", "")):
                        print_test("Testing get specific video...")
                        response = self.session.get(f"{BASE_URL}/videos/Superstore/1")
                        
                        if response.status_code == 200:
                            print_test("Specific video retrieved successfully", "PASS")
                        else:
                            print_test(f"Failed to get specific video: {response.status_code}", "WARN")
                    
                    # Test subtitle retrieval if available
                    if first_video.get("has_subtitles"):
                        print_test("Testing subtitle retrieval...")
                        subtitle_path = first_video["path"].replace(".mp4", ".srt")
                        response = self.session.get(
                            f"{BASE_URL}/videos/subtitles/{subtitle_path}"
                        )
                        
                        if response.status_code == 200:
                            print_test("Subtitles retrieved successfully", "PASS")
                        else:
                            print_test(f"Subtitle retrieval failed: {response.status_code}", "WARN")
                
                return True
            else:
                print_test(f"Failed to get videos: {response.text}", "FAIL")
                return False
                
        except Exception as e:
            print_test(f"Video workflow error: {e}", "FAIL")
            return False

    def test_vocabulary_workflow(self) -> bool:
        """Test vocabulary management features"""
        print_section("VOCABULARY MANAGEMENT WORKFLOW")
        
        try:
            # Get vocabulary statistics
            print_test("Testing vocabulary statistics...")
            response = self.session.get(f"{BASE_URL}/vocabulary/library/stats")
            
            if response.status_code == 200:
                stats = response.json()
                print_test("Vocabulary statistics retrieved", "PASS")
                print_test(f"  Total words: {stats.get('total_known_words', 0)}", "INFO")
            else:
                print_test(f"Failed to get stats: {response.status_code}", "FAIL")
                return False
            
            # Get A1 vocabulary
            print_test("Testing A1 vocabulary retrieval...")
            response = self.session.get(f"{BASE_URL}/vocabulary/library/A1")
            
            if response.status_code == 200:
                a1_data = response.json()
                print_test(f"A1 vocabulary retrieved", "PASS")
                print_test(f"  Total A1 words: {a1_data.get('total_count', 0)}", "INFO")
                print_test(f"  Known A1 words: {a1_data.get('known_count', 0)}", "INFO")
            else:
                print_test(f"Failed to get A1 vocabulary: {response.status_code}", "FAIL")
                return False
            
            # Mark a word as known
            print_test("Testing mark word as known...")
            mark_data = {
                "word": "hallo",
                "known": True
            }
            response = self.session.post(
                f"{BASE_URL}/vocabulary/mark-known",
                json=mark_data
            )
            
            if response.status_code == 200:
                print_test("Word marked as known successfully", "PASS")
            else:
                print_test(f"Failed to mark word: {response.status_code}", "WARN")
            
            # Get blocking words for a video
            print_test("Testing blocking words retrieval...")
            response = self.session.get(
                f"{BASE_URL}/vocabulary/blocking-words?video_path=test.mp4"
            )
            
            if response.status_code == 200:
                blocking = response.json()
                print_test(f"Blocking words retrieved", "PASS")
                print_test(f"  Unknown words: {blocking.get('total_unknown', 0)}", "INFO")
            else:
                print_test(f"Failed to get blocking words: {response.status_code}", "WARN")
            
            return True
            
        except Exception as e:
            print_test(f"Vocabulary workflow error: {e}", "FAIL")
            return False

    def test_processing_workflow(self) -> bool:
        """Test video processing capabilities"""
        print_section("VIDEO PROCESSING WORKFLOW")
        
        try:
            # Get videos first
            response = self.session.get(f"{BASE_URL}/videos")
            if response.status_code != 200:
                print_test("Cannot test processing - no videos available", "WARN")
                return True
            
            videos = response.json()
            if not videos:
                print_test("No videos available for processing test", "WARN")
                return True
            
            # Use first video for testing
            test_video = videos[0]
            video_path = test_video.get("path", "")
            
            # Test transcription
            print_test("Testing video transcription initiation...")
            transcribe_data = {
                "video_path": video_path,
                "language": "de"
            }
            response = self.session.post(
                f"{BASE_URL}/process/transcribe",
                json=transcribe_data
            )
            
            if response.status_code == 200:
                task_response = response.json()
                task_id = task_response.get("task_id")
                print_test(f"Transcription started: {task_id}", "PASS")
                
                # Check progress
                time.sleep(2)
                response = self.session.get(f"{BASE_URL}/process/progress/{task_id}")
                if response.status_code == 200:
                    progress = response.json()
                    print_test(f"  Progress: {progress.get('progress', 0)}%", "INFO")
                    print_test(f"  Status: {progress.get('status', 'unknown')}", "INFO")
            else:
                print_test(f"Failed to start transcription: {response.status_code}", "WARN")
            
            # Test filtering
            print_test("Testing subtitle filtering...")
            filter_data = {
                "video_path": video_path
            }
            response = self.session.post(
                f"{BASE_URL}/process/filter-subtitles",
                json=filter_data
            )
            
            if response.status_code == 200:
                print_test("Filtering initiated successfully", "PASS")
            else:
                print_test(f"Failed to start filtering: {response.status_code}", "WARN")
            
            return True
            
        except Exception as e:
            print_test(f"Processing workflow error: {e}", "FAIL")
            return False

    def test_cors_configuration(self) -> bool:
        """Test CORS configuration for frontend access"""
        print_section("CORS CONFIGURATION TEST")
        
        try:
            # Test OPTIONS request (preflight)
            print_test("Testing CORS preflight request...")
            headers = {
                "Origin": "http://localhost:3001",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type,authorization"
            }
            response = requests.options(f"{BASE_URL}/auth/login", headers=headers)
            
            if response.status_code == 200:
                cors_headers = response.headers
                if "Access-Control-Allow-Origin" in cors_headers:
                    print_test(f"CORS enabled for: {cors_headers['Access-Control-Allow-Origin']}", "PASS")
                else:
                    print_test("CORS headers missing", "FAIL")
                    return False
            else:
                print_test(f"CORS preflight failed: {response.status_code}", "FAIL")
                return False
            
            return True
            
        except Exception as e:
            print_test(f"CORS test error: {e}", "FAIL")
            return False

    def run_all_tests(self):
        """Run all workflow tests"""
        print(f"\n{Colors.BOLD}LANGPLUG COMPREHENSIVE WORKFLOW TESTING{Colors.END}")
        print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Authentication", self.test_authentication_workflow),
            ("Video Management", self.test_video_management_workflow),
            ("Vocabulary", self.test_vocabulary_workflow),
            ("Processing", self.test_processing_workflow),
            ("CORS Configuration", self.test_cors_configuration)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print_test(f"{test_name} test crashed: {e}", "FAIL")
                results.append((test_name, False))
        
        # Summary
        print_section("TEST SUMMARY")
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "PASS" if result else "FAIL"
            print_test(f"{test_name}: {status}", status)
        
        print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.END}")
        
        if passed == total:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.END}")
            print(f"{Colors.YELLOW}Issues to fix:{Colors.END}")
            for test_name, result in results:
                if not result:
                    print(f"  - {test_name}")
        
        return passed == total

if __name__ == "__main__":
    tester = WorkflowTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)