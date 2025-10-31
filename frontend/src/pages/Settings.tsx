import { Card } from '../components/ui/Card';

export const Settings = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Settings</h1>
        <p className="text-gray-600 dark:text-gray-400 mb-6">Configure application settings and preferences</p>
      </div>
      
      <Card>
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Application Settings</h2>
          <p className="text-gray-700 dark:text-gray-300">
            This page is under development. Soon you will be able to configure your application settings and preferences.
          </p>
        </div>
      </Card>
    </div>
  );
};