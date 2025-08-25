# 🎓 EduLearn AI - Next-Generation Learning Platform

<div align="center">

![EduLearn AI](https://img.shields.io/badge/EduLearn-AI%20Powered-blue?style=for-the-badge&logo=google)
![React](https://img.shields.io/badge/React-18.0+-61DAFB?style=for-the-badge&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=for-the-badge&logo=typescript)
![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask)
![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-47A248?style=for-the-badge&logo=mongodb)

**AI-Powered Educational Platform with Advanced MCQ Assessments, Coding Practice, and Personalized Learning**

[🚀 Live Demo](#) • [📖 Documentation](#) • [🐛 Report Bug](#) • [💡 Request Feature](#)

</div>

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🛠️ Technology Stack](#️-technology-stack)
- [🚀 Quick Start](#-quick-start)
- [📁 Project Structure](#-project-structure)
- [🔧 Configuration](#-configuration)
- [🎯 Usage Guide](#-usage-guide)
- [🔒 Security Features](#-security-features)
- [📊 Performance Features](#-performance-features)
- [🧪 Testing](#-testing)
- [🚀 Deployment](#-deployment)
- [🤝 Contributing](#-contributing)
- [📈 Roadmap](#-roadmap)
- [🐛 Troubleshooting](#-troubleshooting)
- [📞 Support](#-support)
- [📄 License](#-license)
- [🙏 Acknowledgments](#-acknowledgments)

---

## ✨ Features

### 🎯 **Smart Assessment System**
- **AI-Generated Questions**: Dynamic MCQ creation using Google Gemini AI
- **Multi-Subject Support**: 10+ subjects including Computer Science, Mathematics, Physics
- **Adaptive Difficulty**: Easy, Medium, Hard with intelligent progression
- **Real-time Feedback**: Instant scoring and detailed explanations
- **Performance Analytics**: Comprehensive insights and progress tracking

### 💻 **Advanced Coding Environment**
- **Multi-Language Support**: Python, JavaScript, Java, C++, and more
- **AI Problem Generation**: Create custom coding challenges on demand
- **Intelligent Evaluation**: Automated code assessment with detailed feedback
- **Test Case Management**: Comprehensive testing with hidden/public cases
- **Real-time Execution**: Live code compilation and output display

### 🎨 **Modern User Experience**
- **Responsive Design**: Beautiful, mobile-first interface
- **3D Visualizations**: Interactive learning elements with Three.js
- **Real-time Updates**: Live progress tracking and notifications
- **Accessibility**: Inclusive design for all users
- **Dark/Light Themes**: Customizable interface preferences

### 👥 **Role-Based Dashboards**

#### 🎓 **Student Features**
- Personalized learning paths
- Progress tracking and analytics
- Study material access
- Peer collaboration tools
- Achievement system

#### 👨‍🏫 **Teacher Features**
- Assignment management
- Student progress monitoring
- Performance analytics
- Content creation tools
- Automated grading

---

## 🛠️ Technology Stack

### **Frontend**
- **React 18** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Three.js** for 3D graphics
- **React Router** for navigation

### **Backend**
- **Flask** REST API
- **MongoDB** database
- **Google Gemini AI** integration
- **JWT** authentication
- **CORS** enabled

### **AI & ML**
- **Google Gemini AI** for question generation
- **Natural Language Processing** for feedback
- **Code Analysis** for programming assessment
- **Personalized Recommendations**

---

## 🚀 Quick Start

### **Prerequisites**
- Node.js 18+ 
- Python 3.8+
- MongoDB 6.0+
- Google Gemini API key

### **1. Clone Repository**
```bash
git clone https://github.com/yourusername/edulearn-ai.git
cd edulearn-ai
```

### **2. Backend Setup**
```bash
cd Backend
pip install -r requirements.txt

# Create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env
echo "MONGO_URI=mongodb://localhost:27017/edulearn" >> .env

# Start backend server
python app.py
```

### **3. Frontend Setup**
```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### **4. Access Application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:5003

---

## 📁 Project Structure

```
EDULEARN/
├── 📁 Backend/                 # Flask API Server
│   ├── app.py                 # Main Flask application
│   ├── fastapi_app.py         # FastAPI alternative
│   ├── models.py              # Database models
│   ├── llm_api.py             # AI integration
│   ├── database.py            # Database operations
│   ├── requirements.txt       # Python dependencies
│   └── README_BACKEND.md      # Backend documentation
├── 📁 src/                    # React Frontend
│   ├── 📁 components/         # Reusable UI components
│   │   ├── 📁 3D/            # Three.js 3D components
│   │   ├── 📁 ui/            # Base UI components
│   │   └── *.tsx             # Feature components
│   ├── 📁 pages/             # Page components
│   │   ├── 📁 student/       # Student dashboard pages
│   │   └── 📁 teacher/       # Teacher dashboard pages
│   ├── 📁 hooks/             # Custom React hooks
│   ├── 📁 contexts/          # React contexts
│   ├── 📁 types/             # TypeScript type definitions
│   └── 📁 utils/             # Utility functions
├── 📁 public/                # Static assets
├── package.json              # Node.js dependencies
├── vite.config.ts           # Vite configuration
└── README.md                # This file
```

---

## 🔧 Configuration

### **Environment Variables**

#### Backend (.env)
```env
GEMINI_API_KEY=your_gemini_api_key
MONGO_URI=mongodb://localhost:27017/edulearn
FLASK_ENV=development
SECRET_KEY=your_secret_key
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:5003
VITE_APP_NAME=EduLearn AI
```

### **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /getQuestions` | Generate MCQ questions |
| `POST /getQuizFeedback` | Get AI-powered feedback |
| `POST /coding/generate` | Create coding problems |
| `POST /coding/evaluate` | Assess code solutions |
| `POST /ChatBot` | AI learning assistant |

---

## 🎯 Usage Guide

### **For Students**

1. **Start Assessment**
   - Navigate to Student Dashboard
   - Select "MCQ Tests" or "Coding Practice"
   - Choose subject, topic, and difficulty
   - Begin your assessment

2. **Review Results**
   - Get instant scoring and feedback
   - Review detailed explanations
   - Access personalized study recommendations
   - Track your progress over time

3. **Practice Coding**
   - Choose from available problems
   - Write code in your preferred language
   - Get real-time feedback and suggestions
   - Generate new problems as needed

### **For Teachers**

1. **Manage Classes**
   - Create and assign assessments
   - Monitor student progress
   - Review submissions and provide feedback
   - Generate performance reports

2. **Content Creation**
   - Upload study materials
   - Create custom assignments
   - Set up discussion forums
   - Manage course content

---

## 🔒 Security Features

- **JWT Authentication** with secure token management
- **Password Hashing** using PBKDF2 with salt
- **Input Validation** and sanitization
- **CORS Protection** with configurable policies
- **Rate Limiting** to prevent abuse
- **Secure File Uploads** with validation

---

## 📊 Performance Features

- **Lazy Loading** for optimal performance
- **Code Splitting** for faster initial load
- **Caching Strategies** for improved response times
- **Database Indexing** for efficient queries
- **CDN Integration** for static assets
- **Progressive Web App** capabilities

---

## 🧪 Testing

### **Backend Testing**
```bash
cd Backend
python test_api.py
```

### **Frontend Testing**
```bash
npm run test
npm run test:coverage
```

---

## 🚀 Deployment

### **Production Build**
```bash
# Frontend
npm run build

# Backend
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5003 app:app
```

### **Docker Deployment**
```bash
# Build and run with Docker Compose
docker-compose up -d
```

---

## 🤝 Contributing

Thank you for your interest in contributing to EduLearn AI! We welcome contributions from the community and appreciate your help in making this platform better.

### **Types of Contributions**

We welcome various types of contributions:

#### 🐛 **Bug Reports**
- Report bugs you find in the application
- Provide detailed steps to reproduce
- Include system information and error logs

#### 💡 **Feature Requests**
- Suggest new features or improvements
- Describe the use case and benefits
- Consider implementation complexity

#### 📝 **Documentation**
- Improve existing documentation
- Add missing documentation
- Fix typos and grammar issues

#### 🔧 **Code Contributions**
- Fix bugs
- Implement new features
- Improve performance
- Add tests
- Refactor code

#### 🎨 **UI/UX Improvements**
- Design improvements
- Accessibility enhancements
- Mobile responsiveness
- User experience optimizations

### **Development Setup**

#### Prerequisites
- Node.js 18.0+
- Python 3.8+
- MongoDB 6.0+
- Git

#### Local Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/edulearn-ai.git
   cd edulearn-ai
   ```

2. **Backend Setup**
   ```bash
   cd Backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd ..
   npm install
   ```

4. **Environment Configuration**
   ```bash
   # Copy environment example
   cp env.example Backend/.env
   cp env.example .env.local
   
   # Edit with your actual values
   nano Backend/.env
   nano .env.local
   ```

5. **Start Development Servers**
   ```bash
   # Terminal 1 - Backend
   cd Backend
   python app.py
   
   # Terminal 2 - Frontend
   npm run dev
   ```

### **Coding Standards**

#### General Guidelines
- **Write clean, readable code**
- **Follow existing patterns** in the codebase
- **Add comments** for complex logic
- **Use meaningful variable names**
- **Keep functions small and focused**

#### Frontend (React/TypeScript)
- Use **TypeScript** for all new code
- Follow **ESLint** and **Prettier** configurations
- Use **functional components** with hooks
- Prefer **named exports** over default exports

#### Backend (Python/Flask)
- Follow **PEP 8** style guidelines
- Use **type hints** for function parameters
- Add **docstrings** for functions and classes
- Use **meaningful variable names**

### **Testing**

#### Frontend Testing
```bash
# Run all tests
npm run test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test -- --watch
```

#### Backend Testing
```bash
# Run backend tests
cd Backend
python test_api.py

# Run with coverage
python -m pytest --cov=.
```

### **Pull Request Process**

#### Before Submitting
1. **Check existing issues** to avoid duplicates
2. **Create a feature branch** from `main`
3. **Make your changes** following coding standards
4. **Add tests** for new functionality
5. **Update documentation** if needed
6. **Test thoroughly** before submitting

#### Creating a Pull Request
1. **Fork the repository** if you haven't already
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and commit:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```
4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Create a Pull Request** with:
   - Clear title and description
   - Link to related issues
   - Screenshots for UI changes
   - Test results

### **Commit Message Format**

Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(auth): add OAuth login support
fix(api): resolve CORS issue with frontend
docs(readme): update installation instructions
```

### **Issue Labels**

We use the following labels to categorize issues:

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `priority: high`: High priority issues
- `priority: low`: Low priority issues
- `frontend`: Frontend-related changes
- `backend`: Backend-related changes
- `ui/ux`: User interface improvements

---

## 📈 Roadmap

### **v2.1** - Enhanced AI Features
- [ ] Advanced adaptive learning algorithms
- [ ] Voice-based interactions
- [ ] Multi-language support for content
- [ ] Enhanced code analysis

### **v2.2** - Social Learning
- [ ] Study groups and peer learning
- [ ] Discussion forums with AI moderation
- [ ] Collaborative projects
- [ ] Gamification elements

### **v2.3** - Mobile App
- [ ] React Native mobile application
- [ ] Offline learning capabilities
- [ ] Push notifications
- [ ] Mobile-optimized assessments

---

## 🐛 Troubleshooting

### **Common Issues**

#### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'flask'`
```bash
# Solution: Install dependencies
cd Backend
pip install -r requirements.txt
```

**Error**: `Connection refused to MongoDB`
```bash
# Solution: Start MongoDB
# Windows: net start MongoDB
# macOS: brew services start mongodb-community
# Linux: sudo systemctl start mongod
```

#### Frontend Won't Start

**Error**: `Cannot find module`
```bash
# Solution: Install dependencies
npm install
```

**Error**: `Port already in use`
```bash
# Solution: Kill process or use different port
npm run dev -- --port 3001
```

#### Docker Issues

**Error**: `Port already in use`
```bash
# Solution: Stop existing containers
docker-compose down
docker system prune -f
```

**Error**: `Permission denied`
```bash
# Solution: Run with sudo (Linux/macOS)
sudo docker-compose up -d
```

### **Environment Variables**

Ensure all required environment variables are set:

#### Backend (.env)
```env
GEMINI_API_KEY=your_gemini_api_key
MONGO_URI=mongodb://localhost:27017/edulearn
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
```

#### Frontend (.env.local)
```env
VITE_API_URL=http://localhost:5003
VITE_APP_NAME=EduLearn AI
```

### **Getting Help**

If you encounter issues:

1. **Check the logs**:
   - Backend: `Backend/api_debug.log`
   - Frontend: Browser console
   - Docker: `docker-compose logs`

2. **Run tests**:
   ```bash
   # Backend tests
   cd Backend && python test_api.py
   
   # Frontend tests
   npm run test
   ```

3. **Search existing issues**: [GitHub Issues](https://github.com/yourusername/edulearn-ai/issues)

4. **Create new issue**: Include error logs and system information

---

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/edulearn-ai/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/edulearn-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/edulearn-ai/discussions)
- **Email**: support@edulearn.ai

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Gemini AI** for intelligent question generation
- **React Community** for excellent frontend tools
- **Flask Community** for robust backend framework
- **Three.js** for 3D graphics capabilities
- **All Contributors** who made this project possible

---

<div align="center">

**Made with ❤️ by the EduLearn AI Team**

[![GitHub stars](https://img.shields.io/github/stars/yourusername/edulearn-ai?style=social)](https://github.com/yourusername/edulearn-ai)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/edulearn-ai?style=social)](https://github.com/yourusername/edulearn-ai)
[![GitHub issues](https://img.shields.io/github/issues/yourusername/edulearn-ai)](https://github.com/yourusername/edulearn-ai/issues)

</div>
