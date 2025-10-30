# EDULEARN Frontend

React + TypeScript frontend for the EDULEARN AI-powered Adaptive Learning Platform.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Development Server](#running-the-development-server)
- [Project Structure](#project-structure)
- [Build for Production](#build-for-production)
- [Technology Stack](#technology-stack)
- [Development Guide](#development-guide)
- [Troubleshooting](#troubleshooting)

## ✅ Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js 18+** (Node.js 20+ recommended)
- **npm 9+** or **yarn 1.22+**
- **Git** (for version control)

### System Requirements

- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: 1GB free space
- **Network**: Internet connection (for dependencies)

### Verify Installation

```bash
# Check Node.js version
node --version  # Should be 18.0.0 or higher

# Check npm version
npm --version  # Should be 9.0.0 or higher

# Check yarn version (if using yarn)
yarn --version  # Should be 1.22.0 or higher
```

## 🚀 Installation

### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 2: Install Dependencies

Using npm:
```bash
npm install
```

Or using yarn:
```bash
yarn install
```

**Note**: If you encounter dependency conflicts, try:
```bash
# Clear cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Or with yarn
yarn cache clean
rm -rf node_modules yarn.lock
yarn install
```

### Step 3: Configure Environment Variables

1. Create a `.env` file in the `frontend` directory:
   ```bash
   cp .env.example .env  # If .env.example exists
   # Or create manually
   touch .env
   ```

2. Add required environment variables (see [Configuration](#configuration) section)

## ⚙️ Configuration

Create a `.env` file in the `frontend` directory:

```env
# API Configuration - Backend URL
VITE_API_BASE_URL=http://localhost:5001

# Google OAuth (Optional - for social login)
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# Analytics (Optional)
VITE_ANALYTICS_ID=your-analytics-id
```

### Getting Configuration Values

1. **Backend URL**:
   - Development: `http://localhost:5001`
   - Production: Your deployed backend URL (e.g., `https://api.edulearn.com`)

2. **Google OAuth Client ID** (optional):
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create/select project
   - Go to Credentials → Create OAuth 2.0 Client ID
   - Set authorized JavaScript origins
   - Copy Client ID to `.env`

## 🏃 Running the Development Server

### Start Development Server

```bash
npm run dev

# Or with yarn
yarn dev
```

The frontend will be available at: **http://localhost:5173**

### Development Server Features

- **Hot Module Replacement (HMR)**: Changes reflect instantly
- **Fast Refresh**: React components update without losing state
- **Source Maps**: Easy debugging with original source code
- **TypeScript**: Full type checking and IntelliSense

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5001 (make sure backend is running)
- **API Documentation**: http://localhost:5001/docs

### Verify Frontend is Running

1. Open http://localhost:5173 in your browser
2. You should see the EDULEARN landing page or login page
3. Check browser console for any errors (F12)

## 📁 Project Structure

```
frontend/
├── public/                  # Static assets
│   └── ...
├── src/
│   ├── api/                # API service layer
│   │   ├── authService.ts
│   │   ├── assessmentService.ts
│   │   ├── codingService.ts
│   │   └── ...
│   ├── components/         # React components
│   │   ├── ui/            # Basic UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   └── ...
│   │   ├── teacher/       # Teacher-specific components
│   │   ├── admin/         # Admin components
│   │   └── ...
│   ├── contexts/          # React contexts
│   │   ├── ThemeContext.tsx
│   │   └── ToastContext.tsx
│   ├── hooks/             # Custom React hooks
│   │   ├── useAuth.ts
│   │   └── ...
│   ├── pages/             # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Login.tsx
│   │   ├── TeacherDashboard.tsx
│   │   └── ...
│   ├── types/             # TypeScript types
│   │   └── index.ts
│   ├── utils/             # Utility functions
│   │   ├── api.ts
│   │   ├── constants.ts
│   │   └── ...
│   ├── App.tsx            # Main App component
│   ├── main.tsx           # Application entry point
│   └── index.css          # Global styles
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript configuration
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.cjs     # PostCSS configuration
├── eslint.config.js       # ESLint configuration
└── README.md              # This file
```

## 🛠️ Technology Stack

### Core Framework
- **React 18.2.0** - Modern UI library with hooks
- **TypeScript 5.9.2** - Type-safe JavaScript
- **Vite 6.2.4** - Next-generation build tool

### UI & Styling
- **Tailwind CSS 3.4.1** - Utility-first CSS framework
- **Framer Motion 11.0.8** - Animation library
- **Lucide React 0.544.0** - Icon library

### Code Editing
- **Monaco Editor 0.53.0** - VS Code's editor (for coding challenges)
- **@monaco-editor/react 4.7.0** - React wrapper

### Routing & State
- **React Router DOM 7.9.1** - Client-side routing
- **React Context API** - Global state management

### HTTP & API
- **Axios 1.9.0** - HTTP client for API requests

### Development Tools
- **ESLint 9.36.0** - Code linting
- **PostCSS 8.4.35** - CSS processing
- **Autoprefixer 10.4.21** - CSS vendor prefixes

## 🔧 Development Guide

### Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview

# Lint code
npm run lint

# Format code (if Prettier is configured)
npm run format
```

### Adding New Components

1. Create component file in appropriate directory:
   ```typescript
   // src/components/MyComponent.tsx
   import React from 'react';

   interface MyComponentProps {
     title: string;
   }

   const MyComponent: React.FC<MyComponentProps> = ({ title }) => {
     return <div>{title}</div>;
   };

   export default MyComponent;
   ```

2. Import and use in pages or other components

### Adding New Pages

1. Create page component in `src/pages/`:
   ```typescript
   // src/pages/MyPage.tsx
   import React from 'react';
   import { useNavigate } from 'react-router-dom';

   const MyPage: React.FC = () => {
     return <div>My New Page</div>;
   };

   export default MyPage;
   ```

2. Add route in `src/App.tsx`:
   ```typescript
   import MyPage from './pages/MyPage';

   <Route path="/my-page" element={<MyPage />} />
   ```

### Styling Components

The project uses Tailwind CSS. Use utility classes:

```tsx
<div className="bg-blue-500 text-white p-4 rounded-lg">
  <h1 className="text-2xl font-bold">Title</h1>
</div>
```

For theme-aware styling:
```tsx
<div className="bg-background text-foreground">
  Theme-aware content
</div>
```

### API Integration

Use the API service layer in `src/api/`:

```typescript
import api from '../api/authService';

// Example: Login
const handleLogin = async (email: string, password: string) => {
  try {
    const response = await api.login({ email, password });
    // Handle success
  } catch (error) {
    // Handle error
  }
};
```

### State Management

Use React Context for global state:

```typescript
// Using theme context
import { useTheme } from '../contexts/ThemeContext';

const MyComponent = () => {
const { theme, toggleTheme } = useTheme();
  return <div className={theme === 'dark' ? 'dark' : ''}>Content</div>;
};

// Using auth context
import { useAuth } from '../hooks/useAuth';

const MyComponent = () => {
  const { user, login, logout } = useAuth();
  return <div>Hello, {user?.name}</div>;
};
```

## 📦 Build for Production

### Create Production Build

```bash
npm run build
```

This creates an optimized production build in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

This serves the production build locally for testing.

### Production Build Features

- **Minified JavaScript**: Reduced file sizes
- **Optimized Assets**: Compressed images and fonts
- **Tree Shaking**: Removed unused code
- **Code Splitting**: Automatic route-based code splitting
- **Source Maps**: For debugging (optional)

## 🚀 Deployment

### Option 1: Vercel (Recommended)

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Deploy:
   ```bash
   vercel
   ```

3. Or connect GitHub repository at [vercel.com](https://vercel.com)

4. Configure:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`
   - **Environment Variables**: Add all `.env` variables

### Option 2: Netlify

1. Install Netlify CLI:
```bash
   npm i -g netlify-cli
   ```

2. Deploy:
   ```bash
   netlify deploy --prod
   ```

3. Or connect GitHub repository at [netlify.com](https://netlify.com)

4. Configure:
   - **Build command**: `npm run build`
   - **Publish directory**: `dist`
   - **Environment variables**: Add in Netlify dashboard

### Option 3: Manual Deployment

1. Build the application:
   ```bash
   npm run build
   ```

2. The `dist/` folder contains all static files

3. Upload `dist/` contents to any static hosting service:
   - AWS S3 + CloudFront
   - GitHub Pages
   - Firebase Hosting
   - Any web server (Nginx, Apache, etc.)

### Environment Variables for Production

Ensure all production environment variables are set in your hosting platform:

```env
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_GOOGLE_CLIENT_ID=your-production-client-id
```

**Important**: Environment variables prefixed with `VITE_` are exposed to the browser. Never include sensitive information!

## 🆘 Troubleshooting

### Common Issues

1. **Module Not Found Errors**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Port Already in Use**
   ```bash
   # Change port in vite.config.js or use:
   npm run dev -- --port 3000
   ```

3. **Build Errors**
   - Check TypeScript errors: `npm run build`
   - Fix linting errors: `npm run lint`
   - Clear build cache: `rm -rf dist .vite`

4. **API Connection Errors**
   - Verify backend is running: http://localhost:5001/health/
   - Check `VITE_API_BASE_URL` in `.env`
   - Verify CORS settings on backend
- Check browser console for errors

5. **TypeScript Errors**
   ```bash
   # Check types
   npx tsc --noEmit
   ```

6. **Dependency Conflicts**
   ```bash
   # Update dependencies
   npm update
   
   # Or reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

7. **Slow Development Server**
   - Close unnecessary browser tabs
   - Disable browser extensions
   - Check system resources (RAM, CPU)

### Browser Compatibility

- **Chrome**: Latest 2 versions
- **Firefox**: Latest 2 versions
- **Safari**: Latest 2 versions
- **Edge**: Latest 2 versions

### Performance Optimization

1. **Code Splitting**: Already configured via React Router
2. **Lazy Loading**: Use `React.lazy()` for route components
3. **Image Optimization**: Use optimized image formats (WebP)
4. **Bundle Analysis**: Use `npm run build -- --analyze` (if configured)

## 🧪 Testing (Optional)

If tests are set up:

```bash
# Run tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

## 📝 Additional Resources

- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [React Router Docs](https://reactrouter.com/)

## 🤝 Contributing

1. Follow React best practices
2. Use TypeScript for type safety
3. Write clean, reusable components
4. Follow existing code structure
5. Update documentation as needed

## 📄 License

MIT License - see LICENSE file for details

---

**EDULEARN Frontend** - Building the future of education.
