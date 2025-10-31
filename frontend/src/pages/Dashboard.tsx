import { useState, useEffect } from 'react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { StatCard } from '../components/StatCard';
import { InsightCard } from '../components/InsightCard';
import { RecommendationsTable } from '../components/RecommendationsTable';
import { ClientSelector } from '../components/ClientSelector';
import api, { Recommendation, StatData } from '../services/api';
import { MessageSquare, Play, Clock } from 'lucide-react';
import { Toast } from '../components/ui/Toast';
import { AddCloudClientModal } from '../components/AddCloudClientModal';
import { CronJobModal } from '../components/CronJobModal';

interface DashboardProps {
  onOpenCloudModal?: () => void;
}

export const Dashboard = ({ onOpenCloudModal }: DashboardProps) => {
  // Create a local function for opening the modal if not provided as a prop
  const [isCloudModalOpen, setIsCloudModalOpen] = useState(false);
  const [isCronModalOpen, setIsCronModalOpen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  
  const handleOpenCloudModal = () => {
    if (onOpenCloudModal) {
      onOpenCloudModal();
    } else {
      setIsCloudModalOpen(true);
    }
  };
  const [selectedClientId, setSelectedClientId] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [stats, setStats] = useState<StatData[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [hasAnalyzed, setHasAnalyzed] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{ type: 'user' | 'ai'; message: string; timestamp: Date }>>([]);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error'; visible: boolean }>({
    message: '',
    type: 'success',
    visible: false,
  });

  useEffect(() => {
    const loadData = async () => {
      try {
        const [statsData, recsData] = await Promise.all([
          api.getStats(),
          api.getRecommendations(),
        ]);
        setStats(statsData);
        setRecommendations(recsData);
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      }
    };
    loadData();
  }, [refreshKey]);

  const handleAnalyze = async () => {
    if (!selectedClientId) {
      setToast({ message: 'Please select a cloud client first', type: 'error', visible: true });
      return;
    }
    setIsAnalyzing(true);
    const result = await api.analyze(selectedClientId);
    setIsAnalyzing(false);
    setHasAnalyzed(true);
    setToast({ message: result.message, type: 'success', visible: true });
    setRefreshKey(prev => prev + 1);
  };

  const handleUpdateRecommendation = (id: string, status: 'approved' | 'rejected') => {
    setRecommendations(prev =>
      prev.map(rec => (rec.id === id ? { ...rec, status } : rec))
    );
  };

  const handleCronToggle = () => {
    setIsCronModalOpen(true);
  };

  const handleSaveCronJob = (cronPattern: string) => {
    setToast({ 
      message: `Cron job scheduled successfully with pattern: ${cronPattern}`, 
      type: 'success', 
      visible: true 
    });
  };

  const handleSendMessage = async () => {
    if (!chatMessage.trim()) return;

    const userMessage = chatMessage.trim();
    setChatMessage('');
    
    setChatHistory(prev => [...prev, { type: 'user', message: userMessage, timestamp: new Date() }]);
    
    setIsChatLoading(true);
    
    const response = await api.chatWithAI(userMessage, selectedClientId || undefined);
    
    setIsChatLoading(false);
    
    setChatHistory(prev => [...prev, { type: 'ai', message: response.message, timestamp: new Date() }]);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400">Monitor and optimize your cloud spending</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <ClientSelector
            key={refreshKey}
            selectedClientId={selectedClientId}
            onSelectClient={setSelectedClientId}
          />
          <Button onClick={handleOpenCloudModal}>
            Add Cloud Client
          </Button>
          <Button onClick={handleAnalyze} disabled={isAnalyzing}>
            {isAnalyzing ? (
              <>
                <Play className="w-4 h-4 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Start Analysis
              </>
            )}
          </Button>
          <Button onClick={handleCronToggle} variant="secondary">
            <Clock className="w-4 h-4 mr-2" />
            Enable Cron Job
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat, idx) => (
          <StatCard key={idx} {...stat} delay={idx * 0.1} />
        ))}
      </div>

      <Card hover={false}>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">AI Insights & Alerts</h2>
        {hasAnalyzed ? (
          <div className="space-y-3">
            {mockInsights.map((insight, idx) => (
              <InsightCard key={insight.id} insight={insight} index={idx} />
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            Click "Start Analysis" to view insights and alerts
          </div>
        )}
      </Card>

      <Card hover={false}>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">AI Recommendations</h2>
        {hasAnalyzed ? (
          <RecommendationsTable
            recommendations={recommendations}
            onUpdate={handleUpdateRecommendation}
          />
        ) : (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            Click "Start Analysis" to view recommendations
          </div>
        )}
      </Card>

      <Card hover={false}>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <MessageSquare className="w-6 h-6 text-blue-600 dark:text-blue-400" />
          Chat with Agentic AI
        </h2>
        
        {/* Chat History */}
        {chatHistory.length > 0 && (
          <div className="mb-4 max-h-96 overflow-y-auto space-y-3 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
            {chatHistory.map((chat, idx) => (
              <div
                key={idx}
                className={`flex ${chat.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-2 ${
                    chat.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700'
                  }`}
                >
                  <p className="text-sm whitespace-pre-line">{chat.message}</p>
                  <span className="text-xs opacity-70 mt-1 block">
                    {chat.timestamp.toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
            {isChatLoading && (
              <div className="flex justify-start">
                <div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 rounded-lg px-4 py-2">
                  <p className="text-sm">AI is typing...</p>
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* Chat Input */}
        <div className="flex gap-3">
          <input
            type="text"
            value={chatMessage}
            onChange={(e) => setChatMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about your cloud costs, S3 buckets, resources..."
            disabled={isChatLoading}
            className="flex-1 px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
          <Button onClick={handleSendMessage} disabled={isChatLoading || !chatMessage.trim()}>
            Send
          </Button>
        </div>
      </Card>

      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.visible}
        onClose={() => setToast({ ...toast, visible: false })}
      />

      <AddCloudClientModal
        isOpen={isCloudModalOpen}
        onClose={() => setIsCloudModalOpen(false)}
        onClientAdded={() => {
          setIsCloudModalOpen(false);
          // Refresh the client selector by incrementing the key
          setRefreshKey(prev => prev + 1);
        }}
      />

      <CronJobModal
        isOpen={isCronModalOpen}
        onClose={() => setIsCronModalOpen(false)}
        onSave={handleSaveCronJob}
      />
    </div>
  );
};
