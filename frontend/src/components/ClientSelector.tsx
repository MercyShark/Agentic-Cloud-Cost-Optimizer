import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Cloud, Check } from 'lucide-react';
import api from '../services/api';
import { CloudClient } from '../types/CloudClient';

interface ClientSelectorProps {
  selectedClientId: string | null;
  onSelectClient: (clientId: string | null) => void;
}

export const ClientSelector = ({ selectedClientId, onSelectClient }: ClientSelectorProps) => {
  const [clients, setClients] = useState<CloudClient[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    setLoading(true);
    const { data, error } = await api.getCloudClients();

    if (!error && data) {
      setClients(data);
      if (data.length > 0 && !selectedClientId) {
        onSelectClient(data[0].id);
      }
    }
    setLoading(false);
  };

  const selectedClient = clients.find(c => c.id === selectedClientId);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-3 px-4 py-3 bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 rounded-lg hover:border-blue-500 dark:hover:border-blue-400 transition-all min-w-[280px]"
      >
        <Cloud className="w-5 h-5 text-blue-600 dark:text-blue-400" />
        <div className="flex-1 text-left">
          {loading ? (
            <span className="text-gray-600 dark:text-gray-400">Loading clients...</span>
          ) : selectedClient ? (
            <>
              <div className="text-sm font-semibold text-gray-900 dark:text-white">
                {selectedClient.name}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                {selectedClient.providers.join(', ')}
              </div>
            </>
          ) : (
            <span className="text-gray-600 dark:text-gray-400">No clients available</span>
          )}
        </div>
        <ChevronDown
          className={`w-5 h-5 text-gray-600 dark:text-gray-400 transition-transform ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 z-10"
            />
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute top-full left-0 mt-2 w-full bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-lg shadow-xl z-20 max-h-[300px] overflow-y-auto"
            >
              {clients.length === 0 ? (
                <div className="p-4 text-center text-gray-600 dark:text-gray-400">
                  No cloud clients found. Add one to get started.
                </div>
              ) : (
                clients.map((client) => (
                  <button
                    key={client.id}
                    onClick={() => {
                      onSelectClient(client.id);
                      setIsOpen(false);
                    }}
                    className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors border-b border-gray-100 dark:border-gray-700 last:border-b-0"
                  >
                    <Cloud className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    <div className="flex-1 text-left">
                      <div className="text-sm font-semibold text-gray-900 dark:text-white">
                        {client.name}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {client.providers.join(', ')}
                      </div>
                    </div>
                    {selectedClientId === client.id && (
                      <Check className="w-5 h-5 text-green-600 dark:text-green-400" />
                    )}
                  </button>
                ))
              )}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
