import { motion } from 'framer-motion';
import { 
  BarChart3, Bell, Cloud, Sun, Moon, Menu, X, Settings, 
  Users, ServerCog, AlertCircle, MessageSquare, Cpu
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

interface SidebarProps {
  currentPage?: string;
}

export const Sidebar = ({ currentPage }: SidebarProps) => {
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  // On mobile, the sidebar is closed by default, on desktop it's open
  const [isOpen, setIsOpen] = useState(false); // Default to closed for SSR compatibility

  // Get current page from location
  const activePage = currentPage || location.pathname.substring(1) || 'home';

  // Fix: use useEffect instead of useState
  useEffect(() => {
    setIsOpen(window.innerWidth >= 1024);
  }, []);

  const menuCategories = [
    {
      title: "General",
      items: [
        { id: 'home', label: 'Home', icon: Cloud },
        { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
      ]
    },
    {
      title: "Management",
      items: [
        { id: 'resources', label: 'Resources', icon: ServerCog },
        { id: 'optimization', label: 'Optimization', icon: Cpu },
        { id: 'alerts', label: 'Alerts', icon: AlertCircle },
      ]
    },
    {
      title: "Settings",
      items: [
        { id: 'notifications', label: 'Notifications', icon: Bell },
        { id: 'integrations', label: 'Integrations', icon: MessageSquare },
        { id: 'team', label: 'Team', icon: Users },
        { id: 'settings', label: 'Settings', icon: Settings },
      ]
    },
  ];

  const handleNavigate = (page: string) => {
    navigate(`/${page}`);
    
    // Only close the sidebar on mobile screens
    if (window.innerWidth < 1024) {
      setIsOpen(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 left-4 z-50 lg:hidden p-3 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700"
      >
        {isOpen ? (
          <X className="w-6 h-6 text-blue-600 dark:text-blue-400" />
        ) : (
          <Menu className="w-6 h-6 text-blue-600 dark:text-blue-400" />
        )}
      </button>

      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={() => setIsOpen(false)}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
        />
      )}

      <motion.aside
        initial={{ x: 0 }}
        animate={{ x: isOpen ? 0 : -300 }}
        className="fixed left-0 top-0 bottom-0 h-full w-72 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 z-40 transition-transform duration-300 shadow-lg lg:transform-none"
      >
        <div className="flex flex-col h-full p-6">
          <div className="mb-8 lg:mb-12">
            <div className="flex items-center gap-3">
              <Cloud className="w-10 h-10 text-blue-600 dark:text-blue-400" />
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">Agentic</h2>
                <p className="text-xs text-gray-600 dark:text-gray-400">Cost Optimizer</p>
              </div>
            </div>
          </div>

          <nav className="flex-1 space-y-6">
            {menuCategories.map((category, index) => (
              <div key={index} className="space-y-2">
                <h3 className="text-xs uppercase font-semibold text-gray-500 dark:text-gray-400 px-4 mb-2">
                  {category.title}
                </h3>
                
                {category.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = activePage === item.id;

                  return (
                    <motion.button
                      key={item.id}
                      onClick={() => handleNavigate(item.id)}
                      whileHover={{ x: 4 }}
                      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                        isActive
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span className="font-medium">{item.label}</span>
                    </motion.button>
                  );
                })}
              </div>
            ))}
          </nav>

          <motion.button
            onClick={toggleTheme}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-3 px-4 py-3 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white transition-colors"
          >
            {theme === 'light' ? (
              <>
                <Moon className="w-5 h-5" />
                <span className="font-medium">Dark Mode</span>
              </>
            ) : (
              <>
                <Sun className="w-5 h-5" />
                <span className="font-medium">Light Mode</span>
              </>
            )}
          </motion.button>
        </div>
      </motion.aside>
    </>
  );
};
