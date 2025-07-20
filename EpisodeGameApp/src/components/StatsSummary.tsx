import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { useTheme } from '../theme/ThemeProvider';
import { createCommonStyles, getSemanticColors } from '../theme/styleUtils';

interface StatItem {
  label: string;
  value: number | string;
  color?: string;
}

interface StatsSummaryProps {
  stats: StatItem[];
  layout?: 'horizontal' | 'vertical' | 'grid';
  showDividers?: boolean;
  style?: ViewStyle;
  itemStyle?: ViewStyle;
}

const StatsSummary: React.FC<StatsSummaryProps> = ({
  stats,
  layout = 'horizontal',
  showDividers = true,
  style,
  itemStyle,
}) => {
  const { theme } = useTheme();
  const commonStyles = createCommonStyles(theme);
  const semanticColors = getSemanticColors(theme);
  const styles = createStyles(theme);
  const renderStatItem = (stat: StatItem, index: number) => (
    <React.Fragment key={index}>
      <View style={[styles.statItem, itemStyle]}>
        <Text style={[styles.statNumber, stat.color && { color: stat.color }]}>
          {stat.value}
        </Text>
        <Text style={styles.statLabel}>{stat.label}</Text>
      </View>
      {showDividers && index < stats.length - 1 && layout === 'horizontal' && (
        <View style={styles.statDivider} />
      )}
    </React.Fragment>
  );

  const getContainerStyle = () => {
    const baseStyle = [styles.container, style];
    
    switch (layout) {
      case 'horizontal':
        return [...baseStyle, styles.horizontalLayout];
      case 'vertical':
        return [...baseStyle, styles.verticalLayout];
      case 'grid':
        return [...baseStyle, styles.gridLayout];
      default:
        return baseStyle;
    }
  };

  return (
    <View style={getContainerStyle()}>
      {stats.map((stat, index) => renderStatItem(stat, index))}
    </View>
  );
};

// Helper function to create common stat configurations
export const createGameStats = ({
  known = 0,
  unknown = 0,
  skipped = 0,
  correct = 0,
  incorrect = 0,
  total = 0,
  score = 0,
  mode = 'vocabulary',
  theme
}: {
  known?: number;
  unknown?: number;
  skipped?: number;
  correct?: number;
  incorrect?: number;
  total?: number;
  score?: number;
  mode?: 'vocabulary' | 'game' | 'results';
  theme?: any;
}): StatItem[] => {
  const colors = theme ? {
    success: theme.colors.success,
    error: theme.colors.error,
    warning: theme.colors.warning,
    neutral: theme.colors.onSurfaceVariant,
  } : {
    success: '#4CAF50',
    error: '#F44336',
    warning: '#FF9800',
    neutral: '#666666',
  };
  
  switch (mode) {
    case 'vocabulary':
      return [
        { label: 'Known', value: known, color: colors.success },
        { label: 'Unknown', value: unknown, color: colors.error },
        { label: 'Skipped', value: skipped, color: colors.warning },
      ];
    case 'game':
      return [
        { label: 'Correct', value: correct, color: colors.success },
        { label: 'Incorrect', value: incorrect, color: colors.error },
        { label: 'Total', value: total, color: colors.neutral },
      ];
    case 'results':
      return [
        { label: 'Score', value: score, color: colors.success },
        { label: 'Correct', value: correct, color: colors.success },
        { label: 'Incorrect', value: incorrect, color: colors.error },
        { label: 'Total', value: total, color: colors.neutral },
      ];
    default:
      return [];
  }
};

const createStyles = (theme: any) => StyleSheet.create({
  container: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    ...theme.shadows.sm,
  },
  horizontalLayout: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  verticalLayout: {
    flexDirection: 'column',
    gap: theme.spacing.lg,
  },
  gridLayout: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statItem: {
    alignItems: 'center',
    minWidth: 60,
  },
  statNumber: {
    fontSize: theme.typography.fontSize['2xl'],
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.onSurface,
  },
  statLabel: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.onSurfaceVariant,
    marginTop: theme.spacing.xs,
    textAlign: 'center',
  },
  statDivider: {
    width: 1,
    height: 40,
    backgroundColor: theme.colors.outline,
  },
});

export default StatsSummary;