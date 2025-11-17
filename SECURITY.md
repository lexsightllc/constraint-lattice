# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take the security of Constraint Lattice seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: opensource@example.com

### What to Include

Please include the following information in your report:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Varies based on severity, typically 30-90 days

## Security Best Practices

### Deployment Security

1. **Environment Variables**: Never commit sensitive credentials or API keys
2. **Docker Security**:
   - Run containers as non-root user (implemented in Dockerfile)
   - Use multi-stage builds to minimize attack surface
   - Regularly update base images
3. **Network Security**:
   - Configure CORS appropriately for production
   - Use HTTPS/TLS in production
   - Implement rate limiting on API endpoints

### Dependency Management

1. **Regular Updates**: Keep dependencies up to date using `make update-deps`
2. **Security Scanning**: Run `make security-scan` before deployment
3. **SBOM Generation**: Generate Software Bill of Materials with `make sbom`

### API Security

1. **Input Validation**: All API inputs are validated using Pydantic models
2. **Rate Limiting**: Implement rate limiting in production (not included in dev environment)
3. **Authentication**: Add authentication middleware for production deployments
4. **Audit Logging**: All constraint applications are logged with full audit trails

### Data Security

1. **PII Handling**: Be cautious when processing Personally Identifiable Information
2. **Audit Trails**: Review JSONL audit logs regularly for anomalous activity
3. **Data Retention**: Implement appropriate data retention policies

## Known Security Considerations

### Current Limitations

1. **No Built-in Authentication**: The API does not include authentication by default. Implement OAuth2, JWT, or similar for production.
2. **CORS Configuration**: Default CORS allows all origins. Configure restrictively in production.
3. **Rate Limiting**: Not implemented by default. Add rate limiting middleware for production.

### Recommended Production Enhancements

```python
# Example: Add authentication middleware
from fastapi import Security, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/constraints/apply")
async def apply_constraints_endpoint(
    request: ConstraintRequest,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    # Verify token
    verify_token(credentials.credentials)
    # ... rest of endpoint logic
```

```python
# Example: Add rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/constraints/apply")
@limiter.limit("10/minute")
async def apply_constraints_endpoint(request: ConstraintRequest):
    # ... endpoint logic
```

## Security Updates

Security updates are released as patch versions (e.g., 0.1.1, 0.1.2) and announced via:
- GitHub Security Advisories
- Release notes
- Project documentation

## Vulnerability Disclosure Policy

We follow responsible disclosure practices:

1. **Private Disclosure**: Report vulnerabilities privately first
2. **Collaborative Fix**: Work with us to verify and fix the issue
3. **Public Disclosure**: After a fix is released, we'll publicly acknowledge the vulnerability
4. **Credit**: Security researchers who responsibly disclose vulnerabilities will be credited

## Security Tools

The project includes several security tools:

```bash
# Run security scan
make security-scan

# Check for known vulnerabilities
safety check

# Static security analysis
bandit -r src/

# Generate SBOM
make sbom
```

## Compliance

Constraint Lattice is designed to support:
- **GDPR**: Audit trails for data processing transparency
- **SOC 2**: Comprehensive logging and monitoring
- **ISO 27001**: Security controls and documentation

## Contact

For security concerns, contact: opensource@example.com

For general questions, use GitHub Issues or Discussions.
