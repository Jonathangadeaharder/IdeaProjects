#!/usr/bin/env python3
"""Script to rename test functions to follow When<Scenario>_Then<ExpectedOutcome> pattern."""

import re
import os
from pathlib import Path

# Enhanced test naming pattern mappings
RENAME_PATTERNS = [
    # Auth patterns
    (r"test_register_(.*)_returns_(.*)", r"test_WhenRegister\1_ThenReturns\2"),
    (r"test_register_(.*)_creates_(.*)", r"test_WhenRegister\1_ThenCreates\2"),
    (r"test_register_creates_(.*)", r"test_WhenRegisterCalled_ThenCreates\1"),
    (r"test_register_rejects_(.*)", r"test_WhenRegisterWith\1_ThenRejects"),
    (r"test_register_prevents_(.*)", r"test_WhenRegisterWith\1_ThenPrevents"),
    (r"test_login_(.*)_returns_(.*)", r"test_WhenLogin\1_ThenReturns\2"),
    (r"test_login_(.*)_raises_(.*)", r"test_WhenLogin\1_ThenRaises\2"),
    (r"test_login_returns_(.*)", r"test_WhenLoginCalled_ThenReturns\1"),
    (r"test_login_rejects_(.*)", r"test_WhenLoginWith\1_ThenRejects"),
    (r"test_logout_(.*)_returns_(.*)", r"test_WhenLogout\1_ThenReturns\2"),
    (r"test_validate_(.*)_raises_(.*)", r"test_WhenValidate\1_ThenRaises\2"),

    # Processing patterns
    (r"test_transcribe_returns_(.*)", r"test_WhenTranscribeCalled_ThenReturns\1"),
    (r"test_transcribe_requires_(.*)", r"test_WhenTranscribeWithout\1_ThenReturnsValidationError"),
    (r"test_chunk_rejects_(.*)", r"test_WhenChunkWith\1_ThenRejectsWithValidationError"),
    (r"test_processing_requires_(.*)", r"test_WhenProcessingWithout\1_ThenReturns401"),
    (r"test_filter_subtitles_returns_(.*)", r"test_WhenFilterSubtitlesCalled_ThenReturns\1"),
    (r"test_filter_subtitles_requires_(.*)", r"test_WhenFilterSubtitlesWithout\1_ThenRejected"),
    (r"test_translate_subtitles_returns_(.*)", r"test_WhenTranslateSubtitlesCalled_ThenReturns\1"),
    (r"test_translate_subtitles_requires_(.*)", r"test_WhenTranslateSubtitlesWithout\1_ThenValidationError"),

    # Parse/format patterns
    (r"test_parse_(.*)_returns_(.*)", r"test_WhenParse\1Called_ThenReturns\2"),
    (r"test_format_(.*)_returns_(.*)", r"test_WhenFormat\1Called_ThenReturns\2"),
    (r"test_format_(.*)_matches_(.*)", r"test_WhenFormat\1Called_ThenMatches\2"),
    (r"test_segments_to_srt_roundtrip", r"test_WhenSegmentsToSrtCalled_ThenRoundtripWorks"),

    # Additional specific patterns found in second pass
    (r"test_register_route_via_(.*)", r"test_WhenRegisterRouteVia\1_ThenSucceeds"),
    (r"test_register_route_enforces_(.*)", r"test_WhenRegisterRouteEnforces\1_ThenValidates"),
    (r"test_logout_revokes_(.*)", r"test_WhenLogoutCalled_ThenRevokes\1"),
    (r"test_logout_invalid_(.*)", r"test_WhenLogoutWithInvalid\1_ThenFails"),
    (r"test_debug_(.*)", r"test_WhenDebug\1Called_ThenSucceeds"),
    (r"test_health_endpoint_reports_(.*)", r"test_WhenHealthEndpointCalled_ThenReports\1"),
    (r"test_health_endpoint_is_(.*)", r"test_WhenHealthEndpoint_Then\1"),
    (r"test_minimal_post", r"test_WhenMinimalPostCalled_ThenSucceeds"),

    # More specific naming patterns found in codebase
    (r"test_([a-z_]+)_returns_([a-z_]+)", r"test_When\1Called_ThenReturns\2"),
    (r"test_([a-z_]+)_creates_([a-z_]+)", r"test_When\1Called_ThenCreates\2"),
    (r"test_([a-z_]+)_rejects_([a-z_]+)", r"test_When\1With\2_ThenRejects"),
    (r"test_([a-z_]+)_prevents_([a-z_]+)", r"test_When\1With\2_ThenPrevents"),
    (r"test_([a-z_]+)_matches_([a-z_]+)", r"test_When\1Called_ThenMatches\2"),
    (r"test_([a-z_]+)_requires_([a-z_]+)", r"test_When\1Without\2_ThenReturnsError"),

    # More comprehensive catch-all patterns (order matters - specific first, then general)
    (r"test_with_data_post", r"test_WhenWithDataPostCalled_ThenSucceeds"),
    (r"test_full_pipeline_fast", r"test_WhenFullPipelineFastCalled_ThenSucceeds"),
    (r"test_full_pipeline_missing_fields_returns_(.*)", r"test_WhenFullPipelineMissingFields_ThenReturns\1"),
    (r"test_filter_subtitles_missing_file_returns_(.*)", r"test_WhenFilterSubtitlesMissingFile_ThenReturns\1"),
    (r"test_chunk_endpoint_processes_(.*)", r"test_WhenChunkEndpointProcesses\1_ThenSucceeds"),
    (r"test_update_languages_accepts_(.*)", r"test_WhenUpdateLanguagesAccepts\1_ThenSucceeds"),
    (r"test_supported_languages_lists_(.*)", r"test_WhenSupportedLanguagesLists\1_ThenSucceeds"),
    (r"test_endpoints_require_(.*)", r"test_WhenEndpointsRequire\1_ThenValidates"),
    (r"test_video_upload_conflict_returns_(.*)", r"test_WhenVideoUploadConflict_ThenReturns\1"),
    (r"test_get_subtitles_serves_(.*)", r"test_WhenGetSubtitlesServes\1_ThenSucceeds"),
    (r"test_stream_video_sets_(.*)", r"test_WhenStreamVideoSets\1_ThenSucceeds"),
    (r"test_windows_absolute_(.*)", r"test_WhenWindowsAbsolute\1_ThenSucceeds"),
    (r"test_stream_video_missing_file_returns_(.*)", r"test_WhenStreamVideoMissingFile_ThenReturns\1"),
    (r"test_upload_subtitle_accepts_(.*)", r"test_WhenUploadSubtitleAccepts\1_ThenSucceeds"),
    (r"test_get_videos_includes_(.*)", r"test_WhenGetVideosIncludes\1_ThenSucceeds"),

    # General patterns
    (r"test_(.*)_endpoint_returns_(.*)", r"test_When\1EndpointCalled_ThenReturns\2"),
    (r"test_(.*)_error_returns_(.*)", r"test_When\1Error_ThenReturns\2"),
    (r"test_(.*)_updates_(.*)", r"test_When\1Called_ThenUpdates\2"),
    (r"test_(.*)_deletes_(.*)", r"test_When\1Called_ThenDeletes\2"),

    # Final catch-all for any remaining snake_case functions
    (r"test_([a-z][a-z_]*[a-z])$", r"test_When\1Called_ThenSucceeds"),
    (r"test_([a-z][a-z_]*[a-z])_([a-z][a-z_]*[a-z])$", r"test_When\1\2_ThenSucceeds"),
]

