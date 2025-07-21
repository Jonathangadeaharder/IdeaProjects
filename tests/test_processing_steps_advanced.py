#!/usr/bin/env python3
"""
Advanced unit tests for ProcessingStep classes.
Focuses on edge cases, error scenarios, and integration testing.
"""

import unittest
import os
import tempfile
import shutil
import json
from unittest.mock import Mock, MagicMock, patch, mock_open, call
from dataclasses import dataclass
from typing import Any, Optional, Set, List

# Import the classes under test
from processing_steps import ProcessingContext, ProcessingPipeline
from concrete_processing_steps import (
    PreviewTranscriptionStep,
    FullTranscriptionStep,
    A1FilterStep,
    TranslationStep,
    PreviewProcessingStep,
    CLIAnalysisStep
)


class TestProcessingPipeline(unittest.TestCase):
    """Test ProcessingPipeline orchestration and error handling."""
    
    def setUp(self):
        self.mock_model_manager = Mock()
        self.context = ProcessingContext(
            video_file="test_video.mp4",
            model_manager=self.mock_model_manager,
            language="de"
        )
    
    def test_empty_pipeline_execution(self):
        """Test pipeline execution with no steps."""
        pipeline = ProcessingPipeline([])
        result = pipeline.execute(self.context)
        self.assertTrue(result)
    
    def test_single_step_success(self):
        """Test pipeline with single successful step."""
        mock_step = Mock()
        mock_step.execute.return_value = True
        mock_step.name = "Test Step"
        
        pipeline = ProcessingPipeline([mock_step])
        result = pipeline.execute(self.context)
        
        self.assertTrue(result)
        mock_step.execute.assert_called_once_with(self.context)
    
    def test_single_step_failure(self):
        """Test pipeline with single failing step."""
        mock_step = Mock()
        mock_step.execute.return_value = False
        mock_step.name = "Failing Step"
        
        pipeline = ProcessingPipeline([mock_step])
        result = pipeline.execute(self.context)
        
        self.assertFalse(result)
        mock_step.execute.assert_called_once_with(self.context)
    
    def test_multiple_steps_all_success(self):
        """Test pipeline with multiple successful steps."""
        mock_step1 = Mock()
        mock_step1.execute.return_value = True
        mock_step1.name = "Step 1"
        
        mock_step2 = Mock()
        mock_step2.execute.return_value = True
        mock_step2.name = "Step 2"
        
        pipeline = ProcessingPipeline([mock_step1, mock_step2])
        result = pipeline.execute(self.context)
        
        self.assertTrue(result)
        mock_step1.execute.assert_called_once_with(self.context)
        mock_step2.execute.assert_called_once_with(self.context)
    
    def test_multiple_steps_early_failure(self):
        """Test pipeline stops on first failure."""
        mock_step1 = Mock()
        mock_step1.execute.return_value = False
        mock_step1.name = "Failing Step"
        
        mock_step2 = Mock()
        mock_step2.execute.return_value = True
        mock_step2.name = "Should Not Execute"
        
        pipeline = ProcessingPipeline([mock_step1, mock_step2])
        result = pipeline.execute(self.context)
        
        self.assertFalse(result)
        mock_step1.execute.assert_called_once_with(self.context)
        mock_step2.execute.assert_not_called()
    
    def test_step_exception_handling(self):
        """Test pipeline handles step exceptions gracefully."""
        mock_step = Mock()
        mock_step.execute.side_effect = Exception("Step crashed")
        mock_step.name = "Crashing Step"
        
        pipeline = ProcessingPipeline([mock_step])
        
        # Pipeline should handle exceptions and return False
        with patch('processing_steps.console.print') as mock_console:
            result = pipeline.execute(self.context)
        
        self.assertFalse(result)
        mock_console.assert_called()


