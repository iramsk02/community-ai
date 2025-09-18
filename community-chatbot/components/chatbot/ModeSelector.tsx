import Image from 'next/image';

import { Button } from '@/components/ui/button';

import type { IntegrationMode } from './types';

interface ModeSelectorProps {
  integrationModes: IntegrationMode[]
  selectedMode: string
  handleModeChange: (modeId: string) => void
}

export function ModeSelector({ integrationModes, selectedMode, handleModeChange }: ModeSelectorProps) {
  return (
    <div className="bg-white dark:bg-gray-800 p-4 dark:border-gray-700 border-b">
      <div className="gap-2 sm:gap-3 grid grid-cols-2 lg:grid-cols-4">
        {integrationModes.map((mode) => (
          <Button
            key={mode.id}
            variant={selectedMode === mode.id ? "default" : "outline"}
            className={`flex flex-col sm:flex-row items-center sm:items-start justify-center sm:justify-start gap-1 sm:gap-2 h-auto p-2 sm:p-3 text-center sm:text-left transition-all ${selectedMode === mode.id
              ? mode.color
              : "hover:bg-gray-50 dark:hover:bg-gray-700"
              }`}
            onClick={() => handleModeChange(mode.id)}
          >
            <div className="bg-white p-1 rounded-full">
              <Image
                src={mode.image}
                alt={mode.name}
                width={20}
                height={20}
              />
            </div>
            <span className="max-w-[80px] sm:max-w-none font-medium text-xs sm:text-sm truncate">
              {mode.name}
            </span>
          </Button>
        ))}
      </div>
    </div>
  )
}