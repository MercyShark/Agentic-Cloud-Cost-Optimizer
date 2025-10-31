import { motion } from 'framer-motion';
import { AlertTriangle, Info } from 'lucide-react';
import { Insight } from '../services/api';

interface InsightCardProps {
  insight: Insight;
  index: number;
}

export const InsightCard = ({ insight, index }: InsightCardProps) => {
  const severityColors = {
    high: 'bg-red-100 dark:bg-red-900/30 border-red-300 dark:border-red-700',
    medium: 'bg-yellow-100 dark:bg-yellow-900/30 border-yellow-300 dark:border-yellow-700',
    low: 'bg-blue-100 dark:bg-blue-900/30 border-blue-300 dark:border-blue-700',
  };

  const iconColors = {
    high: 'text-red-600 dark:text-red-400',
    medium: 'text-yellow-600 dark:text-yellow-400',
    low: 'text-blue-600 dark:text-blue-400',
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      className={`p-4 rounded-lg border-2 ${severityColors[insight.severity]}`}
    >
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg ${iconColors[insight.severity]}`}>
          {insight.severity === 'high' ? (
            <AlertTriangle className="w-5 h-5" />
          ) : (
            <Info className="w-5 h-5" />
          )}
        </div>
        <div className="flex-1">
          <h4 className="font-bold text-gray-900 dark:text-white mb-1">{insight.title}</h4>
          <p className="text-sm text-gray-700 dark:text-gray-300">{insight.description}</p>
        </div>
        <span className="text-xs font-semibold uppercase px-2 py-1 rounded bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300">
          {insight.severity}
        </span>
      </div>
    </motion.div>
  );
};
