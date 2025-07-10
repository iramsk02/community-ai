import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Loader2 } from "lucide-react"
import type { Message } from "@ai-sdk/react"
import { ChatMessage } from "./ChatMessage"
import type { IntegrationMode } from "./types"
import { useEffect } from "react"
import Image from "next/image"

interface ChatPanelProps {
  messages: Message[]
  status: string
  error: Error | undefined
  reload: () => void
  scrollAreaRef: React.RefObject<HTMLDivElement>
  currentMode: IntegrationMode | undefined
  quickActions: string[]
  handleQuickAction: (action: string) => void
  integrationModes: IntegrationMode[]
}

export function ChatPanel({
  messages,
  status,
  error,
  reload,
  scrollAreaRef,
  currentMode,
  quickActions,
  handleQuickAction,
  integrationModes,
}: ChatPanelProps) {
  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollElement = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]') as HTMLElement
      if (scrollElement) {
        scrollElement.scrollTo({
          top: scrollElement.scrollHeight,
          behavior: 'smooth'
        })
      }
    }
  }, [messages, status])

  return (
    <div className="flex-1 flex flex-col bg-gray-50 dark:bg-gray-800 min-h-0">
      <ScrollArea className="flex-1 min-h-0" ref={scrollAreaRef}>
        <div className="max-w-4xl mx-auto space-y-4 p-4 pb-6">
          {messages.length === 0 && (
            <div className="text-center py-8">
              <div className="bg-white dark:bg-gray-900 rounded-lg p-6 shadow-sm">
                <div className="flex items-center gap-3 mb-4">
                  {currentMode && <Image src={currentMode.image} alt={currentMode.name} width={32} height={32} />}
                  <div>
                    <h3 className="text-lg font-semibold">{currentMode?.name}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{currentMode?.description}</p>
                  </div>
                </div>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Hello! I'm your Mifos Community assistant. I can help with general questions or connect to Slack,
                  Jira, and GitHub. Select a mode above to get started!
                </p>
                <div className="text-left space-y-2 mb-6">
                  <p className="font-semibold text-gray-800 dark:text-gray-200">How to use:</p>
                  <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                    {integrationModes.map((mode) => (
                      <li key={mode.id} className="flex items-center gap-2">
                        <Image src={mode.image} alt={mode.name} width={16} height={16} />
                        <span><strong>{mode.name}:</strong> {mode.description}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-3">Quick actions:</p>
                  <div className="flex flex-wrap gap-2">
                    {quickActions.map((action, index) => (
                      <Button
                        key={index}
                        variant="outline"
                        size="sm"
                        className="text-xs hover:bg-blue-50 hover:border-blue-300 dark:hover:bg-gray-700"
                        onClick={() => handleQuickAction(action)}
                      >
                        {action}
                      </Button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}

          {(status === "submitted" || status === "streaming") && (
            <div className="flex gap-3 justify-start">
              <div className="bg-white dark:bg-gray-900 shadow-sm border rounded-lg px-4 py-3">
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {status === "submitted" ? "Thinking..." : "Typing..."}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {error && (
        <div className="p-4 bg-red-50 border-t border-red-200">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <p className="text-sm text-red-600">Something went wrong. Please try again.</p>
            <Button variant="outline" size="sm" onClick={reload}>
              Retry
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}