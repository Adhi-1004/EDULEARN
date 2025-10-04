# modLRN Frontend

React frontend for the modLRN AI-powered Adaptive Learning Platform.

## 🏗️ Architecture

The frontend follows a modern React architecture with TypeScript:

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── api/              # Centralized API services
│   │   ├── authService.ts      # Authentication operations
│   │   ├── assessmentService.ts # Assessment management
│   │   ├── codingService.ts    # Coding platform functionality
│   │   └── index.ts            # Service exports
│   ├── components/        # Reusable UI components
│   │   ├── ui/           # Basic UI components
│   │   └── ...           # Feature-specific components
│   ├── contexts/         # React contexts
│   │   ├── ThemeContext.tsx    # Theme management
│   │   └── ToastContext.tsx    # Notification system
│   ├── hooks/            # Custom React hooks
│   │   └── useAuth.ts          # Authentication hook
│   ├── pages/           # Page components
│   │   ├── Dashboard.tsx       # Student dashboard
│   │   ├── CodingPlatform.tsx # Coding challenges
│   │   ├── TeacherDashboard.tsx # Teacher interface
│   │   └── ...
│   ├── types/           # TypeScript type definitions
│   │   └── index.ts            # Type exports
│   └── utils/           # Utility functions
│       ├── api.ts              # API configuration
│       ├── constants.ts        # Application constants
│       └── roleUtils.ts        # Role-based utilities
├── package.json         # Dependencies and scripts
├── tsconfig.json        # TypeScript configuration
├── vite.config.js       # Vite configuration
└── tailwind.config.js    # Tailwind CSS configuration
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🛠️ Technology Stack

- **React 18**: Modern React with hooks and concurrent features
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Animation library
- **Monaco Editor**: Code editor component
- **Axios**: HTTP client for API requests
- **React Router**: Client-side routing

## 🎨 UI Components

### Core Components

- **Button**: Customizable button component
- **Card**: Container component with consistent styling
- **Input**: Form input component
- **LoadingSpinner**: Loading state indicator
- **Toast**: Notification system

### Feature Components

- **CodeEditor**: Monaco-based code editor
- **FaceLogin**: Face recognition authentication
- **Leaderboard**: Student rankings
- **ProgressCharts**: Analytics visualization
- **TestInterface**: Assessment interface

## 🔧 Development

### Project Structure

- **Pages**: Route components in `src/pages/`
- **Components**: Reusable UI components in `src/components/`
- **API Services**: Centralized API logic in `src/api/`
- **Hooks**: Custom React hooks in `src/hooks/`
- **Contexts**: Global state management in `src/contexts/`
- **Types**: TypeScript definitions in `src/types/`

### Adding New Features

1. Create components in `src/components/`
2. Add pages in `src/pages/`
3. Update routing in `src/App.tsx`
4. Add API services in `src/api/`
5. Define types in `src/types/`

### Styling

The project uses Tailwind CSS for styling:

```tsx
// Example component with Tailwind classes
<div className="bg-purple-900 text-white p-4 rounded-lg">
  <h1 className="text-2xl font-bold">Welcome to modLRN</h1>
</div>
```

### State Management

The app uses React Context for global state:

```tsx
// Using authentication context
const { user, login, logout } = useAuth();

// Using toast notifications
const { success, error } = useToast();
```

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch
```

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop (1024px+)
- Tablet (768px - 1023px)
- Mobile (320px - 767px)

## 🎨 Theming

The app supports light and dark themes:

```tsx
// Using theme context
const { theme, toggleTheme } = useTheme();

// Theme-aware styling
<div className={`${theme === 'dark' ? 'bg-gray-900' : 'bg-white'}`}>
  Content
</div>
```

## 🔐 Authentication

The app supports multiple authentication methods:

- **Email/Password**: Traditional login
- **Google OAuth**: Social login
- **Face Recognition**: Biometric authentication

### Authentication Flow

```tsx
// Login with email/password
const response = await authService.login({
  email: 'user@example.com',
  password: 'password'
});

// Google OAuth login
const response = await authService.googleLogin({
  token: googleToken,
  user: googleUser
});
```

## 📊 Analytics

The app includes comprehensive analytics:

- **Student Progress**: Track learning progress
- **Coding Analytics**: Monitor coding performance
- **Assessment Results**: View test scores and feedback
- **Learning Paths**: AI-generated recommendations

## 🚀 Deployment

### Build for Production

```bash
# Create production build
npm run build

# The build output will be in the `dist/` directory
```

### Environment Variables

Create a `.env` file for environment-specific configuration:

```env
VITE_API_BASE_URL=http://localhost:5001
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

### Deployment Platforms

- **Vercel**: Optimized for React applications
- **Netlify**: Simple static site deployment
- **GitHub Pages**: Free hosting for public repositories

## 🎯 Key Features

### Student Features
- **Dashboard**: Personalized learning overview
- **Coding Platform**: Interactive coding challenges
- **Assessments**: AI-generated tests and quizzes
- **Progress Tracking**: Detailed analytics and insights
- **Learning Paths**: Personalized recommendations

### Teacher Features
- **Assessment Creation**: AI-assisted question generation
- **Student Management**: Monitor student progress
- **Analytics Dashboard**: Track class performance
- **Content Management**: Oversee AI-generated content

### Admin Features
- **User Management**: Comprehensive user administration
- **System Analytics**: Platform-wide statistics
- **Content Oversight**: Monitor and moderate content
- **Role Management**: Granular permission system

## 🆘 Troubleshooting

### Common Issues

1. **Build Errors**: Check TypeScript types and imports
2. **API Connection**: Verify backend is running and accessible
3. **Authentication**: Check token storage and expiration
4. **Styling**: Ensure Tailwind CSS is properly configured

### Development Tips

- Use React DevTools for debugging
- Check browser console for errors
- Verify API responses in Network tab
- Use TypeScript for type safety

## 🤝 Contributing

1. Follow React best practices
2. Use TypeScript for type safety
3. Write clean, maintainable code
4. Add appropriate error handling
5. Test components thoroughly

## 📚 Resources

- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Vite Guide](https://vitejs.dev/guide/)

---

**modLRN Frontend** - Building the future of education.
