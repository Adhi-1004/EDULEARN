import React, { useState, useEffect, useCallback, memo } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Bell, X } from "lucide-react";
import { User } from "../types";
import { useTheme } from "../contexts/ThemeContext";
import { useToast } from "../contexts/ToastContext";
import ThemeToggle from "./ui/ThemeToggle";
import UserProfileDropdown from "./ui/UserProfileDropdown";
import BackendStatusIndicator from "./BackendStatusIndicator";
import { getNavigationItems, canAccessRoute, getUserDisplayName, getRoleDisplayName } from "../utils/roleUtils";
import api from "../utils/api";
import { ANIMATION_VARIANTS, TRANSITION_DEFAULTS } from "../utils/constants";
import { 
    getNotifications, 
    markNotificationAsRead, 
    markAllNotificationsAsRead,
    deleteNotification,
    formatNotificationTime,
    getNotificationIcon,
    getNotificationTypeDisplayName,
    Notification 
} from "../services/notificationService";

interface NavbarProps {
    user: User | null;
    setUser: (user: User | null) => void;
}

const Navbar: React.FC<NavbarProps> = ({ user, setUser }) => {
    const { mode, colorScheme } = useTheme();
    const { success } = useToast();
    const navigate = useNavigate();
    const location = useLocation();
    const [scrolled, setScrolled] = useState(false);
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [showNotifications, setShowNotifications] = useState(false);
    const [unreadCount, setUnreadCount] = useState(0);

    const handleScroll = useCallback(() => {
        setScrolled(window.scrollY > 20);
    }, []);

    useEffect(() => {
        window.addEventListener("scroll", handleScroll);
        
        return () => {
            window.removeEventListener("scroll", handleScroll);
        };
    }, [handleScroll]);

    // Fetch notifications when user is authenticated
    useEffect(() => {
        const fetchNotifications = async () => {
            if (user) {
                try {
                    const response = await getNotifications();
                    setNotifications(response.notifications);
                    setUnreadCount(response.unread_count);
                } catch (error) {
                    console.error("Error fetching notifications:", error);
                }
            }
        };

        fetchNotifications();
        
        // Set up polling for notifications every 30 seconds
        const interval = setInterval(fetchNotifications, 30000);
        
        return () => clearInterval(interval);
    }, [user]);

    // Close notifications dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (showNotifications) {
                const target = event.target as Element;
                if (!target.closest('.notification-dropdown')) {
                    setShowNotifications(false);
                }
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [showNotifications]);

    const handleLogout = useCallback(async () => {
        try {
            await api.post("/auth/logout");
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            setUser(null);
            success('Logout Successful!', 'You have been logged out successfully.');
            navigate("/login", { replace: true });
        } catch (error) {
            console.error("Logout failed:", error);
            // Still logout locally even if server logout fails
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            setUser(null);
            success('Logout Successful!', 'You have been logged out successfully.');
            navigate("/login", { replace: true });
        }
    }, [setUser, navigate, success]);

    const isActive = useCallback((path: string) => {
        return location.pathname === path || (path === '/coding' && location.pathname.startsWith('/coding'));
    }, [location.pathname]);

    // Notification handlers
    const handleNotificationClick = useCallback(async (notification: Notification) => {
        if (!notification.read) {
            try {
                await markNotificationAsRead(notification._id);
                setNotifications(prev => 
                    prev.map(n => n._id === notification._id ? { ...n, read: true } : n)
                );
                setUnreadCount(prev => Math.max(0, prev - 1));
            } catch (error) {
                console.error('Failed to mark notification as read:', error);
            }
        }
    }, []);

    const handleMarkAllAsRead = useCallback(async () => {
        try {
            await markAllNotificationsAsRead();
            setNotifications(prev => prev.map(n => ({ ...n, read: true })));
            setUnreadCount(0);
        } catch (error) {
            console.error('Failed to mark all notifications as read:', error);
        }
    }, []);

    const handleDeleteNotification = useCallback(async (notificationId: string) => {
        try {
            await deleteNotification(notificationId);
            setNotifications(prev => prev.filter(n => n._id !== notificationId));
            setUnreadCount(prev => Math.max(0, prev - 1));
        } catch (error) {
            console.error('Failed to delete notification:', error);
        }
    }, []);

    const navItems = user ? getNavigationItems(user) : [
        { path: "/login", label: "Login" }
    ];



    return (
        <motion.nav
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            transition={TRANSITION_DEFAULTS}
            className={`
                fixed top-0 left-0 right-0 z-50 transition-all duration-500
                ${scrolled 
                    ? colorScheme === 'dark'
                        ? mode === 'professional'
                            ? "bg-gray-900/95 backdrop-blur-xl border-b border-gray-700/50 shadow-2xl"
                            : "bg-gradient-to-r from-indigo-900/95 via-purple-900/95 to-pink-900/95 backdrop-blur-xl border-b border-white/10 shadow-2xl"
                        : mode === 'professional'
                            ? "bg-white/95 backdrop-blur-xl border-b border-gray-200/50 shadow-lg"
                            : "bg-gradient-to-r from-white/95 via-purple-50/95 to-pink-50/95 backdrop-blur-xl border-b border-purple-200/30 shadow-lg"
                    : colorScheme === 'dark'
                        ? mode === 'professional'
                            ? "bg-gray-900/60 backdrop-blur-md"
                            : "bg-gradient-to-r from-indigo-900/60 via-purple-900/60 to-pink-900/60 backdrop-blur-md"
                        : mode === 'professional'
                            ? "bg-white/60 backdrop-blur-md"
                            : "bg-gradient-to-r from-white/60 via-purple-50/60 to-pink-50/60 backdrop-blur-md"
                }
            `}
        >
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Left Side - Logo and Status */}
                    <div className="flex items-center space-x-4">
                        <Link to="/" className="flex items-center space-x-3">
                            <motion.div
                                className={`
                                    w-10 h-10 rounded-xl flex items-center justify-center text-lg font-bold
                                    ${mode === 'professional'
                                        ? colorScheme === 'dark'
                                            ? 'bg-gradient-to-br from-gray-700 to-gray-800 text-gray-200'
                                            : 'bg-gradient-to-br from-gray-800 to-gray-900 text-white'
                                        : 'bg-gradient-to-br from-purple-500 to-pink-500 text-white'
                                    }
                                `}
                                whileHover={{ scale: 1.05, rotate: 5 }}
                                whileTap={{ scale: 0.95 }}
                                transition={TRANSITION_DEFAULTS}
                            >
                                %L
                            </motion.div>
                            <motion.span 
                                className={`
                                    text-2xl font-bold transition-all duration-300
                                    ${mode === 'professional' 
                                        ? colorScheme === 'dark'
                                            ? 'font-serif text-gray-200'
                                            : 'font-serif text-gray-800'
                                        : colorScheme === 'dark'
                                            ? 'bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400'
                                            : 'bg-clip-text text-transparent bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600'
                                    }
                                `}
                                whileHover={{ scale: 1.02 }}
                                transition={TRANSITION_DEFAULTS}
                            >
                                {mode === 'professional' ? 'LearnAI Pro' : 'LearnAI'}
                            </motion.span>
                        </Link>
                        <BackendStatusIndicator />
                    </div>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center space-x-8">
                        {/* Navigation Links */}
                        <div className="flex items-center space-x-6">
                            {navItems.map((item) => (
                                <Link 
                                    key={item.path}
                                    to={item.path}
                                    className={`
                                        px-4 py-2 rounded-xl transition-all duration-300 font-medium
                                        ${mode === 'professional' ? 'font-serif' : 'font-sans'}
                                        ${isActive(item.path)
                                            ? colorScheme === 'dark'
                                                ? mode === 'professional'
                                                    ? "text-gray-200 bg-gray-800/50"
                                                    : "text-blue-400 bg-purple-900/30"
                                                : mode === 'professional'
                                                    ? "text-gray-800 bg-gray-100/50"
                                                    : "text-blue-600 bg-purple-100/50"
                                            : colorScheme === 'dark'
                                                ? mode === 'professional'
                                                    ? "text-gray-400 hover:text-gray-200 hover:bg-gray-800/30"
                                                    : "text-purple-200 hover:text-blue-400 hover:bg-purple-900/20"
                                                : mode === 'professional'
                                                    ? "text-gray-600 hover:text-gray-800 hover:bg-gray-100/30"
                                                    : "text-purple-700 hover:text-blue-600 hover:bg-purple-100/30"
                                        }
                                    `}
                                >
                                    {item.label}
                                </Link>
                            ))}
                        </div>
                        
                        {/* Right Side Controls */}
                        <div className="flex items-center space-x-4">
                            <ThemeToggle />
                            
                            {user ? (
                                <>
                                    {/* Notifications Bell */}
                                    <div className="relative">
                                        <motion.button
                                            whileHover={{ scale: 1.05 }}
                                            whileTap={{ scale: 0.95 }}
                                            onClick={() => setShowNotifications(!showNotifications)}
                                            className={`
                                                relative p-2 rounded-lg transition-all duration-300
                                                ${colorScheme === 'dark'
                                                    ? mode === 'professional'
                                                        ? "text-gray-400 hover:text-gray-200 hover:bg-gray-800/30"
                                                        : "text-purple-200 hover:text-blue-400 hover:bg-purple-900/20"
                                                    : mode === 'professional'
                                                        ? "text-gray-600 hover:text-gray-800 hover:bg-gray-100/30"
                                                        : "text-purple-700 hover:text-blue-600 hover:bg-purple-100/30"
                                                }
                                            `}
                                        >
                                            <Bell className="h-6 w-6" />
                                            {unreadCount > 0 && (
                                                <motion.span
                                                    initial={{ scale: 0 }}
                                                    animate={{ scale: 1 }}
                                                    className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center font-bold border-2 border-white"
                                                >
                                                    {unreadCount > 9 ? '9+' : unreadCount}
                                                </motion.span>
                                            )}
                                        </motion.button>

                                        {/* Notifications Dropdown */}
                                        <AnimatePresence>
                                            {showNotifications && (
                                                <motion.div
                                                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                                                    animate={{ opacity: 1, y: 0, scale: 1 }}
                                                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                                                    transition={{ duration: 0.2 }}
                                                    className="notification-dropdown absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden z-50"
                                                >
                                                    <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                                                        <div className="flex items-center justify-between">
                                                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                                                                Notifications
                                                            </h3>
                                                            {unreadCount > 0 && (
                                                                <button
                                                                    onClick={handleMarkAllAsRead}
                                                                    className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
                                                                >
                                                                    Mark all as read
                                                                </button>
                                                            )}
                                                        </div>
                                                    </div>
                                                    
                                                    <div className="max-h-96 overflow-y-auto">
                                                        {notifications.length > 0 ? (
                                                            notifications.map((notification) => (
                                                                <motion.div
                                                                    key={notification._id}
                                                                    initial={{ opacity: 0, x: -20 }}
                                                                    animate={{ opacity: 1, x: 0 }}
                                                                    className={`
                                                                        p-4 border-b border-gray-100 dark:border-gray-700 cursor-pointer transition-all duration-200 hover:bg-gray-50 dark:hover:bg-gray-700
                                                                        ${!notification.read ? 'bg-blue-50 dark:bg-blue-900/20' : ''}
                                                                    `}
                                                                    onClick={() => handleNotificationClick(notification)}
                                                                >
                                                                    <div className="flex items-start space-x-3">
                                                                        <div className="flex-shrink-0">
                                                                            <span className="text-lg">
                                                                                {getNotificationIcon(notification.notification_type)}
                                                                            </span>
                                                                        </div>
                                                                        <div className="flex-1 min-w-0">
                                                                            <div className="flex items-center justify-between">
                                                                                <p className={`
                                                                                    text-sm font-medium
                                                                                    ${!notification.read 
                                                                                        ? 'text-gray-900 dark:text-white' 
                                                                                        : 'text-gray-600 dark:text-gray-400'
                                                                                    }
                                                                                `}>
                                                                                    {getNotificationTypeDisplayName(notification.notification_type)}
                                                                                </p>
                                                                                <div className="flex items-center space-x-2">
                                                                                    <span className="text-xs text-gray-500 dark:text-gray-400">
                                                                                        {formatNotificationTime(notification.timestamp)}
                                                                                    </span>
                                                                                    <button
                                                                                        onClick={(e) => {
                                                                                            e.stopPropagation();
                                                                                            handleDeleteNotification(notification._id);
                                                                                        }}
                                                                                        className="text-gray-400 hover:text-red-500 transition-colors"
                                                                                    >
                                                                                        <X className="h-4 w-4" />
                                                                                    </button>
                                                                                </div>
                                                                            </div>
                                                                            <p className={`
                                                                                text-sm mt-1
                                                                                ${!notification.read 
                                                                                    ? 'text-gray-800 dark:text-gray-200' 
                                                                                    : 'text-gray-600 dark:text-gray-400'
                                                                                }
                                                                            `}>
                                                                                {notification.message}
                                                                            </p>
                                                                        </div>
                                                                    </div>
                                                                </motion.div>
                                                            ))
                                                        ) : (
                                                            <div className="p-8 text-center">
                                                                <Bell className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                                                                <p className="text-gray-500 dark:text-gray-400">
                                                                    No notifications yet
                                                                </p>
                                                            </div>
                                                        )}
                                                    </div>
                                                </motion.div>
                                            )}
                                        </AnimatePresence>
                                    </div>

                                    <UserProfileDropdown user={user} onLogout={handleLogout} />
                                </>
                            ) : (
                                <Link 
                                    to="/signup"
                                    className={`
                                        px-6 py-2.5 rounded-xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105
                                        ${mode === 'professional' 
                                            ? colorScheme === 'dark'
                                                ? 'bg-gradient-to-r from-gray-700 to-gray-800 text-white hover:from-gray-600 hover:to-gray-700' 
                                                : 'bg-gradient-to-r from-gray-800 to-gray-900 text-white hover:from-gray-700 hover:to-gray-800'
                                            : 'bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-white hover:from-blue-600 hover:via-purple-600 hover:to-pink-600'
                                        }
                                    `}
                                >
                                    Sign Up
                                </Link>
                            )}
                        </div>
                    </div>

                    {/* Mobile Menu Button */}
                    <div className="md:hidden flex items-center space-x-3">
                        <ThemeToggle />
                        <motion.button
                            whileTap={{ scale: 0.95 }}
                            onClick={() => setIsMenuOpen(!isMenuOpen)}
                            className={`
                                p-2 rounded-xl transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2
                                ${colorScheme === 'dark' 
                                    ? 'text-purple-200 hover:text-blue-400 hover:bg-purple-900/20 focus:ring-purple-500' 
                                    : 'text-purple-700 hover:text-blue-600 hover:bg-purple-100/30 focus:ring-purple-400'
                                }
                            `}
                            aria-label="Toggle menu"
                        >
                            <svg className="w-6 h-6" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                                {isMenuOpen ? (
                                    <path d="M6 18L18 6M6 6l12 12" />
                                ) : (
                                    <path d="M4 6h16M4 12h16M4 18h16" />
                                )}
                            </svg>
                        </motion.button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            <AnimatePresence>
                {isMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.3 }}
                        className={`
                            md:hidden border-b backdrop-blur-xl
                            ${colorScheme === 'dark' 
                                ? mode === 'professional'
                                    ? 'bg-gray-900/95 border-gray-700/50'
                                    : 'bg-gradient-to-b from-indigo-900/95 via-purple-900/95 to-pink-900/95 border-white/10'
                                : mode === 'professional'
                                    ? 'bg-white/95 border-gray-200/50'
                                    : 'bg-gradient-to-b from-white/95 via-purple-50/95 to-pink-50/95 border-purple-200/30'
                            }
                        `}
                    >
                        <div className="px-4 pt-2 pb-4 space-y-2">
                            {navItems.map((item, index) => (
                                <motion.div
                                    key={item.path}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                >
                                    <Link
                                        to={item.path}
                                        className={`
                                            block px-4 py-3 rounded-xl text-base font-medium transition-all duration-200
                                            ${mode === 'professional' ? 'font-serif' : 'font-sans'}
                                            ${isActive(item.path)
                                                ? colorScheme === 'dark' 
                                                    ? mode === 'professional'
                                                        ? "text-gray-200 bg-gray-800/50" 
                                                        : "text-blue-400 bg-purple-800/30"
                                                    : mode === 'professional'
                                                        ? "text-gray-800 bg-gray-100/50"
                                                        : "text-blue-600 bg-purple-100/50"
                                                : colorScheme === 'dark'
                                                    ? mode === 'professional'
                                                        ? "text-gray-400 hover:text-gray-200 hover:bg-gray-800/30"
                                                        : "text-purple-200 hover:text-blue-400 hover:bg-purple-800/20"
                                                    : mode === 'professional'
                                                        ? "text-gray-600 hover:text-gray-800 hover:bg-gray-100/30"
                                                        : "text-purple-700 hover:text-blue-600 hover:bg-purple-100/30"
                                            }
                                        `}
                                        onClick={() => setIsMenuOpen(false)}
                                    >
                                        {item.label}
                                    </Link>
                                </motion.div>
                            ))}
                            
                            {user && (
                                <motion.div
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: navItems.length * 0.1 }}
                                    className="pt-2 border-t border-gray-700/30"
                                >
                                    <UserProfileDropdown user={user} onLogout={handleLogout} />
                                </motion.div>
                            )}
                            
                            {!user && (
                                <motion.div
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: navItems.length * 0.1 }}
                                    className="pt-2"
                                >
                                    <Link
                                        to="/signup"
                                        className={`
                                            block px-4 py-3 rounded-xl text-base font-medium transition-all duration-200 text-center
                                            ${mode === 'professional' 
                                                ? colorScheme === 'dark'
                                                    ? 'bg-gradient-to-r from-gray-700 to-gray-800 text-white' 
                                                    : 'bg-gradient-to-r from-gray-800 to-gray-900 text-white'
                                                : 'bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-white'
                                            }
                                        `}
                                        onClick={() => setIsMenuOpen(false)}
                                    >
                                        Sign Up
                                    </Link>
                                </motion.div>
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.nav>
    );
};

export default memo(Navbar);