class TestPreviewTranscriptionStepAdvanced(unittest.TestCase):
    """Advanced tests for PreviewTranscriptionStep."""
    
    def setUp(self):
        self.step = PreviewTranscriptionStep()
        self.mock_model_manager = Mock()
        self.context = ProcessingContext(
            video_file="test_video.mp4",
            model_manager=self.mock_model_manager,
            language="de"
        )
        self.temp_dir = tempfile.mkdtemp()
        self.test_video_path = os.path.join(self.temp_dir, "test_video.mp4")
        self.context.video_file = self.test_video_path
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('concrete_processing_steps.VideoFileClip')
    def test_video_file_not_found(self, mock_video_clip):
        """Test handling when video file doesn't exist."""
        mock_video_clip.side_effect = FileNotFoundError("Video file not found")
        
        result = self.step.execute(self.context)
        self.assertFalse(result)
    
    @patch('concrete_processing_steps.VideoFileClip')
    def test_video_clip_exception(self, mock_video_clip):
        """Test handling of VideoFileClip exceptions."""
        mock_video_clip.side_effect = Exception("Corrupted video file")
        
        result = self.step.execute(self.context)
        self.assertFalse(result)
    
    @patch('concrete_processing_steps.VideoFileClip')
    @patch('concrete_processing_steps.os.path.exists')
    def test_temp_file_cleanup_on_exception(self, mock_exists, mock_video_clip):
        """Test that temporary files are cleaned up even on exceptions."""
        # Setup video mock
        mock_video = Mock()
        mock_video.duration = 1200
        mock_audio = Mock()
        mock_video.audio = mock_audio
        mock_video_clip.return_value.__enter__.return_value = mock_video
        
        # Mock audio processing to raise exception
        mock_audio.subclipped.side_effect = Exception("Audio processing failed")
        
        # Mock file existence check
        mock_exists.return_value = True
        
        with patch('concrete_processing_steps.os.remove') as mock_remove:
            result = self.step.execute(self.context)
        
        self.assertFalse(result)
        # Verify cleanup was attempted
        mock_remove.assert_called()
    
    @patch('concrete_processing_steps.VideoFileClip')
    def test_whisper_model_unavailable(self, mock_video_clip):
        """Test handling when Whisper model is unavailable."""
        # Setup video mock
        mock_video = Mock()
        mock_video.duration = 1200
        mock_video.audio = Mock()
        mock_video_clip.return_value.__enter__.return_value = mock_video
        
        # Mock model manager to return None
        self.mock_model_manager.get_whisper_model_safe.return_value.__enter__.return_value = None
        
        result = self.step.execute(self.context)
        self.assertFalse(result)
    
    @patch('concrete_processing_steps.VideoFileClip')
    @patch('builtins.open', new_callable=mock_open)
    def test_file_write_permission_error(self, mock_file, mock_video_clip):
        """Test handling of file write permission errors."""
        # Setup video and model mocks
        mock_video = Mock()
        mock_video.duration = 1200
        mock_video.audio = Mock()
        mock_video_clip.return_value.__enter__.return_value = mock_video
        
        mock_whisper = Mock()
        mock_whisper.transcribe.return_value = {'segments': []}
        self.mock_model_manager.get_whisper_model_safe.return_value.__enter__.return_value = mock_whisper
        
        # Mock file write to raise permission error
        mock_file.side_effect = PermissionError("Permission denied")
        
        result = self.step.execute(self.context)
        self.assertFalse(result)


