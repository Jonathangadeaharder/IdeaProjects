// Reusable UI Components for EpisodeGameApp

// Processing and Progress Components
export { default as ProcessingStatusIndicator } from './ProcessingStatusIndicator';
export { default as ProgressBar } from './ProgressBar';

// Game Components
export { default as VocabularyCard } from './VocabularyCard';
export { default as StatsSummary } from './StatsSummary';

// Video Components
export { default as VideoControls } from './VideoControls';
export { default as SubtitleDisplay } from './SubtitleDisplay';

// UI Components
export { default as ActionButtonsRow } from './ActionButtonsRow';

// Theme System
export { useTheme, ThemeProvider } from '../theme/ThemeProvider';
export { createCommonStyles, getSemanticColors, getDifficultyColors, getOptionStateColors } from '../theme/styleUtils';
export type { Theme } from '../theme';

// Export component types and helper functions
export type { ProcessingStage } from './ProcessingStatusIndicator';
export type { VocabularyWord } from './VocabularyCard';
export type { GameStatsData } from './StatsSummary';
export type { ActionButton } from './ActionButtonsRow';

// Utility Functions
export { createGameStats } from './StatsSummary';
export { createCommonButtons } from './ActionButtonsRow';
export { createSubtitleEntries, defaultSubtitles } from './SubtitleDisplay';