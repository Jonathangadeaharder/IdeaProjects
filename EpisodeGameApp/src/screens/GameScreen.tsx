import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Alert,
  Dimensions,
} from 'react-native';
import { useSelectedEpisode, useGameActions } from '../stores/useAppStore';

// Import reusable components
import {
  ProgressBar,
  VocabularyCard,
  StatsSummary,
  ActionButtonsRow,
  createGameStats,
  createCommonButtons,
  useTheme,
  createCommonStyles,
  getSemanticColors,
  getOptionStateColors,
} from '../components';
import { useGameLogic } from '../hooks';

interface Question {
  id: string;
  word: string;
  options: string[];
  correctAnswer: string;
}

const { width } = Dimensions.get('window');

export default function GameScreen({ navigation }: any) {
  const theme = useTheme();
  const selectedEpisode = useSelectedEpisode();
  const { startGame, answerQuestion, completeGame } = useGameActions();
  const [questions, setQuestions] = useState<Question[]>([]);
  
  // Use the new game logic hook
  const gameLogic = useGameLogic({
    onGameComplete: () => {
      completeGame();
      navigation.navigate('Results');
    },
    onAnswerSubmitted: (questionId, answer, isCorrect) => {
      answerQuestion(questionId, answer, isCorrect);
    },
  });

  useEffect(() => {
    if (selectedEpisode) {
      generateQuestions();
      startGame();
      gameLogic.startGame();
    }
  }, [selectedEpisode]);

  useEffect(() => {
    if (questions.length > 0) {
      gameLogic.setQuestions(questions);
    }
  }, [questions]);

  const generateQuestions = () => {
    if (!selectedEpisode) return;

    const generatedQuestions: Question[] = selectedEpisode.vocabularyWords.map((word, index) => {
      // Generate fake options for multiple choice
      const fakeOptions = [
        'option1',
        'option2',
        'option3',
      ];
      
      const correctAnswer = `meaning of ${word}`;
      const allOptions = [correctAnswer, ...fakeOptions].sort(() => Math.random() - 0.5);

      return {
        id: `q${index}`,
        word,
        options: allOptions,
        correctAnswer,
      };
    });

    setQuestions(generatedQuestions);
  };

  const handleAnswerSelect = (answer: string) => {
    gameLogic.selectAnswer(answer);
  };

  const handleSubmitAnswer = () => {
    gameLogic.submitAnswer();
  };

  const handleWatchVideo = () => {
    navigation.navigate('VideoPlayer');
  };

  const styles = createStyles(theme);

  if (!selectedEpisode || questions.length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.loadingText}>Loading...</Text>
      </SafeAreaView>
    );
  }

  const currentQuestion = gameLogic.currentQuestion || questions[gameLogic.currentQuestionIndex];
  const progress = ((gameLogic.currentQuestionIndex + 1) / questions.length) * 100;

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.episodeTitle}>{selectedEpisode.title}</Text>
        <ProgressBar
          progress={progress}
          label={`${gameLogic.currentQuestionIndex + 1} / ${questions.length}`}
        />
      </View>

      <View style={styles.gameArea}>
        <View style={styles.timerContainer}>
          <Text style={[styles.timer, { color: gameLogic.timeLeft <= 10 ? getSemanticColors(theme).error : getSemanticColors(theme).success }]}>
            {gameLogic.timeLeft}s
          </Text>
        </View>

        <View style={styles.questionContainer}>
          <Text style={styles.questionText}>What does this word mean?</Text>
          <Text style={styles.wordText}>{currentQuestion?.word}</Text>
        </View>

        <View style={styles.optionsContainer}>
          {currentQuestion?.options.map((option, index) => {
            let buttonStyle = [styles.optionButton];
            let textStyle = [styles.optionText];

            if (gameLogic.showResult) {
              if (option === currentQuestion.correctAnswer) {
                const correctColors = getOptionStateColors(theme, 'correct');
                buttonStyle.push({ borderColor: correctColors.border, backgroundColor: correctColors.background });
                textStyle.push({ color: correctColors.text, fontWeight: '500' });
              } else if (option === gameLogic.selectedAnswer && option !== currentQuestion.correctAnswer) {
                const incorrectColors = getOptionStateColors(theme, 'incorrect');
                buttonStyle.push({ borderColor: incorrectColors.border, backgroundColor: incorrectColors.background });
                textStyle.push({ color: incorrectColors.text, fontWeight: '500' });
              }
            } else if (gameLogic.selectedAnswer === option) {
              const selectedColors = getOptionStateColors(theme, 'selected');
              buttonStyle.push({ borderColor: selectedColors.border, backgroundColor: selectedColors.background });
              textStyle.push({ color: selectedColors.text, fontWeight: '500' });
            }

            return (
              <TouchableOpacity
                key={index}
                style={buttonStyle}
                onPress={() => handleAnswerSelect(option)}
                disabled={gameLogic.showResult}
              >
                <Text style={textStyle}>{option}</Text>
              </TouchableOpacity>
            );
          })}
        </View>

        {!gameLogic.showResult ? (
          <TouchableOpacity
            style={[styles.submitButton, !gameLogic.selectedAnswer && styles.disabledButton]}
            onPress={handleSubmitAnswer}
            disabled={!gameLogic.selectedAnswer}
          >
            <Text style={styles.submitButtonText}>Submit Answer</Text>
          </TouchableOpacity>
        ) : (
          <View style={styles.resultContainer}>
            <Text style={[styles.resultText, 
              { color: gameLogic.selectedAnswer === currentQuestion?.correctAnswer ? getSemanticColors(theme).success : getSemanticColors(theme).error }
            ]}>
              {gameLogic.selectedAnswer === currentQuestion?.correctAnswer ? '✅ Correct!' : '❌ Incorrect'}
            </Text>
          </View>
        )}
        <StatsSummary
          stats={createGameStats({
            correct: gameLogic.stats.correctAnswers,
            incorrect: gameLogic.stats.incorrectAnswers,
            total: questions.length,
            timeLeft: gameLogic.timeLeft,
          }, 'game', theme)}
        />
      </View>

      <ActionButtonsRow
        buttons={createCommonButtons({
          onWatchVideo: handleWatchVideo,
        }, 'game', theme)}
      />
    </SafeAreaView>
  );
}

