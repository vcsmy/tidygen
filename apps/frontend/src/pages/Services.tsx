import React, { useState } from 'react';
import { 
  Server, 
  GraduationCap, 
  Headphones, 
  Shield, 
  Zap, 
  Globe, 
  Users, 
  CheckCircle, 
  ArrowRight, 
  Star,
  Clock,
  Award,
  MessageCircle,
  BookOpen,
  Code,
  Database
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface Service {
  id: string;
  title: string;
  description: string;
  features: string[];
  pricing: {
    starting: string;
    unit: string;
  };
  icon: React.ComponentType<any>;
  popular?: boolean;
  category: 'hosting' | 'training' | 'support' | 'development';
}

const services: Service[] = [
  // Hosting Services
  {
    id: 'managed-hosting',
    title: 'Managed Hosting',
    description: 'Fully managed cloud hosting with automatic backups, monitoring, and updates',
    features: [
      '24/7 server monitoring',
      'Automatic backups',
      'SSL certificates',
      'CDN integration',
      '99.9% uptime guarantee',
      'Performance optimization',
      'Security updates',
      'Technical support'
    ],
    pricing: {
      starting: '$29',
      unit: '/month'
    },
    icon: Server,
    popular: true,
    category: 'hosting'
  },
  {
    id: 'self-hosted-support',
    title: 'Self-Hosted Support',
    description: 'Expert support for your self-hosted TidyGen installation',
    features: [
      'Installation assistance',
      'Configuration guidance',
      'Troubleshooting support',
      'Performance tuning',
      'Security hardening',
      'Migration services',
      'Custom setup scripts',
      'Documentation updates'
    ],
    pricing: {
      starting: '$99',
      unit: '/hour'
    },
    icon: Shield,
    category: 'hosting'
  },
  {
    id: 'enterprise-hosting',
    title: 'Enterprise Hosting',
    description: 'Dedicated infrastructure with custom configurations and SLA guarantees',
    features: [
      'Dedicated servers',
      'Custom configurations',
      'SLA guarantees',
      'Priority support',
      'Custom integrations',
      'Advanced monitoring',
      'Disaster recovery',
      'Compliance assistance'
    ],
    pricing: {
      starting: '$299',
      unit: '/month'
    },
    icon: Globe,
    category: 'hosting'
  },

  // Training Services
  {
    id: 'basic-training',
    title: 'Basic Training',
    description: 'Essential training for your team to get started with TidyGen',
    features: [
      '2-hour live session',
      'Core module overview',
      'Basic operations',
      'User management',
      'Reporting basics',
      'Q&A session',
      'Training materials',
      '30-day email support'
    ],
    pricing: {
      starting: '$199',
      unit: '/session'
    },
    icon: GraduationCap,
    category: 'training'
  },
  {
    id: 'advanced-training',
    title: 'Advanced Training',
    description: 'Comprehensive training covering advanced features and best practices',
    features: [
      '4-hour live session',
      'Advanced configurations',
      'Custom workflows',
      'API integration',
      'Web3 features',
      'Security best practices',
      'Performance optimization',
      '60-day email support'
    ],
    pricing: {
      starting: '$399',
      unit: '/session'
    },
    icon: Zap,
    popular: true,
    category: 'training'
  },
  {
    id: 'certification-program',
    title: 'Certification Program',
    description: 'Official certification program for TidyGen administrators and developers',
    features: [
      'Comprehensive curriculum',
      'Hands-on labs',
      'Certification exam',
      'Official certificate',
      'Digital badge',
      'Lifetime access',
      'Community membership',
      'Job placement assistance'
    ],
    pricing: {
      starting: '$999',
      unit: '/program'
    },
    icon: Award,
    category: 'training'
  },

  // Support Services
  {
    id: 'community-support',
    title: 'Community Support',
    description: 'Access to our vibrant community and basic support channels',
    features: [
      'Discord community access',
      'GitHub issue tracking',
      'Documentation access',
      'Community forums',
      'Basic troubleshooting',
      'Feature requests',
      'Bug reports',
      'Community contributions'
    ],
    pricing: {
      starting: 'Free',
      unit: ''
    },
    icon: Users,
    category: 'support'
  },
  {
    id: 'priority-support',
    title: 'Priority Support',
    description: 'Fast response times and dedicated support for your business needs',
    features: [
      '24-hour response time',
      'Email and chat support',
      'Remote assistance',
      'Priority bug fixes',
      'Feature prioritization',
      'Monthly check-ins',
      'Performance reviews',
      'Best practice guidance'
    ],
    pricing: {
      starting: '$149',
      unit: '/month'
    },
    icon: Headphones,
    popular: true,
    category: 'support'
  },
  {
    id: 'enterprise-support',
    title: 'Enterprise Support',
    description: 'Dedicated support team with SLA guarantees and custom solutions',
    features: [
      '2-hour response time',
      'Dedicated support engineer',
      'Phone and video support',
      'Custom integrations',
      'SLA guarantees',
      'Quarterly reviews',
      'Custom training',
      'White-label support'
    ],
    pricing: {
      starting: '$499',
      unit: '/month'
    },
    icon: MessageCircle,
    category: 'support'
  },

  // Development Services
  {
    id: 'custom-development',
    title: 'Custom Development',
    description: 'Tailored development services for your specific business requirements',
    features: [
      'Custom modules',
      'API integrations',
      'UI/UX customization',
      'Workflow automation',
      'Third-party integrations',
      'Performance optimization',
      'Security enhancements',
      'Code documentation'
    ],
    pricing: {
      starting: '$125',
      unit: '/hour'
    },
    icon: Code,
    category: 'development'
  },
  {
    id: 'migration-services',
    title: 'Migration Services',
    description: 'Seamless migration from your existing ERP system to TidyGen',
    features: [
      'Data analysis',
      'Migration planning',
      'Data transformation',
      'Testing and validation',
      'Go-live support',
      'User training',
      'Documentation',
      'Post-migration support'
    ],
    pricing: {
      starting: '$2,999',
      unit: '/project'
    },
    icon: Database,
    category: 'development'
  },
  {
    id: 'consulting',
    title: 'Business Consulting',
    description: 'Strategic consulting to optimize your business processes with TidyGen',
    features: [
      'Process analysis',
      'Workflow optimization',
      'Best practice recommendations',
      'ROI analysis',
      'Implementation planning',
      'Change management',
      'Training strategy',
      'Ongoing optimization'
    ],
    pricing: {
      starting: '$175',
      unit: '/hour'
    },
    icon: BookOpen,
    category: 'development'
  }
];

const serviceCategories = {
  hosting: { name: 'Hosting & Infrastructure', icon: Server },
  training: { name: 'Training & Education', icon: GraduationCap },
  support: { name: 'Support & Maintenance', icon: Headphones },
  development: { name: 'Development & Consulting', icon: Code },
};

export default function Services() {
  const [selectedCategory, setSelectedCategory] = useState<string>('hosting');

  const filteredServices = services.filter(service => 
    selectedCategory === 'all' || service.category === selectedCategory
  );

  const handleServiceSelect = (service: Service) => {
    console.log('Service selected:', service.id);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <Badge variant="outline" className="mb-4">
          <Star className="h-3 w-3 mr-1" />
          Professional Services
        </Badge>
        <h1 className="text-4xl font-bold mb-4">
          Get Expert Help with TidyGen
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Whether you need hosting, training, support, or custom development, 
          our team of experts is here to help you succeed with TidyGen.
        </p>
      </div>

      {/* Service Categories */}
      <div className="mb-12">
        <Tabs value={selectedCategory} onValueChange={setSelectedCategory}>
          <TabsList className="grid w-full grid-cols-4">
            {Object.entries(serviceCategories).map(([key, category]) => (
              <TabsTrigger key={key} value={key} className="flex items-center">
                <category.icon className="h-4 w-4 mr-2" />
                {category.name}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
      </div>

        {/* Services Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredServices.map((service) => {
            const Icon = service.icon;
            return (
              <Card 
                key={service.id} 
                className={`relative transition-all duration-200 hover:shadow-lg ${
                  service.popular ? 'ring-2 ring-primary shadow-lg' : ''
                }`}
              >
                {service.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-primary text-primary-foreground">
                      <Star className="h-3 w-3 mr-1" />
                      Popular
                    </Badge>
                  </div>
                )}

                <CardHeader>
                  <div className="flex items-center mb-4">
                    <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center mr-4">
                      <Icon className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <CardTitle className="text-xl">{service.title}</CardTitle>
                      <Badge variant="secondary" className="mt-1">
                        {serviceCategories[service.category].name}
                      </Badge>
                    </div>
                  </div>
                  <p className="text-muted-foreground">{service.description}</p>
                </CardHeader>

                <CardContent className="space-y-6">
                  {/* Features */}
                  <div className="space-y-2">
                    <h4 className="font-semibold">What's Included:</h4>
                    <ul className="space-y-1">
                      {service.features.map((feature, index) => (
                        <li key={index} className="flex items-center text-sm">
                          <CheckCircle className="h-4 w-4 text-green-600 mr-2 flex-shrink-0" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Pricing */}
                  <div className="border-t pt-4">
                    <div className="flex items-baseline justify-between mb-4">
                      <div>
                        <span className="text-2xl font-bold">
                          {service.pricing.starting}
                        </span>
                        <span className="text-muted-foreground ml-1">
                          {service.pricing.unit}
                        </span>
                      </div>
                      <Badge variant="outline">
                        <Clock className="h-3 w-3 mr-1" />
                        Flexible
                      </Badge>
                    </div>

                    <Button 
                      className="w-full" 
                      onClick={() => handleServiceSelect(service)}
                    >
                      Get Started
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Why Choose Our Services */}
        <Card>
          <CardHeader>
            <CardTitle>Why Choose Our Services?</CardTitle>
            <p className="text-muted-foreground">Trusted by businesses worldwide</p>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Award className="h-6 w-6 text-primary" />
                </div>
                <h3 className="font-semibold mb-2">Expert Team</h3>
                <p className="text-sm text-muted-foreground">
                  Our team consists of certified professionals with years of experience in ERP systems and Web3 technologies.
                </p>
              </div>

              <div className="text-center">
                <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Shield className="h-6 w-6 text-primary" />
                </div>
                <h3 className="font-semibold mb-2">Proven Track Record</h3>
                <p className="text-sm text-muted-foreground">
                  We've successfully helped hundreds of businesses implement and optimize their ERP systems.
                </p>
              </div>

              <div className="text-center">
                <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Zap className="h-6 w-6 text-primary" />
                </div>
                <h3 className="font-semibold mb-2">Fast Implementation</h3>
                <p className="text-sm text-muted-foreground">
                  Our streamlined processes ensure quick implementation without compromising quality.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
