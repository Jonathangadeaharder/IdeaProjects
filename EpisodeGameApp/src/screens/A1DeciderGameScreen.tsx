import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Alert,
  Dimensions,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import {
  useGameAndProcessingOptimized,
  useGameActions,
  useProcessingActions,
  useVocabularyActions,
  useSelectedEpisode,
} from '../stores/useAppStore';
import SubtitleService from '../services/SubtitleService';
import PythonBridgeService from '../services/PythonBridgeService';

// Import reusable components
import {
  ProcessingStatusIndicator,
  ProgressBar,
  VocabularyCard,
  StatsSummary,
  ActionButtonsRow,
  createGameStats,
  createCommonButtons,
  useTheme,
  createCommonStyles,
  getSemanticColors,
} from '../components';
import useProcessingWorkflow from '../hooks/useProcessingWorkflow';

interface ProcessingProgress {
  stage: 'transcription' | 'filtering' | 'translation' | 'complete';
  progress: number;
  message: string;
}

interface VocabularyWordWithStatus {
  word: string;
  isKnown?: boolean;
}

const { width } = Dimensions.get('window');

export default function A1DeciderGameScreen({ navigation }: any) {
  const { theme } = useTheme();
  const { selectedEpisode, gameStarted, gameCompleted, isProcessing, processingStage } = useGameAndProcessingOptimized();
  const { selectEpisode, startGame, completeGame, updateEpisodeStatus } = useGameActions();
  const { startProcessing, updateProcessingProgress, completeProcessing } = useProcessingActions();
  const { addKnownWord, addUnknownWord, addSkippedWord, setVocabularyAnalysis } = useVocabularyActions();
  const [gamePhase, setGamePhase] = useState<'processing' | 'vocabulary-check' | 'complete'>('processing');
  const [vocabularyWords, setVocabularyWords] = useState<VocabularyWordWithStatus[]>([]);
  const [currentWordIndex, setCurrentWordIndex] = useState(0);

  // Use the new processing workflow hook
  const processingWorkflow = useProcessingWorkflow({
    onStageChange: (stage) => {
      console.log('Processing stage changed to:', stage);
    },
    onComplete: (result) => {
      setGamePhase('vocabulary-check');
      completeProcessing();
    },
    onError: (stage, error) => {
      console.error(`Processing error in ${stage}:`, error);
      Alert.alert('Processing Error', `Error in ${stage}: ${error}`);
      completeProcessing();
    },
  });

  useEffect(() => {
    if (selectedEpisode) {
      processEpisode();
    }
  }, [selectedEpisode]);

  const processEpisode = async () => {
    if (!selectedEpisode) return;

    startProcessing('transcription');
    startGame();
    processingWorkflow.startProcessing();

    try {
      // Check if episode needs processing
      const status = await SubtitleService.checkSubtitleStatus(selectedEpisode);
      
      if (!status.isTranscribed || !status.hasFilteredSubtitles || !status.hasTranslatedSubtitles) {
        // Run the complete processing workflow with new hook integration
        await SubtitleService.processEpisode(selectedEpisode, (progress) => {
          updateProcessingProgress(progress.stage, progress.progress, progress.message);
          // Update the new workflow hook as well
          const stepId = progress.stage;
          processingWorkflow.updateStepProgress(stepId, progress.progress, progress.message);
          
          // Complete steps as they finish
          if (progress.progress >= 100) {
            processingWorkflow.completeStep(stepId, progress);
          }
        });
      } else {
        // If already processed, complete immediately
        processingWorkflow.completeStep('transcription', null);
        processingWorkflow.completeStep('filtering', null);
        processingWorkflow.completeStep('translation', null);
      }

      // Load real vocabulary for assessment
      const subtitleUrl = selectedEpisode.subtitleUrl;
      const vocabulary = await SubtitleService.loadRealVocabulary(subtitleUrl);
      const vocabularyWithStatus = vocabulary.map(vocabWord => ({ word: vocabWord.german, isKnown: undefined }));
      setVocabularyWords(vocabularyWithStatus);
      
    } catch (error) {
      console.error('Error in workflow:', error);
      Alert.alert('Error', 'Failed to process episode. Please try again.');
      processingWorkflow.failStep('transcription', 'Failed to process episode');
      completeProcessing();
    }
  };

  const handleWordKnowledge = (isKnown: boolean) => {
    const currentWord = vocabularyWords[currentWordIndex];
    if (!currentWord) return;

    if (isKnown) {
      addKnownWord(currentWord.word);
    } else {
      addUnknownWord(currentWord.word);
    }

    moveToNextWord();
  };

  const handleSkipWord = () => {
    const currentWord = vocabularyWords[currentWordIndex];
    if (!currentWord) return;

    addSkippedWord(currentWord.word);
    moveToNextWord();
  };

  const moveToNextWord = () => {
    if (currentWordIndex < vocabularyWords.length - 1) {
      setCurrentWordIndex(currentWordIndex + 1);
    } else {
      // Vocabulary check complete
      completeVocabularyCheck();
    }
  };

  const completeVocabularyCheck = () => {
    setGamePhase('complete');
    completeGame();
    
    // Update episode status to show all processing as complete
    updateEpisodeStatus(true, true);
    
    // Show summary
    Alert.alert(
      'Vocabulary Check Complete!',
      `Vocabulary check complete! Results will be available in the next screen.`,
      [
        {
          text: 'Watch Video',
          onPress: () => navigation.navigate('VideoPlayer')
        },
        {
          text: 'View Results',
          onPress: () => navigation.navigate('Results')
        }
      ]
    );
  };

  const handleWatchVideo = () => {
    navigation.navigate('VideoPlayer');
  };



  const styles = createStyles(theme);

  if (!selectedEpisode) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.loadingText}>No episode selected</Text>
      </SafeAreaView>
    );
  }

  if (isProcessing) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.processingContainer}>
          <Text style={styles.episodeTitle}>{selectedEpisode.title}</Text>
          
          <ProcessingStatusIndicator
            currentStage={processingWorkflow.currentStage}
            progress={processingWorkflow.overallProgress}
            message={processingWorkflow.currentStep?.message || 'Processing episode...'}
            isProcessing={processingWorkflow.isProcessing}
          />
        </View>
      </SafeAreaView>
    );
  }

  if (gamePhase === 'vocabulary-check' && vocabularyWords.length > 0) {
    const currentWord = vocabularyWords[currentWordIndex];
    const progress = ((currentWordIndex + 1) / vocabularyWords.length) * 100;

    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.episodeTitle}>{selectedEpisode.title}</Text>
          <Text style={styles.subtitle}>Vocabulary Knowledge Check</Text>
          
          <ProgressBar
            progress={progress}
            label={`${currentWordIndex + 1} / ${vocabularyWords.length}`}
          />
        </View>

        <View style={styles.gameArea}>
          <VocabularyCard
            word={currentWord.word}
            question="Do you know this word?"
            onKnown={() => handleWordKnowledge(true)}
            onUnknown={() => handleWordKnowledge(false)}
            onSkip={handleSkipWord}
          />

          <StatsSummary
            stats={createGameStats({
              known: 0,
              unknown: 0,
              skipped: 0,
              total: vocabularyWords.length,
              mode: 'vocabulary',
              theme: theme
            })}
          />
        </View>

        <ActionButtonsRow
          buttons={createCommonButtons({
            onWatchVideo: handleWatchVideo,
          })}
        />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.completeContainer}>
        <Text style={styles.completeTitle}>Processing Complete!</Text>
        <Text style={styles.completeMessage}>
          Your episode is ready with filtered subtitles containing only unknown words.
        </Text>
        
        <ActionButtonsRow
          buttons={createCommonButtons({
            onWatchVideo: handleWatchVideo,
          })}
        />
      </View>
    </SafeAreaView>
  );
}

