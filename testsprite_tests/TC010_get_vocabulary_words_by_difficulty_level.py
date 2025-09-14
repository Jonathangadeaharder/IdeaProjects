import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_get_vocabulary_words_by_difficulty_level():
    """
    Test the /api/vocabulary/level/{level} GET endpoint to verify that vocabulary words are returned
    correctly filtered by the specified difficulty level, including total and known word counts.
    """
    # We will test a known CEFR level, e.g. "A1". If not existent, adjust accordingly.
    level = "A1"
    url = f"{BASE_URL}/api/vocabulary/level/{level}"

    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"HTTP request failed: {e}"

    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # Validate top-level keys
    assert isinstance(data, dict), "Response JSON is not an object"
    expected_keys = {"level", "words", "total_count", "known_count"}
    assert expected_keys.issubset(data.keys()), f"Response missing keys: {expected_keys - data.keys()}"

    # Validate 'level' matches requested level (case insensitive)
    assert data["level"].lower() == level.lower(), f"Returned level '{data['level']}' does not match requested '{level}'"

    # Validate 'words' is a list of vocabulary words
    words = data["words"]
    assert isinstance(words, list), "'words' should be a list"

    # Each word item should be a dict (VocabularyLibraryWord), check at least one if exists
    if words:
        assert all(isinstance(word, dict) for word in words), "Each vocabulary word should be a dict"

    # Validate 'total_count' and 'known_count' are integers and counts consistent
    total_count = data["total_count"]
    known_count = data["known_count"]
    assert isinstance(total_count, int) and total_count >= 0, "'total_count' should be a non-negative integer"
    assert isinstance(known_count, int) and known_count >= 0, "'known_count' should be a non-negative integer"
    assert known_count <= total_count, "'known_count' cannot be greater than 'total_count'"

test_get_vocabulary_words_by_difficulty_level()