class TestA1FilterStepAdvanced(unittest.TestCase):
    """Advanced tests for A1FilterStep."""
    
    def setUp(self):
        self.step = A1FilterStep()
        self.mock_model_manager = Mock()
        self.context = ProcessingContext(
            video_file="test_video.mp4",
            model_manager=self.mock_model_manager,
            known_words={"der", "die", "das", "ist", "ein", "eine"}
        )
        self.temp_dir = tempfile.mkdtemp()
        self.test_srt_path = os.path.join(self.temp_dir, "test.srt")
        self.context.full_srt = self.test_srt_path
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('concrete_processing_steps.load_subtitles')
    def test_spacy_model_unavailable(self, mock_load):
        """Test handling when SpaCy model is unavailable."""
        mock_load.return_value = [Mock()]
        self.mock_model_manager.get_spacy_model_safe.return_value.__enter__.return_value = None
        
        result = self.step.execute(self.context)
        self.assertFalse(result)
    
    @patch('concrete_processing_steps.load_subtitles')
    def test_empty_known_words_set(self, mock_load):
        """Test behavior with empty known words set."""
        mock_sub = Mock()
        mock_sub.text = "Das ist ein Test"
        mock_load.return_value = [mock_sub]
        
        # Empty known words set
        self.context.known_words = set()
        
        # Mock SpaCy processing
        mock_tokens = [Mock(text="das", is_alpha=True), Mock(text="ist", is_alpha=True)]
        mock_doc = Mock()
        mock_doc.__iter__ = Mock(return_value=iter(mock_tokens))
        mock_nlp = Mock(return_value=mock_doc)
        self.mock_model_manager.get_spacy_model_safe.return_value.__enter__.return_value = mock_nlp
        
        with patch('concrete_processing_steps.save_subtitles') as mock_save:
            with patch('concrete_processing_steps.pysrt.SubRipFile') as mock_srt_file:
                result = self.step.execute(self.context)
        
        # Should succeed and include all words as unknown
        self.assertTrue(result)
    
    @patch('concrete_processing_steps.load_subtitles')
    def test_large_known_words_set_performance(self, mock_load):
        """Test performance with large known words set."""
        # Create large known words set
        large_known_words = {f"word{i}" for i in range(10000)}
        self.context.known_words = large_known_words
        
        # Create subtitle with mix of known and unknown words
        mock_sub = Mock()
        mock_sub.text = "word1 unknown_word word2"
        mock_load.return_value = [mock_sub]
        
        # Mock SpaCy processing
        mock_tokens = [
            Mock(text="word1", is_alpha=True),
            Mock(text="unknown_word", is_alpha=True),
            Mock(text="word2", is_alpha=True)
        ]
        mock_doc = Mock()
        mock_doc.__iter__ = Mock(return_value=iter(mock_tokens))
        mock_nlp = Mock(return_value=mock_doc)
        self.mock_model_manager.get_spacy_model_safe.return_value.__enter__.return_value = mock_nlp
        
        with patch('concrete_processing_steps.save_subtitles') as mock_save:
            with patch('concrete_processing_steps.pysrt.SubRipFile') as mock_srt_file:
                result = self.step.execute(self.context)
        
        self.assertTrue(result)
    
    @patch('concrete_processing_steps.load_subtitles')
    def test_special_characters_handling(self, mock_load):
        """Test handling of subtitles with special characters."""
        mock_sub = Mock()
        mock_sub.text = "Hällö! Wörld? 123 @#$%"
        mock_load.return_value = [mock_sub]
        
        # Mock SpaCy to return only alphabetic tokens
        mock_tokens = [
            Mock(text="Hällö", is_alpha=True),
            Mock(text="!", is_alpha=False),
            Mock(text="Wörld", is_alpha=True),
            Mock(text="?", is_alpha=False),
            Mock(text="123", is_alpha=False),
        ]
        mock_doc = Mock()
        mock_doc.__iter__ = Mock(return_value=iter(mock_tokens))
        mock_nlp = Mock(return_value=mock_doc)
        self.mock_model_manager.get_spacy_model_safe.return_value.__enter__.return_value = mock_nlp
        
        with patch('concrete_processing_steps.save_subtitles') as mock_save:
            with patch('concrete_processing_steps.pysrt.SubRipFile') as mock_srt_file:
                result = self.step.execute(self.context)
        
        self.assertTrue(result)
    
    @patch('concrete_processing_steps.load_subtitles')
    @patch('concrete_processing_steps.save_subtitles')
    def test_save_subtitles_failure(self, mock_save, mock_load):
        """Test handling when saving filtered subtitles fails."""
        mock_load.return_value = [Mock(text="test")]
        mock_save.side_effect = IOError("Disk full")
        
        # Mock SpaCy processing
        mock_nlp = Mock()
        self.mock_model_manager.get_spacy_model_safe.return_value.__enter__.return_value = mock_nlp
        
        result = self.step.execute(self.context)
        self.assertFalse(result)


