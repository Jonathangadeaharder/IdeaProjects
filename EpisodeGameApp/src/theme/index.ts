// Design System Theme Configuration
// Centralized theme provider for consistent colors, typography, and spacing

export interface Theme {
  colors: {
    // Primary Colors
    primary: string;
    primaryLight: string;
    primaryDark: string;
    
    // Secondary Colors
    secondary: string;
    secondaryLight: string;
    secondaryDark: string;
    
    // Semantic Colors
    success: string;
    successLight: string;
    warning: string;
    warningLight: string;
    error: string;
    errorLight: string;
    info: string;
    infoLight: string;
    
    // Neutral Colors
    background: string;
    surface: string;
    surfaceVariant: string;
    outline: string;
    outlineVariant: string;
    
    // Text Colors
    onBackground: string;
    onSurface: string;
    onSurfaceVariant: string;
    onPrimary: string;
    onSecondary: string;
    
    // Interactive States
    disabled: string;
    disabledText: string;
    
    // Shadow
    shadow: string;
  };
  
  typography: {
    // Font Families
    fontFamily: {
      regular: string;
      medium: string;
      bold: string;
    };
    
    // Font Sizes
    fontSize: {
      xs: number;    // 10px
      sm: number;    // 12px
      base: number;  // 14px
      md: number;    // 16px
      lg: number;    // 18px
      xl: number;    // 20px
      '2xl': number; // 24px
      '3xl': number; // 28px
      '4xl': number; // 32px
      '5xl': number; // 36px
    };
    
    // Font Weights
    fontWeight: {
      normal: '400';
      medium: '500';
      semibold: '600';
      bold: '700';
    };
    
    // Line Heights
    lineHeight: {
      tight: number;
      normal: number;
      relaxed: number;
    };
  };
  
  spacing: {
    xs: number;   // 4px
    sm: number;   // 8px
    md: number;   // 12px
    lg: number;   // 16px
    xl: number;   // 20px
    '2xl': number; // 24px
    '3xl': number; // 32px
    '4xl': number; // 40px
    '5xl': number; // 48px
    '6xl': number; // 64px
  };
  
  borderRadius: {
    none: number;
    sm: number;   // 4px
    md: number;   // 8px
    lg: number;   // 12px
    xl: number;   // 16px
    full: number; // 9999px
  };
  
  shadows: {
    sm: {
      shadowColor: string;
      shadowOffset: { width: number; height: number };
      shadowOpacity: number;
      shadowRadius: number;
      elevation: number;
    };
    md: {
      shadowColor: string;
      shadowOffset: { width: number; height: number };
      shadowOpacity: number;
      shadowRadius: number;
      elevation: number;
    };
    lg: {
      shadowColor: string;
      shadowOffset: { width: number; height: number };
      shadowOpacity: number;
      shadowRadius: number;
      elevation: number;
    };
  };
}

// Default Light Theme
export const lightTheme: Theme = {
  colors: {
    // Primary Colors (Blue)
    primary: '#2196F3',
    primaryLight: '#E3F2FD',
    primaryDark: '#1976D2',
    
    // Secondary Colors (Green)
    secondary: '#4CAF50',
    secondaryLight: '#E8F5E8',
    secondaryDark: '#388E3C',
    
    // Semantic Colors
    success: '#4CAF50',
    successLight: '#E8F5E8',
    warning: '#FF9800',
    warningLight: '#FFF3E0',
    error: '#F44336',
    errorLight: '#FFEBEE',
    info: '#2196F3',
    infoLight: '#E3F2FD',
    
    // Neutral Colors
    background: '#F5F5F5',
    surface: '#FFFFFF',
    surfaceVariant: '#F8F9FA',
    outline: '#E0E0E0',
    outlineVariant: '#EEEEEE',
    
    // Text Colors
    onBackground: '#333333',
    onSurface: '#333333',
    onSurfaceVariant: '#666666',
    onPrimary: '#FFFFFF',
    onSecondary: '#FFFFFF',
    
    // Interactive States
    disabled: '#CCCCCC',
    disabledText: '#999999',
    
    // Shadow
    shadow: '#000000',
  },
  
  typography: {
    fontFamily: {
      regular: 'System',
      medium: 'System',
      bold: 'System',
    },
    
    fontSize: {
      xs: 10,
      sm: 12,
      base: 14,
      md: 16,
      lg: 18,
      xl: 20,
      '2xl': 24,
      '3xl': 28,
      '4xl': 32,
      '5xl': 36,
    },
    
    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
    },
    
    lineHeight: {
      tight: 1.2,
      normal: 1.5,
      relaxed: 1.8,
    },
  },
  
  spacing: {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 20,
    '2xl': 24,
    '3xl': 32,
    '4xl': 40,
    '5xl': 48,
    '6xl': 64,
  },
  
  borderRadius: {
    none: 0,
    sm: 4,
    md: 8,
    lg: 12,
    xl: 16,
    full: 9999,
  },
  
  shadows: {
    sm: {
      shadowColor: '#000000',
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.1,
      shadowRadius: 2,
      elevation: 2,
    },
    md: {
      shadowColor: '#000000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 3,
    },
    lg: {
      shadowColor: '#000000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.15,
      shadowRadius: 8,
      elevation: 5,
    },
  },
};

// Dark Theme (for future use)
export const darkTheme: Theme = {
  ...lightTheme,
  colors: {
    ...lightTheme.colors,
    background: '#121212',
    surface: '#1E1E1E',
    surfaceVariant: '#2C2C2C',
    outline: '#404040',
    outlineVariant: '#333333',
    onBackground: '#FFFFFF',
    onSurface: '#FFFFFF',
    onSurfaceVariant: '#CCCCCC',
  },
};

export default lightTheme;