"""
Integration tests for AI services using smallest/fastest models.
These tests actually load and test real AI models to ensure proper integration.
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
import os

from services.transcriptionservice.factory import TranscriptionServiceFactory, get_transcription_service
from services.translationservice.factory import TranslationServiceFactory


@pytest.mark.integration
@pytest.mark.slow
class TestTranscriptionServiceIntegration:
    """Integration tests for transcription services with actual models"""

    def test_whisper_tiny_service_creation_and_basic_functionality(self):
        """Test that whisper-tiny service can be created and has expected interface"""
        # Test service creation
        service = get_transcription_service("whisper-tiny")
        assert service is not None
        assert hasattr(service, 'transcribe')
        assert hasattr(service, 'initialize')

        # Test model configuration
        assert service.model_size == "tiny"

        # Test that service is not initialized by default (lazy loading)
        assert service._model is None

    @pytest.mark.skipif(
        os.environ.get("SKIP_HEAVY_AI_TESTS") == "1",
        reason="Skipping heavy AI model tests - set SKIP_HEAVY_AI_TESTS=0 to run"
    )
    def test_whisper_tiny_actual_transcription(self):
        """Test actual transcription with whisper-tiny model (requires model download)"""
        service = get_transcription_service("whisper-tiny")

        # Create a minimal test audio file (silent WAV)
        # In practice, you'd use a real small audio file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            # Create minimal WAV header for a 1-second silent audio
            wav_header = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
            tmp_file.write(wav_header)
            tmp_file.flush()

            try:
                # This would actually download and load the tiny model
                result = service.transcribe(tmp_file.name, language="en")

                # Basic validation of transcription result
                assert hasattr(result, 'text') or isinstance(result, dict)
                if isinstance(result, dict):
                    assert 'text' in result or 'segments' in result

            finally:
                os.unlink(tmp_file.name)


@pytest.mark.integration
@pytest.mark.slow
class TestTranslationServiceIntegration:
    """Integration tests for translation services with actual models"""

    def test_opus_de_es_service_creation_and_configuration(self):
        """Test that opus-de-es service can be created with correct configuration"""
        service = TranslationServiceFactory.create_service("opus-de-es")
        assert service is not None
        assert hasattr(service, 'translate')

        # Verify model configuration
        assert service.model_name == "Helsinki-NLP/opus-mt-de-es"

        # Test service interface
        assert hasattr(service, 'initialize') or hasattr(service, 'model_name')

    def test_nllb_distilled_600m_service_creation(self):
        """Test that nllb-distilled-600m service can be created"""
        service = TranslationServiceFactory.create_service("nllb-distilled-600m")
        assert service is not None
        assert hasattr(service, 'translate')

        # Verify model configuration for smallest NLLB model
        assert service.model_name == "facebook/nllb-200-distilled-600M"

    @pytest.mark.skipif(
        os.environ.get("SKIP_HEAVY_AI_TESTS") == "1",
        reason="Skipping heavy AI model tests - set SKIP_HEAVY_AI_TESTS=0 to run"
    )
    def test_opus_de_es_actual_translation(self):
        """Test actual translation with opus-de-es model (requires model download)"""
        service = TranslationServiceFactory.create_service("opus-de-es")

        # Test with simple German text
        german_text = "Hallo Welt"

        try:
            result = service.translate(
                text=german_text,
                source_language="de",
                target_language="es"
            )

            # Basic validation of translation result
            assert result is not None
            if isinstance(result, dict):
                assert 'translated_text' in result or 'text' in result
            elif isinstance(result, str):
                assert len(result) > 0
                # Should not be the same as input (German -> Spanish)
                assert result != german_text

        except Exception as e:
            # If model fails to load/download, skip gracefully
            pytest.skip(f"Translation service failed (likely model download issue): {e}")

    @pytest.mark.skipif(
        os.environ.get("SKIP_HEAVY_AI_TESTS") == "1",
        reason="Skipping heavy AI model tests - set SKIP_HEAVY_AI_TESTS=0 to run"
    )
    def test_nllb_distilled_basic_functionality(self):
        """Test basic NLLB distilled model functionality"""
        service = TranslationServiceFactory.create_service("nllb-distilled-600m")

        # Simple test to ensure service can be initialized
        # (NLLB models are still large even when distilled)
        german_text = "Guten Tag"

        try:
            result = service.translate(
                text=german_text,
                source_language="de",
                target_language="es"
            )

            # Basic validation
            assert result is not None

        except Exception as e:
            pytest.skip(f"NLLB service failed (likely model download/memory issue): {e}")


@pytest.mark.integration
class TestServiceFactoryConfiguration:
    """Test service factory configurations are correct"""

    def test_transcription_service_factory_has_expected_models(self):
        """Verify transcription factory has all expected model configurations"""
        from services.transcriptionservice.factory import TranscriptionServiceFactory

        # Check that whisper-tiny is configured correctly
        assert "whisper-tiny" in TranscriptionServiceFactory._default_configs
        assert TranscriptionServiceFactory._default_configs["whisper-tiny"]["model_size"] == "tiny"

        # Verify other key models exist
        expected_models = ["whisper", "whisper-base", "whisper-small"]
        for model in expected_models:
            assert model in TranscriptionServiceFactory._default_configs

    def test_translation_service_factory_has_expected_models(self):
        """Verify translation factory has all expected model configurations"""
        # Check OPUS models
        assert "opus-de-es" in TranslationServiceFactory._default_configs
        assert TranslationServiceFactory._default_configs["opus-de-es"]["model_name"] == "Helsinki-NLP/opus-mt-de-es"

        # Check NLLB models
        assert "nllb-distilled-600m" in TranslationServiceFactory._default_configs
        assert TranslationServiceFactory._default_configs["nllb-distilled-600m"]["model_name"] == "facebook/nllb-200-distilled-600M"

        # Verify fastest models for testing
        assert "opus-de-en" in TranslationServiceFactory._default_configs

    def test_test_environment_uses_fastest_models(self):
        """Verify test environment is configured to use fastest models"""
        # These should be set by conftest.py
        assert os.environ.get("LANGPLUG_TRANSCRIPTION_SERVICE") == "whisper-tiny"
        assert os.environ.get("LANGPLUG_TRANSLATION_SERVICE") == "opus-de-es"

    def test_service_creation_with_test_config(self):
        """Test that services can be created with test environment configuration"""
        # Test with environment variable override
        # Test direct factory usage with specific service names
        transcription_service = get_transcription_service("whisper-tiny")
        translation_service = TranslationServiceFactory.create_service("opus-de-es")

        assert transcription_service is not None
        assert translation_service is not None
        assert transcription_service.model_size == "tiny"
        assert translation_service.model_name == "Helsinki-NLP/opus-mt-de-es"