def apply_name_transformations(function_name: str) -> str:
    """Apply naming transformations to make camelCase."""
    # Convert underscores to camelCase for common patterns
    transformations = {
        'user_creates': 'UserCreates',
        'user_conflict': 'UserConflict',
        'endpoint_returns': 'EndpointReturns',
        'invalid_credentials': 'InvalidCredentials',
        'session_expired': 'SessionExpired',
        'language_preferences': 'LanguagePreferences',
        'video_path': 'VideoPath',
        'inverted_time_range': 'InvertedTimeRange',
        'task_identifier': 'TaskIdentifier',
        'task_metadata': 'TaskMetadata',
        'json_formats': 'JsonFormats',
        'json_detail': 'JsonDetail',
        'me_endpoint': 'MeEndpoint',
        'auth_states': 'AuthStates',
        'active_user': 'ActiveUser',
        'missing_email': 'MissingEmail',
        'duplicate_username': 'DuplicateUsername',
        'bearer_token': 'BearerToken',
        'wrong_password': 'WrongPassword',
        'content_returns': 'ContentReturns',
        'parse_content': 'ParseContent',
        'format_timestamp': 'FormatTimestamp',
        'segments_to_srt': 'SegmentsToSrt',
        'roundtrip_works': 'RoundtripWorks',
        'route_via': 'RouteVia',
        'contract_name': 'ContractName',
        'enforces_uuid': 'EnforcesUuid',
        'uuid_ids': 'UuidIds',
        'revokes_token': 'RevokesToken',
        'invalid_token': 'InvalidToken',
        'frontend_logs': 'FrontendLogs',
        'missing_level': 'MissingLevel',
        'debug_health': 'DebugHealth',
        'reports_status': 'ReportsStatus',
        'is_read_only': 'IsReadOnly',
        'minimal_post': 'MinimalPost',
        'with_data_post': 'WithDataPost',
        'full_pipeline_fast': 'FullPipelineFast',
        'missing_fields': 'MissingFields',
        'missing_file': 'MissingFile',
        'endpoint_processes': 'EndpointProcesses',
        'existing_video': 'ExistingVideo',
        'update_languages': 'UpdateLanguages',
        'accepts_valid': 'AcceptsValid',
        'valid_payload': 'ValidPayload',
        'supported_languages': 'SupportedLanguages',
        'lists_known': 'ListsKnown',
        'known_codes': 'KnownCodes',
        'endpoints_require': 'EndpointsRequire',
        'mandatory_fields': 'MandatoryFields',
        'video_upload': 'VideoUpload',
        'conflict_returns': 'ConflictReturns',
        'get_subtitles': 'GetSubtitles',
        'serves_existing': 'ServesExisting',
        'existing_file': 'ExistingFile',
        'stream_video': 'StreamVideo',
        'sets_accept': 'SetsAccept',
        'accept_ranges': 'AcceptRanges',
        'windows_absolute': 'WindowsAbsolute',
        'subtitle_path': 'SubtitlePath',
        'missing_file_returns': 'MissingFileReturns',
        'upload_subtitle': 'UploadSubtitle',
        'accepts_valid_file': 'AcceptsValidFile',
        'valid_file': 'ValidFile',
        'get_videos': 'GetVideos',
        'includes_expected': 'IncludesExpected',
        'expected_fields': 'ExpectedFields',
    }

    result = function_name
    for pattern, replacement in transformations.items():
        result = result.replace(pattern, replacement)

    return result

