import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  ArrowRight, 
  Play, 
  Download, 
  Sparkles, 
  Building2, 
  Users, 
  BarChart3,
  Shield,
  Github,
  Server,
  BookOpen,
  ExternalLink
} from "lucide-react";

interface HeroSectionProps {
  onEnterApp: () => void;
  onRequestDemo: () => void;
  onStartTrial: () => void;
}

export function HeroSection({ onEnterApp, onRequestDemo, onStartTrial }: HeroSectionProps) {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-primary/5 via-background to-accent/5">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Column - Content */}
          <div className="space-y-8">
            <div className="space-y-4">
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary" className="w-fit">
                  <Sparkles className="h-3 w-3 mr-1" />
                  Free & Open Source
                </Badge>
                <Badge variant="outline" className="w-fit">
                  <Shield className="h-3 w-3 mr-1" />
                  Web3 Foundation Grant Candidate
                </Badge>
              </div>
              
              <h1 className="text-2xl lg:text-4xl font-bold tracking-tight">
                iNeat Community Edition
                <span className="text-primary"> – Free, Open Source, and Self-Hosted</span>
              </h1>
              
              <p className="text-xl text-muted-foreground max-w-2xl">
                A simplified, single-tenant version of iNeat ERP perfect for developers, small businesses, 
                and grant foundations. Self-host your own Web3-aligned ERP system with full control over your data.
              </p>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <Button size="lg" className="group" asChild>
                <a href="https://github.com/ineat/ineat-erp-community" target="_blank" rel="noopener noreferrer">
                  <Github className="h-4 w-4 mr-2" />
                  Get on GitHub
                  <ArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </a>
              </Button>
              
              <Button size="lg" variant="outline" className="group" asChild>
                <a href="#deploy" onClick={(e) => { e.preventDefault(); document.getElementById('deploy')?.scrollIntoView({ behavior: 'smooth' }); }}>
                  <Server className="h-4 w-4 mr-2" />
                  Deploy Now
                  <ArrowRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </a>
              </Button>
            </div>

            {/* Secondary CTAs */}
            <div className="flex flex-col sm:flex-row gap-4">
              <Button variant="ghost" size="sm" className="group" asChild>
                <a href="https://docs.ineat.io/community-edition/self-hosting" target="_blank" rel="noopener noreferrer">
                  <BookOpen className="h-4 w-4 mr-2" />
                  Self-Host Guide
                  <ExternalLink className="h-3 w-3 ml-2" />
                </a>
              </Button>
              
              <Button variant="ghost" size="sm" className="group" asChild>
                <a href="https://discord.gg/ineat-community" target="_blank" rel="noopener noreferrer">
                  <Users className="h-4 w-4 mr-2" />
                  Join Community
                  <ExternalLink className="h-3 w-3 ml-2" />
                </a>
              </Button>
            </div>

            {/* Trust Indicators */}
            <div className="flex flex-wrap items-center gap-6 text-sm text-muted-foreground">
              <div className="flex items-center space-x-1">
                <Github className="h-4 w-4" />
                <span>Open Source</span>
              </div>
              <div className="flex items-center space-x-1">
                <Shield className="h-4 w-4" />
                <span>Self-Hosted</span>
              </div>
              <div className="flex items-center space-x-1">
                <Users className="h-4 w-4" />
                <span>Community Driven</span>
              </div>
              <div className="flex items-center space-x-1">
                <BarChart3 className="h-4 w-4" />
                <span>Web3 Aligned</span>
              </div>
            </div>
          </div>

          {/* Right Column - Visual */}
          <div className="relative">
            <div className="relative z-10">
              {/* Self-Hosted Dashboard Preview */}
              <div className="bg-card border rounded-lg shadow-2xl overflow-hidden">
                <div className="bg-muted/50 px-4 py-3 border-b">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span className="ml-4 text-sm text-muted-foreground">iNeat Community Edition</span>
                    <Badge variant="outline" className="ml-auto text-xs">Self-Hosted</Badge>
                  </div>
                </div>
                
                <div className="p-6 space-y-4">
                  {/* Mock Dashboard Content */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-primary/10 p-4 rounded-lg">
                      <div className="flex items-center space-x-2 mb-2">
                        <Users className="h-4 w-4 text-primary" />
                        <span className="text-sm font-medium">Active Users</span>
                      </div>
                      <div className="text-2xl font-bold">12</div>
                      <div className="text-xs text-muted-foreground">Your team</div>
                    </div>
                    
                    <div className="bg-success/10 p-4 rounded-lg">
                      <div className="flex items-center space-x-2 mb-2">
                        <BarChart3 className="h-4 w-4 text-success" />
                        <span className="text-sm font-medium">Data Control</span>
                      </div>
                      <div className="text-2xl font-bold">100%</div>
                      <div className="text-xs text-muted-foreground">Your servers</div>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span>Inventory Management</span>
                      <Badge variant="secondary" className="text-xs">Active</Badge>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span>Financial Reports</span>
                      <Badge variant="secondary" className="text-xs">Active</Badge>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span>Web3 Integration</span>
                      <Badge variant="secondary" className="text-xs">Ready</Badge>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Background Elements */}
            <div className="absolute -top-4 -right-4 w-72 h-72 bg-primary/10 rounded-full blur-3xl"></div>
            <div className="absolute -bottom-8 -left-8 w-96 h-96 bg-accent/10 rounded-full blur-3xl"></div>
          </div>
        </div>
      </div>
    </section>
  );
}
