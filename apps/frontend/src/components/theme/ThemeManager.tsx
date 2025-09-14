import React, { useState } from 'react';
import { 
  Palette, 
  Download, 
  Upload, 
  RefreshCw, 
  Eye, 
  Save, 
  Settings,
  Image,
  Type,
  Layout,
  Zap,
  Copy,
  Check
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { useTheme } from '@/contexts/ThemeContext';
// Tenant context removed for Community Edition

export default function ThemeManager() {
  // Tenant context removed for Community Edition
  const { 
    currentTheme, 
    whiteLabelSettings, 
    updateTheme, 
    resetTheme, 
    updateWhiteLabelSettings,
    toggleBranding,
    generateThemeCSS,
    exportTheme,
    importTheme,
    isLoading 
  } = useTheme();

  const [activeTab, setActiveTab] = useState('colors');
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  // Check if white-label is enabled
  const isWhiteLabelEnabled = false; // Disabled for Community Edition

  if (!isWhiteLabelEnabled) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card>
          <CardContent className="text-center py-8">
            <Palette className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">White-Label Feature Required</h3>
            <p className="text-muted-foreground mb-4">
              Theme management is available with Enterprise plan or white-label license.
            </p>
            <Button onClick={() => window.location.href = '/pricing'}>
              Upgrade to Enterprise
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const handleColorChange = (colorKey: string, value: string) => {
    updateTheme({
      colors: {
        ...currentTheme.colors,
        [colorKey]: value,
      },
    });
  };

  const handleTypographyChange = (typographyKey: string, value: any) => {
    updateTheme({
      typography: {
        ...currentTheme.typography,
        [typographyKey]: value,
      },
    });
  };

  const handleSpacingChange = (spacingKey: string, value: string) => {
    updateTheme({
      spacing: {
        ...currentTheme.spacing,
        [spacingKey]: value,
      },
    });
  };

  const handleBorderRadiusChange = (radiusKey: string, value: string) => {
    updateTheme({
      borderRadius: {
        ...currentTheme.borderRadius,
        [radiusKey]: value,
      },
    });
  };

  const handleCustomCSSChange = (css: string) => {
    updateTheme({
      customCSS: css,
    });
  };

  const handleWhiteLabelChange = (key: string, value: any) => {
    updateWhiteLabelSettings({
      [key]: value,
    });
  };

  const copyThemeCSS = async () => {
    const css = generateThemeCSS();
    await navigator.clipboard.writeText(css);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const exportThemeData = () => {
    const data = exportTheme();
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `theme-${currentTheme.name.toLowerCase().replace(/\s+/g, '-')}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const importThemeData = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        importTheme(content);
      };
      reader.readAsText(file);
    }
  };

  const actions = (
    <div className="flex items-center space-x-2">
      <Button variant="outline" onClick={() => setIsPreviewOpen(true)}>
        <Eye className="h-4 w-4 mr-2" />
        Preview
      </Button>
      <Button variant="outline" onClick={copyThemeCSS}>
        {copied ? (
          <Check className="h-4 w-4 mr-2" />
        ) : (
          <Copy className="h-4 w-4 mr-2" />
        )}
        {copied ? 'Copied!' : 'Copy CSS'}
      </Button>
      <Button variant="outline" onClick={exportThemeData}>
        <Download className="h-4 w-4 mr-2" />
        Export
      </Button>
      <Button variant="outline" onClick={() => document.getElementById('import-theme')?.click()}>
        <Upload className="h-4 w-4 mr-2" />
        Import
      </Button>
      <Button variant="outline" onClick={resetTheme}>
        <RefreshCw className="h-4 w-4 mr-2" />
        Reset
      </Button>
      <input
        id="import-theme"
        type="file"
        accept=".json"
        onChange={importThemeData}
        className="hidden"
      />
    </div>
  );

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Theme Management</h1>
            <p className="text-muted-foreground">Customize your application's appearance and branding</p>
          </div>
          <div className="flex items-center space-x-2">
            {actions}
          </div>
        </div>

        {/* White-Label Settings */}
        <Card>
          <CardHeader>
            <CardTitle>White-Label Settings</CardTitle>
            <p className="text-muted-foreground">Configure your branded experience</p>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="company-name">Company Name</Label>
                  <Input
                    id="company-name"
                    value={whiteLabelSettings?.companyName || ''}
                    onChange={(e) => handleWhiteLabelChange('companyName', e.target.value)}
                    placeholder="Your Company Name"
                  />
                </div>
                
                <div>
                  <Label htmlFor="support-email">Support Email</Label>
                  <Input
                    id="support-email"
                    type="email"
                    value={whiteLabelSettings?.supportEmail || ''}
                    onChange={(e) => handleWhiteLabelChange('supportEmail', e.target.value)}
                    placeholder="support@yourcompany.com"
                  />
                </div>
                
                <div>
                  <Label htmlFor="custom-domain">Custom Domain</Label>
                  <Input
                    id="custom-domain"
                    value={whiteLabelSettings?.customDomain || ''}
                    onChange={(e) => handleWhiteLabelChange('customDomain', e.target.value)}
                    placeholder="app.yourcompany.com"
                  />
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <Label htmlFor="footer-text">Footer Text</Label>
                  <Textarea
                    id="footer-text"
                    value={whiteLabelSettings?.footerText || ''}
                    onChange={(e) => handleWhiteLabelChange('footerText', e.target.value)}
                    placeholder="© 2024 Your Company. All rights reserved."
                    rows={3}
                  />
                </div>
                
                <div className="flex items-center space-x-2">
                  <Switch
                    id="remove-branding"
                    checked={whiteLabelSettings?.removeBranding || false}
                    onCheckedChange={toggleBranding}
                  />
                  <Label htmlFor="remove-branding">Remove TidyGen Branding</Label>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Theme Customization */}
        <Card>
          <CardHeader>
            <CardTitle>Theme Customization</CardTitle>
            <p className="text-muted-foreground">Customize colors, typography, and spacing</p>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <Label htmlFor="custom-css">Custom CSS</Label>
                <Textarea
                  id="custom-css"
                  value={currentTheme.customCSS || ''}
                  onChange={(e) => handleCustomCSSChange(e.target.value)}
                  placeholder="/* Add your custom CSS here */"
                  rows={10}
                  className="font-mono text-sm"
                />
                <p className="text-sm text-muted-foreground mt-2">
                  Add custom CSS to further customize your theme. Use CSS custom properties for consistency.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
