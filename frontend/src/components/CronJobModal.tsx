import { useState } from 'react';
import { Modal } from './ui/Modal';
import { Button } from './ui/Button';
import { Clock, Info } from 'lucide-react';

interface CronJobModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (cronPattern: string) => void;
}

export const CronJobModal = ({ isOpen, onClose, onSave }: CronJobModalProps) => {
  const [cronPattern, setCronPattern] = useState('0 0 * * *');
  const [selectedPreset, setSelectedPreset] = useState('daily');

  const cronPresets = [
    { id: 'hourly', label: 'Every Hour', pattern: '0 * * * *' },
    { id: 'daily', label: 'Daily at Midnight', pattern: '0 0 * * *' },
    { id: 'weekly', label: 'Weekly on Monday', pattern: '0 0 * * 1' },
    { id: 'monthly', label: 'Monthly on 1st', pattern: '0 0 1 * *' },
    { id: 'custom', label: 'Custom Pattern', pattern: '' },
  ];

  const handlePresetChange = (presetId: string) => {
    setSelectedPreset(presetId);
    const preset = cronPresets.find(p => p.id === presetId);
    if (preset && preset.pattern) {
      setCronPattern(preset.pattern);
    }
  };

  const handleSave = () => {
    if (cronPattern.trim()) {
      onSave(cronPattern);
      onClose();
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Configure Cron Job Schedule">
      <div className="space-y-6">
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 flex items-start gap-3">
          <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-800 dark:text-blue-200">
            <p className="font-semibold mb-1">Cron Pattern Format:</p>
            <p className="font-mono text-xs">* * * * *</p>
            <p className="text-xs mt-1">minute hour day month weekday</p>
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-3">
            Select Schedule Preset
          </label>
          <div className="grid grid-cols-1 gap-2">
            {cronPresets.map((preset) => (
              <label
                key={preset.id}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg border-2 cursor-pointer transition-all ${
                  selectedPreset === preset.id
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-300 dark:border-gray-600 hover:border-blue-400'
                }`}
              >
                <input
                  type="radio"
                  name="cronPreset"
                  checked={selectedPreset === preset.id}
                  onChange={() => handlePresetChange(preset.id)}
                  className="w-4 h-4 text-blue-600"
                />
                <div className="flex-1">
                  <div className="font-medium text-gray-900 dark:text-white">
                    {preset.label}
                  </div>
                  {preset.pattern && (
                    <div className="text-xs font-mono text-gray-500 dark:text-gray-400">
                      {preset.pattern}
                    </div>
                  )}
                </div>
                <Clock className="w-5 h-5 text-gray-400" />
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-900 dark:text-white mb-2">
            Cron Pattern
          </label>
          <input
            type="text"
            value={cronPattern}
            onChange={(e) => {
              setCronPattern(e.target.value);
              setSelectedPreset('custom');
            }}
            placeholder="0 0 * * *"
            className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
          />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            Enter a custom cron pattern or select a preset above
          </p>
        </div>

        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
            Quick Reference:
          </h4>
          <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
            <div className="flex justify-between">
              <span className="font-mono">* * * * *</span>
              <span>Every minute</span>
            </div>
            <div className="flex justify-between">
              <span className="font-mono">0 * * * *</span>
              <span>Every hour</span>
            </div>
            <div className="flex justify-between">
              <span className="font-mono">0 0 * * *</span>
              <span>Daily at midnight</span>
            </div>
            <div className="flex justify-between">
              <span className="font-mono">0 0 * * 0</span>
              <span>Weekly on Sunday</span>
            </div>
          </div>
        </div>

        <div className="flex gap-3 pt-4">
          <Button onClick={handleSave} className="flex-1">
            Enable Cron Job
          </Button>
          <Button onClick={onClose} variant="secondary" className="flex-1">
            Cancel
          </Button>
        </div>
      </div>
    </Modal>
  );
};
