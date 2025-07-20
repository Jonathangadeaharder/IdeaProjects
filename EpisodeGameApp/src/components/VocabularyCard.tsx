import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ViewStyle } from 'react-native';
import { useTheme } from '../theme/ThemeProvider';
import { createCommonStyles, getOptionStateColors } from '../theme/styleUtils';

interface VocabularyCardProps {
  word: string;
  questionText?: string;
  options?: string[];
  selectedAnswer?: string;
  correctAnswer?: string;
  showResult?: boolean;
  onAnswerSelect?: (answer: string) => void;
  onKnown?: () => void;
  onUnknown?: () => void;
  onSkip?: () => void;
  mode?: 'knowledge-check' | 'multiple-choice' | 'display-only';
  style?: ViewStyle;
}

const VocabularyCard: React.FC<VocabularyCardProps> = ({
  word,
  questionText = 'Do you know this word?',
  options = [],
  selectedAnswer,
  correctAnswer,
  showResult = false,
  onAnswerSelect,
  onKnown,
  onUnknown,
  onSkip,
  mode = 'knowledge-check',
  style,
}) => {
  const { theme } = useTheme();
  const commonStyles = createCommonStyles(theme);
  const optionColors = getOptionStateColors(theme);
  const styles = createStyles(theme);
  const renderKnowledgeCheckButtons = () => (
    <View style={styles.actionsContainer}>
      <TouchableOpacity
        style={[styles.actionButton, styles.knownButton]}
        onPress={onKnown}
      >
        <Text style={styles.actionButtonText}>✓ I Know It</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={[styles.actionButton, styles.unknownButton]}
        onPress={onUnknown}
      >
        <Text style={styles.actionButtonText}>✗ Don't Know</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={[styles.actionButton, styles.skipButton]}
        onPress={onSkip}
      >
        <Text style={styles.actionButtonText}>⏭ Skip</Text>
      </TouchableOpacity>
    </View>
  );

  const renderMultipleChoiceOptions = () => (
    <View style={styles.optionsContainer}>
      {options.map((option, index) => {
        let buttonStyle = [styles.optionButton];
        let textStyle = [styles.optionText];

        if (showResult) {
          if (option === correctAnswer) {
            buttonStyle.push({
              backgroundColor: optionColors.correct.background,
              borderColor: optionColors.correct.border,
            });
            textStyle.push({ color: optionColors.correct.text, fontWeight: theme.typography.fontWeight.medium });
          } else if (option === selectedAnswer && option !== correctAnswer) {
            buttonStyle.push({
              backgroundColor: optionColors.incorrect.background,
              borderColor: optionColors.incorrect.border,
            });
            textStyle.push({ color: optionColors.incorrect.text, fontWeight: theme.typography.fontWeight.medium });
          }
        } else if (selectedAnswer === option) {
          buttonStyle.push({
            backgroundColor: optionColors.selected.background,
            borderColor: optionColors.selected.border,
          });
          textStyle.push({ color: optionColors.selected.text, fontWeight: theme.typography.fontWeight.medium });
        }

        return (
          <TouchableOpacity
            key={index}
            style={buttonStyle}
            onPress={() => onAnswerSelect?.(option)}
            disabled={showResult}
          >
            <Text style={textStyle}>{option}</Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );

  const renderDisplayOnly = () => (
    <View style={styles.displayContainer}>
      <Text style={styles.displayWord}>{word}</Text>
    </View>
  );

  return (
    <View style={[styles.container, style]}>
      <View style={styles.questionContainer}>
        <Text style={styles.questionText}>{questionText}</Text>
        <Text style={styles.wordText}>{word}</Text>
      </View>

      {mode === 'knowledge-check' && renderKnowledgeCheckButtons()}
      {mode === 'multiple-choice' && renderMultipleChoiceOptions()}
      {mode === 'display-only' && renderDisplayOnly()}
    </View>
  );
};

const createStyles = (theme: any) => StyleSheet.create({
  container: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.xl,
    padding: theme.spacing.xl,
    marginVertical: theme.spacing.md,
    ...theme.shadows.md,
  },
  questionContainer: {
    alignItems: 'center',
    marginBottom: theme.spacing.xl,
  },
  questionText: {
    fontSize: theme.typography.fontSize.lg,
    color: theme.colors.onSurfaceVariant,
    marginBottom: theme.spacing.md,
    textAlign: 'center',
  },
  wordText: {
    fontSize: theme.typography.fontSize['5xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.onSurface,
    textAlign: 'center',
  },
  actionsContainer: {
    gap: theme.spacing.md,
  },
  actionButton: {
    padding: theme.spacing.lg,
    borderRadius: theme.borderRadius.lg,
    alignItems: 'center',
  },
  knownButton: {
    backgroundColor: theme.colors.success,
  },
  unknownButton: {
    backgroundColor: theme.colors.error,
  },
  skipButton: {
    backgroundColor: theme.colors.warning,
  },
  actionButtonText: {
    color: theme.colors.onPrimary,
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.bold,
  },
  optionsContainer: {
    gap: theme.spacing.md,
  },
  optionButton: {
    backgroundColor: theme.colors.surface,
    padding: theme.spacing.lg,
    borderRadius: theme.borderRadius.lg,
    borderWidth: 2,
    borderColor: theme.colors.outline,
  },
  optionText: {
    fontSize: theme.typography.fontSize.md,
    color: theme.colors.onSurface,
    textAlign: 'center',
  },
  displayContainer: {
    alignItems: 'center',
    padding: theme.spacing.md,
  },
  displayWord: {
    fontSize: theme.typography.fontSize.lg,
    color: theme.colors.onSurface,
    fontWeight: theme.typography.fontWeight.medium,
  },
});

export default VocabularyCard;