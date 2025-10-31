import { useState } from 'react';
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { Sidebar } from './components/Sidebar';
import { Home } from './pages/Home';
import { Dashboard } from './pages/Dashboard';
import { Notifications } from './pages/Notifications';
import { Resources } from './pages/Resources';
import { Optimization } from './pages/Optimization';
import { Alerts } from './pages/Alerts';
import { Integrations } from './pages/Integrations';
import { Team } from './pages/Team';
import { Settings } from './pages/Settings';
import { AddCloudClientModal } from './components/AddCloudClientModal';
import { motion } from 'framer-motion';

// Layout component to handle the sidebar and main content layout
const Layout = ({ children }: { children: React.ReactNode }) => {
  const location = useLocation();
  const [isCloudModalOpen, setIsCloudModalOpen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleClientAdded = () => {
    setRefreshKey(prev => prev + 1);
  };

  // Get current page from path
  const currentPath = location.pathname.substring(1) || 'home';

  // Special case for dashboard to handle the cloud modal
  const childrenWithProps = currentPath === 'dashboard'
    ? React.cloneElement(children as React.ReactElement, {
        key: refreshKey,
        onOpenCloudModal: () => setIsCloudModalOpen(true)
      })
    : children;

  // Only show sidebar on non-home pages
  const isHomePage = currentPath === 'home' || currentPath === '';
  
  return (
    <>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
        {!isHomePage ? (
          <div className="flex min-h-screen">
            <Sidebar />
            <motion.main
              key={location.pathname}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="flex-1 p-6 lg:p-8 overflow-y-auto ml-0 lg:ml-72"
            >
              {childrenWithProps}
            </motion.main>
          </div>
        ) : (
          childrenWithProps
        )}

        <AddCloudClientModal
          isOpen={isCloudModalOpen}
          onClose={() => setIsCloudModalOpen(false)}
          onClientAdded={handleClientAdded}
        />
      </div>
    </>
  );
};

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Layout><Home /></Layout>} />
          <Route path="/home" element={<Layout><Home /></Layout>} />
          <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
          <Route path="/notifications" element={<Layout><Notifications /></Layout>} />
          <Route path="/resources" element={<Layout><Resources /></Layout>} />
          <Route path="/optimization" element={<Layout><Optimization /></Layout>} />
          <Route path="/alerts" element={<Layout><Alerts /></Layout>} />
          <Route path="/integrations" element={<Layout><Integrations /></Layout>} />
          <Route path="/team" element={<Layout><Team /></Layout>} />
          <Route path="/settings" element={<Layout><Settings /></Layout>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
