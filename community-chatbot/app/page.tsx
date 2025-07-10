"use client"
import type React from "react"
import { useChat } from "@ai-sdk/react"
import { useEffect, useRef, useState } from "react"
import { Sidebar } from "@/components/chatbot/Sidebar"
import { ChatHeader } from "@/components/chatbot/ChatHeader"
import { ModeSelector } from "@/components/chatbot/ModeSelector"
import { ChatPanel } from "@/components/chatbot/ChatPanel"
import { MessageInput } from "@/components/chatbot/MessageInput"
import type { ChatHistoryItem, IntegrationMode } from "@/components/chatbot/types"
// Integration modes configuration
const integrationModes: IntegrationMode[] = [
  {
    id: "general",
    name: "General Assistant",
    icon: "🤖",
    image: "/mifos.png",
    color: "bg-blue-600 hover:bg-blue-700 text-white",
    description: "Ask about features, documentation, or community",
    systemPrompt:
      "You are a helpful Mifos Community assistant. Help with general questions about Mifos features, documentation, and community support.",
  },
  {
    id: "slack",
    name: "Slack Assistant",
    icon: "💬",
    image: "/slack.png",
    color: "bg-purple-600 hover:bg-purple-700 text-white",
    description: "Get channel info, user details, or search messages",
    systemPrompt:
      "You are a Slack integration assistant. Help users with Slack channel management, user queries, message searches, and workspace administration.",
    useCustomBackend: true,
  },
  {
    id: "jira",
    name: "Jira Assistant",
    icon: "🔷",
    image: "/jira.svg",
    color: "bg-blue-500 hover:bg-blue-600 text-white",
    description: "Check ticket status, create issues, or view reports",
    systemPrompt:
      "You are a Jira integration assistant. Help users with ticket management, issue creation, project tracking, and generating reports.",
  },
  {
    id: "github",
    name: "GitHub Assistant",
    icon: "🐙",
    image: "/github.png",
    color: "bg-purple-600 hover:bg-purple-700 text-white",
    description: "Review PRs, check issues, or get repo info",
    systemPrompt:
      "You are a GitHub integration assistant. Help users with pull request reviews, issue tracking, repository management, and code collaboration.",
  },
]


const quickActions = [
 "How to create new client?",
 "API documentation",
 "Troubleshoot reporting",
 "Mobile banking setup",
]