class TestTranslationStepAdvanced(unittest.TestCase):
    """Advanced tests for TranslationStep."""
    
    def setUp(self):
        self.step = TranslationStep()
        self.mock_model_manager = Mock()
        self.context = ProcessingContext(
            video_file="test_video.mp4",
            model_manager=self.mock_model_manager,
            src_lang="de",
            tgt_lang="en"
        )
        self.temp_dir = tempfile.mkdtemp()
        self.test_srt_path = os.path.join(self.temp_dir, "test.srt")
        self.context.full_srt = self.test_srt_path
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_prefers_filtered_over_full_subtitles(self):
        """Test that filtered subtitles are preferred over full subtitles."""
        self.context.filtered_srt = "filtered.srt"
        self.context.full_srt = "full.srt"
        
        with patch('concrete_processing_steps.load_subtitles') as mock_load:
            mock_load.return_value = None  # Simulate load failure
            result = self.step.execute(self.context)
        
        # Should try to load filtered subtitles first
        mock_load.assert_called_with("filtered.srt")
        self.assertFalse(result)
    
    @patch('concrete_processing_steps.load_subtitles')
    def test_translation_model_unavailable(self, mock_load):
        """Test handling when translation model is unavailable."""
        mock_load.return_value = [Mock()]
        
        # Mock model manager to return None for translation model
        self.mock_model_manager.get_translation_model_safe.return_value = (None, None)
        
        result = self.step.execute(self.context)
        self.assertFalse(result)
    
    @patch('concrete_processing_steps.load_subtitles')
    def test_tokenizer_unavailable(self, mock_load):
        """Test handling when tokenizer is unavailable."""
        mock_load.return_value = [Mock()]
        
        # Mock model manager to return model but no tokenizer
        mock_model = Mock()
        self.mock_model_manager.get_translation_model_safe.return_value = (mock_model, None)
        
        result = self.step.execute(self.context)
        self.assertFalse(result)
    
    @patch('concrete_processing_steps.load_subtitles')
    def test_translation_with_empty_subtitles(self, mock_load):
        """Test translation with empty subtitle list."""
        mock_load.return_value = []  # Empty subtitle list
        
        # Mock translation components
        mock_model = Mock()
        mock_tokenizer = Mock()
        self.mock_model_manager.get_translation_model_safe.return_value = (mock_model, mock_tokenizer)
        
        with patch('concrete_processing_steps.save_subtitles') as mock_save:
            with patch('concrete_processing_steps.pysrt.SubRipFile') as mock_srt_file:
                result = self.step.execute(self.context)
        
        self.assertTrue(result)  # Should succeed with empty list
        mock_save.assert_called_once()
    
    @patch('concrete_processing_steps.load_subtitles')
    def test_translation_model_exception(self, mock_load):
        """Test handling of translation model exceptions."""
        mock_sub = Mock()
        mock_sub.text = "Test text"
        mock_load.return_value = [mock_sub]
        
        # Mock translation components
        mock_model = Mock()
        mock_tokenizer = Mock()
        
        # Mock tokenizer to work but model to fail
        mock_inputs = Mock()
        mock_inputs.to.return_value = mock_inputs
        mock_tokenizer.return_value = mock_inputs
        mock_model.generate.side_effect = RuntimeError("CUDA out of memory")
        
        self.mock_model_manager.get_translation_model_safe.return_value = (mock_model, mock_tokenizer)
        
        result = self.step.execute(self.context)
        self.assertFalse(result)
    
    @patch('concrete_processing_steps.load_subtitles')
    def test_very_long_subtitle_text(self, mock_load):
        """Test translation of very long subtitle text."""
        # Create subtitle with very long text
        long_text = "Das ist ein sehr langer Text. " * 100  # 3000+ characters
        mock_sub = Mock()
        mock_sub.text = long_text
        mock_load.return_value = [mock_sub]
        
        # Mock translation components
        mock_model = Mock()
        mock_tokenizer = Mock()
        
        # Mock successful translation
        mock_inputs = Mock()
        mock_inputs.to.return_value = mock_inputs
        mock_tokenizer.return_value = mock_inputs
        mock_model.generate.return_value = [[1, 2, 3]]
        mock_tokenizer.decode.return_value = "This is a very long text. " * 100
        
        self.mock_model_manager.get_translation_model_safe.return_value = (mock_model, mock_tokenizer)
        
        with patch('concrete_processing_steps.save_subtitles') as mock_save:
            with patch('concrete_processing_steps.pysrt.SubRipFile') as mock_srt_file:
                result = self.step.execute(self.context)
        
        self.assertTrue(result)
        # Verify tokenizer was called with truncation
        mock_tokenizer.assert_called_with([long_text], return_tensors='pt', padding=True, truncation=True)


