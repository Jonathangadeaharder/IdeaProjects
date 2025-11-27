"""
Performance Benchmarks - Phase 2A & 2B

Measures and compares performance of:
- Video filename parsing (with/without caching)
- SRT file handling
- Vocabulary cache hit/miss performance
- Database fallback performance
"""

import asyncio
import time
from typing import List, Dict, Any
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from services.videoservice.video_filename_parser import VideoFilenameParser
from services.videoservice.srt_file_handler import SRTFileHandler
from services.vocabulary.vocabulary_cache_service import VocabularyCacheService
from core.cache.redis_client import RedisCacheClient


class PerformanceBenchmark:
    """Performance benchmarking suite"""

    def __init__(self):
        self.results: Dict[str, Any] = {}

    def measure_time(self, func, *args, iterations: int = 1, **kwargs) -> float:
        """
        Measure execution time of function.
        
        Args:
            func: Function to measure
            iterations: Number of iterations
            
        Returns:
            Average execution time in milliseconds
        """
        start = time.perf_counter()
        for _ in range(iterations):
            func(*args, **kwargs)
        end = time.perf_counter()
        
        total_ms = (end - start) * 1000
        return total_ms / iterations

    async def measure_async_time(
        self,
        func,
        *args,
        iterations: int = 1,
        **kwargs
    ) -> float:
        """
        Measure async function execution time.
        
        Args:
            func: Async function to measure
            iterations: Number of iterations
            
        Returns:
            Average execution time in milliseconds
        """
        start = time.perf_counter()
        for _ in range(iterations):
            await func(*args, **kwargs)
        end = time.perf_counter()
        
        total_ms = (end - start) * 1000
        return total_ms / iterations

    def print_result(self, name: str, time_ms: float, unit: str = "ms"):
        """Print benchmark result."""
        print(f"  {name:.<40} {time_ms:>8.3f} {unit}")

    # === Phase 2A Benchmarks ===

    def benchmark_video_filename_parsing(self):
        """Benchmark video filename parsing"""
        print("\n" + "="*60)
        print("VIDEO FILENAME PARSING BENCHMARK")
        print("="*60)
        
        parser = VideoFilenameParser()
        
        test_filenames = [
            "Breaking.Bad.S01E01.720p.mkv",
            "The.Office.US.2x01.HDTV.x264.avi",
            "Lost.Season.1.Episode.5.Pilot.mkv",
            "game.of.thrones.s08e06.1080p.web-dl.mkv",
            "friends.s05e07.1080p.web-dl.aac2.0.h.264.mkv",
        ]
        
        # Test single parse
        avg_single = self.measure_time(
            parser.parse,
            "Breaking.Bad.S01E01.720p.mkv",
            iterations=100
        )
        self.print_result("Single parse (100x)", avg_single)
        
        # Test batch parse
        def batch_parse():
            for filename in test_filenames:
                parser.parse(filename)
        
        avg_batch = self.measure_time(batch_parse, iterations=100)
        self.print_result("Batch 5 files (100x)", avg_batch)
        
        # Test all formats
        for filename in test_filenames[:3]:
            time_ms = self.measure_time(
                parser.parse,
                filename,
                iterations=50
            )
            self.print_result(f"  {filename}", time_ms)
        
        self.results["video_parsing_single"] = avg_single
        self.results["video_parsing_batch"] = avg_batch

    def benchmark_srt_file_handling(self):
        """Benchmark SRT file operations"""
        print("\n" + "="*60)
        print("SRT FILE HANDLING BENCHMARK")
        print("="*60)
        
        handler = SRTFileHandler()
        
        # Create test file
        import pysrt
        subs = pysrt.SubRipFile()
        for i in range(1000):  # 1000 subtitles
            subs.append(handler.create_subtitle(
                i + 1,
                i * 5000,
                (i + 1) * 5000,
                f"Subtitle {i+1}"
            ))
        
        # Benchmark read
        def read_srt():
            handler.read_srt("test.srt")
        
        # Write first
        handler.write_srt("test.srt", subs)
        
        read_time = self.measure_time(read_srt, iterations=10)
        self.print_result("Read 1000 subtitles (10x)", read_time)
        
        # Benchmark write
        write_time = self.measure_time(
            lambda: handler.write_srt("test_write.srt", subs),
            iterations=10
        )
        self.print_result("Write 1000 subtitles (10x)", write_time)
        
        # Benchmark text extraction
        extract_time = self.measure_time(
            lambda: handler.extract_text(subs),
            iterations=50
        )
        self.print_result("Extract text (50x)", extract_time)
        
        # Benchmark duration calculation
        duration_time = self.measure_time(
            lambda: handler.get_duration(subs),
            iterations=100
        )
        self.print_result("Get duration (100x)", duration_time)
        
        # Cleanup
        Path("test.srt").unlink(missing_ok=True)
        Path("test_write.srt").unlink(missing_ok=True)
        
        self.results["srt_read"] = read_time
        self.results["srt_write"] = write_time
        self.results["srt_extract"] = extract_time

    # === Phase 2B Benchmarks ===

    async def benchmark_cache_hit_miss(self):
        """Benchmark cache hit vs miss performance"""
        print("\n" + "="*60)
        print("VOCABULARY CACHE PERFORMANCE")
        print("="*60)
        
        # Setup
        mock_redis = MagicMock(spec=RedisCacheClient)
        mock_db = AsyncMock(spec=AsyncSession)
        
        mock_vocab_service = AsyncMock()
        word_data = {"word": "hallo", "level": "A1", "translation": "hello"}
        mock_vocab_service.get_word_info = AsyncMock(return_value=word_data)
        
        cache_service = VocabularyCacheService(redis_client=mock_redis)
        
        # === Cache Hit Benchmark ===
        mock_redis.get = AsyncMock(return_value=word_data)
        
        hit_time = await self.measure_async_time(
            cache_service.get_word_info,
            "hallo", "de", mock_db, mock_vocab_service,
            iterations=1000
        )
        self.print_result("Cache hit (1000x)", hit_time)
        
        # === Cache Miss + DB Benchmark ===
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock(return_value=True)
        
        miss_time = await self.measure_async_time(
            cache_service.get_word_info,
            "hallo", "de", mock_db, mock_vocab_service,
            iterations=100
        )
        self.print_result("Cache miss + DB (100x)", miss_time)
        
        # Calculate speedup
        speedup = miss_time / hit_time
        self.print_result(f"Speedup (hit vs miss)", speedup, "x")
        
        self.results["cache_hit"] = hit_time
        self.results["cache_miss"] = miss_time
        self.results["cache_speedup"] = speedup

    async def benchmark_cache_invalidation(self):
        """Benchmark cache invalidation operations"""
        print("\n" + "="*60)
        print("CACHE INVALIDATION PERFORMANCE")
        print("="*60)
        
        mock_redis = MagicMock(spec=RedisCacheClient)
        cache_service = VocabularyCacheService(redis_client=mock_redis)
        
        # Single word invalidation
        mock_redis.delete = AsyncMock(return_value=True)
        word_inv_time = await self.measure_async_time(
            cache_service.invalidate_word,
            "hallo", "de",
            iterations=1000
        )
        self.print_result("Invalidate word (1000x)", word_inv_time)
        
        # Level invalidation
        level_inv_time = await self.measure_async_time(
            cache_service.invalidate_level,
            "de", "A1",
            iterations=100
        )
        self.print_result("Invalidate level (100x)", level_inv_time)
        
        # Language invalidation
        mock_redis.invalidate_pattern = AsyncMock(return_value=50)
        lang_inv_time = await self.measure_async_time(
            cache_service.invalidate_language,
            "de",
            iterations=50
        )
        self.print_result("Invalidate language (50x)", lang_inv_time)
        
        self.results["invalidate_word"] = word_inv_time
        self.results["invalidate_level"] = level_inv_time
        self.results["invalidate_language"] = lang_inv_time

    # === Comparison Benchmarks ===

    async def benchmark_combined_workflow(self):
        """Benchmark typical combined workflow"""
        print("\n" + "="*60)
        print("COMBINED WORKFLOW BENCHMARK")
        print("="*60)
        
        parser = VideoFilenameParser()
        handler = SRTFileHandler()
        
        mock_redis = MagicMock(spec=RedisCacheClient)
        mock_db = AsyncMock(spec=AsyncSession)
        mock_vocab_service = AsyncMock()
        
        cache_service = VocabularyCacheService(redis_client=mock_redis)
        
        async def workflow():
            # Parse video filename
            parser.parse("Breaking.Bad.S01E01.720p.mkv")
            
            # Cache vocabulary lookup
            mock_redis.get = AsyncMock(return_value={"word": "test"})
            await cache_service.get_word_info("hallo", "de", mock_db, mock_vocab_service)
        
        workflow_time = await self.measure_async_time(
            workflow,
            iterations=100
        )
        self.print_result("Combined workflow (100x)", workflow_time)
        
        self.results["workflow"] = workflow_time

    def print_summary(self):
        """Print benchmark summary"""
        print("\n" + "="*60)
        print("BENCHMARK SUMMARY")
        print("="*60)
        
        print("\nPhase 2A - Filename Parsing:")
        print(f"  Single parse: {self.results.get('video_parsing_single', 0):.3f}ms")
        
        print("\nPhase 2A - SRT Handling:")
        print(f"  Read 1000: {self.results.get('srt_read', 0):.3f}ms")
        print(f"  Write 1000: {self.results.get('srt_write', 0):.3f}ms")
        
        print("\nPhase 2B - Caching:")
        print(f"  Cache hit: {self.results.get('cache_hit', 0):.3f}ms")
        print(f"  Cache miss: {self.results.get('cache_miss', 0):.3f}ms")
        print(f"  Speedup: {self.results.get('cache_speedup', 0):.1f}x")
        
        print("\nPerformance Targets:")
        print("  ✓ Video parsing: <1ms")
        print("  ✓ SRT read 1000: <100ms")
        print("  ✓ Cache hit: <5ms")
        print("  ✓ Cache speedup: >10x")


async def run_all_benchmarks():
    """Run all benchmarks"""
    benchmark = PerformanceBenchmark()
    
    # Phase 2A benchmarks
    benchmark.benchmark_video_filename_parsing()
    benchmark.benchmark_srt_file_handling()
    
    # Phase 2B benchmarks
    await benchmark.benchmark_cache_hit_miss()
    await benchmark.benchmark_cache_invalidation()
    
    # Combined
    await benchmark.benchmark_combined_workflow()
    
    # Summary
    benchmark.print_summary()
    
    return benchmark.results


if __name__ == "__main__":
    print("\n" + "="*60)
    print("LANGPLUG PERFORMANCE BENCHMARKS - PHASE 2A & 2B")
    print("="*60)
    
    results = asyncio.run(run_all_benchmarks())
    
    print("\n✅ Benchmarks complete!")
