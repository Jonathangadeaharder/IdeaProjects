"""
Integration tests for vocabulary game and library integration

Tests that words marked as known during the game correctly appear
in the vocabulary library with the proper known status.
"""

import pytest
from database.models import VocabularyWord
from tests.helpers import AsyncAuthHelper


class TestGameVocabularyLibraryIntegration:
    """Test integration between vocabulary game and vocabulary library"""

    @pytest.fixture
    async def test_vocabulary_words(self, app):
        """Create test vocabulary words in the database"""
        # Get a database session from the app's test session factory
        async with app.state._test_session_factory() as session:
            words = [
                VocabularyWord(
                    word="Haus",
                    lemma="haus",
                    language="de",
                    difficulty_level="A1",
                    part_of_speech="noun",
                    gender="das",
                    translation_en="house",
                ),
                VocabularyWord(
                    word="Buch",
                    lemma="buch",
                    language="de",
                    difficulty_level="A1",
                    part_of_speech="noun",
                    gender="das",
                    translation_en="book",
                ),
                VocabularyWord(
                    word="schon",
                    lemma="schon",
                    language="de",
                    difficulty_level="A2",
                    part_of_speech="adverb",
                    translation_en="already",
                ),
            ]

            for word in words:
                session.add(word)

            await session.commit()

            return words

    @pytest.mark.asyncio
    async def test_WhenWordMarkedKnownInGame_ThenAppearsInVocabularyLibraryAsKnown(
        self, async_client, url_builder, test_vocabulary_words
    ):
        """
        Test that marking a word as known during vocabulary game
        makes it appear as known in the vocabulary library
        """
        # Create and authenticate a user
        helper = AsyncAuthHelper(async_client)
        user, _token, headers = await helper.create_authenticated_user()

        # Get initial vocabulary library state for A1 level
        initial_library_response = await async_client.get(
            url_builder.url_for("get_vocabulary_level", level="A1"),
            params={"target_language": "de", "translation_language": "es", "limit": 10},
            headers=headers,
        )
        assert initial_library_response.status_code == 200
        initial_library = initial_library_response.json()

        # Verify initial state - words should exist but not be marked as known
        initial_known_count = initial_library.get("known_count", 0)
        test_word_lemma = test_vocabulary_words[0].lemma  # "haus"

        # Find the test word in initial library
        initial_word_status = None
        for word in initial_library["words"]:
            if word["lemma"] == test_word_lemma:
                initial_word_status = word.get("is_known", False)
                break

        assert initial_word_status is False, "Word should not be marked as known initially"

        # Mark word as known (simulating what happens during game)
        mark_response = await async_client.post(
            url_builder.url_for("mark_word_known"),
            json={"lemma": test_word_lemma, "language": "de", "known": True},
            headers=headers,
        )
        assert mark_response.status_code == 200
        mark_data = mark_response.json()

        # Verify marking was successful
        assert mark_data["success"] is True
        assert mark_data["known"] is True
        assert mark_data["lemma"] == test_word_lemma

        # Query vocabulary library again
        updated_library_response = await async_client.get(
            url_builder.url_for("get_vocabulary_level", level="A1"),
            params={"target_language": "de", "translation_language": "es", "limit": 10},
            headers=headers,
        )
        assert updated_library_response.status_code == 200
        updated_library = updated_library_response.json()

        # Verify known count increased
        updated_known_count = updated_library.get("known_count", 0)
        assert updated_known_count == initial_known_count + 1

        # Verify the specific word now shows as known
        word_found = False
        for word in updated_library["words"]:
            if word["lemma"] == test_word_lemma:
                assert word.get("is_known", False) is True, f"Word '{test_word_lemma}' should be marked as known"
                word_found = True
                break

        assert word_found, f"Word '{test_word_lemma}' should appear in vocabulary library"

    @pytest.mark.asyncio
    async def test_WhenMultipleWordsMarkedKnownInGame_ThenAllAppearInVocabularyLibrary(
        self, async_client, url_builder, test_vocabulary_words
    ):
        """
        Test marking multiple words as known during game session
        and verifying they all appear correctly in vocabulary library
        """
        # Create and authenticate a user
        helper = AsyncAuthHelper(async_client)
        user, _token, headers = await helper.create_authenticated_user()

        # Get initial statistics
        initial_stats_response = await async_client.get(
            url_builder.url_for("get_vocabulary_stats"),
            params={"target_language": "de", "translation_language": "es"},
            headers=headers,
        )
        assert initial_stats_response.status_code == 200
        initial_stats = initial_stats_response.json()
        initial_total_known = initial_stats.get("total_known", 0)

        # Mark multiple words as known (simulating game progression)
        words_to_mark = [test_vocabulary_words[0], test_vocabulary_words[1]]  # Mark "haus" and "buch"
        marked_lemmas = []

        for word in words_to_mark:
            mark_response = await async_client.post(
                url_builder.url_for("mark_word_known"),
                json={"lemma": word.lemma, "language": "de", "known": True},
                headers=headers,
            )
            assert mark_response.status_code == 200
            assert mark_response.json()["success"] is True
            marked_lemmas.append(word.lemma)

        # Verify statistics updated correctly
        updated_stats_response = await async_client.get(
            url_builder.url_for("get_vocabulary_stats"),
            params={"target_language": "de", "translation_language": "es"},
            headers=headers,
        )
        assert updated_stats_response.status_code == 200
        updated_stats = updated_stats_response.json()
        updated_total_known = updated_stats.get("total_known", 0)

        assert updated_total_known == initial_total_known + len(words_to_mark)

        # Verify all marked words appear as known in vocabulary library
        library_response = await async_client.get(
            url_builder.url_for("get_vocabulary_level", level="A1"),
            params={"target_language": "de", "translation_language": "es", "limit": 20},
            headers=headers,
        )
        assert library_response.status_code == 200
        library = library_response.json()

        # Check each marked word
        found_words = set()
        for word in library["words"]:
            if word["lemma"] in marked_lemmas:
                assert word.get("is_known", False) is True, f"Word '{word['lemma']}' should be marked as known"
                found_words.add(word["lemma"])

        assert found_words == set(marked_lemmas), "All marked words should appear in vocabulary library"

    @pytest.mark.asyncio
    async def test_WhenWordUnmarkedInVocabularyLibrary_ThenRemovedFromKnownList(
        self, async_client, url_builder, test_vocabulary_words
    ):
        """
        Test vocabulary library management: unmarking a word (marking as unknown)
        correctly removes it from known words in vocabulary library.

        Note: This is for library management UI, not the game. The game should
        never show words that are already marked as known.
        """
        # Create and authenticate a user
        helper = AsyncAuthHelper(async_client)
        user, _token, headers = await helper.create_authenticated_user()

        test_word_lemma = test_vocabulary_words[0].lemma  # "haus"

        # Mark word as known
        mark_known_response = await async_client.post(
            url_builder.url_for("mark_word_known"),
            json={"lemma": test_word_lemma, "language": "de", "known": True},
            headers=headers,
        )
        assert mark_known_response.status_code == 200

        # Verify word shows as known
        library_after_marking = await async_client.get(
            url_builder.url_for("get_vocabulary_level", level="A1"),
            params={"target_language": "de", "translation_language": "es", "limit": 10},
            headers=headers,
        )
        library_after_marking_data = library_after_marking.json()

        word_is_known = False
        for word in library_after_marking_data["words"]:
            if word["lemma"] == test_word_lemma:
                word_is_known = word.get("is_known", False)
                break

        assert word_is_known is True

        # Mark word as unknown
        mark_unknown_response = await async_client.post(
            url_builder.url_for("mark_word_known"),
            json={"lemma": test_word_lemma, "language": "de", "known": False},
            headers=headers,
        )
        assert mark_unknown_response.status_code == 200
        assert mark_unknown_response.json()["known"] is False

        # Verify word no longer shows as known
        library_after_unmarking = await async_client.get(
            url_builder.url_for("get_vocabulary_level", level="A1"),
            params={"target_language": "de", "translation_language": "es", "limit": 10},
            headers=headers,
        )
        library_after_unmarking_data = library_after_unmarking.json()

        word_is_known_after = False
        for word in library_after_unmarking_data["words"]:
            if word["lemma"] == test_word_lemma:
                word_is_known_after = word.get("is_known", False)
                break

        assert word_is_known_after is False

    @pytest.mark.asyncio
    async def test_WhenUnknownWordMarkedKnownInGame_ThenAppearsInVocabularyLibrary(
        self, async_client, url_builder
    ):
        """
        Test marking a word as known that is NOT in the vocabulary database
        (e.g., a word from actual video content like 'brauriger')

        After the fix, unknown words should be saved with vocabulary_id = NULL
        """
        # Create and authenticate a user
        helper = AsyncAuthHelper(async_client)
        user, _token, headers = await helper.create_authenticated_user()

        # Mark a word that doesn't exist in vocabulary database
        unknown_word = "brauriger"  # Example from the original issue
        unknown_word_lemma = "braurig"  # Lemmatized form

        mark_response = await async_client.post(
            url_builder.url_for("mark_word_known"),
            json={"lemma": unknown_word, "language": "de", "known": True},
            headers=headers,
        )
        assert mark_response.status_code == 200
        mark_data = mark_response.json()

        # Verify marking was successful even for unknown word
        assert mark_data["success"] is True
        assert mark_data["known"] is True
        assert mark_data["level"] == "unknown"  # Should have "unknown" level for words not in DB

        # Verify the word appears in user's known words
        # Note: It won't appear in vocabulary library queries filtered by level,
        # but it should appear in the user's vocabulary progress
        stats_response = await async_client.get(
            url_builder.url_for("get_vocabulary_stats"),
            params={"target_language": "de", "translation_language": "es"},
            headers=headers,
        )
        assert stats_response.status_code == 200
        stats = stats_response.json()

        # Total known should include the unknown word
        assert stats["total_known"] >= 1

    @pytest.mark.asyncio
    async def test_WhenGameStarts_ThenOnlyShowsUnknownWords(self, async_client, url_builder, test_vocabulary_words):
        """
        CRITICAL: Test that vocabulary game ONLY shows words the user doesn't know.

        This is the core functionality - users should never see words they've
        already marked as known during game sessions.
        """
        # Create and authenticate a user
        helper = AsyncAuthHelper(async_client)
        user, _token, headers = await helper.create_authenticated_user()

        # Mark one word as known
        known_word = test_vocabulary_words[0]  # "haus"
        mark_response = await async_client.post(
            url_builder.url_for("mark_word_known"),
            json={"lemma": known_word.lemma, "language": "de", "known": True},
            headers=headers,
        )
        assert mark_response.status_code == 200

        # Start a vocabulary game
        game_start_response = await async_client.post(
            url_builder.url_for("game_start_session"),
            json={"game_type": "vocabulary", "difficulty": "beginner", "total_questions": 5},
            headers=headers,
        )
        assert game_start_response.status_code == 200
        game_session = game_start_response.json()

        # Extract questions from the game session
        questions = game_session.get("session_data", {}).get("questions", [])
        assert len(questions) > 0, "Game should have generated questions"

        # Verify that NONE of the questions are about the known word
        for question in questions:
            question_text = question.get("question_text", "")
            # Check if the known word appears in any question
            assert known_word.word.lower() not in question_text.lower(), (
                f"Game showed word '{known_word.word}' which user marked as known! "
                f"Question: {question_text}"
            )

        # Verify all questions are about unknown words only
        # (This is the critical assertion - game must filter out known words)
        for question in questions:
            question_text = question.get("question_text", "")
            # The question should not contain any word the user marked as known
            for word in [known_word]:
                assert word.word.lower() not in question_text.lower()
                assert word.lemma.lower() not in question_text.lower()
