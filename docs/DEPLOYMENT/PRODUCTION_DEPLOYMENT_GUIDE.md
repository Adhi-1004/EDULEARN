# EDULEARN Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying EDULEARN to production environments.

## Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB 6.0+
- Redis 6.0+ (for caching and sessions)
- Nginx (for reverse proxy)
- SSL certificates
- Domain name configured

## Environment Setup

### 1. Backend Environment Variables

Create a `.env` file in the backend directory:

```bash
# Database
MONGO_URI=mongodb://localhost:27017
DB_NAME=edulearn_production

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Redis (for caching)
REDIS_URL=redis://localhost:6379

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# AI Services
GEMINI_API_KEY=your-gemini-api-key

# Monitoring
LOG_LEVEL=INFO
ENABLE_AUDIT_LOGS=true

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### 2. Frontend Environment Variables

Create a `.env.production` file in the frontend directory:

```bash
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_APP_NAME=EDULEARN
VITE_APP_VERSION=1.0.0
VITE_ENABLE_ANALYTICS=true
VITE_GOOGLE_ANALYTICS_ID=your-ga-id
```

## Database Setup

### 1. MongoDB Configuration

```bash
# Start MongoDB with production settings
mongod --config /etc/mongod.conf

# Create production database
mongo
use edulearn_production

# Create indexes for performance
python init_database.py
```

### 2. Database Migration

```bash
# Run migration scripts
python migration_assessment_models.py

# Verify migration
python test_db.py
```

## Backend Deployment

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Database Initialization

```bash
python init_database.py
```

### 3. Start Backend Service

#### Development Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Production Mode with Gunicorn
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Production Mode with Docker
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

```bash
docker build -t edulearn-backend .
docker run -d -p 8000:8000 --env-file .env edulearn-backend
```

## Frontend Deployment

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Build for Production

```bash
npm run build
```

### 3. Deploy Static Files

#### Option 1: Nginx
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    root /path/to/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Option 2: Vercel
```bash
npm install -g vercel
vercel --prod
```

#### Option 3: Netlify
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

## Nginx Configuration

### Complete Nginx Config

```nginx
# /etc/nginx/sites-available/edulearn
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Frontend
    root /var/www/edulearn/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API Proxy
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Health check
    location /health {
        proxy_pass http://backend;
        access_log off;
    }
}

# Rate limiting
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
}
```

## SSL Certificate Setup

### Using Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Logging

### 1. Application Monitoring

```bash
# Install monitoring tools
pip install prometheus-client
pip install grafana-api

# Start monitoring
python -m prometheus_client
```

### 2. Log Management

```bash
# Configure log rotation
sudo nano /etc/logrotate.d/edulearn

# /var/log/edulearn/*.log {
#     daily
#     missingok
#     rotate 52
#     compress
#     delaycompress
#     notifempty
#     create 644 www-data www-data
# }
```

### 3. Health Checks

```bash
# Create health check script
cat > /usr/local/bin/edulearn-health.sh << 'EOF'
#!/bin/bash
curl -f http://localhost:8000/health || exit 1
EOF

chmod +x /usr/local/bin/edulearn-health.sh

# Add to crontab
crontab -e
# Add: */5 * * * * /usr/local/bin/edulearn-health.sh
```

## Performance Optimization

### 1. Database Optimization

```bash
# Run maintenance scripts
python maintenance_database.py

# Monitor database performance
mongo --eval "db.runCommand({collStats: 'assessments'})"
```

### 2. Caching Setup

```bash
# Install Redis
sudo apt install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
# Set: maxmemory 256mb
# Set: maxmemory-policy allkeys-lru

# Start Redis
sudo systemctl start redis
sudo systemctl enable redis
```

### 3. CDN Configuration

```bash
# Configure CloudFlare or AWS CloudFront
# Update frontend build to use CDN URLs
```

## Security Hardening

### 1. Firewall Configuration

```bash
# Configure UFW
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. Database Security

```bash
# Enable MongoDB authentication
mongo
use admin
db.createUser({
  user: "admin",
  pwd: "secure-password",
  roles: ["userAdminAnyDatabase", "dbAdminAnyDatabase", "readWriteAnyDatabase"]
})

# Update MongoDB config
sudo nano /etc/mongod.conf
# Add:
# security:
#   authorization: enabled
```

### 3. Application Security

```bash
# Install security headers middleware
pip install secure

# Configure security settings
export SECURE_SSL_REDIRECT=True
export SECURE_HSTS_SECONDS=31536000
export SECURE_HSTS_INCLUDE_SUBDOMAINS=True
```

## Backup Strategy

### 1. Database Backup

```bash
# Create backup script
cat > /usr/local/bin/edulearn-backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mongodump --db edulearn_production --out /backups/edulearn_$DATE
tar -czf /backups/edulearn_$DATE.tar.gz /backups/edulearn_$DATE
rm -rf /backups/edulearn_$DATE
find /backups -name "edulearn_*.tar.gz" -mtime +7 -delete
EOF

chmod +x /usr/local/bin/edulearn-backup.sh

# Schedule backups
crontab -e
# Add: 0 2 * * * /usr/local/bin/edulearn-backup.sh
```

### 2. Application Backup

```bash
# Backup application files
tar -czf /backups/edulearn-app-$(date +%Y%m%d).tar.gz /var/www/edulearn/
```

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Database initialized and migrated
- [ ] SSL certificates installed
- [ ] Nginx configured and tested
- [ ] Backend service running
- [ ] Frontend built and deployed
- [ ] Health checks working
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Security hardening completed
- [ ] Performance optimization applied
- [ ] Documentation updated

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**: Check if backend service is running
2. **Database Connection Error**: Verify MongoDB is running and accessible
3. **SSL Certificate Issues**: Check certificate validity and Nginx configuration
4. **Rate Limiting**: Adjust rate limits in Nginx and application
5. **Memory Issues**: Monitor memory usage and optimize queries

### Log Locations

- Application logs: `/var/log/edulearn/`
- Nginx logs: `/var/log/nginx/`
- MongoDB logs: `/var/log/mongodb/`
- System logs: `/var/log/syslog`

### Performance Monitoring

```bash
# Monitor system resources
htop
iotop
netstat -tulpn

# Monitor application
curl http://localhost:8000/health
curl http://localhost:8000/metrics
```

## Maintenance

### Regular Tasks

1. **Daily**: Check health endpoints and logs
2. **Weekly**: Review performance metrics and optimize
3. **Monthly**: Update dependencies and security patches
4. **Quarterly**: Review and test backup/restore procedures

### Updates

```bash
# Update application
git pull origin main
pip install -r requirements.txt
npm install
npm run build
sudo systemctl restart edulearn-backend
sudo systemctl reload nginx
```

This deployment guide ensures a robust, secure, and scalable production environment for EDULEARN.
