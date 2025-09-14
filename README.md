# TidyGen ERP Community Edition

<div align="center">

![TidyGen ERP](https://img.shields.io/badge/TidyGen%20ERP-Community%20Edition-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.12+-blue)
![Django](https://img.shields.io/badge/Django-4.2+-green)
![Self-Hosted](https://img.shields.io/badge/Self--Hosted-✓-orange)

**A comprehensive, single-tenant ERP system designed for small to medium businesses. Built with Django REST Framework and modern web technologies.**

[🚀 Quick Start](#quick-start) • [📖 Documentation](DEPLOYMENT.md) • [🤝 Contributing](#contributing) • [💬 Community](https://github.com/your-org/tidygen-erp-community/discussions)

</div>

---

## 🎯 Why TidyGen ERP Community Edition?

**TidyGen ERP Community Edition** is a powerful, self-hosted ERP solution that gives you complete control over your business data and operations. Perfect for businesses that want enterprise-grade functionality without the complexity of multi-tenant systems.

### ✨ Key Benefits

- **🔒 Self-Hosted**: Your data stays on your infrastructure
- **💰 Cost-Effective**: No monthly subscriptions or per-user fees
- **🛠️ Customizable**: Open-source code you can modify and extend
- **📈 Scalable**: Grows with your business from startup to enterprise
- **🔧 Modern Tech Stack**: Built with Django, React, and PostgreSQL

## 📊 Community vs Commercial Edition

| Feature | Community Edition | Commercial Edition |
|---------|------------------|-------------------|
| **🏠 Deployment** | Self-hosted only | Cloud-hosted + Self-hosted |
| **👥 Tenancy** | Single-tenant | Multi-tenant |
| **💰 Cost** | Free (MIT License) | Subscription-based |
| **🛠️ Customization** | Full source code access | Limited customization |
| **📞 Support** | Community support | Enterprise support |
| **🔄 Updates** | Manual updates | Automatic updates |
| **🏢 Multi-Company** | Single organization | Multiple organizations |
| **🤝 Dealer/Reseller Portals** | ❌ Not included | ✅ Included |
| **📈 Advanced Analytics** | Basic reporting | Advanced BI & analytics |
| **🔐 Enterprise Security** | Standard security | Advanced security features |
| **☁️ Cloud Integration** | Manual setup | Built-in cloud services |
| **📱 Mobile Apps** | Web-based | Native mobile apps |
| **🔌 Third-party Integrations** | Manual integration | Pre-built integrations |

> **💡 Need multi-tenant, dealer/reseller portals, or enterprise support?** Check out our [Commercial Edition](https://tidygen-erp.com/commercial) for advanced features and professional support.

## 🚀 Features

### Core ERP Modules
- **👥 Human Resources Management** - Employee records, payroll, leave management
- **📦 Inventory Management** - Stock tracking, suppliers, purchase orders
- **💼 Sales & CRM** - Customer management, sales tracking, invoicing
- **💰 Financial Management** - Accounting, invoicing, expense tracking
- **📅 Project Management** - Task scheduling, resource allocation
- **📊 Analytics & Reporting** - Business intelligence and insights
- **⛓️ Web3 Integration** - **REAL blockchain features with smart contracts, multi-chain support**

## 🚀 Quick Start

Get TidyGen ERP Community Edition running in minutes with Docker!

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/downloads)
- 4GB RAM minimum (8GB recommended)

### 🎯 One-Click Setup (Recommended)

   ```bash
# Clone and setup in one command
git clone https://github.com/your-org/tidygen-erp-community.git
cd tidygen-erp-community
chmod +x setup.sh
./setup.sh
```

### 📋 Manual Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/tidygen-erp-community.git
   cd tidygen-erp-community
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env if you need custom settings
   ```

3. **Start the application:**
   ```bash
   docker-compose up -d
   ```

4. **Access your ERP system:**
   - 🌐 **Web Application**: http://localhost:8000
   - ⚙️ **Admin Interface**: http://localhost:8000/admin
   - 📚 **API Documentation**: http://localhost:8000/api/docs

5. **Default login credentials:**
   - **Username**: `admin`
   - **Password**: `admin123`
   - ⚠️ **Important**: Change the default password after first login!

### 🔧 What Happens During Setup

The setup process automatically:
- ✅ Creates and configures PostgreSQL database
- ✅ Sets up Redis for caching
- ✅ Runs database migrations
- ✅ Creates default organization
- ✅ Sets up admin user
- ✅ Collects static files
- ✅ Starts the Django development server

### 🎉 You're Ready!

Your TidyGen ERP Community Edition is now running! Start by:
1. Setting up your organization details
2. Adding your first employees
3. Configuring your inventory
4. Setting up your chart of accounts

## 🏗️ Architecture

TidyGen ERP Community Edition is built with a modern, scalable architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React/Next)  │◄──►│   (Django API)  │◄──►│   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Cache         │
                       │   (Redis)       │
                       └─────────────────┘
```

### Technology Stack

- **🎨 Frontend**: React 18, Next.js 14, TypeScript, Tailwind CSS
- **⚙️ Backend**: Django 4.2+, Django REST Framework, Python 3.12+
- **🗄️ Database**: PostgreSQL 15+ (primary), Redis 7+ (cache)
- **🐳 Deployment**: Docker, Docker Compose, Nginx
- **🔐 Authentication**: JWT tokens, Role-based access control
- **📊 Monitoring**: Built-in health checks, logging, and metrics

## 🔧 Troubleshooting

### Common Issues

#### Docker Issues
```bash
# If containers won't start
docker-compose down
docker-compose up -d

# If you get permission errors
sudo chown -R $USER:$USER .

# If database connection fails
docker-compose logs db
```

#### Port Conflicts
```bash
# If port 8000 is already in use
# Edit docker-compose.yml and change the port mapping:
# ports:
#   - "8001:8000"  # Use port 8001 instead
```

#### Database Issues
```bash
# Reset the database
docker-compose down -v
docker-compose up -d

# View database logs
docker-compose logs db
```

#### Environment Issues
```bash
# Check if .env file exists
ls -la .env

# Recreate .env file
cp .env.example .env
```

### Getting Help

- 📖 **Documentation**: Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides
- 🐛 **Bug Reports**: [Create an issue](https://github.com/your-org/tidygen-erp-community/issues)
- 💬 **Community**: [Join discussions](https://github.com/your-org/tidygen-erp-community/discussions)

## 🛠️ Development

We welcome contributions from the community! Here's how to get started with development:

### Backend Development

```bash
cd apps/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py setup_single_organization --create-admin
python manage.py runserver
```

### Frontend Development

```bash
cd apps/frontend
npm install
npm run dev
```

### Development with Docker

```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f backend

# Run tests
docker-compose exec backend python manage.py test
```

## ☁️ Cloud Deployment

Deploy TidyGen ERP Community Edition to popular cloud platforms with one-click deployment!

### 🚀 One-Click Deploy Options

#### Vercel (Frontend)
```bash
# Deploy frontend to Vercel
./scripts/deploy/vercel-deploy.sh
```

#### Render (Full Stack)
```bash
# Get deployment instructions for Render
./scripts/deploy/render-deploy.sh
```

#### DigitalOcean App Platform (Full Stack)
```bash
# Get deployment instructions for DigitalOcean
./scripts/deploy/digitalocean-deploy.sh
```

### 📋 Quick Cloud Setup

1. **Choose your platform:**
   - **Vercel**: Best for frontend-only deployment
   - **Render**: Great for full-stack with free tier
   - **DigitalOcean**: Professional hosting with managed databases

2. **Run the deployment script:**
   ```bash
   # For Vercel
   ./scripts/deploy/vercel-deploy.sh
   
   # For Render
   ./scripts/deploy/render-deploy.sh
   
   # For DigitalOcean
   ./scripts/deploy/digitalocean-deploy.sh
   ```

3. **Follow the platform-specific instructions**

### 🔧 Production Deployment

For advanced production setups, see [DEPLOYMENT.md](DEPLOYMENT.md).

#### Docker Production
```bash
# Set up production environment
cp .env.example .env.prod
# Edit .env.prod with your production settings

# Deploy with production Docker Compose
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

## ⚙️ Configuration

The system uses environment variables for configuration. See `apps/backend/env.example` for all available options.

### Key Configuration Options

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Django secret key
- `ALLOWED_HOSTS`: Allowed hostnames
- `CORS_ALLOWED_ORIGINS`: CORS configuration
- `WEB3_ENABLED`: Enable/disable Web3 features

## 📚 API Documentation

The API documentation is available at `/api/docs/` when running the application. It provides:

- Interactive API explorer
- Request/response examples
- Authentication information
- Schema definitions

## 🧩 Modules

### Core ERP Modules

- **👤 Accounts**: User authentication and management
- **👥 HR**: Human resources management
- **📦 Inventory**: Stock and supplier management
- **💼 Sales**: Customer and sales management
- **💰 Finance**: Accounting and financial management
- **🛒 Purchasing**: Purchase order management
- **💳 Payroll**: Employee payroll processing
- **📅 Scheduling**: Task and resource scheduling
- **📊 Analytics**: Business intelligence and reporting
- **⛓️ Web3**: Blockchain integration features

## 🔒 Security

- **🔐 JWT-based authentication** with refresh tokens
- **👥 Role-based access control** (RBAC)
- **🌐 CORS protection** for cross-origin requests
- **⏱️ Rate limiting** to prevent abuse
- **✅ Input validation** and sanitization
- **🛡️ SQL injection protection**
- **🔒 HTTPS support** for production deployments

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Ways to Contribute

- 🐛 **Report bugs** and issues
- 💡 **Suggest new features**
- 📝 **Improve documentation**
- 🔧 **Submit code improvements**
- 🧪 **Add tests**
- 🌍 **Translate to other languages**

### Getting Started

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Development Guidelines

- Follow the existing code style
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass
- Follow semantic commit messages

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Community Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/your-org/tidygen-erp-community/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-org/tidygen-erp-community/discussions)
- 📖 **Documentation**: [Read the docs](https://docs.tidygen-erp.com)
- 🌐 **Community Forum**: [Join the discussion](https://community.tidygen-erp.com)

### Commercial Support

For enterprise features, multi-tenant support, dealer/reseller portals, and professional support, check out our [Commercial Edition](https://tidygen-erp.com/commercial).

## 🗺️ Roadmap

### Upcoming Features

- [ ] 📱 **Mobile Application** - Native iOS and Android apps
- [ ] 📊 **Advanced Analytics** - Enhanced reporting and BI features
- [ ] 🔌 **Third-party Integrations** - Popular business tools integration
- [ ] 🌍 **Multi-language Support** - Internationalization
- [ ] ⛓️ **Advanced Web3 Features** - Enhanced blockchain integration
- [ ] 🤖 **AI-powered Insights** - Machine learning for business intelligence
- [ ] 📈 **Advanced Workflow Automation** - Custom business process automation

### Community Requests

Have a feature request? [Submit it here](https://github.com/your-org/tidygen-erp-community/issues/new?template=feature_request.md)!

---

<div align="center">

**Made with ❤️ by the TidyGen ERP Community**

[⭐ Star us on GitHub](https://github.com/your-org/tidygen-erp-community) • [🐦 Follow us on Twitter](https://twitter.com/tidygen_erp) • [💼 Visit our website](https://tidygen-erp.com)

</div>