import { StyleSheet, ViewStyle, TextStyle } from 'react-native';
import { Theme } from './index';

// Utility function to create themed styles
export const createThemedStyles = <T extends Record<string, ViewStyle | TextStyle>>(
  styleFactory: (theme: Theme) => T
) => {
  return (theme: Theme): T => styleFactory(theme);
};

// Common style patterns using theme
export const createCommonStyles = (theme: Theme) => {
  return StyleSheet.create({
    // Container Styles
    container: {
      flex: 1,
      backgroundColor: theme.colors.background,
    } as ViewStyle,
    
    surface: {
      backgroundColor: theme.colors.surface,
      borderRadius: theme.borderRadius.lg,
      padding: theme.spacing.lg,
      ...theme.shadows.md,
    } as ViewStyle,
    
    card: {
      backgroundColor: theme.colors.surface,
      borderRadius: theme.borderRadius.xl,
      padding: theme.spacing.xl,
      marginVertical: theme.spacing.md,
      ...theme.shadows.md,
    } as ViewStyle,
    
    // Header Styles
    header: {
      backgroundColor: theme.colors.surface,
      padding: theme.spacing.xl,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.outline,
    } as ViewStyle,
    
    // Text Styles
    headingLarge: {
      fontSize: theme.typography.fontSize['3xl'],
      fontWeight: theme.typography.fontWeight.bold,
      color: theme.colors.onSurface,
      marginBottom: theme.spacing.sm,
    } as TextStyle,
    
    headingMedium: {
      fontSize: theme.typography.fontSize['2xl'],
      fontWeight: theme.typography.fontWeight.bold,
      color: theme.colors.onSurface,
      marginBottom: theme.spacing.sm,
    } as TextStyle,
    
    headingSmall: {
      fontSize: theme.typography.fontSize.xl,
      fontWeight: theme.typography.fontWeight.bold,
      color: theme.colors.onSurface,
      marginBottom: theme.spacing.sm,
    } as TextStyle,
    
    bodyLarge: {
      fontSize: theme.typography.fontSize.lg,
      color: theme.colors.onSurface,
      lineHeight: theme.typography.fontSize.lg * theme.typography.lineHeight.normal,
    } as TextStyle,
    
    bodyMedium: {
      fontSize: theme.typography.fontSize.md,
      color: theme.colors.onSurface,
      lineHeight: theme.typography.fontSize.md * theme.typography.lineHeight.normal,
    } as TextStyle,
    
    bodySmall: {
      fontSize: theme.typography.fontSize.base,
      color: theme.colors.onSurfaceVariant,
      lineHeight: theme.typography.fontSize.base * theme.typography.lineHeight.normal,
    } as TextStyle,
    
    caption: {
      fontSize: theme.typography.fontSize.sm,
      color: theme.colors.onSurfaceVariant,
      lineHeight: theme.typography.fontSize.sm * theme.typography.lineHeight.normal,
    } as TextStyle,
    
    // Button Styles
    buttonPrimary: {
      backgroundColor: theme.colors.primary,
      padding: theme.spacing.lg,
      borderRadius: theme.borderRadius.lg,
      alignItems: 'center',
    } as ViewStyle,
    
    buttonSecondary: {
      backgroundColor: theme.colors.secondary,
      padding: theme.spacing.lg,
      borderRadius: theme.borderRadius.lg,
      alignItems: 'center',
    } as ViewStyle,
    
    buttonOutline: {
      backgroundColor: 'transparent',
      padding: theme.spacing.lg,
      borderRadius: theme.borderRadius.lg,
      borderWidth: 2,
      borderColor: theme.colors.outline,
      alignItems: 'center',
    } as ViewStyle,
    
    buttonDisabled: {
      backgroundColor: theme.colors.disabled,
      padding: theme.spacing.lg,
      borderRadius: theme.borderRadius.lg,
      alignItems: 'center',
    } as ViewStyle,
    
    buttonTextPrimary: {
      color: theme.colors.onPrimary,
      fontSize: theme.typography.fontSize.lg,
      fontWeight: theme.typography.fontWeight.bold,
    } as TextStyle,
    
    buttonTextSecondary: {
      color: theme.colors.onSecondary,
      fontSize: theme.typography.fontSize.lg,
      fontWeight: theme.typography.fontWeight.bold,
    } as TextStyle,
    
    buttonTextOutline: {
      color: theme.colors.onSurface,
      fontSize: theme.typography.fontSize.lg,
      fontWeight: theme.typography.fontWeight.bold,
    } as TextStyle,
    
    buttonTextDisabled: {
      color: theme.colors.disabledText,
      fontSize: theme.typography.fontSize.lg,
      fontWeight: theme.typography.fontWeight.bold,
    } as TextStyle,
    
    // Input Styles
    input: {
      backgroundColor: theme.colors.surface,
      borderWidth: 2,
      borderColor: theme.colors.outline,
      borderRadius: theme.borderRadius.lg,
      padding: theme.spacing.lg,
      fontSize: theme.typography.fontSize.md,
      color: theme.colors.onSurface,
    } as ViewStyle,
    
    inputFocused: {
      borderColor: theme.colors.primary,
    } as ViewStyle,
    
    inputError: {
      borderColor: theme.colors.error,
    } as ViewStyle,
    
    // State Styles
    success: {
      backgroundColor: theme.colors.successLight,
      borderColor: theme.colors.success,
    } as ViewStyle,
    
    warning: {
      backgroundColor: theme.colors.warningLight,
      borderColor: theme.colors.warning,
    } as ViewStyle,
    
    error: {
      backgroundColor: theme.colors.errorLight,
      borderColor: theme.colors.error,
    } as ViewStyle,
    
    info: {
      backgroundColor: theme.colors.infoLight,
      borderColor: theme.colors.info,
    } as ViewStyle,
    
    // Layout Styles
    row: {
      flexDirection: 'row',
      alignItems: 'center',
    } as ViewStyle,
    
    column: {
      flexDirection: 'column',
    } as ViewStyle,
    
    center: {
      justifyContent: 'center',
      alignItems: 'center',
    } as ViewStyle,
    
    spaceBetween: {
      justifyContent: 'space-between',
    } as ViewStyle,
    
    spaceAround: {
      justifyContent: 'space-around',
    } as ViewStyle,
    
    // Spacing Utilities
    marginXs: { margin: theme.spacing.xs } as ViewStyle,
    marginSm: { margin: theme.spacing.sm } as ViewStyle,
    marginMd: { margin: theme.spacing.md } as ViewStyle,
    marginLg: { margin: theme.spacing.lg } as ViewStyle,
    marginXl: { margin: theme.spacing.xl } as ViewStyle,
    
    paddingXs: { padding: theme.spacing.xs } as ViewStyle,
    paddingSm: { padding: theme.spacing.sm } as ViewStyle,
    paddingMd: { padding: theme.spacing.md } as ViewStyle,
    paddingLg: { padding: theme.spacing.lg } as ViewStyle,
    paddingXl: { padding: theme.spacing.xl } as ViewStyle,
  });
};

