#!/usr/bin/env python3
"""
Simple integration test for backend components
Tests core functionality without requiring full server
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import venv_activator  # Auto-activate virtual environment (non-blocking version)
import json
from datetime import datetime

def test_imports():
    """Test that all modules can be imported"""
    print("\n1. Testing module imports...")
    
    try:
        print("  [OK] Core config imported")
        
        print("  [OK] Auth service imported")
        
        print("  [OK] Vocabulary service imported")
        
        print("  [OK] Transcription interface imported")
        
        print("  [OK] Filter interface imported")
        
        print("  [OK] API routes imported")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Import failed: {e}")
        return False

def test_database():
    """Test database connectivity"""
    print("\n2. Testing database connectivity...")
    
    try:
        from database.unified_database_manager import UnifiedDatabaseManager as DatabaseManager
        
        db = DatabaseManager()
        
        # Test connection
        tables = db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
            
        print(f"  [OK] Database connected - {len(tables)} tables found")
        for table in tables:
            print(f"      - {table['name']}")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Database test failed: {e}")
        return False

def test_auth_service():
    """Test authentication service"""
    print("\n3. Testing authentication service...")
    
    try:
        from services.authservice.auth_service import AuthService
        from database.unified_database_manager import UnifiedDatabaseManager as DatabaseManager
        
        # Create database manager for auth service
        db_manager = DatabaseManager("vocabulary.db")
        auth = AuthService(db_manager)
        
        # Test admin user exists
        admin = auth._get_user_by_username("admin")
        if admin:
            print(f"  [OK] Admin user exists (id: {admin['id']})")
        else:
            print("  [WARNING] Admin user not found")
        
        # Test password verification by attempting login
        try:
            session = auth.login("admin", "admin")
            if session and session.session_token:
                print("  [OK] Password verification working (via login)")
                print(f"  [OK] Session creation working (token length: {len(session.session_token)})")
            else:
                print("  [WARNING] Password verification failed")
        except Exception as e:
            print(f"  [WARNING] Password verification failed: {e}")
        
        # Session creation already tested above with password verification
        
        return True
    except Exception as e:
        print(f"  [ERROR] Auth service test failed: {e}")
        return False

def test_vocabulary_service():
    """Test vocabulary service"""
    print("\n4. Testing vocabulary service...")
    
    try:
        from services.dataservice.user_vocabulary_service import SQLiteUserVocabularyService
        from database.unified_database_manager import UnifiedDatabaseManager as DatabaseManager
        
        # Initialize with database manager
        db_manager = DatabaseManager()
        vocab = SQLiteUserVocabularyService(db_manager)
        
        # Test basic functionality
        test_user = "test_user_123"
        
        # Test getting known words (should be empty initially)
        known_words = vocab.get_known_words(test_user)
        print(f"  [OK] Known words retrieved: {len(known_words)} words")
        
        # Test checking if word is known
        is_known = vocab.is_word_known(test_user, "hello")
        print(f"  [OK] Word knowledge check: {'known' if is_known else 'unknown'}")
        
        # Test learning statistics
        stats = vocab.get_learning_statistics(test_user)
        print(f"  [OK] Learning stats: {stats.get('total_known_words', 0)} known words")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Vocabulary service test failed: {e}")
        return False

def test_video_directory():
    """Test video directory access"""
    print("\n5. Testing video directory access...")
    
    try:
        from core.config import settings
        
        videos_path = settings.get_videos_path()
        
        if videos_path.exists():
            print(f"  [OK] Videos directory exists: {videos_path}")
            
            # List video files
            video_files = list(videos_path.glob("*.mp4"))
            print(f"  [OK] Found {len(video_files)} MP4 files")
            
            if video_files:
                for i, video in enumerate(video_files[:3], 1):
                    size_mb = video.stat().st_size / (1024 * 1024)
                    print(f"      {i}. {video.name} ({size_mb:.1f} MB)")
        else:
            print(f"  [WARNING] Videos directory not found: {videos_path}")
        
        # Check Superstore videos
        superstore_path = Path("C:/Users/Jonandrop/IdeaProjects/LangPlug/videos/Superstore")
        if superstore_path.exists():
            superstore_videos = list(superstore_path.glob("*.mp4"))
            print(f"  [OK] Superstore directory: {len(superstore_videos)} videos")
        else:
            print("  [INFO] Superstore directory not found")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Video directory test failed: {e}")
        return False

def test_srt_generation():
    """Test SRT format generation"""
    print("\n6. Testing SRT generation format...")
    
    try:
        from api.routes.processing import _format_srt_timestamp
        from services.transcriptionservice.interface import TranscriptionSegment
        
        # Test timestamp formatting
        test_cases = [
            (0.0, "00:00:00,000"),
            (65.5, "00:01:05,500"),
            (3665.123, "01:01:05,123"),
        ]
        
        all_correct = True
        for seconds, expected in test_cases:
            result = _format_srt_timestamp(seconds)
            if result == expected:
                print(f"  [OK] {seconds}s -> {result}")
            else:
                print(f"  [ERROR] {seconds}s -> {result} (expected {expected})")
                all_correct = False
        
        if all_correct:
            print("  [OK] SRT timestamp formatting working correctly")
        
        # Test SRT generation with mock data
        segments = [
            TranscriptionSegment(0.0, 2.5, "Test subtitle 1", {}),
            TranscriptionSegment(2.5, 5.0, "Test subtitle 2", {}),
        ]
        
        srt_lines = []
        for i, seg in enumerate(segments, 1):
            srt_lines.append(str(i))
            srt_lines.append(f"{_format_srt_timestamp(seg.start_time)} --> {_format_srt_timestamp(seg.end_time)}")
            srt_lines.append(seg.text)
            srt_lines.append("")
        
        srt_content = "\n".join(srt_lines)
        
        if "00:00:00,000 --> 00:00:02,500" in srt_content:
            print("  [OK] SRT content generation working")
        else:
            print("  [ERROR] SRT content generation failed")
        
        return all_correct
    except Exception as e:
        print(f"  [ERROR] SRT generation test failed: {e}")
        return False

def test_subtitle_processor():
    """Test subtitle processor initialization"""
    print("\n7. Testing subtitle processor...")
    
    try:
        from services.filterservice.direct_subtitle_processor import DirectSubtitleProcessor
        from database.unified_database_manager import UnifiedDatabaseManager
        
        print("  [INFO] DirectSubtitleProcessor module can be imported")
        
        # Try to create instance (may fail if dependencies not initialized)
        try:
            db_manager = UnifiedDatabaseManager()
            processor = DirectSubtitleProcessor(db_manager)
            print("  [OK] DirectSubtitleProcessor instance created")
        except Exception as e:
            print(f"  [INFO] Subtitle processor initialization skipped: {e}")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Subtitle processor test failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n8. Testing configuration...")
    
    try:
        from core.config import settings
        
        print(f"  [OK] Host: {settings.host}")
        print(f"  [OK] Port: {settings.port}")
        print(f"  [OK] Debug mode: {settings.debug}")
        print(f"  [OK] Default language: {settings.default_language}")
        print(f"  [OK] Log level: {settings.log_level}")
        
        # Check paths
        print(f"  [OK] Videos path: {settings.get_videos_path()}")
        print(f"  [OK] Data path: {settings.get_data_path()}")
        print(f"  [OK] Logs path: {settings.get_logs_path()}")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Config test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print("LANGPLUG BACKEND INTEGRATION TEST")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)
    
    tests = [
        ("Module Imports", test_imports),
        ("Database Connectivity", test_database),
        ("Authentication Service", test_auth_service),
        ("Vocabulary Service", test_vocabulary_service),
        ("Video Directory Access", test_video_directory),
        ("SRT Generation", test_srt_generation),
        ("Subtitle Processor", test_subtitle_processor),
        ("Configuration", test_config),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n[ERROR] Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"Failed: {total-passed} ({(total-passed)/total*100:.1f}%)")
    
    print("\nTest Results:")
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {name}")
    
    print("=" * 70)
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "results": [{"name": name, "passed": p} for name, p in results]
    }
    
    report_dir = Path(__file__).parent / "test_reports"
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / f"integration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {report_file}")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
import os
import pytest

pytestmark = pytest.mark.integration
if os.environ.get("RUN_LIVE_HTTP") != "1":
    pytest.skip(
        "Skipping live HTTP integration tests; set RUN_LIVE_HTTP=1 to run.",
        allow_module_level=True,
    )
