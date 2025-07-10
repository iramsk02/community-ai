import { Avatar, AvatarFallback,AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { History, Plus, Loader2 } from "lucide-react"
import type { IntegrationMode } from "./types"
import { ThemeToggle } from "./ThemeToggle"

interface ChatHeaderProps {
  currentMode: IntegrationMode | undefined
  isCreatingNewChat: boolean
  setSidebarOpen: (open: boolean) => void
  createNewConversation: () => void
}

export function ChatHeader({
  currentMode,
  isCreatingNewChat,
  setSidebarOpen,
  createNewConversation,
}: ChatHeaderProps) {
  return (
    <div className="flex items-center gap-3 p-4 border-b bg-white dark:bg-gray-800 dark:border-gray-700">
      <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setSidebarOpen(true)}>
        <History className="h-5 w-5" />
      </Button>
      <Avatar>
      <AvatarImage src="/mifos.png" alt="Mifos Logo" />
      <AvatarFallback className="bg-blue-600 text-white">M</AvatarFallback>
      </Avatar>
      <div className="flex-1">
        <h1 className="text-xl font-bold">Mifos Assistant</h1>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          <span className="text-sm text-green-600">Online</span>
          {currentMode && (
            <Badge variant="outline" className="text-xs">
              {currentMode.name}
            </Badge>
          )}
        </div>
      </div>
      <div className="flex items-center gap-2">
        <Button variant="outline" size="sm" onClick={createNewConversation} disabled={isCreatingNewChat}>
          {isCreatingNewChat ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
          New Chat
        </Button>
        <ThemeToggle />
      </div>
    </div>
  )
}