const createStyles = (theme: any) => {
  const commonStyles = createCommonStyles(theme);
  
  return StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.colors.background,
    },
    loadingText: {
      ...commonStyles.bodyMedium,
      textAlign: 'center',
      marginTop: theme.spacing.xl,
    },
    processingContainer: {
      flex: 1,
      padding: theme.spacing.lg,
      justifyContent: 'center',
    },
    header: {
      backgroundColor: theme.colors.surface,
      padding: theme.spacing.lg,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.outline,
    },
    episodeTitle: {
      ...commonStyles.headingMedium,
      marginBottom: theme.spacing.xs,
    },
    subtitle: {
      ...commonStyles.bodyMedium,
      color: theme.colors.onSurfaceVariant,
      marginBottom: theme.spacing.sm,
    },
    gameArea: {
      flex: 1,
      padding: theme.spacing.lg,
      justifyContent: 'center',
    },
    completeContainer: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      padding: theme.spacing.lg,
    },
    completeTitle: {
      fontSize: 28,
      fontWeight: 'bold',
      color: getSemanticColors(theme).success,
      marginBottom: theme.spacing.md,
      textAlign: 'center',
    },
    completeMessage: {
      ...commonStyles.bodyMedium,
      color: theme.colors.onSurfaceVariant,
      textAlign: 'center',
      marginBottom: theme.spacing.xl,
      lineHeight: 24,
    },
  });
};