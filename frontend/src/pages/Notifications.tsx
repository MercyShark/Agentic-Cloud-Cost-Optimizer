import { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Toast } from '../components/ui/Toast';
import api from '../services/api';
import { 
  Send, Mail
} from 'lucide-react';

// Custom SlackLogo icon since it doesn't exist in lucide-react
const SlackIcon = () => (
  <svg 
    viewBox="0 0 24 24" 
    width="24" 
    height="24" 
    stroke="currentColor" 
    strokeWidth="2" 
    fill="none" 
    strokeLinecap="round" 
    strokeLinejoin="round"
    className="lucide lucide-slack"
  >
    <rect width="3" height="8" x="13" y="2" rx="1.5" />
    <path d="M19 8.5V10h1.5A1.5 1.5 0 1 0 19 8.5" />
    <rect width="3" height="8" x="8" y="14" rx="1.5" />
    <path d="M5 15.5V14H3.5A1.5 1.5 0 1 0 5 15.5" />
    <rect width="8" height="3" x="14" y="13" rx="1.5" />
    <path d="M15.5 19H14v1.5a1.5 1.5 0 1 0 1.5-1.5" />
    <rect width="8" height="3" x="2" y="8" rx="1.5" />
    <path d="M8.5 5H10V3.5A1.5 1.5 0 1 0 8.5 5" />
  </svg>
);

// Custom Discord icon since it doesn't exist in lucide-react
const DiscordIcon = () => (
  <svg 
    viewBox="0 0 24 24" 
    width="24" 
    height="24" 
    stroke="currentColor" 
    strokeWidth="2" 
    fill="none" 
    strokeLinecap="round" 
    strokeLinejoin="round"
    className="lucide lucide-discord"
  >
    <path d="M9 12a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" />
    <path d="M15 12a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" />
    <path d="M20 4.5v15.5a1 1 0 0 1-1 1h-14a1 1 0 0 1-1-1v-15.5c0-.34.14-.66.38-.88a3 3 0 0 1 .62-.42c.6-.33 1.3-.7 2-.7s1.4.37 2 .7c.3.16.48.27.62.42.24.22.38.54.38.88Z" />
    <path d="M16 4c0-1.1-.9-2-2-2h-4c-1.1 0-2 .9-2 2" />
  </svg>
);

interface NotificationChannel {
  id: string;
  name: string;
  description: string;
  icon: React.FC | React.ElementType;
  color: string;
  darkColor: string;
  enabled: boolean;
  webhookPlaceholder: string;
}

