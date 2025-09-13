# Security Policy

## Supported Versions

We provide security updates for the following versions of iNeat ERP Community Edition:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do NOT create a public issue

**Do not** create a public GitHub issue for security vulnerabilities. This could put other users at risk.

### 2. Report privately

Please report security vulnerabilities privately by:

- **Email**: security@ineat-erp.com
- **GitHub Security Advisories**: Use the "Report a vulnerability" button on the repository's Security tab

### 3. Include the following information

When reporting a vulnerability, please include:

- **Description**: Clear description of the vulnerability
- **Steps to reproduce**: Detailed steps to reproduce the issue
- **Impact**: Potential impact and severity
- **Environment**: Affected versions and configurations
- **Proof of concept**: If applicable, include a minimal proof of concept

### 4. Response timeline

We will:

- **Acknowledge** your report within 48 hours
- **Investigate** the issue within 7 days
- **Provide updates** on our progress
- **Release a fix** as soon as possible (typically within 30 days)

## Security Best Practices

### For Users

1. **Keep your installation updated**
   - Regularly update to the latest version
   - Monitor security advisories

2. **Secure your deployment**
   - Use HTTPS in production
   - Keep your server and dependencies updated
   - Use strong passwords and secrets
   - Enable firewall rules
   - Regular backups

3. **Access control**
   - Use strong, unique passwords
   - Enable two-factor authentication where possible
   - Regularly review user permissions
   - Remove unused accounts

4. **Network security**
   - Use VPN for remote access
   - Restrict database access
   - Use secure connections (SSL/TLS)

### For Developers

1. **Code security**
   - Follow secure coding practices
   - Validate all inputs
   - Use parameterized queries
   - Implement proper authentication and authorization

2. **Dependencies**
   - Keep dependencies updated
   - Use tools like `safety` to check for vulnerabilities
   - Review dependency changes

3. **Testing**
   - Include security tests in your test suite
   - Perform regular security audits
   - Use static analysis tools

## Security Features

iNeat ERP Community Edition includes several security features:

### Authentication & Authorization

- JWT-based authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Session management
- Account lockout protection

### Input Validation

- SQL injection protection
- XSS prevention
- CSRF protection
- Input sanitization
- File upload validation

### Network Security

- HTTPS support
- CORS configuration
- Rate limiting
- Security headers
- Request validation

### Data Protection

- Database encryption at rest
- Secure file storage
- Audit logging
- Data backup encryption

## Security Updates

Security updates are released as:

- **Patch releases** (1.0.x) for critical security fixes
- **Minor releases** (1.x.0) for security improvements
- **Security advisories** for important security information

## Responsible Disclosure

We follow responsible disclosure practices:

1. **Report privately** to security@ineat-erp.com
2. **Allow reasonable time** for us to fix the issue
3. **Coordinate disclosure** with our security team
4. **Credit researchers** who responsibly disclose vulnerabilities

## Security Tools

We use various security tools and practices:

- **Static Analysis**: Bandit, ESLint security rules
- **Dependency Scanning**: Safety, npm audit
- **Dynamic Analysis**: OWASP ZAP, Burp Suite
- **Code Review**: Manual security review process
- **Penetration Testing**: Regular security assessments

## Contact

For security-related questions or concerns:

- **Email**: security@ineat-erp.com
- **PGP Key**: Available upon request
- **Response Time**: Within 48 hours

## Acknowledgments

We thank the security researchers and community members who help keep iNeat ERP Community Edition secure by responsibly disclosing vulnerabilities.

---

**Note**: This security policy applies to iNeat ERP Community Edition. For commercial support and enterprise security features, please contact our commercial team.
