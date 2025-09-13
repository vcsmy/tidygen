import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Mail, 
  Phone, 
  MapPin, 
  ExternalLink,
  Building2,
  ArrowRight,
  Twitter,
  Linkedin,
  Youtube
} from "lucide-react";

export function FooterSection() {
  const footerLinks = {
    product: [
      { name: "Features", href: "#features" },
      { name: "Deploy", href: "#deploy" },
      { name: "GitHub", href: "https://github.com/ineat/ineat-erp-community" },
      { name: "API Documentation", href: "https://docs.ineat.io/api" },
      { name: "Self-Hosting Guide", href: "https://docs.ineat.io/community-edition/self-hosting" }
    ],
    community: [
      { name: "Discord", href: "https://discord.gg/ineat-community" },
      { name: "GitHub Discussions", href: "https://github.com/ineat/ineat-erp-community/discussions" },
      { name: "Contributing", href: "https://github.com/ineat/ineat-erp-community/blob/main/CONTRIBUTING.md" },
      { name: "Bug Reports", href: "https://github.com/ineat/ineat-erp-community/issues" },
      { name: "Feature Requests", href: "https://github.com/ineat/ineat-erp-community/issues" }
    ],
    resources: [
      { name: "Documentation", href: "https://docs.ineat.io/community-edition" },
      { name: "Installation Guide", href: "https://docs.ineat.io/community-edition/installation" },
      { name: "Configuration", href: "https://docs.ineat.io/community-edition/configuration" },
      { name: "Troubleshooting", href: "https://docs.ineat.io/community-edition/troubleshooting" },
      { name: "FAQ", href: "https://docs.ineat.io/community-edition/faq" }
    ],
    legal: [
      { name: "License", href: "https://github.com/ineat/ineat-erp-community/blob/main/LICENSE" },
      { name: "Privacy Policy", href: "#" },
      { name: "Terms of Service", href: "#" },
      { name: "Security", href: "https://github.com/ineat/ineat-erp-community/security" },
      { name: "Code of Conduct", href: "https://github.com/ineat/ineat-erp-community/blob/main/CODE_OF_CONDUCT.md" }
    ]
  };

  const socialLinks = [
    { name: "Twitter", icon: <Twitter className="h-5 w-5" />, href: "#" },
    { name: "LinkedIn", icon: <Linkedin className="h-5 w-5" />, href: "#" },
    { name: "YouTube", icon: <Youtube className="h-5 w-5" />, href: "#" }
  ];

  return (
    <footer className="bg-muted/50 border-t">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Newsletter Section */}
        <div className="py-12 border-b">
          <div className="max-w-2xl mx-auto text-center space-y-6">
            <div className="space-y-2">
              <h3 className="text-2xl font-bold">Stay Updated</h3>
              <p className="text-muted-foreground">
                Get the latest updates, features, and industry insights delivered to your inbox.
              </p>
            </div>
            <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
              <Input 
                type="email" 
                placeholder="Enter your email" 
                className="flex-1"
              />
              <Button>
                Subscribe
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              No spam, unsubscribe at any time.
            </p>
          </div>
        </div>

        {/* Main Footer Content */}
        <div className="py-12">
          <div className="grid grid-cols-2 md:grid-cols-6 gap-8">
            {/* Company Info */}
            <div className="col-span-2 space-y-4">
              <div className="flex items-center space-x-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
                  <Building2 className="h-5 w-5 text-primary-foreground" />
                </div>
                <span className="text-xl font-bold">iNEAT-ERP</span>
              </div>
              <p className="text-sm text-muted-foreground max-w-xs">
                Free, open-source, self-hosted ERP system perfect for developers, small businesses, 
                and grant foundations. Full control over your data with Web3 alignment.
              </p>
              <div className="flex space-x-4">
                {socialLinks.map((social) => (
                  <a
                    key={social.name}
                    href={social.href}
                    className="text-muted-foreground hover:text-foreground transition-colors"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {social.icon}
                    <span className="sr-only">{social.name}</span>
                  </a>
                ))}
              </div>
            </div>

            {/* Product Links */}
            <div className="space-y-4">
              <h4 className="font-semibold">Product</h4>
              <ul className="space-y-2">
                {footerLinks.product.map((link) => (
                  <li key={link.name}>
                    <a
                      href={link.href}
                      className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {link.name}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Community Links */}
            <div className="space-y-4">
              <h4 className="font-semibold">Community</h4>
              <ul className="space-y-2">
                {footerLinks.community.map((link) => (
                  <li key={link.name}>
                    <a
                      href={link.href}
                      className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                      target={link.href.startsWith('http') ? '_blank' : undefined}
                      rel={link.href.startsWith('http') ? 'noopener noreferrer' : undefined}
                    >
                      {link.name}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Resources Links */}
            <div className="space-y-4">
              <h4 className="font-semibold">Resources</h4>
              <ul className="space-y-2">
                {footerLinks.resources.map((link) => (
                  <li key={link.name}>
                    <a
                      href={link.href}
                      className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {link.name}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Legal Links */}
            <div className="space-y-4">
              <h4 className="font-semibold">Legal</h4>
              <ul className="space-y-2">
                {footerLinks.legal.map((link) => (
                  <li key={link.name}>
                    <a
                      href={link.href}
                      className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {link.name}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="py-8 border-t">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="flex items-center space-x-3">
              <Mail className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">Email</p>
                <p className="text-sm text-muted-foreground">support@ineat-erp.com</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Phone className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">Phone</p>
                <p className="text-sm text-muted-foreground">+1 (555) 123-4567</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <MapPin className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">Address</p>
                <p className="text-sm text-muted-foreground">San Francisco, CA</p>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Footer */}
        <div className="py-6 border-t">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="text-sm text-muted-foreground">
              © 2024 iNeat Community Edition. Open source under MIT License.
            </div>
            <div className="flex items-center space-x-4 text-sm text-muted-foreground">
              <span>Free & open-source ERP solution</span>
              <a
                href="https://ineat.io"
                className="flex items-center space-x-1 hover:text-foreground transition-colors"
                target="_blank"
                rel="noopener noreferrer"
              >
                <ExternalLink className="h-4 w-4" />
                <span>Need multi-tenant SaaS? Visit the Commercial Edition →</span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