export default function ChatbotPage() {
 const [selectedMode, setSelectedMode] = useState("general")
 const [sidebarOpen, setSidebarOpen] = useState(false)
  /**
  * Chat History Management:
  * - Each assistant mode has its own separate chat history
  * - Conversations are identified by mode-specific IDs (e.g., "general-1", "slack-1")
  * - This prevents chat history mixing between different assistants
  */
 // Initialize chat history with separate conversations for each mode
 const [chatHistory, setChatHistory] = useState<ChatHistoryItem[]>([
  {
    id: "general-1",
    title: "General Questions",
    date: "Today",
    icon: "/mifos.png",
    messages: [],
    mode: "general",
    active: true,
  },
  {
    id: "slack-1",
    title: "Slack Assistant",
    date: "Today",
    icon: "/slack.png",
    messages: [],
    mode: "slack",
    active: false,
  },
  {
    id: "jira-1",
    title: "Jira Assistant",
    date: "Today",
    icon: "/jira.svg",
    messages: [],
    mode: "jira",
    active: false,
  },
  {
    id: "github-1",
    title: "GitHub Assistant",
    date: "Today",
    icon: "/github.png",
    messages: [],
    mode: "github",
    active: false,
  },
])
  // Track active conversation per mode
 const [activeConversationIds, setActiveConversationIds] = useState<Record<string, string>>({
   general: "general-1",
   slack: "slack-1",
   jira: "jira-1",
   github: "github-1",
 })
  const [isCreatingNewChat, setIsCreatingNewChat] = useState(false)
  // Get current active conversation ID for the selected mode
 const activeConversationId = activeConversationIds[selectedMode]
  /**
  * Per-Assistant State Management:
  * Each assistant (General, Slack, Jira, GitHub) has its own independent state for:
  * - messages: Chat history specific to that assistant
  * - input: Current input text for that assistant
  * - status: Current status (ready, submitted, streaming, error)
  * - error: Error state specific to that assistant
  *
  * This prevents chat history mixing and message loss when switching between assistants.
  */
  // General Assistant state
 const [generalMessages, setGeneralMessages] = useState<any[]>([])
 const [generalInput, setGeneralInput] = useState("")
 const [generalStatus, setGeneralStatus] = useState<"ready" | "submitted" | "streaming" | "error">("ready")
 const [generalError, setGeneralError] = useState<Error | undefined>(undefined)


 // Slack Assistant state
 const [slackMessages, setSlackMessages] = useState<any[]>([])
 const [slackInput, setSlackInput] = useState("")
 const [slackStatus, setSlackStatus] = useState<"ready" | "submitted" | "streaming" | "error">("ready")
 const [slackError, setSlackError] = useState<Error | undefined>(undefined)


 // Jira Assistant state
 const [jiraMessages, setJiraMessages] = useState<any[]>([])
 const [jiraInput, setJiraInput] = useState("")
 const [jiraStatus, setJiraStatus] = useState<"ready" | "submitted" | "streaming" | "error">("ready")
 const [jiraError, setJiraError] = useState<Error | undefined>(undefined)


 // GitHub Assistant state
 const [githubMessages, setGithubMessages] = useState<any[]>([])
 const [githubInput, setGithubInput] = useState("")
 const [githubStatus, setGithubStatus] = useState<"ready" | "submitted" | "streaming" | "error">("ready")
 const [githubError, setGithubError] = useState<Error | undefined>(undefined)


 // Get current mode before useChat
 const currentModeConfig = integrationModes.find((mode) => mode.id === selectedMode)


 // General Assistant useChat hook
 const generalChatHook = useChat({
   api: "/api/chat",
   body: {
     mode: "general",
     conversationId: activeConversationIds.general,
   },
   onFinish: (message) => {
     const updatedMessages = [...generalMessages, message]
     setGeneralMessages(updatedMessages)
     saveChatToHistory(activeConversationIds.general, updatedMessages)
   },
 })




 // Jira Assistant useChat hook 
 const jiraChatHook = useChat({
   api: "/api/chat",
   body: {
     mode: "jira",
     conversationId: activeConversationIds.jira,
   },
   onFinish: () => {
     console.log("Jira onFinish - messages:", jiraChatHook.messages)
     saveChatToHistory(activeConversationIds.jira, jiraChatHook.messages)
   },
 })


 // GitHub Assistant useChat hook
 const githubChatHook = useChat({
   api: "/api/chat",
   body: {
     mode: "github",
     conversationId: activeConversationIds.github,
   },
   onFinish: () => {
     console.log("GitHub onFinish - messages:", githubChatHook.messages)
     saveChatToHistory(activeConversationIds.github, githubChatHook.messages)
   },
 })


 // Effect for syncing conversation history with per-assistant state
 useEffect(() => {
   const currentChat = chatHistory.find(chat => chat.id === activeConversationId);
   if (currentChat) {
     switch (selectedMode) {
       case "general":
         setGeneralMessages(currentChat.messages || []);
         break;
       case "slack":
         setSlackMessages(currentChat.messages || []);
         break;
     }
   }
 }, [selectedMode, activeConversationId, chatHistory])


 // Handler for General Assistant submission
const handleGeneralSubmit = async (event?: { preventDefault?: () => void }) => {
 if (event?.preventDefault) event.preventDefault()


 if (!generalInput.trim()) return


 // Add user message to UI
 const userMessage = {
   id: crypto.randomUUID(),
   role: "user",
   content: generalInput,
 }


 setGeneralMessages((prev) => [...prev, userMessage])
   setGeneralInput("")
   setGeneralStatus("submitted")


   try {
     const response = await fetch("http://localhost:8000/chat", {
       method: "POST",
       headers: {
         "Content-Type": "application/json",
       },
       body: JSON.stringify({
         message: userMessage.content,
         conversation_id: activeConversationId,
       }),
     })


     if (!response.ok) {
       throw new Error(`HTTP error! status: ${response.status}`)
     }


     const data = await response.json()


     const assistantMessage = {
       id: crypto.randomUUID(),
       role: "assistant",
       content: data.response,
     }


     setGeneralMessages((prev) => {
       const updated = [...prev, assistantMessage]
       saveChatToHistory(activeConversationId, updated)
       return updated
     })
     setGeneralStatus("ready")
 } catch (error) {
   console.error("Error sending General message:", error)
   setGeneralError(error instanceof Error ? error : new Error(String(error)))
   setGeneralStatus("error")
 }
}




 // Handler for Jira Assistant submission 
 const handleJiraSubmit = (event?: { preventDefault?: () => void }) => {
   if (event?.preventDefault) event.preventDefault()
   if (!jiraChatHook.input.trim()) return
   jiraChatHook.handleSubmit(event)
 }


 // Handler for GitHub Assistant submission
 const handleGithubSubmit = (event?: { preventDefault?: () => void }) => {
   if (event?.preventDefault) event.preventDefault()
   if (!githubChatHook.input.trim()) return
   githubChatHook.handleSubmit(event)
 }
 const handleSlackSubmit = async (event?: { preventDefault?: () => void } | undefined) => {
   if (event?.preventDefault) event.preventDefault()
  
   if (!slackInput.trim()) return   
   // Add user message to UI
   const userMessage = {
     id: crypto.randomUUID(),
     role: "user",
     content: slackInput,
   }
  
   setSlackMessages((prev) => [...prev, userMessage])
   setSlackInput("")
   setSlackStatus("submitted")
  
   try {
     // Call the backend
     const response = await fetch("http://localhost:8000/chat", {
       method: "POST",
       headers: {
         "Content-Type": "application/json",
       },
       body: JSON.stringify({
         message: userMessage.content,
         conversation_id: activeConversationId,
       }),
     })
    
     if (!response.ok) {
       throw new Error(`HTTP error! status: ${response.status}`)
     }
    
     const data = await response.json()
    
     // Add assistant response to UI
     const assistantMessage = {
       id: crypto.randomUUID(),
       role: "assistant",
       content: data.response,
     }
    
     setSlackMessages((prev) => {
       const updated = [...prev, assistantMessage]
       saveChatToHistory(activeConversationId, updated)
       return updated
     })
     setSlackStatus("ready")
   } catch (error) {
     console.error("Error sending Slack message:", error)
     setSlackError(error instanceof Error ? error : new Error(String(error)))
     setSlackStatus("error")
   }
 }


 // Get current assistant state based on selected mode
 const getCurrentAssistantState = () => {
   switch (selectedMode) {
     case "general":
return {
 messages: generalMessages,
 input: generalInput,
 handleInputChange: (e: any) => setGeneralInput(e.target.value),
 handleSubmit: handleGeneralSubmit,
 status: generalStatus,
 stop: () => {},
 error: generalError,
 reload: () => {
   setGeneralError(undefined);
   setGeneralStatus("ready");
 },
 setMessages: setGeneralMessages,
}
     case "slack":
       return {
         messages: slackMessages,
         input: slackInput,
         handleInputChange: (e: any) => setSlackInput(e.target.value),
         handleSubmit: handleSlackSubmit,
         status: slackStatus,
         stop: () => {}, // No streaming for Slack
         error: slackError,
         reload: () => { setSlackError(undefined); setSlackStatus("ready"); },
         setMessages: setSlackMessages,
       }
     case "jira":
       return {
         messages: jiraChatHook.messages,
         input: jiraChatHook.input,
         handleInputChange: jiraChatHook.handleInputChange,
         handleSubmit: handleJiraSubmit,
         status: jiraChatHook.status,
         stop: jiraChatHook.stop,
         error: jiraChatHook.error,
         reload: jiraChatHook.reload,
         setMessages: jiraChatHook.setMessages,
       }
     case "github":
       return {
         messages: githubChatHook.messages,
         input: githubChatHook.input,
         handleInputChange: githubChatHook.handleInputChange,
         handleSubmit: handleGithubSubmit,
         status: githubChatHook.status,
         stop: githubChatHook.stop,
         error: githubChatHook.error,
         reload: githubChatHook.reload,
         setMessages: githubChatHook.setMessages,
       }
     default:
return {
 messages: generalMessages,
 input: generalInput,
 handleInputChange: (e: any) => setGeneralInput(e.target.value),
 handleSubmit: handleGeneralSubmit,
 status: generalStatus,
 stop: () => {},
 error: generalError,
 reload: () => {
   setGeneralError(undefined);
   setGeneralStatus("ready");
 },
 setMessages: setGeneralMessages,
}
   }
 }


 // Get current assistant state
 const { messages, input, handleInputChange, handleSubmit, status, stop, error, reload, setMessages } = getCurrentAssistantState()


 const scrollAreaRef = useRef<HTMLDivElement>(null)


 const saveChatToHistory = (conversationId: string, updatedMessages: any[]) => {
   setChatHistory((prev) =>
     prev.map((chat) =>
       chat.id === conversationId
         ? {
             ...chat,
             messages: updatedMessages,
             title: updatedMessages.length > 0 ? generateChatTitle(updatedMessages[0].content) : chat.title,
           }
         : chat,
     ),
   )
 }


 const generateChatTitle = (firstMessage: string) => {
   const words = firstMessage.split(" ").slice(0, 4).join(" ")
   return words.length > 30 ? words.substring(0, 30) + "..." : words
 }


 const createNewConversation = async () => {
   setIsCreatingNewChat(true)
   const newId = Date.now().toString()
   const currentMode = integrationModes.find((mode) => mode.id === selectedMode)


   const newChat: ChatHistoryItem = {
     id: newId,
     title: `New ${currentMode?.name || "Chat"}`,
     date: "Now",
     icon: currentMode?.image || "/mifos.png",
     messages: [],
     mode: selectedMode,
   }


   setChatHistory((prev) => [newChat, ...prev.map((chat) => ({ ...chat, active: false }))])


   // Update the active conversation ID for the current mode
   setActiveConversationIds(prev => ({
     ...prev,
     [selectedMode]: newId
   }))


   // Clear the current assistant's messages
   switch (selectedMode) {
     case "general":
       setGeneralMessages([])
       break;
     case "slack":
       setSlackMessages([])
       break;
     case "jira":
       jiraChatHook.setMessages([])
       break;
     case "github":
       githubChatHook.setMessages([])
       break;
   }


   setIsCreatingNewChat(false)
   setSidebarOpen(false)
 }


 const switchConversation = (conversationId: string) => {
   const conversation = chatHistory.find((chat) => chat.id === conversationId)
   if (conversation) {
     // Update active conversation for the conversation's mode
     setActiveConversationIds(prev => ({
       ...prev,
       [conversation.mode]: conversationId
     }))
    
     // Update the corresponding assistant's messages
     switch (conversation.mode) {
       case "general":
         setGeneralMessages(conversation.messages)
         break;
       case "slack":
         setSlackMessages(conversation.messages)
         break;
     }
    
     setSelectedMode(conversation.mode)
     setChatHistory((prev) =>
       prev.map((chat) => ({
         ...chat,
         active: chat.id === conversationId,
       })),
     )
     setSidebarOpen(false)
   }
 }


 const deleteConversation = (conversationId: string, e: React.MouseEvent) => {
   e.stopPropagation()
  
   const conversationToDelete = chatHistory.find(chat => chat.id === conversationId)
   if (!conversationToDelete) return
  
   // Don't allow deletion of the last conversation for a mode
   const conversationsForMode = chatHistory.filter(chat => chat.mode === conversationToDelete.mode)
   if (conversationsForMode.length <= 1) return


   setChatHistory((prev) => prev.filter((chat) => chat.id !== conversationId))


   // If we're deleting the active conversation for this mode, switch to another one
   if (activeConversationIds[conversationToDelete.mode] === conversationId) {
     const remainingChatsForMode = chatHistory.filter((chat) =>
       chat.id !== conversationId && chat.mode === conversationToDelete.mode
     )
     if (remainingChatsForMode.length > 0) {
       setActiveConversationIds(prev => ({
         ...prev,
         [conversationToDelete.mode]: remainingChatsForMode[0].id
       }))
       // Only switch conversation if we're currently in that mode
       if (selectedMode === conversationToDelete.mode) {
         switchConversation(remainingChatsForMode[0].id)
       }
     }
   }
 }


 const handleModeChange = (modeId: string) => {
   setSelectedMode(modeId)
  
   // Switch to the active conversation for the new mode
   const activeConvId = activeConversationIds[modeId]
   const activeConversation = chatHistory.find(chat => chat.id === activeConvId)
  
   if (activeConversation) {
     // Update chat history to mark the new active conversation
     setChatHistory((prev) =>
       prev.map((chat) => ({
         ...chat,
         active: chat.id === activeConvId,
       }))
     )
    
     // Update per-assistant state for the new mode
     switch (modeId) {
       case "general":
         setGeneralMessages(activeConversation.messages || [])
         break;
       case "slack":
         setSlackMessages(activeConversation.messages || [])
         break;
     }
   }
 }


 const handleQuickAction = (action: string) => {
   // Set the input for the current assistant
   switch (selectedMode) {
     case "general":
       setGeneralInput(action)
       break;
     case "slack":
       setSlackInput(action)
       break;
     case "jira":
       jiraChatHook.handleInputChange({ target: { value: action } } as any)
       break;
     case "github":
       githubChatHook.handleInputChange({ target: { value: action } } as any)
       break;
   }
  
   setTimeout(() => {
     const form = document.querySelector("form")
     if (form) {
       form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }))
     }
   }, 100)
 }


 const currentMode = integrationModes.find((mode) => mode.id === selectedMode)


 return (
   <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
     <Sidebar
       sidebarOpen={sidebarOpen}
       setSidebarOpen={setSidebarOpen}
       chatHistory={chatHistory}
       isCreatingNewChat={isCreatingNewChat}
       createNewConversation={createNewConversation}
       switchConversation={switchConversation}
       deleteConversation={deleteConversation}
       integrationModes={integrationModes}
       currentMode={selectedMode}
     />
     <div className="flex-1 flex flex-col min-h-0">
       <ChatHeader
         currentMode={currentMode}
         isCreatingNewChat={isCreatingNewChat}
         setSidebarOpen={setSidebarOpen}
         createNewConversation={createNewConversation}
       />
       <ModeSelector
         integrationModes={integrationModes}
         selectedMode={selectedMode}
         handleModeChange={handleModeChange}
       />
       <ChatPanel
         key={`${selectedMode}-${activeConversationId}`}
         messages={messages}
         status={status}
         error={error}
         reload={reload}
         scrollAreaRef={scrollAreaRef}
         currentMode={currentMode}
         quickActions={quickActions}
         handleQuickAction={handleQuickAction}
         integrationModes={integrationModes}
       />
       <MessageInput
         input={input}
         handleInputChange={handleInputChange}
         handleSubmit={handleSubmit}
         status={status}
         stop={stop}
         currentModeName={currentMode?.name}
       />
     </div>
   </div>
 )
}



