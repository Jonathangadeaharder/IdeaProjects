import React, { createContext, useContext, ReactNode } from 'react';
import { Theme, lightTheme, darkTheme } from './index';

interface ThemeContextType {
  theme: Theme;
  isDark: boolean;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
  initialTheme?: 'light' | 'dark';
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ 
  children, 
  initialTheme = 'light' 
}) => {
  const [isDark, setIsDark] = React.useState(initialTheme === 'dark');
  
  const theme = isDark ? darkTheme : lightTheme;
  
  const toggleTheme = () => {
    setIsDark(!isDark);
  };
  
  const value = {
    theme,
    isDark,
    toggleTheme,
  };
  
  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export default ThemeProvider;