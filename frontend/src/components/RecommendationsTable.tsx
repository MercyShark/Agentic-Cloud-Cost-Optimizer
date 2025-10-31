import { useState } from 'react';
import { Check, X, Loader2 } from 'lucide-react';
import { Button } from './ui/Button';
import api, { Recommendation } from '../services/api';
import { Toast } from './ui/Toast';

interface RecommendationsTableProps {
  recommendations: Recommendation[];
  onUpdate: (id: string, status: 'approved' | 'rejected') => void;
}

export const RecommendationsTable = ({ recommendations, onUpdate }: RecommendationsTableProps) => {
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error'; visible: boolean }>({
    message: '',
    type: 'success',
    visible: false,
  });

  const handleApprove = async (id: string) => {
    setLoadingId(id);
    const result = await api.approveRecommendation(id);
    onUpdate(id, 'approved');
    setLoadingId(null);
    setToast({ message: result.message, type: 'success', visible: true });
  };

  const handleReject = async (id: string) => {
    const result = await api.rejectRecommendation(id);
    onUpdate(id, 'rejected');
    setToast({ message: result.message, type: 'success', visible: true });
  };

  return (
    <>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700">
              <th className="text-left py-4 px-4 font-semibold text-gray-900 dark:text-white">Resource Name</th>
              <th className="text-left py-4 px-4 font-semibold text-gray-900 dark:text-white">Current Cost</th>
              <th className="text-left py-4 px-4 font-semibold text-gray-900 dark:text-white">AI Recommendation</th>
              <th className="text-left py-4 px-4 font-semibold text-gray-900 dark:text-white">Est. Saving</th>
              <th className="text-left py-4 px-4 font-semibold text-gray-900 dark:text-white">Action</th>
            </tr>
          </thead>
          <tbody>
            {recommendations.map((rec) => (
              <tr
                key={rec.id}
                className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
              >
                <td className="py-4 px-4 text-gray-900 dark:text-white font-medium">{rec.resourceName}</td>
                <td className="py-4 px-4 text-gray-700 dark:text-gray-300">{rec.currentCost}</td>
                <td className="py-4 px-4 text-gray-700 dark:text-gray-300 max-w-xs">{rec.recommendation}</td>
                <td className="py-4 px-4 text-green-600 dark:text-green-400 font-semibold">{rec.estimatedSaving}</td>
                <td className="py-4 px-4">
                  {rec.status === 'pending' ? (
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleApprove(rec.id)}
                        disabled={loadingId === rec.id}
                        className="p-2 bg-green-100 dark:bg-green-900/30 hover:bg-green-200 dark:hover:bg-green-800/50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Approve"
                      >
                        {loadingId === rec.id ? (
                          <Loader2 className="w-5 h-5 text-green-600 dark:text-green-400 animate-spin" />
                        ) : (
                          <Check className="w-5 h-5 text-green-600 dark:text-green-400" />
                        )}
                      </button>
                      <button
                        onClick={() => handleReject(rec.id)}
                        disabled={loadingId === rec.id}
                        className="p-2 bg-red-100 dark:bg-red-900/30 hover:bg-red-200 dark:hover:bg-red-800/50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Reject"
                      >
                        <X className="w-5 h-5 text-red-600 dark:text-red-400" />
                      </button>
                    </div>
                  ) : (
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        rec.status === 'approved'
                          ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                          : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                      }`}
                    >
                      {rec.status}
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
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
