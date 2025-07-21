#!/usr/bin/env python3
"""
Comprehensive unit tests for ProcessingStep classes.
Tests critical business logic for transcription, filtering, translation, and preview processing.
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import Mock, MagicMock, patch, mock_open
from dataclasses import dataclass
from typing import Any, Optional, Set

# Import the classes under test
from processing_steps import ProcessingContext, ProcessingStep
from concrete_processing_steps import (
    PreviewTranscriptionStep,
    FullTranscriptionStep,
    A1FilterStep,
    TranslationStep,
    PreviewProcessingStep,
    CLIAnalysisStep
)


class MockModelManager:
    """Mock model manager for testing."""
    
    def __init__(self):
        self.device = 'cpu'
        self.whisper_model = Mock()
        self.spacy_model = Mock()
        self.translation_model = Mock()
        self.tokenizer = Mock()
    
    def get_whisper_model_safe(self):
        return self.whisper_model
    
    def get_spacy_model_safe(self):
        return self.spacy_model
    
    def get_translation_model_safe(self, src_lang, tgt_lang):
        return (self.translation_model, self.tokenizer)
    
    def cleanup_cuda_memory(self):
        pass


class TestProcessingContext(unittest.TestCase):
    """Test ProcessingContext functionality."""
    
    def setUp(self):
        self.mock_model_manager = MockModelManager()
        self.context = ProcessingContext(
            video_file="test_video.mp4",
            model_manager=self.mock_model_manager,
            language="de",
            src_lang="de",
            tgt_lang="en"
        )
    
    def test_context_initialization(self):
        """Test that ProcessingContext initializes correctly."""
        self.assertEqual(self.context.video_file, "test_video.mp4")
        self.assertEqual(self.context.language, "de")
        self.assertEqual(self.context.src_lang, "de")
        self.assertEqual(self.context.tgt_lang, "en")
        self.assertIsNotNone(self.context.model_manager)
    
    def test_context_implements_interfaces(self):
        """Test that ProcessingContext implements all required interfaces."""
        from processing_interfaces import (
            ITranscriptionContext,
            IFilteringContext,
            ITranslationContext,
            IPreviewProcessingContext,
            IConfigurationContext,
            IMetadataContext
        )
        
        self.assertIsInstance(self.context, ITranscriptionContext)
        self.assertIsInstance(self.context, IFilteringContext)
        self.assertIsInstance(self.context, ITranslationContext)
        self.assertIsInstance(self.context, IPreviewProcessingContext)
        self.assertIsInstance(self.context, IConfigurationContext)
        self.assertIsInstance(self.context, IMetadataContext)


class TestPreviewTranscriptionStep(unittest.TestCase):
    """Test PreviewTranscriptionStep business logic."""
    
    def setUp(self):
        self.step = PreviewTranscriptionStep()
        self.mock_model_manager = MockModelManager()
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
    def test_skip_preview_when_disabled(self, mock_video_clip):
        """Test that preview is skipped when no_preview is True."""
        self.context.no_preview = True
        result = self.step.execute(self.context)
        self.assertTrue(result)
        mock_video_clip.assert_not_called()
    
    @patch('concrete_processing_steps.VideoFileClip')
    def test_skip_preview_for_short_video(self, mock_video_clip):
        """Test that preview is skipped for videos <= 10 minutes."""
        mock_video = Mock()
        mock_video.duration = 300  # 5 minutes
        mock_video.audio = Mock()
        mock_video_clip.return_value.__enter__.return_value = mock_video
        
        result = self.step.execute(self.context)
        self.assertTrue(result)
    
    @patch('concrete_processing_steps.VideoFileClip')
    def test_error_on_no_audio(self, mock_video_clip):
        """Test error handling when video has no audio."""
        mock_video = Mock()
        mock_video.duration = 1200  # 20 minutes
        mock_video.audio = None
        mock_video_clip.return_value.__enter__.return_value = mock_video
        
        result = self.step.execute(self.context)
        self.assertFalse(result)
    
    @patch('concrete_processing_steps.VideoFileClip')
    @patch('builtins.open', new_callable=mock_open)
    @patch('concrete_processing_steps.dict_to_srt')
    def test_successful_preview_creation(self, mock_dict_to_srt, mock_file, mock_video_clip):
        """Test successful preview subtitle creation."""
        # Setup mocks
        mock_video = Mock()
        mock_video.duration = 1200  # 20 minutes
        mock_audio = Mock()
        mock_video.audio = mock_audio
        mock_video_clip.return_value.__enter__.return_value = mock_video
        
        # Mock audio subclipping and transcription
        mock_audio_10min = Mock()
        mock_audio.subclipped.return_value = mock_audio_10min
        
        # Mock whisper model
        mock_whisper = Mock()
        mock_whisper.transcribe.return_value = {
            'segments': [{'text': 'Test transcription', 'start': 0, 'end': 5}]
        }
        self.mock_model_manager.whisper_model.__enter__.return_value = mock_whisper
        
        mock_dict_to_srt.return_value = "Test SRT content"
        
        result = self.step.execute(self.context)
        self.assertTrue(result)
        self.assertIsNotNone(self.context.preview_srt)
        mock_whisper.transcribe.assert_called_once()


class TestA1FilterStep(unittest.TestCase):
    """Test A1FilterStep business logic."""
    
    def setUp(self):
        self.step = A1FilterStep()
        self.mock_model_manager = MockModelManager()
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
    
    def test_error_when_no_subtitle_file(self):
        """Test error handling when no subtitle file is available."""
        self.context.full_srt = None
        result = self.step.execute(self.context)
        self.assertFalse(result)
    
    def test_error_when_no_known_words(self):
        """Test error handling when known_words is not provided."""
        self.context.known_words = None
        
        with patch('concrete_processing_steps.load_subtitles') as mock_load:
            mock_load.return_value = [Mock()]
            result = self.step.execute(self.context)
            self.assertFalse(result)
    
    @patch('concrete_processing_steps.load_subtitles')
    @patch('concrete_processing_steps.save_subtitles')
    @patch('concrete_processing_steps.pysrt.SubRipFile')
    def test_successful_filtering(self, mock_srt_file, mock_save, mock_load):
        """Test successful subtitle filtering."""
        # Mock subtitle data
        mock_sub1 = Mock()
        mock_sub1.text = "Das ist ein Test"  # All known words
        mock_sub2 = Mock()
        mock_sub2.text = "Das ist schwierig"  # Contains unknown word 'schwierig'
        mock_load.return_value = [mock_sub1, mock_sub2]
        
        # Mock SpaCy model
        mock_token1 = Mock()
        mock_token1.text = "das"
        mock_token1.is_alpha = True
        mock_token2 = Mock()
        mock_token2.text = "ist"
        mock_token2.is_alpha = True
        mock_token3 = Mock()
        mock_token3.text = "schwierig"
        mock_token3.is_alpha = True
        
        mock_doc = Mock()
        mock_doc.__iter__ = Mock(return_value=iter([mock_token1, mock_token2, mock_token3]))
        
        mock_nlp = Mock()
        mock_nlp.return_value = mock_doc
        self.mock_model_manager.spacy_model.__enter__.return_value = mock_nlp
        
        # Mock filtered subtitles container
        mock_filtered_subs = Mock()
        mock_srt_file.return_value = mock_filtered_subs
        
        result = self.step.execute(self.context)
        self.assertTrue(result)
        self.assertIsNotNone(self.context.filtered_srt)
        mock_save.assert_called_once()


class TestTranslationStep(unittest.TestCase):
    """Test TranslationStep business logic."""
    
    def setUp(self):
        self.step = TranslationStep()
        self.mock_model_manager = MockModelManager()
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
    
    def test_error_when_no_subtitle_file(self):
        """Test error handling when no subtitle file is available."""
        self.context.full_srt = None
        self.context.filtered_srt = None
        result = self.step.execute(self.context)
        self.assertFalse(result)
    
    @patch('concrete_processing_steps.load_subtitles')
    @patch('concrete_processing_steps.save_subtitles')
    @patch('concrete_processing_steps.pysrt.SubRipFile')
    def test_successful_translation(self, mock_srt_file, mock_save, mock_load):
        """Test successful subtitle translation."""
        # Mock subtitle data
        mock_sub = Mock()
        mock_sub.text = "Das ist ein Test"
        mock_load.return_value = [mock_sub]
        
        # Mock translation model and tokenizer
        mock_model = Mock()
        mock_tokenizer = Mock()
        
        # Mock tokenizer inputs
        mock_inputs = Mock()
        mock_inputs.to.return_value = mock_inputs
        mock_tokenizer.return_value = mock_inputs
        
        # Mock model generation
        mock_translated = [[1, 2, 3]]  # Mock token IDs
        mock_model.generate.return_value = mock_translated
        
        # Mock tokenizer decode
        mock_tokenizer.decode.return_value = "This is a test"
        
        self.mock_model_manager.translation_model = mock_model
        self.mock_model_manager.tokenizer = mock_tokenizer
        
        # Mock translated subtitles container
        mock_translated_subs = Mock()
        mock_srt_file.return_value = mock_translated_subs
        
        result = self.step.execute(self.context)
        self.assertTrue(result)
        self.assertIsNotNone(self.context.translated_srt)
        mock_save.assert_called_once()
        self.assertEqual(mock_sub.text, "This is a test")


class TestCLIAnalysisStep(unittest.TestCase):
    """Test CLIAnalysisStep business logic."""
    
    def setUp(self):
        self.step = CLIAnalysisStep()
        self.mock_model_manager = MockModelManager()
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
    
    def test_error_when_no_subtitle_file(self):
        """Test error handling when subtitle file doesn't exist."""
        self.context.full_srt = None
        result = self.step.execute(self.context)
        self.assertFalse(result)
    
    @patch('concrete_processing_steps.load_subtitles')
    def test_error_when_subtitles_fail_to_load(self, mock_load):
        """Test error handling when subtitles fail to load."""
        mock_load.return_value = None
        
        # Create the file so it exists
        with open(self.test_srt_path, 'w') as f:
            f.write("dummy content")
        
        result = self.step.execute(self.context)
        self.assertFalse(result)
    
    @patch('concrete_processing_steps.load_subtitles')
    def test_successful_analysis(self, mock_load):
        """Test successful subtitle analysis."""
        # Mock subtitle data with various scenarios
        mock_sub1 = Mock()
        mock_sub1.text = "Das ist ein Test"  # All known words
        mock_sub2 = Mock()
        mock_sub2.text = "Das ist schwierig"  # One unknown word
        mock_sub3 = Mock()
        mock_sub3.text = "Kompliziert und schwierig"  # Multiple unknown words
        
        mock_load.return_value = [mock_sub1, mock_sub2, mock_sub3]
        
        # Create the file so it exists
        with open(self.test_srt_path, 'w') as f:
            f.write("dummy content")
        
        result = self.step.execute(self.context)
        self.assertTrue(result)


