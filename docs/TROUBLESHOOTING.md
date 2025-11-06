# Troubleshooting Guide

## Overview

This guide provides solutions to common issues encountered when using or developing the EDULEARN platform.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Database Issues](#database-issues)
3. [Authentication Issues](#authentication-issues)
4. [API Issues](#api-issues)
5. [Frontend Issues](#frontend-issues)
6. [Code Execution Issues](#code-execution-issues)
7. [Performance Issues](#performance-issues)
8. [Deployment Issues](#deployment-issues)

---

## Installation Issues

### Python Not Found

**Problem:** `python: command not found` or `python is not recognized`

**Solutions:**
1. **Windows:**
   - Download Python from [python.org](https://www.python.org/downloads/)
   - Check "Add Python to PATH" during installation
   - Restart terminal after installation

2. **Linux/Mac:**
   ```bash
   # Check if Python is installed
   python3 --version
   
   # If not installed
   # Ubuntu/Debian
   sudo apt-get install python3 python3-pip
   
   # macOS
   brew install python3
   ```

3. **Use python3 explicitly:**
   ```bash
   python3 -m venv venv
   python3 main.py
   ```

### Node.js Not Found

**Problem:** `node: command not found` or `npm: command not found`

**Solutions:**
1. **Download Node.js:**
   - Visit [nodejs.org](https://nodejs.org/)
   - Install LTS version (18+)
   - Restart terminal

2. **Verify Installation:**
   ```bash
   node --version
   npm --version
   ```

3. **Use nvm (Node Version Manager):**
   ```bash
   # Install nvm
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   
   # Install Node.js
   nvm install 18
   nvm use 18
   ```

### Dependencies Installation Fails

**Problem:** `pip install` or `npm install` fails

**Solutions:**
1. **Check Internet Connection:**
   ```bash
   ping google.com
   ```

2. **Use Different Mirror (Python):**
   ```bash
   pip install -r requirements.txt -i https://pypi.org/simple
   ```

3. **Clear Cache:**
   ```bash
   # Python
   pip cache purge
   
   # Node.js
   npm cache clean --force
   ```

4. **Update Package Managers:**
   ```bash
   # Python
   pip install --upgrade pip
   
   # Node.js
   npm install -g npm@latest
   ```

5. **Use Virtual Environment:**
   ```bash
   # Python
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

---

## Database Issues

### MongoDB Connection Failed

**Problem:** `Connection refused` or `Cannot connect to MongoDB`

**Solutions:**
1. **Check MongoDB Status:**
   ```bash
   # Windows
   net start MongoDB
   
   # Linux
   sudo systemctl status mongod
   
   # macOS
   brew services list | grep mongodb
   ```

2. **Start MongoDB:**
   ```bash
   # Windows
   net start MongoDB
   
   # Linux
   sudo systemctl start mongod
   
   # macOS
   brew services start mongodb-community
   ```

3. **Check Connection String:**
   ```env
   # .env file
   MONGO_URI=mongodb://localhost:27017
   DB_NAME=edulearn
   ```

4. **Check Port Availability:**
   ```bash
   # Windows
   netstat -an | findstr :27017
   
   # Linux/Mac
   netstat -an | grep :27017
   ```

5. **Test Connection:**
   ```bash
   mongo
   # or
   mongosh
   ```

### Database Not Found

**Problem:** Database doesn't exist or collections are missing

**Solutions:**
1. **Database Auto-Creation:**
   - MongoDB creates databases automatically on first use
   - Collections are created when first document is inserted

2. **Initialize Database:**
   ```bash
   cd backend
   python init_database.py
   ```

3. **Check Database:**
   ```bash
   mongo
   use edulearn
   show collections
   ```

### Index Creation Fails

**Problem:** Index creation errors or slow queries

**Solutions:**
1. **Check Existing Indexes:**
   ```javascript
   db.collection.getIndexes()
   ```

2. **Create Missing Indexes:**
   ```bash
   python init_database.py
   ```

3. **Drop and Recreate:**
   ```javascript
   db.collection.dropIndex("index_name")
   db.collection.createIndex({field: 1})
   ```

---

## Authentication Issues

### Login Fails

**Problem:** Cannot login with correct credentials

**Solutions:**
1. **Check Credentials:**
   - Verify email and password are correct
   - Check for typos
   - Ensure account is active

2. **Check Password Hash:**
   ```python
   # Verify password hashing
   from passlib.context import CryptContext
   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
   pwd_context.verify("password", hashed_password)
   ```

3. **Check User Status:**
   ```python
   # Verify user is active
   user = await db.users.find_one({"email": email})
   if not user.get("is_active", True):
       # User is deactivated
   ```

4. **Check JWT Secret:**
   ```env
   # Ensure SECRET_KEY is set
   SECRET_KEY=your-secret-key-here
   ```

### Token Expired

**Problem:** `Token has expired` error

**Solutions:**
1. **Re-login:**
   - Tokens expire after 30 minutes
   - Simply log in again

2. **Extend Token Expiry:**
   ```python
   # backend/app/core/security.py
   self.access_token_expire_minutes = 60  # Increase expiry
   ```

3. **Implement Refresh Tokens:**
   - Add refresh token mechanism
   - Store refresh tokens securely

### OAuth Login Fails

**Problem:** Google OAuth not working

**Solutions:**
1. **Check OAuth Credentials:**
   ```env
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

2. **Verify Redirect URI:**
   - Must match Google Console configuration
   - Check allowed redirect URIs

3. **Check OAuth Scope:**
   - Ensure required scopes are requested
   - Verify permissions granted

4. **Check Network:**
   - Ensure Google OAuth endpoints are accessible
   - Check firewall settings

---

## API Issues

### 404 Not Found

**Problem:** API endpoint returns 404

**Solutions:**
1. **Check Endpoint URL:**
   - Verify correct base URL
   - Check API prefix (`/api` or `/auth`)

2. **Check Route Registration:**
   ```python
   # Ensure routes are registered
   app.include_router(auth_router, prefix="/auth")
   app.include_router(api_router, prefix="/api")
   ```

3. **Check HTTP Method:**
   - Verify correct HTTP method (GET, POST, etc.)
   - Check endpoint definition

### 401 Unauthorized

**Problem:** API returns 401 Unauthorized

**Solutions:**
1. **Check Token:**
   - Verify token is included in request
   - Check token format: `Bearer <token>`

2. **Verify Token Validity:**
   ```python
   # Check token expiration
   payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
   ```

3. **Check Authorization Header:**
   ```javascript
   // Frontend
   headers: {
     'Authorization': `Bearer ${token}`
   }
   ```

### 500 Internal Server Error

**Problem:** Server error on API request

**Solutions:**
1. **Check Server Logs:**
   ```bash
   # Backend logs
   tail -f backend/logs/app.log
   ```

2. **Check Database Connection:**
   - Verify MongoDB is running
   - Check connection string

3. **Check Environment Variables:**
   ```bash
   # Verify all required variables are set
   cat backend/.env
   ```

4. **Check Dependencies:**
   ```bash
   # Ensure all packages are installed
   pip list
   ```

---

## Frontend Issues

### Build Fails

**Problem:** `npm run build` fails

**Solutions:**
1. **Check Node Version:**
   ```bash
   node --version  # Should be 18+
   ```

2. **Clear Cache:**
   ```bash
   npm cache clean --force
   rm -rf node_modules
   npm install
   ```

3. **Check TypeScript Errors:**
   ```bash
   npm run type-check
   ```

4. **Check ESLint:**
   ```bash
   npm run lint
   ```

### Development Server Won't Start

**Problem:** `npm run dev` fails

**Solutions:**
1. **Check Port Availability:**
   ```bash
   # Check if port 5173 is in use
   netstat -an | grep :5173
   ```

2. **Change Port:**
   ```javascript
   // vite.config.js
   export default {
     server: {
       port: 3000
     }
   }
   ```

3. **Clear Vite Cache:**
   ```bash
   rm -rf node_modules/.vite
   ```

### API Calls Fail

**Problem:** Frontend cannot connect to backend

**Solutions:**
1. **Check Backend URL:**
   ```javascript
   // frontend/src/utils/api.ts
   const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001'
   ```

2. **Check CORS:**
   ```python
   # backend/app/main.py
   allow_origins=["http://localhost:5173"]
   ```

3. **Check Network:**
   - Verify backend is running
   - Check firewall settings
   - Test with curl:
     ```bash
     curl http://localhost:5001/api/health
     ```

---

## Code Execution Issues

### Judge0 API Fails

**Problem:** Code execution returns errors

**Solutions:**
1. **Check API Key:**
   ```env
   JUDGE0_API_KEY=your-api-key
   JUDGE0_API_HOST=judge0-ce.p.rapidapi.com
   ```

2. **Check API Limits:**
   - Free tier: 50 requests/day
   - Check RapidAPI dashboard

3. **Check Network:**
   - Verify Judge0 endpoints are accessible
   - Check firewall settings

4. **Check Code Format:**
   - Ensure code is properly formatted
   - Check language identifier

### Code Execution Timeout

**Problem:** Code execution times out

**Solutions:**
1. **Increase Timeout:**
   ```python
   timeout = 10  # seconds
   ```

2. **Check Code Complexity:**
   - Optimize code
   - Check for infinite loops

3. **Check Resource Limits:**
   - Verify memory limits
   - Check CPU time limits

---

## Performance Issues

### Slow API Responses

**Problem:** API endpoints are slow

**Solutions:**
1. **Check Database Indexes:**
   ```javascript
   db.collection.getIndexes()
   ```

2. **Optimize Queries:**
   - Use projections to limit fields
   - Add pagination
   - Use aggregation pipelines

3. **Check Connection Pooling:**
   ```python
   # Ensure connection pooling is configured
   ```

4. **Add Caching:**
   - Implement Redis caching
   - Cache frequently accessed data

### High Memory Usage

**Problem:** Application uses too much memory

**Solutions:**
1. **Check Database Queries:**
   - Limit result sets
   - Use pagination
   - Avoid loading all data

2. **Check Frontend:**
   - Implement code splitting
   - Lazy load components
   - Optimize images

3. **Monitor Resources:**
   ```bash
   # Check memory usage
   htop
   # or
   top
   ```

---

## Deployment Issues

### Build Fails in Production

**Problem:** Production build fails

**Solutions:**
1. **Check Environment Variables:**
   - Ensure all required variables are set
   - Verify production values

2. **Check Node Version:**
   - Ensure production Node version matches development

3. **Check Build Scripts:**
   ```json
   {
     "scripts": {
       "build": "vite build"
     }
   }
   ```

### SSL Certificate Issues

**Problem:** SSL certificate errors

**Solutions:**
1. **Check Certificate Validity:**
   ```bash
   openssl x509 -in certificate.crt -text -noout
   ```

2. **Renew Certificate:**
   ```bash
   certbot renew
   ```

3. **Check Nginx Configuration:**
   ```nginx
   ssl_certificate /path/to/certificate.crt;
   ssl_certificate_key /path/to/private.key;
   ```

---

## Getting Help

### Check Logs

**Backend Logs:**
```bash
tail -f backend/logs/app.log
```

**Frontend Console:**
- Open browser DevTools
- Check Console tab for errors

**Network Tab:**
- Check Network tab in DevTools
- Verify API requests and responses

### Common Commands

```bash
# Check backend status
curl http://localhost:5001/api/health

# Check MongoDB
mongo --eval "db.adminCommand('ping')"

# Check Node version
node --version

# Check Python version
python --version

# Check installed packages
pip list
npm list
```

### Support Resources

- **Documentation**: Check relevant docs in `/docs`
- **GitHub Issues**: Report bugs on GitHub
- **Community**: Join community forums
- **Email**: Contact support team

---

**Last Updated:** November 2024  
**Version:** 1.0.0

For additional help, please refer to the main documentation or contact support.

