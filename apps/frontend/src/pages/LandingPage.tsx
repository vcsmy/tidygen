import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { PricingTable } from "@/components/landing/PricingTable";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { 
  Check, 
  Download, 
  Play, 
  Star, 
  Users, 
  Shield, 
  Zap, 
  Globe, 
  Headphones, 
  BookOpen, 
  ArrowRight,
  Building2,
  Sparkles,
  Lock,
  Server,
  Cloud,
  Code,
  BarChart3,
  Settings,
  Mail,
  Phone,
  MapPin,
  Github,
  ExternalLink
} from "lucide-react";
import { HeroSection } from "@/components/landing/HeroSection";
import { AboutSection } from "@/components/landing/AboutSection";
import { FeaturesSection } from "@/components/landing/FeaturesSection";
import { PricingSection } from "@/components/landing/PricingSection";
import { ServicesSection } from "@/components/landing/ServicesSection";
// PartnersSection removed for Community Edition
import { FooterSection } from "@/components/landing/FooterSection";

export default function LandingPage() {
  const navigate = useNavigate();

  const handleEnterApp = () => {
    navigate("/login");
  };

  const handleRequestDemo = () => {
    // In a real implementation, this would open a demo request form
    navigate("/contact?type=demo");
  };

  const handleStartTrial = () => {
    // In a real implementation, this would start a free trial
    navigate("/signup?trial=true");
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
                <Building2 className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold">iNEAT-ERP</span>
            </div>
            
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                Features
              </a>
              <a href="#deploy" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                Deploy
              </a>
              <a href="#services" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                Services
              </a>
              <a href="https://github.com/ineat/ineat-erp-community" target="_blank" rel="noopener noreferrer" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                GitHub
              </a>
            </div>

            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" onClick={handleEnterApp}>
                Sign In
              </Button>
              <Button size="sm" asChild>
                <a href="https://github.com/ineat/ineat-erp-community" target="_blank" rel="noopener noreferrer">
                  <Github className="h-4 w-4 mr-2" />
                  GitHub
                </a>
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <HeroSection 
        onEnterApp={handleEnterApp}
        onRequestDemo={handleRequestDemo}
        onStartTrial={handleStartTrial}
      />

      {/* About Section */}
      <AboutSection />

      {/* Features Section */}
      <FeaturesSection />

      {/* Deploy Section */}
      <div id="deploy" className="py-24 bg-muted/30">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold">
              Deploy iNeat Community Edition
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Get started with iNeat Community Edition in minutes. Choose your preferred deployment method.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <Card className="text-center">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Server className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Docker Compose</CardTitle>
                <p className="text-muted-foreground">Quick setup with Docker</p>
              </CardHeader>
              <CardContent>
                <Button className="w-full" asChild>
                  <a href="https://github.com/ineat/ineat-erp-community#quick-start" target="_blank" rel="noopener noreferrer">
                    <Download className="h-4 w-4 mr-2" />
                    Deploy with Docker
                    <ExternalLink className="h-4 w-4 ml-2" />
                  </a>
                </Button>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Cloud className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Cloud Deploy</CardTitle>
                <p className="text-muted-foreground">One-click cloud deployment</p>
              </CardHeader>
              <CardContent>
                <Button className="w-full" variant="outline" asChild>
                  <a href="https://vercel.com/new/clone?repository-url=https://github.com/ineat/ineat-erp-community" target="_blank" rel="noopener noreferrer">
                    <Cloud className="h-4 w-4 mr-2" />
                    Deploy to Vercel
                    <ExternalLink className="h-4 w-4 ml-2" />
                  </a>
                </Button>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Code className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Manual Setup</CardTitle>
                <p className="text-muted-foreground">Full control installation</p>
              </CardHeader>
              <CardContent>
                <Button className="w-full" variant="outline" asChild>
                  <a href="https://docs.ineat.io/community-edition/installation" target="_blank" rel="noopener noreferrer">
                    <BookOpen className="h-4 w-4 mr-2" />
                    View Docs
                    <ExternalLink className="h-4 w-4 ml-2" />
                  </a>
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Services Section */}
      <ServicesSection />

      {/* Partners Section removed for Community Edition */}

      {/* Footer */}
      <FooterSection />
    </div>
  );
}
