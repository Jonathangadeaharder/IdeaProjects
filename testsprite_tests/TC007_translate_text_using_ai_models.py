import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_translate_text_using_ai_models():
    url = f"{BASE_URL}/processing/translate"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "text": "Hallo Welt",
        "source_lang": "de",
        "target_lang": "en"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Request to translate endpoint failed: {e}"

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # Check at least one string value differs from input text (min validation)
    values_as_strings = [v for v in data.values() if isinstance(v, str)]
    assert any(v.strip() and v.strip().lower() != payload["text"].lower() for v in values_as_strings), "Translated text should differ from source text"


test_translate_text_using_ai_models()
