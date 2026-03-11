import { StateCreator } from 'zustand';

import { authSlice } from '@/lib/store/agent/slices/authSlice';
import { conversationSlice } from '@/lib/store/agent/slices/conversationSlice';
import { Message } from '@/types/chat/types';

import {
  finaliseConversation, generateChatTitle, handleSendError,
  handleStreamingResponse, performStateUpdate,
} from './message/utils';

// Define a type for the combined store
type MessageStore = messageSlice & conversationSlice & authSlice;
export interface messageSlice {
  messages: Message[];
  input: string;
  status: "ready" | "loading" | "submitted" | "streaming" | "error";
  abortController: AbortController | null;

  setInput: (input: string) => void;
  sendMessage: (chatId: string, mode: string, text: string) => Promise<void>;
  fetchMessages: (chatId: string) => Promise<void>;
  handleQuickAction: (action: string, chatId: string, mode: string) => void;
  stopStreaming: () => void;
}

export const createMessageSlice: StateCreator<
  MessageStore,
  [],
  [],
  messageSlice
> = (set, get) => ({
  input: "",
  messages: [],
  status: "ready",
  abortController: null,

  setInput: (input) => set({ input }),

  fetchMessages: async (chatId) => {
    set({ status: 'loading', messages: [] });
    try {
      const chat = get().chats.find(c => c.id === chatId);
      if (!chat) throw new Error("No messages found for this conversation.");
      set({ messages: chat.messages || [], status: 'ready' });
    } catch (err) {
      console.error("Failed to fetch messages:", err);
      set({ status: 'error', messages: [] });
      throw err;
    }
  },

  sendMessage: async (chatId, mode, text) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      timestamp: Date.now(),
    };

    const title =
      get().messages.length === 0 &&
      generateChatTitle(userMessage.content);

    performStateUpdate(set, userMessage, chatId, title);

    const controller = new AbortController();
    set({ abortController: controller });

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [userMessage],
          mode
        }),
        signal: controller.signal,
      });

      await handleStreamingResponse(response, set);
      await finaliseConversation(set, get, chatId, title);

    } catch (err: any) {
      await handleSendError(err, set, get, chatId, title);
      throw err;
    }
  },

  handleQuickAction: (action, chatId, mode) => {
    get().sendMessage(chatId, mode, action);
  },

  stopStreaming: () => {
    get().abortController?.abort();
  },
});