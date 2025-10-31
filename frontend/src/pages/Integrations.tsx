import { Card } from '../components/ui/Card';

export const Integrations = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Integrations</h1>
        <p className="text-gray-600 dark:text-gray-400 mb-6">Connect third-party services and tools</p>
      </div>
      
      <Card>
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Available Integrations</h2>
          <p className="text-gray-700 dark:text-gray-300">
            This page is under development. Soon you will be able to connect to various third-party services and tools.
          </p>
        </div>
      </Card>
    </div>
  );
};