import { Card } from '../components/ui/Card';

export const Alerts = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Alerts</h1>
        <p className="text-gray-600 dark:text-gray-400 mb-6">View and manage your cloud infrastructure alerts</p>
      </div>
      
      <Card>
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Alerts Center</h2>
          <p className="text-gray-700 dark:text-gray-300">
            This page is under development. Soon you will be able to view and manage alerts for your cloud resources.
          </p>
        </div>
      </Card>
    </div>
  );
};