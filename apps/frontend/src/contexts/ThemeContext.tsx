import React, { createContext, useContext, useEffect, useState } from 'react';
// Tenant context removed for Community Edition
import { toast } from '@/components/ui/enhanced-notifications';

// Theme Types
export interface ThemeColors {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  foreground: string;
  muted: string;
  mutedForeground: string;
  popover: string;
  popoverForeground: string;
  card: string;
  cardForeground: string;
  border: string;
  input: string;
  ring: string;
  success: string;
  warning: string;
  error: string;
  info: string;
}

export interface ThemeTypography {
  fontFamily: string;
  fontSize: {
    xs: string;
    sm: string;
    base: string;
    lg: string;
    xl: string;
    '2xl': string;
    '3xl': string;
    '4xl': string;
    '5xl': string;
    '6xl': string;
  };
  fontWeight: {
    light: number;
    normal: number;
    medium: number;
    semibold: number;
    bold: number;
    extrabold: number;
  };
  lineHeight: {
    tight: number;
    snug: number;
    normal: number;
    relaxed: number;
    loose: number;
  };
}

export interface ThemeSpacing {
  xs: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  '2xl': string;
  '3xl': string;
}

export interface ThemeBorderRadius {
  none: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  '2xl': string;
  '3xl': string;
  full: string;
}

export interface ThemeShadows {
  sm: string;
  md: string;
  lg: string;
  xl: string;
  '2xl': string;
  inner: string;
  none: string;
}

export interface CustomTheme {
  id: string;
  name: string;
  description: string;
  colors: ThemeColors;
  typography: ThemeTypography;
  spacing: ThemeSpacing;
  borderRadius: ThemeBorderRadius;
  shadows: ThemeShadows;
  customCSS?: string;
  logo?: string;
  favicon?: string;
  createdAt: string;
  updatedAt: string;
}

export interface WhiteLabelSettings {
  enabled: boolean;
  companyName: string;
  companyLogo?: string;
  favicon?: string;
  customDomain?: string;
  supportEmail: string;
  supportPhone?: string;
  privacyPolicyUrl?: string;
  termsOfServiceUrl?: string;
  customCSS?: string;
  theme: CustomTheme;
  footerText?: string;
  removeBranding: boolean;
  customColors: Partial<ThemeColors>;
}

// Default Theme
const defaultTheme: CustomTheme = {
  id: 'default',
  name: 'Default Theme',
  description: 'Standard TidyGen theme',
  colors: {
    primary: 'hsl(221.2 83.2% 53.3%)',
    secondary: 'hsl(210 40% 98%)',
    accent: 'hsl(210 40% 96%)',
    background: 'hsl(0 0% 100%)',
    foreground: 'hsl(222.2 84% 4.9%)',
    muted: 'hsl(210 40% 96%)',
    mutedForeground: 'hsl(215.4 16.3% 46.9%)',
    popover: 'hsl(0 0% 100%)',
    popoverForeground: 'hsl(222.2 84% 4.9%)',
    card: 'hsl(0 0% 100%)',
    cardForeground: 'hsl(222.2 84% 4.9%)',
    border: 'hsl(214.3 31.8% 91.4%)',
    input: 'hsl(214.3 31.8% 91.4%)',
    ring: 'hsl(221.2 83.2% 53.3%)',
    success: 'hsl(142.1 76.2% 36.3%)',
    warning: 'hsl(38 92% 50%)',
    error: 'hsl(0 84.2% 60.2%)',
    info: 'hsl(221.2 83.2% 53.3%)',
  },
  typography: {
    fontFamily: 'Inter, system-ui, sans-serif',
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
      '5xl': '3rem',
      '6xl': '3.75rem',
    },
    fontWeight: {
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      extrabold: 800,
    },
    lineHeight: {
      tight: 1.25,
      snug: 1.375,
      normal: 1.5,
      relaxed: 1.625,
      loose: 2,
    },
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
    '3xl': '4rem',
  },
  borderRadius: {
    none: '0',
    sm: '0.125rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    '2xl': '1rem',
    '3xl': '1.5rem',
    full: '9999px',
  },
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
    none: '0 0 #0000',
  },
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