const createStyles = (theme: any) => {
  const commonStyles = createCommonStyles(theme);
  
  return StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.colors.background.secondary,
    },
    loadingText: {
      ...commonStyles.text.body,
      textAlign: 'center',
      marginTop: theme.spacing.xl,
    },
    header: {
      backgroundColor: theme.colors.background.primary,
      padding: theme.spacing.lg,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.border.light,
    },
    episodeTitle: {
      ...commonStyles.text.title,
      marginBottom: theme.spacing.sm,
    },
    gameArea: {
      flex: 1,
      padding: theme.spacing.lg,
    },
    timerContainer: {
      alignItems: 'center',
      marginBottom: theme.spacing.lg,
    },
    timer: {
      fontSize: 32,
      fontWeight: 'bold',
    },
    questionContainer: {
      alignItems: 'center',
      marginBottom: theme.spacing.xl,
    },
    questionText: {
      ...commonStyles.text.body,
      color: theme.colors.text.secondary,
      marginBottom: theme.spacing.sm,
    },
    wordText: {
      fontSize: 32,
      fontWeight: 'bold',
      color: theme.colors.text.primary,
    },
    optionsContainer: {
      marginBottom: theme.spacing.xl,
    },
    optionButton: {
      backgroundColor: theme.colors.background.primary,
      padding: theme.spacing.md,
      borderRadius: theme.borderRadius.md,
      marginBottom: theme.spacing.sm,
      borderWidth: 2,
      borderColor: theme.colors.border.light,
    },
    optionText: {
      fontSize: 16,
      color: theme.colors.text.primary,
      textAlign: 'center',
    },
    submitButton: {
      ...commonStyles.button.primary,
      alignItems: 'center',
    },
    disabledButton: {
      backgroundColor: theme.colors.text.disabled,
    },
    submitButtonText: {
      color: theme.colors.background.primary,
      fontSize: 18,
      fontWeight: 'bold',
    },
    resultContainer: {
      alignItems: 'center',
      padding: theme.spacing.md,
    },
    resultText: {
      fontSize: 20,
      fontWeight: 'bold',
    },
  });
};