import { motion } from 'framer-motion';
import { Button } from '../components/ui/Button';
import { Cloud, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface HomeProps {
  onNavigate?: (page: string) => void;
}

export const Home = ({ onNavigate }: HomeProps) => {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      <motion.div
        className="absolute inset-0 z-0"
        animate={{
          background: [
            'radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%)',
            'radial-gradient(circle at 80% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%)',
            'radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%)',
          ],
        }}
        transition={{ duration: 10, repeat: Infinity, ease: 'linear' }}
      />

      <div className="max-w-4xl mx-auto px-6 text-center relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="flex items-center justify-center gap-3 mb-6"
        >
          <Cloud className="w-12 h-12 text-blue-600 dark:text-blue-400" />
          <Sparkles className="w-8 h-8 text-blue-500 dark:text-blue-300" />
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-6xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-gray-900 via-blue-800 to-gray-900 dark:from-white dark:via-blue-300 dark:to-white bg-clip-text text-transparent"
        >
          Agentic Cloud Cost Optimizer
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-12 leading-relaxed max-w-3xl mx-auto"
        >
          An Agentic AI-driven platform that analyzes and optimizes your cloud spending intelligently.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Button 
            onClick={() => {
              window.location.href = 'https://ap-south-1l1of4lbch.auth.ap-south-1.amazoncognito.com/login/continue?client_id=6thj36b803s625augkd3ph5j3p&redirect_uri=http%3A%2F%2Flocalhost%3A5173%2Fdashboard&response_type=code&scope=email+openid+phone'
            }}
            className="text-lg px-8 py-4"
          >
            Login with Cognito
          </Button>
          <Button 
            onClick={() => onNavigate ? onNavigate('dashboard') : navigate('/dashboard')} 
            className="text-lg px-8 py-4"
            variant="secondary"
          >
            Go to Dashboard
          </Button>
        </motion.div>



        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 1 }}
          className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8"
        >
          {[
            { title: 'AI-Powered', desc: 'Intelligent cost analysis' },
            { title: 'Real-Time', desc: 'Live monitoring & alerts' },
            { title: 'Automated', desc: 'Smart optimization actions' },
          ].map((feature, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.2 + idx * 0.1 }}
              className="bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700"
            >
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">{feature.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  );
};
