import { motion } from 'framer-motion';
import { DollarSign, PiggyBank, TrendingUp } from 'lucide-react';
import { Card } from './ui/Card';
import { useEffect, useState } from 'react';

interface StatCardProps {
  label: string;
  value: string;
  change: string;
  icon: string;
  delay: number;
}

export const StatCard = ({ label, value, change, icon, delay }: StatCardProps) => {
  const [count, setCount] = useState(0);
  const targetValue = parseInt(value.replace(/[^0-9.]/g, ''));

  useEffect(() => {
    let start = 0;
    const duration = 2000;
    const increment = targetValue / (duration / 16);

    const timer = setInterval(() => {
      start += increment;
      if (start >= targetValue) {
        setCount(targetValue);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, 16);

    return () => clearInterval(timer);
  }, [targetValue]);

  const IconComponent = icon === 'dollar' ? DollarSign : icon === 'piggy' ? PiggyBank : TrendingUp;

  const displayValue = value.includes('$')
    ? `$${count.toLocaleString()}`
    : value.includes('%')
    ? `${(count / 1000).toFixed(1)}%`
    : count.toLocaleString();

  return (
    <Card delay={delay}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">{label}</p>
          <motion.h3
            className="text-3xl font-bold text-gray-900 dark:text-white mb-2"
          >
            {displayValue}
          </motion.h3>
          {/* <p className={`text-sm font-semibold ${change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
            {change} from last month
          </p> */}
        </div>
        <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
          <IconComponent className="w-8 h-8 text-blue-600 dark:text-blue-400" />
        </div>
      </div>
    </Card>
  );
};
