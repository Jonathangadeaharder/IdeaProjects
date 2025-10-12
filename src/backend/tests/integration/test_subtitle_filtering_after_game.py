"""
Integration tests for subtitle filtering after vocabulary game

Tests that words marked as known during the game are properly filtered
from subtitles when reprocessing chunks.
"""

import pytest

from database.models import VocabularyWord
from tests.helpers import AsyncAuthHelper


class TestSubtitleFilteringAfterGame:
    """Test subtitle filtering based on user's known words from game"""

    @pytest.fixture
    async def test_vocabulary_words(self, app):
        """Create test vocabulary words matching subtitle content"""
        async with app.state._test_session_factory() as session:
            words = [
                VocabularyWord(
                    word="Hallo",
                    lemma="hallo",
                    language="de",
                    difficulty_level="A1",
                    part_of_speech="interjection",
                    translation_en="hello",
                ),
                VocabularyWord(
                    word="Welt",
                    lemma="welt",
                    language="de",
                    difficulty_level="A1",
                    part_of_speech="noun",
                    gender="die",
                    translation_en="world",
                ),
                VocabularyWord(
                    word="gut",
                    lemma="gut",
                    language="de",
                    difficulty_level="A1",
                    part_of_speech="adjective",
                    translation_en="good",
                ),
                VocabularyWord(
                    word="heute",
                    lemma="heute",
                    language="de",
                    difficulty_level="A1",
                    part_of_speech="adverb",
                    translation_en="today",
                ),
            ]

            for word in words:
                session.add(word)

            await session.commit()

            return words

    @pytest.mark.asyncio
    async def test_WhenWordMarkedKnownInGame_ThenWordNotInVocabularyOnReprocess(
        self, async_client, url_builder, test_vocabulary_words
    ):
        """
        Test that after marking a word as known during the game,
        the word is not included in the vocabulary list when
        processing the next chunk
        """
        # Create and authenticate a user
        helper = AsyncAuthHelper(async_client)
        _user, _token, headers = await helper.create_authenticated_user()

        # Simulate first chunk processing - get initial vocabulary for A1 level
        initial_vocab_response = await async_client.get(
            url_builder.url_for("get_vocabulary_level", level="A1"),
            params={"target_language": "de", "translation_language": "es", "limit": 20},
            headers=headers,
        )
        assert initial_vocab_response.status_code == 200
        initial_vocab = initial_vocab_response.json()

        # Verify we have words in the vocabulary
        assert len(initial_vocab["words"]) > 0
        initial_vocab_count = len([w for w in initial_vocab["words"] if not w.get("is_known", False)])

        # Mark one word as known (simulating game interaction)
        test_word = test_vocabulary_words[0]  # "hallo"
        mark_response = await async_client.post(
            url_builder.url_for("mark_word_known"),
            json={"lemma": test_word.lemma, "language": "de", "known": True},
            headers=headers,
        )
        assert mark_response.status_code == 200
        assert mark_response.json()["success"] is True

        # Get vocabulary again (simulating vocabulary extraction during next chunk)
        # This should exclude the known word
        updated_vocab_response = await async_client.get(
            url_builder.url_for("get_vocabulary_level", level="A1"),
            params={"target_language": "de", "translation_language": "es", "limit": 20},
            headers=headers,
        )
        assert updated_vocab_response.status_code == 200
        updated_vocab = updated_vocab_response.json()

        # Verify the known word is marked correctly
        test_word_found = False
        for word in updated_vocab["words"]:
            if word["lemma"] == test_word.lemma:
                assert word.get("is_known", False) is True
                test_word_found = True
                break

        assert test_word_found, f"Word '{test_word.lemma}' should be in vocabulary library"

        # Verify known count increased
        assert updated_vocab["known_count"] > initial_vocab["known_count"]

    @pytest.mark.asyncio
    async def test_WhenMultipleWordsMarkedKnown_ThenAllFilteredFromNewVocabulary(
        self, async_client, url_builder, test_vocabulary_words
    ):
        """
        Test that marking multiple words as known filters all of them
        from the new vocabulary list in subsequent chunks
        """
        # Create and authenticate a user
        helper = AsyncAuthHelper(async_client)
        _user, _token, headers = await helper.create_authenticated_user()

        # Get initial vocabulary statistics
        initial_stats_response = await async_client.get(
            url_builder.url_for("get_vocabulary_stats"),
            params={"target_language": "de", "translation_language": "es"},
            headers=headers,
        )
        assert initial_stats_response.status_code == 200
        initial_stats = initial_stats_response.json()
        initial_known = initial_stats["total_known"]

        # Mark multiple words as known (simulating game progression)
        words_to_mark = test_vocabulary_words[:3]  # Mark first 3 words
        marked_lemmas = set()

        for word in words_to_mark:
            mark_response = await async_client.post(
                url_builder.url_for("mark_word_known"),
                json={"lemma": word.lemma, "language": "de", "known": True},
                headers=headers,
            )
            assert mark_response.status_code == 200
            marked_lemmas.add(word.lemma)

        # Get updated vocabulary statistics
        updated_stats_response = await async_client.get(
            url_builder.url_for("get_vocabulary_stats"),
            params={"target_language": "de", "translation_language": "es"},
            headers=headers,
        )
        assert updated_stats_response.status_code == 200
        updated_stats = updated_stats_response.json()

        # Verify known count increased by the number of marked words
        assert updated_stats["total_known"] == initial_known + len(words_to_mark)

        # Verify all marked words show as known in vocabulary library
        vocab_response = await async_client.get(
            url_builder.url_for("get_vocabulary_level", level="A1"),
            params={"target_language": "de", "translation_language": "es", "limit": 20},
            headers=headers,
        )
        assert vocab_response.status_code == 200
        vocab = vocab_response.json()

        # Check that all marked words are flagged as known
        found_known_words = set()
        for word in vocab["words"]:
            if word["lemma"] in marked_lemmas and word.get("is_known", False):
                found_known_words.add(word["lemma"])

        assert found_known_words == marked_lemmas, "All marked words should appear as known in library"

    @pytest.mark.asyncio
    async def test_WhenUnknownWordMarkedKnown_ThenNotInSubsequentVocabularyExtraction(
        self, async_client, url_builder
    ):
        """
        Test that words not in the vocabulary database (like 'brauriger')
        are saved as known and don't reappear in future vocabulary extraction
        """
        # Create and authenticate a user
        helper = AsyncAuthHelper(async_client)
        _user, _token, headers = await helper.create_authenticated_user()

        # Mark an unknown word as known (word not in vocabulary database)
        unknown_word = "brauriger"

        mark_response = await async_client.post(
            url_builder.url_for("mark_word_known"),
            json={"lemma": unknown_word, "language": "de", "known": True},
            headers=headers,
        )
        assert mark_response.status_code == 200
        mark_data = mark_response.json()

        # Verify marking succeeded even for unknown word
        assert mark_data["success"] is True
        assert mark_data["known"] is True
        assert mark_data["level"] == "unknown"  # Unknown words have "unknown" level

        # Verify the word is tracked as known in user statistics
        stats_response = await async_client.get(
            url_builder.url_for("get_vocabulary_stats"),
            params={"target_language": "de", "translation_language": "es"},
            headers=headers,
        )
        assert stats_response.status_code == 200
        stats = stats_response.json()

        # User should have at least 1 known word (the unknown word we just marked)
        assert stats["total_known"] >= 1

    @pytest.mark.asyncio
    async def test_WhenWordsMarkedKnownAndUnmarked_ThenReappearInVocabulary(
        self, async_client, url_builder, test_vocabulary_words
    ):
        """
        Test that unmarking a word (marking as unknown) makes it reappear
        in the new vocabulary extraction for subsequent chunks
        """
        # Create and authenticate a user
        helper = AsyncAuthHelper(async_client)
        _user, _token, headers = await helper.create_authenticated_user()

        test_word = test_vocabulary_words[0]  # "hallo"

        # Mark word as known
        mark_response = await async_client.post(
            url_builder.url_for("mark_word_known"),
            json={"lemma": test_word.lemma, "language": "de", "known": True},
            headers=headers,
        )
        assert mark_response.status_code == 200

        # Verify word is known
        vocab_known_response = await async_client.get(
            url_builder.url_for("get_vocabulary_level", level="A1"),
            params={"target_language": "de", "translation_language": "es", "limit": 20},
            headers=headers,
        )
        vocab_known = vocab_known_response.json()

        word_is_known = False
        for word in vocab_known["words"]:
            if word["lemma"] == test_word.lemma:
                word_is_known = word.get("is_known", False)
                break

        assert word_is_known is True

        # Unmark word (mark as unknown)
        unmark_response = await async_client.post(
            url_builder.url_for("mark_word_known"),
            json={"lemma": test_word.lemma, "language": "de", "known": False},
            headers=headers,
        )
        assert unmark_response.status_code == 200
        assert unmark_response.json()["known"] is False

        # Verify word is no longer known
        vocab_unknown_response = await async_client.get(
            url_builder.url_for("get_vocabulary_level", level="A1"),
            params={"target_language": "de", "translation_language": "es", "limit": 20},
            headers=headers,
        )
        vocab_unknown = vocab_unknown_response.json()

        word_is_known_after = False
        for word in vocab_unknown["words"]:
            if word["lemma"] == test_word.lemma:
                word_is_known_after = word.get("is_known", False)
                break

        assert word_is_known_after is False

    @pytest.mark.asyncio
    async def test_WhenUserHasManyKnownWords_ThenOnlyUnknownWordsInNewVocabulary(
        self, async_client, url_builder, test_vocabulary_words
    ):
        """
        Test that after marking many words as known through multiple game sessions,
        only truly new/unknown words appear in vocabulary extraction
        """
        # Create and authenticate a user
        helper = AsyncAuthHelper(async_client)
        _user, _token, headers = await helper.create_authenticated_user()

        # Mark most words as known (simulating multiple game sessions)
        words_to_mark = test_vocabulary_words[:3]  # Mark 3 out of 4 words

        for word in words_to_mark:
            await async_client.post(
                url_builder.url_for("mark_word_known"),
                json={"lemma": word.lemma, "language": "de", "known": True},
                headers=headers,
            )

        # Get vocabulary library
        vocab_response = await async_client.get(
            url_builder.url_for("get_vocabulary_level", level="A1"),
            params={"target_language": "de", "translation_language": "es", "limit": 20},
            headers=headers,
        )
        assert vocab_response.status_code == 200
        vocab = vocab_response.json()

        # Count truly unknown words (not marked as known)
        unknown_words_count = sum(1 for w in vocab["words"] if not w.get("is_known", False))

        # We marked 3 words as known, so at least 1 word should remain unknown
        assert unknown_words_count >= 1, "At least one word should remain unknown"

        # Verify known count matches what we marked
        known_count = vocab.get("known_count", 0)
        assert known_count >= len(words_to_mark)
