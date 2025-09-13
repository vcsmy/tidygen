import { Card, CardContent } from "@/components/ui/card";
import { 
  Users, 
  Shield, 
  Star,
  Github,
  Code,
  Server,
  Database,
  Cpu
} from "lucide-react";

export function AboutSection() {
  const features = [
    {
      icon: <Github className="h-6 w-6" />,
      title: "Open Source & Free",
      description: "MIT licensed, completely free to use, modify, and distribute. Full source code available on GitHub."
    },
    {
      icon: <Server className="h-6 w-6" />,
      title: "Self-Hosted Control",
      description: "Deploy on your own infrastructure with complete control over your data and privacy."
    },
    {
      icon: <Code className="h-6 w-6" />,
      title: "Developer Friendly",
      description: "Built with modern technologies, comprehensive APIs, and extensive documentation."
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: "Web3 Aligned",
      description: "Designed with Web3 principles, supporting decentralized identity and blockchain integration."
    },
    {
      icon: <Database className="h-6 w-6" />,
      title: "Single-Tenant Architecture",
      description: "Simplified architecture perfect for small businesses and individual organizations."
    },
    {
      icon: <Cpu className="h-6 w-6" />,
      title: "Lightweight & Fast",
      description: "Optimized for performance with minimal resource requirements and fast deployment."
    }
  ];

  const stats = [
    { label: "GitHub Stars", value: "1.2k+" },
    { label: "Active Contributors", value: "50+" },
    { label: "Community Members", value: "500+" },
    { label: "Deployments", value: "2k+" }
  ];

  return (
    <section id="about" className="py-24 bg-muted/30">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-4 mb-16">
          <div className="flex justify-center mb-4">
            <div className="inline-flex items-center rounded-full border border-border px-2.5 py-0.5 text-xs font-semibold transition-colors text-foreground">
              <Shield className="h-3 w-3 mr-1" />
              Web3 Foundation Grant Candidate
            </div>
          </div>
          <h2 className="text-3xl lg:text-4xl font-bold">
            Why Choose iNeat Community Edition?
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            A free, open-source ERP system designed for developers, small businesses, and grant foundations. 
            Self-host your own Web3-aligned business management solution with complete control over your data.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {features.map((feature, index) => (
            <Card key={index} className="border-0 shadow-sm hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center text-primary">
                    {feature.icon}
                  </div>
                  <div className="space-y-2">
                    <h3 className="font-semibold">{feature.title}</h3>
                    <p className="text-sm text-muted-foreground">{feature.description}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
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

        {/* Trust Section */}
        <div className="mt-16 text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="flex">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className="h-5 w-5 fill-yellow-400 text-yellow-400" />
              ))}
            </div>
            <span className="text-sm font-medium">4.8/5 from 200+ community reviews</span>
          </div>
          <p className="text-sm text-muted-foreground">
            Trusted by developers and small businesses worldwide for reliable, self-hosted ERP management
          </p>
          
          {/* GitHub Stats */}
          <div className="mt-8 flex justify-center space-x-6 text-sm text-muted-foreground">
            <div className="flex items-center space-x-1">
              <Github className="h-4 w-4" />
              <span>1.2k+ Stars</span>
            </div>
            <div className="flex items-center space-x-1">
              <Users className="h-4 w-4" />
              <span>50+ Contributors</span>
            </div>
            <div className="flex items-center space-x-1">
              <Code className="h-4 w-4" />
              <span>MIT License</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
