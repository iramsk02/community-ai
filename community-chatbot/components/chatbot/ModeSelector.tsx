import { Button } from "@/components/ui/button"
import type { IntegrationMode } from "./types"
import Image from "next/image"

interface ModeSelectorProps {
  integrationModes: IntegrationMode[]
  selectedMode: string
  handleModeChange: (modeId: string) => void
}

export function ModeSelector({ integrationModes, selectedMode, handleModeChange }: ModeSelectorProps) {
  return (
    <div className="p-4 border-b bg-white dark:bg-gray-800 dark:border-gray-700">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {integrationModes.map((mode) => (
          <Button
            key={mode.id}
            variant={selectedMode === mode.id ? "default" : "outline"}
            className={`justify-start gap-2 h-auto p-3 transition-all ${
              selectedMode === mode.id ? mode.color : "hover:bg-gray-50 dark:hover:bg-gray-700"
            }`}
            onClick={() => handleModeChange(mode.id)}
          >
            <Image src={mode.image} alt={mode.name} width={24} height={24} />
            <span className="font-medium">{mode.name}</span>
          </Button>
        ))}
      </div>
    </div>
  )
}