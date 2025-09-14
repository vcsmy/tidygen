import * as React from "react";
import { Button } from "@/components/ui/enhanced-button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { useTheme } from "@/contexts/ThemeContext";
import { 
  ArrowRight, 
  Play, 
  Download, 
  Sparkles, 
  Building2, 
  Users, 
  BarChart3,
  Shield,
  Zap,
  Globe,
  CheckCircle,
  Star,
  Github,
  ExternalLink,
} from "lucide-react";

interface EnhancedHeroSectionProps {
  onEnterApp: () => void;
  onTryDemo: () => void;
  onDownloadCommunity: () => void;
}

export function EnhancedHeroSection({ 
  onEnterApp, 
  onTryDemo, 
  onDownloadCommunity 
}: EnhancedHeroSectionProps) {
  const { isDark } = useTheme();

  const features = [
    {
      icon: <Shield className="h-5 w-5" />,
      title: "Enterprise Security",
      description: "Bank-grade security with role-based access control"
    },
    {
      icon: <Zap className="h-5 w-5" />,
      title: "Lightning Fast",
      description: "Optimized performance with modern technology stack"
    },
    {
      icon: <Globe className="h-5 w-5" />,
      title: "Cloud & On-Premise",
      description: "Deploy anywhere - cloud, on-premise, or hybrid"
    }
  ];

  const stats = [
    { label: "Active Users", value: "10,000+" },
    { label: "Companies Served", value: "500+" },
    { label: "Uptime", value: "99.9%" },
    { label: "Support Rating", value: "4.9/5" }
  ];

  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-primary/5 via-background to-accent/5">
      {/* Background Elements */}
      <div className="absolute inset-0 bg-grid-pattern opacity-5" />
      <div className="absolute -top-4 -right-4 w-72 h-72 bg-primary/10 rounded-full blur-3xl" />
      <div className="absolute -bottom-8 -left-8 w-96 h-96 bg-accent/10 rounded-full blur-3xl" />
      
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32 relative">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Column - Content */}
          <div className="space-y-8">
            <div className="space-y-4">
              <Badge variant="secondary" className="w-fit">
                <Sparkles className="h-3 w-3 mr-1" />
                Enterprise-Grade Cleaning ERP
              </Badge>
              
              <h1 className="text-4xl lg:text-6xl font-bold tracking-tight">
                Streamline Your
                <span className="text-primary"> Cleaning Business</span>
              </h1>
              
              <p className="text-xl text-muted-foreground max-w-2xl">
                Complete ERP solution for cleaning services. Manage clients, inventory, 
                scheduling, finance, and HR all in one powerful platform.
              </p>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <Button size="lg" onClick={onTryDemo} className="group">
                <Play className="h-4 w-4 mr-2" />
                Try Demo Enterprise
                <ArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
              
              <Button size="lg" variant="outline" onClick={onDownloadCommunity} className="group">
                <Download className="h-4 w-4 mr-2" />
                Download Community
                <ArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </div>

            {/* Trust Indicators */}
            <div className="flex items-center space-x-6 text-sm text-muted-foreground">
              <div className="flex items-center space-x-1">
                <Shield className="h-4 w-4" />
                <span>Open Source</span>
              </div>
              <div className="flex items-center space-x-1">
                <Users className="h-4 w-4" />
                <span>Trusted by 500+ Companies</span>
              </div>
              <div className="flex items-center space-x-1">
                <BarChart3 className="h-4 w-4" />
                <span>99.9% Uptime</span>
              </div>
            </div>

            {/* Feature Highlights */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {features.map((feature, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center text-primary">
                    {feature.icon}
                  </div>
                  <div className="space-y-1">
                    <h3 className="text-sm font-medium">{feature.title}</h3>
                    <p className="text-xs text-muted-foreground">{feature.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Column - Visual */}
          <div className="relative">
            <div className="relative z-10">
              {/* Dashboard Preview */}
              <Card className="bg-card border shadow-2xl overflow-hidden">
                <div className="bg-muted/50 px-4 py-3 border-b">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span className="ml-4 text-sm text-muted-foreground">TidyGen Dashboard</span>
                  </div>
                </div>
                
                <CardContent className="p-6 space-y-4">
                  {/* Mock Dashboard Content */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-primary/10 p-4 rounded-lg">
                      <div className="flex items-center space-x-2 mb-2">
                        <Building2 className="h-4 w-4 text-primary" />
                        <span className="text-sm font-medium">Total Clients</span>
                      </div>
                      <div className="text-2xl font-bold">1,247</div>
                      <div className="text-xs text-muted-foreground">+12% this month</div>
                    </div>
                    
                    <div className="bg-success/10 p-4 rounded-lg">
                      <div className="flex items-center space-x-2 mb-2">
                        <BarChart3 className="h-4 w-4 text-success" />
                        <span className="text-sm font-medium">Revenue</span>
                      </div>
                      <div className="text-2xl font-bold">$45.2K</div>
                      <div className="text-xs text-muted-foreground">+8% this month</div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="h-2 bg-muted rounded-full">
                      <div className="h-2 bg-primary rounded-full w-3/4"></div>
                    </div>
                    <div className="h-2 bg-muted rounded-full">
                      <div className="h-2 bg-accent rounded-full w-1/2"></div>
                    </div>
                    <div className="h-2 bg-muted rounded-full">
                      <div className="h-2 bg-success rounded-full w-5/6"></div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Floating Cards */}
              <div className="absolute -top-4 -right-4 w-32 h-20 bg-success/10 rounded-lg border border-success/20 p-3 shadow-lg">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-success" />
                  <span className="text-xs font-medium">Real-time Sync</span>
                </div>
                <div className="text-xs text-muted-foreground mt-1">All devices updated</div>
              </div>

              <div className="absolute -bottom-4 -left-4 w-32 h-20 bg-warning/10 rounded-lg border border-warning/20 p-3 shadow-lg">
                <div className="flex items-center space-x-2">
                  <Star className="h-4 w-4 text-warning" />
                  <span className="text-xs font-medium">AI Analytics</span>
                </div>
                <div className="text-xs text-muted-foreground mt-1">Smart insights</div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Section */}
        <div className="mt-16 grid grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-3xl lg:text-4xl font-bold text-primary mb-2">
                {stat.value}
              </div>
              <div className="text-sm text-muted-foreground">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
