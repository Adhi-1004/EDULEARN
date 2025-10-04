# MongoDB Setup Instructions

## Option 1: Install MongoDB Locally (Recommended for Development)

### Windows:
1. Download MongoDB Community Server from: https://www.mongodb.com/try/download/community
2. Install MongoDB with default settings
3. Start MongoDB service:
   ```cmd
   net start MongoDB
   ```

### Alternative: Use MongoDB via Docker
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

## Option 2: Use MongoDB Atlas (Cloud Database)

1. Go to https://www.mongodb.com/atlas
2. Create a free account
3. Create a new cluster
4. Get your connection string
5. Set environment variable:
   ```cmd
   set MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/edulearn
   ```

## Option 3: Quick Start with Docker (Easiest)

If you have Docker installed:
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

## Verify MongoDB is Running

After setup, test the connection:
```bash
# Test if MongoDB is accessible
curl http://localhost:27017
```

## Environment Variables

Create a `.env` file in the backend directory:
```
MONGO_URI=mongodb://localhost:27017
DB_NAME=edulearn
SECRET_KEY=your-secret-key-here
```

## Troubleshooting

If you get connection errors:
1. Check if MongoDB is running: `net start MongoDB` (Windows)
2. Check if port 27017 is available: `netstat -an | findstr :27017`
3. Try restarting MongoDB service