export const Notifications = () => {
  const [discordWebhook, setDiscordWebhook] = useState('');
  const [slackWebhook, setSlackWebhook] = useState('');
  const [emailAddress, setEmailAddress] = useState('');
  const [activeTab, setActiveTab] = useState<'channels' | 'settings'>('channels');
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error'; visible: boolean }>({
    message: '',
    type: 'success',
    visible: false,
  });
  
  const [channels, setChannels] = useState<NotificationChannel[]>([
    {
      id: 'discord',
      name: 'Discord',
      description: 'Receive cost alerts in your Discord server',
      icon: DiscordIcon,
      color: 'indigo-100',
      darkColor: 'indigo-900/30',
      enabled: false,
      webhookPlaceholder: 'https://discord.com/api/webhooks/...'
    },
    {
      id: 'slack',
      name: 'Slack',
      description: 'Get cost optimization alerts in Slack',
      icon: SlackIcon,
      color: 'purple-100',
      darkColor: 'purple-900/30',
      enabled: false,
      webhookPlaceholder: 'https://hooks.slack.com/services/...'
    },
    {
      id: 'email',
      name: 'Email',
      description: 'Receive alerts and reports via email',
      icon: Mail,
      color: 'blue-100',
      darkColor: 'blue-900/30',
      enabled: false,
      webhookPlaceholder: 'your.email@example.com'
    }
  ]);

  const handleConnectDiscord = async () => {
    if (!discordWebhook) {
      setToast({ message: 'Please enter a valid Discord webhook URL', type: 'error', visible: true });
      return;
    }
    
    const result = await api.connectNotification('Discord', discordWebhook);
    
    setToast({ message: result.message, type: 'success', visible: true });
    setChannels(prev => 
      prev.map(channel => 
        channel.id === 'discord' ? { ...channel, enabled: true } : channel
      )
    );
  };

  const handleConnectSlack = async () => {
    if (!slackWebhook) {
      setToast({ message: 'Please enter a valid Slack webhook URL', type: 'error', visible: true });
      return;
    }
    
    const result = await api.connectNotification('Slack', slackWebhook);
    
    setToast({ message: result.message, type: 'success', visible: true });
    setChannels(prev => 
      prev.map(channel => 
        channel.id === 'slack' ? { ...channel, enabled: true } : channel
      )
    );
  };
  
  const handleConnectEmail = async () => {
    if (!emailAddress) {
      setToast({ message: 'Please enter a valid email address', type: 'error', visible: true });
      return;
    }
    
    const result = await api.connectNotification('Email', emailAddress);
    
    setToast({ message: result.message, type: 'success', visible: true });
    setChannels(prev => 
      prev.map(channel => 
        channel.id === 'email' ? { ...channel, enabled: true } : channel
      )
    );
  };

  // Handle toggling between channels and settings tabs
  const renderTabContent = () => {
    if (activeTab === 'settings') {
      return (
        <div className="space-y-6">
          <Card>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Notification Preferences</h3>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center py-3 border-b border-gray-200 dark:border-gray-700">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white">Cost alerts</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Get notified when spending exceeds thresholds</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" defaultChecked className="sr-only peer" />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                </label>
              </div>
              
              <div className="flex justify-between items-center py-3 border-b border-gray-200 dark:border-gray-700">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white">Daily summaries</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Get daily summaries of cost optimization opportunities</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" defaultChecked className="sr-only peer" />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                </label>
              </div>
              
              <div className="flex justify-between items-center py-3">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white">Weekly reports</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Get weekly reports with savings achieved</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" defaultChecked className="sr-only peer" />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>
          </Card>
        </div>
      );
    }
    
    return (
      <div className="space-y-6">
        {/* Discord */}
        <Card delay={0}>
          <div className="flex items-center gap-3 mb-6">
            <div className={`p-3 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg`}>
              <DiscordIcon />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">Discord</h2>
                {channels.find(c => c.id === 'discord')?.enabled && (
                  <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 rounded-full">
                    Connected
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Receive cost alerts in your Discord server</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
                Discord Webhook URL
              </label>
              <input
                type="text"
                value={discordWebhook}
                onChange={(e) => setDiscordWebhook(e.target.value)}
                placeholder="https://discord.com/api/webhooks/..."
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <Button onClick={handleConnectDiscord} className="w-full sm:w-auto">
              <Send className="w-4 h-4 mr-2" />
              Connect Discord
            </Button>
          </div>
        </Card>

        {/* Slack */}
        {/* <Card delay={0.1}>
          <div className="flex items-center gap-3 mb-6">
            <div className={`p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg`}>
              <SlackIcon />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">Slack</h2>
                {channels.find(c => c.id === 'slack')?.enabled && (
                  <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 rounded-full">
                    Connected
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Get cost optimization alerts in Slack</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
                Slack Webhook URL
              </label>
              <input
                type="text"
                value={slackWebhook}
                onChange={(e) => setSlackWebhook(e.target.value)}
                placeholder="https://hooks.slack.com/services/..."
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <Button onClick={handleConnectSlack} className="w-full sm:w-auto">
              <Send className="w-4 h-4 mr-2" />
              Connect Slack
            </Button>
          </div>
        </Card> */}

        {/* Email */}
        <Card delay={0.2}>
          <div className="flex items-center gap-3 mb-6">
            <div className={`p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg`}>
              <Mail className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">Email</h2>
                {channels.find(c => c.id === 'email')?.enabled && (
                  <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 rounded-full">
                    Connected
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Receive alerts and reports via email</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={emailAddress}
                onChange={(e) => setEmailAddress(e.target.value)}
                placeholder="your.email@example.com"
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <Button onClick={handleConnectEmail} className="w-full sm:w-auto">
              <Send className="w-4 h-4 mr-2" />
              Connect Email
            </Button>
          </div>
        </Card>

        {/* Notification info */}
        <Card delay={0.3} hover={false}>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">What notifications will I receive?</h3>
          <ul className="space-y-3">
            {[
              'High-priority cost alerts when spending exceeds thresholds',
              'Daily summaries of cost optimization opportunities',
              'Real-time alerts when AI detects anomalies',
              'Weekly reports with savings achieved',
            ].map((item, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <div className="w-2 h-2 bg-blue-600 dark:bg-blue-400 rounded-full mt-2" />
                <span className="text-gray-700 dark:text-gray-300">{item}</span>
              </li>
            ))}
          </ul>
        </Card>
      </div>
    );
  };

  return (
    <>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Notification Integrations</h1>
          <p className="text-gray-600 dark:text-gray-400 mb-4">Connect your notification channels to receive alerts</p>
          
          {/* Tab navigation */}
          <div className="flex border-b border-gray-200 dark:border-gray-700 mb-4">
            <button
              className={`px-4 py-2 font-medium text-sm ${
                activeTab === 'channels'
                  ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                  : 'text-gray-600 dark:text-gray-400'
              }`}
              onClick={() => setActiveTab('channels')}
            >
              Notification Channels
            </button>
            <button
              className={`px-4 py-2 font-medium text-sm ${
                activeTab === 'settings'
                  ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                  : 'text-gray-600 dark:text-gray-400'
              }`}
              onClick={() => setActiveTab('settings')}
            >
              Alert Settings
            </button>
          </div>
        </div>
        
        {renderTabContent()}
      </div>

      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.visible}
        onClose={() => setToast({ ...toast, visible: false })}
      />
    </>
  );
};