def rename_test_function(content: str) -> str:
    """Rename test functions to follow When<Scenario>_Then<ExpectedOutcome> pattern."""
    lines = content.split('\n')
    result = []

    for line in lines:
        original_line = line

        # Look for both async and sync test function definitions
        async_match = re.match(r'^(.*async def )(test_[a-zA-Z0-9_]+)(\(.*)$', line)
        sync_match = re.match(r'^(.*def )(test_[a-zA-Z0-9_]+)(\(.*)$', line)

        match = async_match or sync_match
        if match:
            prefix, function_name, suffix = match.groups()

            # Skip if already follows When...Then pattern
            if function_name.startswith('test_When') and 'Then' in function_name:
                result.append(line)
                continue

            # Skip fixture functions (conftest.py)
            if function_name in ['test_app', 'test_user', 'test_settings']:
                result.append(line)
                continue

            # Apply pattern-based renaming
            new_name = function_name
            for pattern, replacement in RENAME_PATTERNS:
                if re.match(pattern, function_name):
                    new_name = re.sub(pattern, replacement, function_name)
                    break

            # Apply additional transformations
            new_name = apply_name_transformations(new_name)

            if new_name != function_name:
                line = prefix + new_name + suffix
                print(f"  Renamed: {function_name} -> {new_name}")

        result.append(line)

    return '\n'.join(result)

def process_test_file(file_path: Path):
    """Process a single test file to rename functions."""
    if not file_path.name.startswith('test_') or not file_path.suffix == '.py':
        return False

    print(f"Processing {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    content = rename_test_function(content)

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    return False

def main():
    """Main function to process all test files."""
    backend_tests = Path("tests")
    if not backend_tests.exists():
        print("tests directory not found. Run from Backend directory.")
        return

    files_processed = 0
    files_changed = 0

    # Find all test files recursively
    for test_file in backend_tests.rglob("test_*.py"):
        # Skip conftest files which contain fixtures, not tests
        if test_file.name.startswith('conftest'):
            continue

        files_processed += 1
        if process_test_file(test_file):
            files_changed += 1

    print(f"\nProcessed {files_processed} test files, changed {files_changed} files.")

if __name__ == "__main__":
    main()