# Security Documentation

## Overview

EDULEARN implements comprehensive security measures to protect user data, ensure secure authentication, and maintain platform integrity.

## Table of Contents

1. [Authentication Security](#authentication-security)
2. [Data Security](#data-security)
3. [Code Execution Security](#code-execution-security)
4. [API Security](#api-security)
5. [Infrastructure Security](#infrastructure-security)
6. [Security Best Practices](#security-best-practices)
7. [Security Incident Response](#security-incident-response)

---

## Authentication Security

### Password Security

**Implementation:**
- **Hashing Algorithm**: bcrypt with cost factor 12
- **Salt**: Automatic salt generation per password
- **Storage**: Passwords are never stored in plain text
- **Validation**: Password strength requirements enforced

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

**Code Example:**
```python
# File: backend/app/core/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### JWT Token Security

**Token Configuration:**
- **Algorithm**: HS256 (HMAC-SHA256)
- **Expiration**: 30 minutes (configurable)
- **Storage**: HTTP-only cookies (preferred) or localStorage
- **Validation**: Token signature and expiration checked on every request

**Token Structure:**
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "student|teacher|admin",
  "exp": 1234567890,
  "iat": 1234567890
}
```

**Security Measures:**
- Tokens are signed with a secret key
- Expiration enforced server-side
- Token validation on every protected endpoint
- Secure flag set for HTTPS-only transmission

### OAuth 2.0 Security

**Google OAuth Implementation:**
- **Flow**: Authorization Code Flow
- **State Parameter**: CSRF protection
- **Token Exchange**: Server-side only
- **Scope Limitation**: Minimal required scopes

**Security Features:**
- State parameter validation
- Secure token exchange
- User profile verification
- Automatic account linking

### Face Recognition Security

**Biometric Authentication:**
- **Algorithm**: 128-dimensional face descriptors
- **Matching**: Euclidean distance calculation
- **Threshold**: 0.6 (configurable)
- **Storage**: Encrypted face descriptors

**Security Measures:**
- Face data encrypted at rest
- Server-side matching only
- No raw image storage
- Privacy-compliant implementation

---

## Data Security

### Input Validation

**Pydantic Schema Validation:**
- All API inputs validated using Pydantic schemas
- Type checking and format validation
- Custom validators for business logic
- Automatic error messages

**Example:**
```python
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, regex="^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*])")
    name: str = Field(min_length=1, max_length=100)
```

### SQL Injection Prevention

**MongoDB Security:**
- Parameterized queries only
- No string concatenation in queries
- ObjectId validation
- Query sanitization

**Example:**
```python
# Safe query
user = await collection.find_one({"_id": ObjectId(user_id)})

# Unsafe (never do this)
# user = await collection.find_one({"_id": user_id})  # Without validation
```

### XSS Protection

**Frontend Protection:**
- React's automatic escaping
- Input sanitization
- Content Security Policy (CSP)
- No `dangerouslySetInnerHTML` usage

**Backend Protection:**
- Output encoding
- Content-Type validation
- Response sanitization

### CORS Configuration

**Cross-Origin Resource Sharing:**
```python
# File: backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**Best Practices:**
- Whitelist specific origins
- No wildcard origins in production
- Credentials only when necessary
- Minimal allowed methods

---

## Code Execution Security

### Sandboxed Environment

**Judge0 Integration:**
- Isolated container execution
- Network isolation
- File system restrictions
- Resource limits

**Resource Limits:**
- **CPU Time**: 5 seconds per execution
- **Memory**: 256 MB per execution
- **Output Size**: 1 MB maximum
- **Network**: No external access

**Security Features:**
- Code runs in isolated containers
- No access to host system
- Automatic cleanup after execution
- Timeout enforcement

### Code Validation

**Pre-Execution Checks:**
- Syntax validation
- Language verification
- Size limits
- Dangerous pattern detection

**Blocked Patterns:**
- File system access attempts
- Network requests
- System command execution
- Import restrictions

---

## API Security

### Rate Limiting

**Implementation:**
- SlowAPI for rate limiting
- Per-IP address tracking
- Configurable limits
- Graceful error handling

**Rate Limits:**
- **Authentication Endpoints**: 5 requests/minute
- **API Endpoints**: 100 requests/minute
- **Code Execution**: 20 requests/minute
- **Bulk Operations**: 10 requests/hour

**Example:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/api/endpoint")
@limiter.limit("100/minute")
async def endpoint(request: Request):
    # Endpoint logic
    pass
```

### API Authentication

**Protected Endpoints:**
- JWT token required
- Token validation on every request
- Role-based access control
- Permission checking

**Authentication Flow:**
1. Client sends request with JWT token
2. Backend validates token signature
3. Backend checks token expiration
4. Backend verifies user role
5. Request proceeds if authorized

### Error Handling

**Security-Conscious Error Messages:**
- No sensitive information in errors
- Generic error messages for authentication failures
- Detailed errors only in development
- Logging of security events

---

## Infrastructure Security

### Database Security

**MongoDB Security:**
- Authentication enabled
- Role-based access control
- Encrypted connections (TLS)
- Regular backups
- Access logging

**Best Practices:**
- Strong database passwords
- Limited user permissions
- Network isolation
- Regular security updates

### Server Security

**Production Checklist:**
- [ ] HTTPS enabled
- [ ] SSL/TLS certificates valid
- [ ] Firewall configured
- [ ] Security headers set
- [ ] Regular security updates
- [ ] Intrusion detection
- [ ] Log monitoring

### Environment Variables

**Sensitive Data:**
- Never commit `.env` files
- Use environment variables for secrets
- Rotate secrets regularly
- Use secret management services

**Required Secrets:**
```env
SECRET_KEY=your-secret-key-here
MONGO_URI=mongodb://...
GEMINI_API_KEY=your-api-key
JUDGE0_API_KEY=your-api-key
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

---

## Security Best Practices

### For Developers

1. **Never commit secrets** to version control
2. **Validate all inputs** on both frontend and backend
3. **Use parameterized queries** for database operations
4. **Keep dependencies updated** for security patches
5. **Follow principle of least privilege** for user roles
6. **Log security events** for monitoring
7. **Use HTTPS** in production
8. **Implement rate limiting** on sensitive endpoints
9. **Regular security audits** of code
10. **Stay informed** about security vulnerabilities

### For Administrators

1. **Regular security updates** of system and dependencies
2. **Monitor logs** for suspicious activity
3. **Backup data** regularly
4. **Review access logs** periodically
5. **Implement intrusion detection**
6. **Use strong passwords** for all accounts
7. **Enable two-factor authentication** where possible
8. **Regular security assessments**
9. **Incident response plan** in place
10. **User access reviews** regularly

### For Users

1. **Use strong passwords**
2. **Don't share credentials**
3. **Log out when finished**
4. **Report suspicious activity**
5. **Keep software updated**
6. **Be cautious with links**
7. **Use secure networks** when possible

---

## Security Incident Response

### Incident Types

1. **Unauthorized Access**
2. **Data Breach**
3. **DDoS Attack**
4. **Malicious Code Execution**
5. **Token Compromise**

### Response Procedure

1. **Identify**: Determine the nature and scope of the incident
2. **Contain**: Isolate affected systems
3. **Eradicate**: Remove threat and vulnerabilities
4. **Recover**: Restore systems to normal operation
5. **Document**: Record incident details and response
6. **Notify**: Inform affected users if necessary
7. **Review**: Post-incident analysis and improvements

### Contact Information

**Security Team:**
- Email: security@edulearn.com
- Emergency: [Emergency contact]

**Reporting Security Issues:**
- Use responsible disclosure
- Report via email
- Include detailed information
- Allow time for response

---

## Security Checklist

### Development
- [ ] Input validation implemented
- [ ] Authentication required on protected endpoints
- [ ] Passwords hashed with bcrypt
- [ ] JWT tokens properly validated
- [ ] Rate limiting configured
- [ ] Error messages don't leak information
- [ ] Dependencies up to date
- [ ] Security headers set

### Deployment
- [ ] HTTPS enabled
- [ ] SSL certificates valid
- [ ] Environment variables secured
- [ ] Database authentication enabled
- [ ] Firewall configured
- [ ] Logging enabled
- [ ] Monitoring set up
- [ ] Backup strategy in place

### Ongoing
- [ ] Regular security updates
- [ ] Log monitoring
- [ ] Access reviews
- [ ] Security audits
- [ ] Penetration testing
- [ ] Incident response plan
- [ ] User education

---

## Security Resources

### Documentation
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [MongoDB Security](https://docs.mongodb.com/manual/security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

### Tools
- Dependency scanners
- Security linters
- Penetration testing tools
- Log analysis tools

---

**Last Updated:** November 2024  
**Version:** 1.0.0

For security concerns or to report vulnerabilities, please contact the security team.