class TestPreviewProcessingStep(unittest.TestCase):
    """Test PreviewProcessingStep business logic."""
    
    def setUp(self):
        self.step = PreviewProcessingStep()
        self.mock_model_manager = MockModelManager()
        self.context = ProcessingContext(
            video_file="test_video.mp4",
            model_manager=self.mock_model_manager,
            known_words={"der", "die", "das"},
            src_lang="de",
            tgt_lang="en"
        )
        self.temp_dir = tempfile.mkdtemp()
        self.preview_srt_path = os.path.join(self.temp_dir, "preview.srt")
        self.context.preview_srt = self.preview_srt_path
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_skip_when_no_preview_subtitles(self):
        """Test that step is skipped when no preview subtitles are available."""
        self.context.preview_srt = None
        result = self.step.execute(self.context)
        self.assertTrue(result)
    
    @patch('concrete_processing_steps.A1FilterStep')
    @patch('concrete_processing_steps.TranslationStep')
    def test_successful_preview_processing(self, mock_translation_class, mock_filter_class):
        """Test successful preview processing with filtering and translation."""
        # Mock the filter and translation steps
        mock_filter_step = Mock()
        mock_filter_step.execute.return_value = True
        mock_filter_class.return_value = mock_filter_step
        
        mock_translation_step = Mock()
        mock_translation_step.execute.return_value = True
        mock_translation_class.return_value = mock_translation_step
        
        result = self.step.execute(self.context)
        self.assertTrue(result)
        mock_filter_step.execute.assert_called_once()
        mock_translation_step.execute.assert_called_once()
    
    @patch('concrete_processing_steps.A1FilterStep')
    def test_failure_when_filtering_fails(self, mock_filter_class):
        """Test failure handling when filtering step fails."""
        mock_filter_step = Mock()
        mock_filter_step.execute.return_value = False
        mock_filter_class.return_value = mock_filter_step
        
        result = self.step.execute(self.context)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main(verbosity=2)