// Context Type
interface ThemeContextType {
  // Current theme
  currentTheme: CustomTheme;
  whiteLabelSettings: WhiteLabelSettings | null;
  
  // Theme management
  updateTheme: (theme: Partial<CustomTheme>) => void;
  resetTheme: () => void;
  applyCustomCSS: (css: string) => void;
  
  // White-label management
  updateWhiteLabelSettings: (settings: Partial<WhiteLabelSettings>) => void;
  toggleBranding: (remove: boolean) => void;
  
  // Theme utilities
  generateThemeCSS: () => string;
  exportTheme: () => string;
  importTheme: (themeData: string) => void;
  
  // Loading state
  isLoading: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// API Functions
const themeApi = {
  getWhiteLabelSettings: () => apiClient.get<WhiteLabelSettings>('/themes/white-label/'),
  updateWhiteLabelSettings: (settings: Partial<WhiteLabelSettings>) =>
    apiClient.patch('/themes/white-label/', settings),
  getCustomThemes: () => apiClient.get<CustomTheme[]>('/themes/'),
  createCustomTheme: (theme: CustomTheme) => apiClient.post('/themes/', theme),
  updateCustomTheme: (themeId: string, theme: Partial<CustomTheme>) =>
    apiClient.patch(`/themes/${themeId}/`, theme),
  deleteCustomTheme: (themeId: string) => apiClient.delete(`/themes/${themeId}/`),
};

// Theme Provider
interface ThemeProviderProps {
  children: React.ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  // Tenant context removed for Community Edition
  const [currentTheme, setCurrentTheme] = useState<CustomTheme>(defaultTheme);
  const [whiteLabelSettings, setWhiteLabelSettings] = useState<WhiteLabelSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch white-label settings
  useEffect(() => {
    // White label disabled for Community Edition
    if (false) {
      fetchWhiteLabelSettings();
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchWhiteLabelSettings = async () => {
    try {
      const response = await themeApi.getWhiteLabelSettings();
      setWhiteLabelSettings(response.data);
      
      // Apply custom theme if available
      if (response.data.theme) {
        setCurrentTheme(response.data.theme);
        applyThemeToDOM(response.data.theme);
      }
      
      // Apply custom CSS if available
      if (response.data.customCSS) {
        applyCustomCSS(response.data.customCSS);
      }
    } catch (error) {
      console.error('Failed to fetch white-label settings:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const applyThemeToDOM = (theme: CustomTheme) => {
    const root = document.documentElement;
    
    // Apply CSS custom properties
    Object.entries(theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });
    
    // Apply typography
    root.style.setProperty('--font-family', theme.typography.fontFamily);
    
    // Apply spacing
    Object.entries(theme.spacing).forEach(([key, value]) => {
      root.style.setProperty(`--spacing-${key}`, value);
    });
    
    // Apply border radius
    Object.entries(theme.borderRadius).forEach(([key, value]) => {
      root.style.setProperty(`--radius-${key}`, value);
    });
    
    // Apply shadows
    Object.entries(theme.shadows).forEach(([key, value]) => {
      root.style.setProperty(`--shadow-${key}`, value);
    });
  };

  const applyCustomCSS = (css: string) => {
    // Remove existing custom CSS
    const existingStyle = document.getElementById('custom-theme-css');
    if (existingStyle) {
      existingStyle.remove();
    }
    
    // Add new custom CSS
    const style = document.createElement('style');
    style.id = 'custom-theme-css';
    style.textContent = css;
    document.head.appendChild(style);
  };

  const updateTheme = (themeUpdates: Partial<CustomTheme>) => {
    const updatedTheme = { ...currentTheme, ...themeUpdates };
    setCurrentTheme(updatedTheme);
    applyThemeToDOM(updatedTheme);
    
    // Save to backend if white-label is enabled
    if (whiteLabelSettings?.enabled) {
      saveThemeToBackend(updatedTheme);
    }
  };

  const resetTheme = () => {
    setCurrentTheme(defaultTheme);
    applyThemeToDOM(defaultTheme);
    
    // Remove custom CSS
    const existingStyle = document.getElementById('custom-theme-css');
    if (existingStyle) {
      existingStyle.remove();
    }
    
    // Save to backend
    if (whiteLabelSettings?.enabled) {
      saveThemeToBackend(defaultTheme);
    }
  };

  const saveThemeToBackend = async (theme: CustomTheme) => {
    try {
      await themeApi.updateCustomTheme(theme.id, theme);
    } catch (error) {
      console.error('Failed to save theme:', error);
      toast.error('Save Failed', 'Failed to save theme changes');
    }
  };

  const updateWhiteLabelSettings = async (settings: Partial<WhiteLabelSettings>) => {
    try {
      const updatedSettings = { ...whiteLabelSettings, ...settings };
      setWhiteLabelSettings(updatedSettings);
      
      // Apply theme if updated
      if (settings.theme) {
        setCurrentTheme(settings.theme);
        applyThemeToDOM(settings.theme);
      }
      
      // Apply custom CSS if updated
      if (settings.customCSS) {
        applyCustomCSS(settings.customCSS);
      }
      
      // Save to backend
      await themeApi.updateWhiteLabelSettings(settings);
      toast.success('Settings Updated', 'White-label settings updated successfully');
    } catch (error) {
      console.error('Failed to update white-label settings:', error);
      toast.error('Update Failed', 'Failed to update white-label settings');
    }
  };

  const toggleBranding = (remove: boolean) => {
    updateWhiteLabelSettings({ removeBranding: remove });
  };

  const generateThemeCSS = (): string => {
    const css = `
:root {
  /* Colors */
${Object.entries(currentTheme.colors).map(([key, value]) => `  --color-${key}: ${value};`).join('\n')}
  
  /* Typography */
  --font-family: ${currentTheme.typography.fontFamily};
  
  /* Spacing */
${Object.entries(currentTheme.spacing).map(([key, value]) => `  --spacing-${key}: ${value};`).join('\n')}
  
  /* Border Radius */
${Object.entries(currentTheme.borderRadius).map(([key, value]) => `  --radius-${key}: ${value};`).join('\n')}
  
  /* Shadows */
${Object.entries(currentTheme.shadows).map(([key, value]) => `  --shadow-${key}: ${value};`).join('\n')}
}

/* Custom CSS */
${currentTheme.customCSS || ''}
    `.trim();
    
    return css;
  };

  const exportTheme = (): string => {
    return JSON.stringify(currentTheme, null, 2);
  };

  const importTheme = (themeData: string) => {
    try {
      const theme = JSON.parse(themeData) as CustomTheme;
      updateTheme(theme);
      toast.success('Theme Imported', 'Theme imported successfully');
    } catch (error) {
      console.error('Failed to import theme:', error);
      toast.error('Import Failed', 'Invalid theme data');
    }
  };

  const value: ThemeContextType = {
    currentTheme,
    whiteLabelSettings,
    updateTheme,
    resetTheme,
    applyCustomCSS,
    updateWhiteLabelSettings,
    toggleBranding,
    generateThemeCSS,
    exportTheme,
    importTheme,
    isLoading,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

// Theme-aware component wrapper
interface ThemeAwareProps {
  children: React.ReactNode;
  className?: string;
}

export function ThemeAware({ children, className }: ThemeAwareProps) {
  const { currentTheme, whiteLabelSettings } = useTheme();
  
  const shouldRemoveBranding = whiteLabelSettings?.removeBranding && whiteLabelSettings?.enabled;
  
  return (
    <div 
      className={className}
      data-theme={currentTheme.id}
      data-white-label={whiteLabelSettings?.enabled}
      data-no-branding={shouldRemoveBranding}
    >
      {children}
    </div>
  );
}

export default ThemeProvider;