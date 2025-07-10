import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { Badge } from "@/components/ui/badge"
import { Loader2, Plus, Trash2, ChevronsLeft, ChevronsRight } from "lucide-react"
import type { ChatHistoryItem, IntegrationMode } from "./types"
import { useState } from "react"
import Image from "next/image"

interface SidebarProps {
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
  chatHistory: ChatHistoryItem[]
  isCreatingNewChat: boolean
  createNewConversation: () => void
  switchConversation: (conversationId: string) => void
  deleteConversation: (conversationId: string, e: React.MouseEvent) => void
  integrationModes: IntegrationMode[]
  currentMode: string
}

export function Sidebar({
  sidebarOpen,
  setSidebarOpen,
  chatHistory,
  isCreatingNewChat,
  createNewConversation,
  switchConversation,
  deleteConversation,
  integrationModes,
  currentMode,
}: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false)

  const filteredChatHistory = chatHistory

  const renderHistory = (collapsed: boolean) => (
    <div className="p-2 space-y-1">
      {filteredChatHistory.map((chat) => (
        <div
          key={chat.id}
          className={`group flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
            chat.active
              ? "bg-blue-600 text-white"
              : "hover:bg-gray-100 dark:hover:bg-gray-700"
          }`}
          onClick={() => switchConversation(chat.id)}
        >
          <Image src={chat.icon} alt={chat.title} width={24} height={24} />
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">{chat.title}</p>
              <div className="flex items-center gap-2">
                <p
                  className={`text-sm ${
                    chat.active ? "text-blue-100" : "text-gray-500 dark:text-gray-400"
                  }`}
                >
                  {chat.date}
                </p>
                <Badge
                  variant="outline"
                  className={`text-xs ${
                    chat.active ? "border-blue-200 text-blue-100" : ""
                  }`}
                >
                  {integrationModes.find((m) => m.id === chat.mode)?.name.split(" ")[0]}
                </Badge>
              </div>
            </div>
          )}
          {!collapsed && chatHistory.length > 1 && (
            <Button
              variant="ghost"
              size="icon"
              className={`opacity-0 group-hover:opacity-100 h-6 w-6 ${
                chat.active
                  ? "text-white hover:bg-blue-700"
                  : "hover:bg-gray-200 dark:hover:bg-gray-600"
              }`}
              onClick={(e) => deleteConversation(chat.id, e)}
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          )}
        </div>
      ))}
    </div>
  )

  return (
    <>
      {/* Desktop Sidebar */}
      <div
        className={`hidden lg:flex lg:flex-col lg:border-r dark:border-gray-700 transition-all duration-300 ${
          isCollapsed ? "lg:w-20" : "lg:w-80"
        }`}
      >
        <div
          className={`flex items-center p-4 border-b bg-blue-600 text-white dark:border-gray-700 ${
            isCollapsed ? "justify-center" : "justify-between"
          }`}
        >
          {!isCollapsed && <h2 className="text-lg font-semibold">Conversation History</h2>}
          <Button
            variant="ghost"
            size="icon"
            className="text-white hover:bg-blue-700"
            onClick={() => setIsCollapsed(!isCollapsed)}
          >
            {isCollapsed ? <ChevronsRight /> : <ChevronsLeft />}
          </Button>
        </div>
        <div className="flex items-center justify-center p-2 border-b dark:border-gray-700 bg-white dark:bg-gray-800">
          <Button
            variant="outline"
            size={isCollapsed ? "icon" : "default"}
            className="w-full"
            onClick={createNewConversation}
            disabled={isCreatingNewChat}
          >
            {isCreatingNewChat ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Plus className="h-4 w-4" />
            )}
            {!isCollapsed && <span className="ml-2">New Chat</span>}
          </Button>
        </div>
        <ScrollArea className="flex-1 bg-white dark:bg-gray-800">{renderHistory(isCollapsed)}</ScrollArea>
      </div>

      {/* Mobile Sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetContent side="left" className="w-80 p-0 dark:bg-gray-800 dark:border-gray-700">
          <SheetHeader className="p-4 border-b bg-blue-600 text-white dark:border-gray-700">
            <div className="flex items-center justify-between">
              <SheetTitle className="text-white">Conversation History</SheetTitle>
              <Button
                variant="ghost"
                size="icon"
                className="text-white hover:bg-blue-700"
                onClick={createNewConversation}
                disabled={isCreatingNewChat}
              >
                {isCreatingNewChat ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
              </Button>
            </div>
          </SheetHeader>
          <ScrollArea className="flex-1">{renderHistory(false)}</ScrollArea>
        </SheetContent>
      </Sheet>
    </>
  )
}