class TestCLIAnalysisStepAdvanced(unittest.TestCase):
    """Advanced tests for CLIAnalysisStep."""
    
    def setUp(self):
        self.step = CLIAnalysisStep()
        self.mock_model_manager = Mock()
        self.context = ProcessingContext(
            video_file="test_video.mp4",
            model_manager=self.mock_model_manager,
            known_words={"der", "die", "das", "ist", "ein", "eine"}
        )
        self.temp_dir = tempfile.mkdtemp()
        self.test_srt_path = os.path.join(self.temp_dir, "test.srt")
        self.context.full_srt = self.test_srt_path
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('concrete_processing_steps.load_subtitles')
    def test_analysis_with_large_subtitle_file(self, mock_load):
        """Test analysis performance with large subtitle file."""
        # Create large number of subtitles
        large_subtitle_list = []
        for i in range(1000):
            mock_sub = Mock()
            mock_sub.text = f"Das ist Subtitle {i} mit unbekannt"
            large_subtitle_list.append(mock_sub)
        
        mock_load.return_value = large_subtitle_list
        
        # Create the file so it exists
        with open(self.test_srt_path, 'w') as f:
            f.write("dummy content")
        
        result = self.step.execute(self.context)
        self.assertTrue(result)
    
    @patch('concrete_processing_steps.load_subtitles')
    def test_analysis_with_unicode_characters(self, mock_load):
        """Test analysis with various Unicode characters."""
        mock_sub1 = Mock()
        mock_sub1.text = "Café naïve résumé"  # French accents
        mock_sub2 = Mock()
        mock_sub2.text = "Москва Санкт-Петербург"  # Cyrillic
        mock_sub3 = Mock()
        mock_sub3.text = "東京 大阪"  # Japanese
        mock_sub4 = Mock()
        mock_sub4.text = "Ümlauts: äöüß"  # German umlauts
        
        mock_load.return_value = [mock_sub1, mock_sub2, mock_sub3, mock_sub4]
        
        # Create the file so it exists
        with open(self.test_srt_path, 'w') as f:
            f.write("dummy content")
        
        result = self.step.execute(self.context)
        self.assertTrue(result)
    
    @patch('concrete_processing_steps.load_subtitles')
    def test_analysis_with_empty_subtitles(self, mock_load):
        """Test analysis with empty subtitle texts."""
        mock_sub1 = Mock()
        mock_sub1.text = ""  # Empty text
        mock_sub2 = Mock()
        mock_sub2.text = "   "  # Whitespace only
        mock_sub3 = Mock()
        mock_sub3.text = "\n\t"  # Newlines and tabs
        
        mock_load.return_value = [mock_sub1, mock_sub2, mock_sub3]
        
        # Create the file so it exists
        with open(self.test_srt_path, 'w') as f:
            f.write("dummy content")
        
        result = self.step.execute(self.context)
        self.assertTrue(result)
    
    @patch('concrete_processing_steps.load_subtitles')
    def test_analysis_regex_edge_cases(self, mock_load):
        """Test regex pattern with edge cases."""
        mock_sub1 = Mock()
        mock_sub1.text = "123 !@# $%^ &*()"  # Numbers and symbols only
        mock_sub2 = Mock()
        mock_sub2.text = "word1-word2_word3"  # Words with separators
        mock_sub3 = Mock()
        mock_sub3.text = "UPPERCASE lowercase MiXeD"  # Case variations
        
        mock_load.return_value = [mock_sub1, mock_sub2, mock_sub3]
        
        # Create the file so it exists
        with open(self.test_srt_path, 'w') as f:
            f.write("dummy content")
        
        result = self.step.execute(self.context)
        self.assertTrue(result)
    
    @patch('concrete_processing_steps.load_subtitles')
    def test_analysis_memory_efficiency(self, mock_load):
        """Test that analysis doesn't consume excessive memory."""
        # Create subtitles with repeated patterns to test Counter efficiency
        repeated_subtitles = []
        for i in range(100):
            mock_sub = Mock()
            mock_sub.text = "schwierig unbekannt kompliziert"  # Same unknown words
            repeated_subtitles.append(mock_sub)
        
        mock_load.return_value = repeated_subtitles
        
        # Create the file so it exists
        with open(self.test_srt_path, 'w') as f:
            f.write("dummy content")
        
        result = self.step.execute(self.context)
        self.assertTrue(result)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for complete processing workflows."""
    
    def setUp(self):
        self.mock_model_manager = Mock()
        self.temp_dir = tempfile.mkdtemp()
        self.test_video_path = os.path.join(self.temp_dir, "test_video.mp4")
        
        self.context = ProcessingContext(
            video_file=self.test_video_path,
            model_manager=self.mock_model_manager,
            language="de",
            src_lang="de",
            tgt_lang="en",
            known_words={"der", "die", "das", "ist", "ein", "eine"}
        )
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_workflow_success(self):
        """Test complete workflow from transcription to translation."""
        # Create pipeline with all steps
        steps = [
            FullTranscriptionStep(),
            A1FilterStep(),
            TranslationStep()
        ]
        pipeline = ProcessingPipeline(steps)
        
        # Mock all the dependencies
        with patch('concrete_processing_steps.VideoFileClip') as mock_video_clip:
            with patch('concrete_processing_steps.load_subtitles') as mock_load:
                with patch('concrete_processing_steps.save_subtitles') as mock_save:
                    with patch('concrete_processing_steps.pysrt.SubRipFile') as mock_srt_file:
                        with patch('builtins.open', mock_open()):
                            # Setup mocks for successful execution
                            self._setup_successful_mocks(
                                mock_video_clip, mock_load, mock_save, mock_srt_file
                            )
                            
                            result = pipeline.execute(self.context)
        
        self.assertTrue(result)
        self.assertIsNotNone(self.context.full_srt)
        self.assertIsNotNone(self.context.filtered_srt)
        self.assertIsNotNone(self.context.translated_srt)
    
    def test_workflow_failure_propagation(self):
        """Test that failure in one step stops the entire workflow."""
        steps = [
            FullTranscriptionStep(),
            A1FilterStep(),  # This will fail
            TranslationStep()  # This should not execute
        ]
        pipeline = ProcessingPipeline(steps)
        
        with patch('concrete_processing_steps.VideoFileClip') as mock_video_clip:
            with patch('concrete_processing_steps.load_subtitles') as mock_load:
                # Setup transcription to succeed
                self._setup_transcription_success(mock_video_clip)
                
                # Setup filtering to fail
                mock_load.return_value = None  # This will cause filtering to fail
                
                result = pipeline.execute(self.context)
        
        self.assertFalse(result)
        self.assertIsNotNone(self.context.full_srt)  # Transcription succeeded
        self.assertIsNone(self.context.filtered_srt)  # Filtering failed
        self.assertIsNone(self.context.translated_srt)  # Translation didn't run
    
    def _setup_successful_mocks(self, mock_video_clip, mock_load, mock_save, mock_srt_file):
        """Setup mocks for successful workflow execution."""
        # Setup transcription mocks
        self._setup_transcription_success(mock_video_clip)
        
        # Setup filtering mocks
        mock_sub = Mock()
        mock_sub.text = "Das ist schwierig"  # Contains unknown word
        mock_load.return_value = [mock_sub]
        
        # Setup SpaCy mock
        mock_tokens = [Mock(text="schwierig", is_alpha=True)]
        mock_doc = Mock()
        mock_doc.__iter__ = Mock(return_value=iter(mock_tokens))
        mock_nlp = Mock(return_value=mock_doc)
        self.mock_model_manager.get_spacy_model_safe.return_value.__enter__.return_value = mock_nlp
        
        # Setup translation mocks
        mock_model = Mock()
        mock_tokenizer = Mock()
        mock_inputs = Mock()
        mock_inputs.to.return_value = mock_inputs
        mock_tokenizer.return_value = mock_inputs
        mock_model.generate.return_value = [[1, 2, 3]]
        mock_tokenizer.decode.return_value = "This is difficult"
        self.mock_model_manager.get_translation_model_safe.return_value = (mock_model, mock_tokenizer)
        
        # Setup file operations
        mock_srt_file.return_value = Mock()
    
    def _setup_transcription_success(self, mock_video_clip):
        """Setup mocks for successful transcription."""
        mock_video = Mock()
        mock_video.audio = Mock()
        mock_video_clip.return_value.__enter__.return_value = mock_video
        
        mock_whisper = Mock()
        mock_whisper.transcribe.return_value = {
            'segments': [{'text': 'Test transcription', 'start': 0, 'end': 5}]
        }
        self.mock_model_manager.get_whisper_model_safe.return_value.__enter__.return_value = mock_whisper


if __name__ == '__main__':
    unittest.main(verbosity=2)