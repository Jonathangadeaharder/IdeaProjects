# Design System Documentation

## Overview

The EpisodeGameApp now features a comprehensive design system with a centralized theme provider that ensures consistent colors, typography, and spacing across the entire application. This design system provides a foundation for scalable and maintainable UI development.

## Architecture

### Core Components

1. **Theme Configuration** (`src/theme/index.ts`)
   - Defines the complete theme structure with colors, typography, spacing, and other design tokens
   - Provides both light theme (default) and placeholder for dark theme
   - Centralized source of truth for all design values

2. **Theme Provider** (`src/theme/ThemeProvider.tsx`)
   - React Context provider that makes theme accessible throughout the app
   - Provides `useTheme` hook for consuming theme in components
   - Handles theme switching logic (ready for dark mode implementation)

3. **Style Utilities** (`src/theme/styleUtils.ts`)
   - Helper functions for creating themed styles
   - Common style patterns and semantic color functions
   - Utility functions for different UI states and contexts

## Theme Structure

### Colors

```typescript
colors: {
  // Primary brand colors
  primary: {
    main: '#4CAF50',
    light: '#81C784',
    dark: '#388E3C'
  },
  
  // Secondary colors
  secondary: {
    main: '#2196F3',
    light: '#64B5F6',
    dark: '#1976D2'
  },
  
  // Background colors
  background: {
    primary: '#FFFFFF',
    secondary: '#F5F5F5',
    tertiary: '#FAFAFA'
  },
  
  // Text colors
  text: {
    primary: '#333333',
    secondary: '#666666',
    disabled: '#CCCCCC',
    inverse: '#FFFFFF'
  },
  
  // Surface colors
  surface: {
    light: '#FFFFFF',
    medium: '#F5F5F5',
    dark: '#000000'
  },
  
  // Border colors
  border: {
    light: '#E0E0E0',
    medium: '#CCCCCC',
    dark: '#999999'
  },
  
  // State colors
  state: {
    success: '#4CAF50',
    warning: '#FF9800',
    error: '#F44336',
    info: '#2196F3'
  }
}
```

### Typography

```typescript
typography: {
  fontFamily: {
    regular: 'System',
    medium: 'System',
    bold: 'System'
  },
  fontSize: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 20,
    xxl: 24,
    xxxl: 32
  },
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    loose: 1.8
  }
}
```

### Spacing

```typescript
spacing: {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 20,
  xl: 32,
  xxl: 48
}
```

## Usage Guide

### Basic Theme Usage

```typescript
import { useTheme } from '../components';

function MyComponent() {
  const theme = useTheme();
  
  const styles = StyleSheet.create({
    container: {
      backgroundColor: theme.colors.background.primary,
      padding: theme.spacing.md,
      borderRadius: theme.borderRadius.md,
    },
    text: {
      color: theme.colors.text.primary,
      fontSize: theme.typography.fontSize.md,
    }
  });
  
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Themed Component</Text>
    </View>
  );
}
```

### Using Style Utilities

```typescript
import { useTheme, createCommonStyles } from '../components';

function MyComponent() {
  const theme = useTheme();
  const commonStyles = createCommonStyles(theme);
  
  const styles = StyleSheet.create({
    container: {
      ...commonStyles.container.card,
      // Additional custom styles
    },
    title: {
      ...commonStyles.text.title,
      // Additional custom styles
    },
    button: {
      ...commonStyles.button.primary,
      // Additional custom styles
    }
  });
  
  // Component JSX...
}
```

### Semantic Color Functions

```typescript
import { getSemanticColors, getOptionStateColors } from '../components';

function GameComponent() {
  const theme = useTheme();
  const semanticColors = getSemanticColors(theme);
  const correctColors = getOptionStateColors(theme, 'correct');
  
  const styles = StyleSheet.create({
    successText: {
      color: semanticColors.success,
    },
    correctOption: {
      backgroundColor: correctColors.background,
      borderColor: correctColors.border,
    }
  });
  
  // Component JSX...
}
```

## Migration from Hardcoded Styles

Components have been systematically migrated from hardcoded values to the theme system:

### Before
```typescript
const styles = StyleSheet.create({
  container: {
    backgroundColor: '#F5F5F5',
    padding: 20,
  },
  text: {
    color: '#333333',
    fontSize: 16,
  }
});
```

### After
```typescript
const createStyles = (theme) => {
  return StyleSheet.create({
    container: {
      backgroundColor: theme.colors.background.secondary,
      padding: theme.spacing.lg,
    },
    text: {
      color: theme.colors.text.primary,
      fontSize: theme.typography.fontSize.md,
    }
  });
};

function MyComponent() {
  const theme = useTheme();
  const styles = createStyles(theme);
  // Component JSX...
}
```

## Migrated Components

The following components have been successfully migrated to use the theme system:

### Core Components
- ✅ `VocabularyCard.tsx` - Uses theme for colors, spacing, and option states
- ✅ `StatsSummary.tsx` - Uses theme for layout and semantic colors
- ✅ `ProgressBar.tsx` - Uses theme for progress colors and spacing
- ✅ `ProcessingStatusIndicator.tsx` - Uses theme for status colors and layout

### Screens
- ✅ `EpisodeSelectionScreen.tsx` - Uses theme for layout and difficulty colors
- ✅ `GameScreen.tsx` - Uses theme for game states and interactive elements
- ✅ `A1DeciderGameScreen.tsx` - Uses theme for processing and vocabulary states

### Navigation
- ✅ `App.tsx` - Uses theme for navigation header styling

## Benefits

### 1. Consistency
- Unified color palette across all components
- Consistent spacing and typography
- Standardized interaction states

### 2. Maintainability
- Single source of truth for design tokens
- Easy to update colors and spacing globally
- Reduced code duplication

### 3. Scalability
- Ready for dark mode implementation
- Easy to add new themes or variants
- Supports design system evolution

### 4. Developer Experience
- Type-safe theme access
- Helpful utility functions
- Clear documentation and examples

### 5. Design Flexibility
- Semantic color functions for different contexts
- Common style patterns for rapid development
- Easy customization while maintaining consistency

## Future Enhancements

### Dark Mode Support
The theme system is ready for dark mode implementation:

```typescript
// Future dark theme
export const darkTheme: Theme = {
  colors: {
    background: {
      primary: '#121212',
      secondary: '#1E1E1E',
      tertiary: '#2D2D2D'
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#CCCCCC',
      // ...
    },
    // ... rest of dark theme
  },
  // ... other theme properties
};
```

### Additional Features
- Theme switching functionality
- User preference persistence
- Accessibility improvements
- Animation and transition tokens
- Component-specific theme overrides

## Best Practices

1. **Always use theme values** instead of hardcoded colors or spacing
2. **Use semantic color functions** for context-specific styling
3. **Leverage common styles** for consistent patterns
4. **Create themed style functions** for dynamic styling
5. **Test with different themes** to ensure compatibility

## Component Integration Checklist

When creating or updating components:

- [ ] Import `useTheme` hook
- [ ] Create dynamic styles using theme values
- [ ] Use semantic color functions where appropriate
- [ ] Leverage common style patterns
- [ ] Test component with theme changes
- [ ] Update component documentation

This design system provides a solid foundation for consistent, maintainable, and scalable UI development in the EpisodeGameApp.