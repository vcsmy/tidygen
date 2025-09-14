import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Check, 
  Building2, 
  Users, 
  BarChart3, 
  Shield, 
  Zap, 
  Globe, 
  Headphones, 
  Settings,
  Lock,
  Server,
  Cloud,
  Code,
  Palette,
  Award,
  DollarSign,
  TrendingUp,
  Network,
  Database,
  Smartphone,
  Mail,
  Calendar,
  FileText,
  Github
} from "lucide-react";

export function FeaturesSection() {
  const coreFeatures = [
    {
      icon: <Building2 className="h-6 w-6" />,
      title: "Self-Hosted Architecture",
      description: "Simplified architecture perfect for individual businesses and organizations.",
      benefits: ["Data Security", "Easy Setup", "Full Control"]
    },
    {
      icon: <Users className="h-6 w-6" />,
      title: "User Management",
      description: "Simple user management with role-based access control for your team.",
      benefits: ["Secure Access", "Custom Roles", "User Permissions"]
    },
    {
      icon: <BarChart3 className="h-6 w-6" />,
      title: "Business Analytics",
      description: "Comprehensive reporting and analytics for business insights.",
      benefits: ["Custom Reports", "Data Visualization", "Export Options"]
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: "Data Security",
      description: "Strong security with encryption and secure data handling.",
      benefits: ["Data Encryption", "Secure Storage", "Privacy Control"]
    },
    {
      icon: <Zap className="h-6 w-6" />,
      title: "API Integration",
      description: "RESTful APIs for connecting with your favorite business tools.",
      benefits: ["REST APIs", "Webhooks", "Easy Integration"]
    },
    {
      icon: <Globe className="h-6 w-6" />,
      title: "Custom Branding",
      description: "Customize the interface to match your brand and preferences.",
      benefits: ["Custom Themes", "Brand Colors", "Logo Upload"]
    }
  ];

  const communityFeatures = [
    {
      icon: <Palette className="h-5 w-5" />,
      title: "Custom Theming",
      description: "Complete brand customization with custom CSS and themes."
    },
    {
      icon: <Code className="h-5 w-5" />,
      title: "Open Source",
      description: "Full source code available with MIT license for complete freedom."
    },
    {
      icon: <Shield className="h-5 w-5" />,
      title: "Data Privacy",
      description: "Complete control over your data with self-hosted deployment."
    },
    {
      icon: <TrendingUp className="h-5 w-5" />,
      title: "Performance Metrics",
      description: "Real-time analytics and KPI tracking for business growth."
    },
    {
      icon: <Network className="h-5 w-5" />,
      title: "API Integration",
      description: "RESTful APIs for connecting with your favorite business tools."
    },
    {
      icon: <Database className="h-5 w-5" />,
      title: "Data Management",
      description: "Advanced data import/export with backup and recovery options."
    },
    {
      icon: <Smartphone className="h-5 w-5" />,
      title: "Mobile Access",
      description: "Responsive design that works perfectly on all devices."
    },
    {
      icon: <Users className="h-5 w-5" />,
      title: "Community Support",
      description: "Active community support through Discord and GitHub discussions."
    }
  ];

  return (
    <section id="features" className="py-24 bg-muted/30">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-4 mb-16">
          <Badge variant="secondary" className="w-fit mx-auto">
            <Zap className="h-3 w-3 mr-1" />
            Community Features
          </Badge>
          <h2 className="text-3xl lg:text-4xl font-bold">
            Built for Developers & Small Businesses
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Our open-source ERP platform delivers powerful features with 
            complete data control, self-hosting capabilities, and community-driven development.
          </p>
        </div>

        {/* Core Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {coreFeatures.map((feature, index) => (
            <Card key={index} className="relative group hover:shadow-lg transition-all duration-300">
              <CardHeader className="pb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-lg bg-primary/10 text-primary">
                    {feature.icon}
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <p className="text-muted-foreground">
                  {feature.description}
                </p>
                
                <div className="space-y-2">
                  {feature.benefits.map((benefit, idx) => (
                    <div key={idx} className="flex items-center space-x-2">
                      <Check className="h-4 w-4 text-success flex-shrink-0" />
                      <span className="text-sm">{benefit}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Community Features */}
        <div className="bg-card border rounded-lg p-8">
          <div className="text-center space-y-4 mb-8">
            <h3 className="text-2xl font-bold">Community Edition Features</h3>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Powerful features designed for developers, small businesses, and grant foundations 
              who need complete control over their ERP system.
            </p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {communityFeatures.map((feature, index) => (
              <div key={index} className="text-center space-y-3">
                <div className="mx-auto p-3 rounded-lg bg-primary/10 text-primary w-fit">
                  {feature.icon}
                </div>
                <h4 className="font-semibold">{feature.title}</h4>
                <p className="text-sm text-muted-foreground">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Feature Highlights */}
        <div className="mt-16 grid md:grid-cols-3 gap-8">
          <div className="text-center space-y-4">
            <div className="mx-auto p-4 rounded-full bg-primary/10 text-primary w-fit">
              <Server className="h-8 w-8" />
            </div>
            <h4 className="text-xl font-semibold">Self-Hosted</h4>
            <p className="text-muted-foreground">
              Deploy on your own infrastructure with complete control over your data and privacy.
            </p>
          </div>
          
          <div className="text-center space-y-4">
            <div className="mx-auto p-4 rounded-full bg-success/10 text-success w-fit">
              <Lock className="h-8 w-8" />
            </div>
            <h4 className="text-xl font-semibold">Privacy First</h4>
            <p className="text-muted-foreground">
              Your data stays on your servers with strong encryption and privacy controls.
            </p>
          </div>
          
          <div className="text-center space-y-4">
            <div className="mx-auto p-4 rounded-full bg-warning/10 text-warning w-fit">
              <Settings className="h-8 w-8" />
            </div>
            <h4 className="text-xl font-semibold">Fully Customizable</h4>
            <p className="text-muted-foreground">
              Open source code allows complete customization and integration with your tools.
            </p>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-16 text-center">
          <div className="space-y-6">
            <h3 className="text-2xl font-bold">Ready to Get Started?</h3>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Join the community of developers and small businesses using TidyGen Community Edition 
              to manage their operations with complete data control and privacy.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" asChild>
                <a href="https://github.com/tidygen/tidygen-community" target="_blank" rel="noopener noreferrer">
                  <Github className="h-4 w-4 mr-2" />
                  Get on GitHub
                </a>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <a href="https://docs.tidygen.io/community-edition/installation" target="_blank" rel="noopener noreferrer">
                  <FileText className="h-4 w-4 mr-2" />
                  Installation Guide
                </a>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
