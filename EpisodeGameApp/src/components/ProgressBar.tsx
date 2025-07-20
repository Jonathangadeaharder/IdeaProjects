import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { useTheme } from '../theme/ThemeProvider';

interface ProgressBarProps {
  progress: number; // 0-100
  current?: number;
  total?: number;
  color?: string;
  backgroundColor?: string;
  height?: number;
  showPercentage?: boolean;
  showFraction?: boolean;
  style?: ViewStyle;
  textStyle?: ViewStyle;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  current,
  total,
  color,
  backgroundColor,
  height = 8,
  showPercentage = true,
  showFraction = false,
  style,
  textStyle,
}) => {
  const { theme } = useTheme();
  const styles = createStyles(theme);
  
  const progressColor = color || theme.colors.success;
  const progressBgColor = backgroundColor || theme.colors.outline;
  const clampedProgress = Math.max(0, Math.min(100, progress));
  
  const renderText = () => {
    if (showFraction && current !== undefined && total !== undefined) {
      return `${current} / ${total}`;
    }
    if (showPercentage) {
      return `${Math.round(clampedProgress)}%`;
    }
    return null;
  };

  const text = renderText();

  return (
    <View style={[styles.container, style]}>
      <View style={[styles.progressBar, { height, backgroundColor: progressBgColor }]}>
        <View 
          style={[
            styles.progressFill, 
            { 
              width: `${clampedProgress}%`,
              backgroundColor: progressColor,
              height,
            }
          ]} 
        />
      </View>
      {text && (
        <Text style={[styles.progressText, textStyle]}>
          {text}
        </Text>
      )}
    </View>
  );
};

const createStyles = (theme: any) => StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '100%',
  },
  progressBar: {
    flex: 1,
    backgroundColor: theme.colors.outline,
    borderRadius: theme.borderRadius.sm,
    marginRight: theme.spacing.md,
  },
  progressFill: {
    borderRadius: theme.borderRadius.sm,
  },
  progressText: {
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.onSurfaceVariant,
    fontWeight: theme.typography.fontWeight.medium,
    minWidth: 40,
  },
});

export default ProgressBar;