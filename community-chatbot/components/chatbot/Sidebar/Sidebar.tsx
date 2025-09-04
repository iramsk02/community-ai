"use client"

import { ChatHistory } from '@/components/chatbot/Sidebar/ChatHistory';
import { NewChatButton } from '@/components/chatbot/Sidebar/NewChatButton';
import {
  Header as SidebarHeader,
} from '@/components/chatbot/Sidebar/SidebarHeader';
import { ChatHistoryItem, IntegrationMode } from '@/components/chatbot/types';
import { Sidebar, SidebarContent, useSidebar } from '@/components/ui/sidebar';

interface SidebarProps {
  chatHistory: ChatHistoryItem[]
  isCreatingNewChat: boolean
  createNewConversation: () => void
  switchConversation: (conversationId: string) => void
  deleteConversation: (conversationId: string, e: React.MouseEvent) => void
  integrationModes: IntegrationMode[]
}

export function AppSidebar({
  chatHistory,
  isCreatingNewChat,
  createNewConversation,
  switchConversation,
  deleteConversation,
  integrationModes,
}: SidebarProps) {
  const { state } = useSidebar()
  const isExpanded = state === "expanded"

  return (
    <Sidebar side="left" variant="sidebar" collapsible="icon">
      {/* Header */}
      <SidebarHeader isExpanded={isExpanded} />

      {/* Content */}
      <SidebarContent className="flex flex-col h-full">
        {/* New Chat Button */}
        <NewChatButton
          isExpanded={isExpanded}
          isCreatingNewChat={isCreatingNewChat}
          createNewConversation={createNewConversation}
        />

        {/* Scrollable History */}
        <ChatHistory
          chatHistory={chatHistory}
          deleteConversation={deleteConversation}
          integrationModes={integrationModes}
          isExpanded={isExpanded}
          switchConversation={switchConversation}
        />
      </SidebarContent>
    </Sidebar>
  )
}
