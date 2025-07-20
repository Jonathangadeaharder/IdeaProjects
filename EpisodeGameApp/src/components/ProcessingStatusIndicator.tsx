import React from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { useTheme } from '../theme/ThemeProvider';

interface ProcessingStep {
  id: string;
  name: string;
  number: number;
}

interface ProcessingStatusIndicatorProps {
  currentStage: 'transcription' | 'filtering' | 'translation' | 'complete' | null;
  progress: number;
  message: string;
  isProcessing: boolean;
  steps?: ProcessingStep[];
}

const defaultSteps: ProcessingStep[] = [
  { id: 'transcription', name: 'Transcribe', number: 1 },
  { id: 'filtering', name: 'Filter', number: 2 },
  { id: 'translation', name: 'Translate', number: 3 },
];

const ProcessingStatusIndicator: React.FC<ProcessingStatusIndicatorProps> = ({
  currentStage,
  progress,
  message,
  isProcessing,
  steps = defaultSteps,
}) => {
  const { theme } = useTheme();
  const styles = createStyles(theme);
  const getProgressColor = () => {
    if (!currentStage) return theme.colors.success;
    
    switch (currentStage) {
      case 'transcription': return theme.colors.warning;
      case 'filtering': return theme.colors.info;
      case 'translation': return theme.colors.secondary;
      case 'complete': return theme.colors.success;
      default: return theme.colors.success;
    }
  };

  const getStageTitle = () => {
    if (!currentStage) return 'Processing';
    
    switch (currentStage) {
      case 'transcription': return 'Creating Subtitles';
      case 'filtering': return 'Analyzing Vocabulary';
      case 'translation': return 'Translating Subtitles';
      case 'complete': return 'Complete';
      default: return 'Processing';
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.processingCard}>
        <Text style={styles.stageTitle}>{getStageTitle()}</Text>
        
        <View style={styles.progressContainer}>
          <View style={styles.progressBar}>
            <View 
              style={[
                styles.progressFill, 
                { 
                  width: `${progress || 0}%`,
                  backgroundColor: getProgressColor()
                }
              ]} 
            />
          </View>
          <Text style={styles.progressText}>
            {progress || 0}%
          </Text>
        </View>
        
        <Text style={styles.progressMessage}>
          {message || 'Initializing...'}
        </Text>
        
        {isProcessing && (
          <ActivityIndicator 
            size="large" 
            color={getProgressColor()} 
            style={styles.spinner}
          />
        )}
      </View>
      
      <View style={styles.stageIndicators}>
        {steps.map((step) => (
          <View 
            key={step.id}
            style={[
              styles.stageIndicator, 
              currentStage === step.id && styles.activeStage
            ]}
          >
            <Text style={styles.stageNumber}>{step.number}</Text>
            <Text style={styles.stageName}>{step.name}</Text>
          </View>
        ))}
      </View>
    </View>
  );
};

const createStyles = (theme: any) => StyleSheet.create({
  container: {
    padding: theme.spacing.xl,
  },
  processingCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.xl,
    padding: theme.spacing['2xl'],
    marginVertical: theme.spacing.xl,
    alignItems: 'center',
    ...theme.shadows.md,
  },
  stageTitle: {
    fontSize: theme.typography.fontSize['2xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.onSurface,
    marginBottom: theme.spacing.xl,
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '100%',
    marginBottom: theme.spacing.lg,
  },
  progressBar: {
    flex: 1,
    height: 8,
    backgroundColor: theme.colors.outline,
    borderRadius: theme.borderRadius.sm,
    marginRight: theme.spacing.md,
  },
  progressFill: {
    height: '100%',
    backgroundColor: theme.colors.success,
    borderRadius: theme.borderRadius.sm,
  },
  progressText: {
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.onSurfaceVariant,
    fontWeight: theme.typography.fontWeight.medium,
    minWidth: 40,
  },
  progressMessage: {
    fontSize: theme.typography.fontSize.md,
    color: theme.colors.onSurfaceVariant,
    textAlign: 'center',
    marginBottom: theme.spacing.xl,
  },
  spinner: {
    marginTop: theme.spacing.md,
  },
  stageIndicators: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
  },
  stageIndicator: {
    alignItems: 'center',
    opacity: 0.5,
  },
  activeStage: {
    opacity: 1,
  },
  stageNumber: {
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.success,
    marginBottom: theme.spacing.xs,
  },
  stageName: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.onSurfaceVariant,
  },
});

export default ProcessingStatusIndicator;