// Semantic color helpers
export const getSemanticColors = (theme: Theme) => ({
  success: {
    background: theme.colors.successLight,
    border: theme.colors.success,
    text: theme.colors.success,
  },
  warning: {
    background: theme.colors.warningLight,
    border: theme.colors.warning,
    text: theme.colors.warning,
  },
  error: {
    background: theme.colors.errorLight,
    border: theme.colors.error,
    text: theme.colors.error,
  },
  info: {
    background: theme.colors.infoLight,
    border: theme.colors.info,
    text: theme.colors.info,
  },
});

// Difficulty level color mapping
export const getDifficultyColors = (theme: Theme) => ({
  beginner: theme.colors.success,
  intermediate: theme.colors.warning,
  advanced: theme.colors.error,
});

// Option state color mapping
export const getOptionStateColors = (theme: Theme) => ({
  default: {
    background: theme.colors.surface,
    border: theme.colors.outline,
    text: theme.colors.onSurface,
  },
  selected: {
    background: theme.colors.infoLight,
    border: theme.colors.info,
    text: theme.colors.info,
  },
  correct: {
    background: theme.colors.successLight,
    border: theme.colors.success,
    text: theme.colors.success,
  },
  incorrect: {
    background: theme.colors.errorLight,
    border: theme.colors.error,
    text: theme.colors.error,
  },
});