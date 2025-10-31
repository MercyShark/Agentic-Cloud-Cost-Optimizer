import { useState } from 'react';
import { Modal } from './ui/Modal';
import { Button } from './ui/Button';
import { Cloud, Copy, Check } from 'lucide-react';
import api from '../services/api';
import { Toast } from './ui/Toast';

interface AddCloudClientModalProps {
  isOpen: boolean;
  onClose: () => void;
  onClientAdded?: () => void;
}

export const AddCloudClientModal = ({ isOpen, onClose, onClientAdded }: AddCloudClientModalProps) => {
  const [clientName, setClientName] = useState('');
  const [description, setDescription] = useState('');
  const [providers, setProviders] = useState<string[]>([]);
  const [iamRoleArn, setIamRoleArn] = useState('');
  const [copied, setCopied] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error'; visible: boolean }>({
    message: '',
    type: 'success',
    visible: false,
  });

  const cloudFormationUrl = 'https://sova-stack-bucket-fd246022.s3.ap-south-1.amazonaws.com/stack.yaml';

  const handleProviderToggle = (provider: string) => {
    setProviders(prev =>
      prev.includes(provider)
        ? prev.filter(p => p !== provider)
        : [...prev, provider]
    );
  };

  const handleCopyUrl = () => {
    navigator.clipboard.writeText(cloudFormationUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleTestRole = async () => {
    const result = await api.testRole();
    setToast({ message: result.message, type: 'success', visible: true });
  };

  const handleConnect = async () => {
    if (!clientName.trim() || providers.length === 0) {
      setToast({ message: 'Please fill in client name and select at least one provider', type: 'error', visible: true });
      return;
    }

    setIsConnecting(true);

    const { data, error } = await api.addCloudClient({
      name: clientName,
      description: description,
      providers: providers,
      iam_role_arn: iamRoleArn || undefined,
    });

    setIsConnecting(false);

    if (error) {
      setToast({ message: 'Failed to add cloud client: ' + error, type: 'error', visible: true });
      return;
    }

    setToast({ message: 'Cloud client added successfully!', type: 'success', visible: true });
    setTimeout(() => {
      onClose();
      setClientName('');
      setDescription('');
      setProviders([]);
      setIamRoleArn('');
      if (onClientAdded) onClientAdded();
    }, 1500);
  };

  return (
    <>
      <Modal isOpen={isOpen} onClose={onClose} title="Add Cloud Client">
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
              Client Name
            </label>
            <input
              type="text"
              value={clientName}
              onChange={(e) => setClientName(e.target.value)}
              placeholder="e.g., Production AWS Account"
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description of this cloud account"
              rows={3}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-3">
              Cloud Providers
            </label>
            <div className="flex flex-wrap gap-3">
              {['AWS', 'Azure', 'GCP'].map((provider) => (
                <label
                  key={provider}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg border-2 border-gray-300 dark:border-gray-600 cursor-pointer hover:border-blue-500 dark:hover:border-blue-400 transition-colors"
                >
                  <input
                    type="checkbox"
                    checked={providers.includes(provider)}
                    onChange={() => handleProviderToggle(provider)}
                    className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                  />
                  <Cloud className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  <span className="text-gray-900 dark:text-white font-medium">{provider}</span>
                </label>
              ))}
            </div>
          </div>

          {providers.includes('AWS') && (
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
                  CloudFormation Stack URL
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={cloudFormationUrl}
                    readOnly
                    className="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm"
                  />
                  <button
                    onClick={handleCopyUrl}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center gap-2"
                  >
                    {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    {copied ? 'Copied' : 'Copy'}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
                  IAM Role ARN
                </label>
                <input
                  type="text"
                  value={iamRoleArn}
                  onChange={(e) => setIamRoleArn(e.target.value)}
                  placeholder="arn:aws:iam::123456789012:role/AgenticCostOptimizer"
                  className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <Button onClick={handleTestRole} variant="secondary" className="w-full">
                Test Role
              </Button>
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <Button onClick={handleConnect} disabled={isConnecting} className="flex-1">
              {isConnecting ? 'Connecting...' : 'Connect'}
            </Button>
            <Button onClick={onClose} variant="secondary" className="flex-1">
              Cancel
            </Button>
          </div>
        </div>
      </Modal>

      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.visible}
        onClose={() => setToast({ ...toast, visible: false })}
      />
    </>
  );
};
