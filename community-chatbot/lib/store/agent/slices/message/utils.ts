import type { StoreApi } from 'zustand';

import { updateConversation } from '@/lib/firestore';
import { authSlice } from '@/lib/store/agent/slices/authSlice';
import { conversationSlice } from '@/lib/store/agent/slices/conversationSlice';
import { messageSlice } from '@/lib/store/agent/slices/messageSlice';
import { Message } from '@/types/chat/types';

type MessageStore = messageSlice & conversationSlice & authSlice;

// Generates a title for a new chat based on the first message.
export const generateChatTitle = (firstMessage: string): string => {
    const words = firstMessage.split(" ").slice(0, 6).join(" ");
    return words.length > 40 ? words.substring(0, 40) + "..." : words;
};

// Performs an optimistic update by adding the user's message to the state immediately.
export const performStateUpdate = (
    set: StoreApi<MessageStore>['setState'],
    userMessage: Message,
    chatId: string,
    newTitle: string  | false
) => {
    set((state) => {
        const updatedMessages = [...state.messages, userMessage];
        const updatedChats = state.chats
            .map(c =>
                c.id === chatId
                    ? { ...c, messages: updatedMessages, updatedAt: new Date(), ...(newTitle && { title: newTitle }) }
                    : c
            )
            .sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime());

        return { messages: updatedMessages, input: "", status: "submitted", chats: updatedChats };
    });
};


// Handles the streaming response from the API, updating the state as data arrives.
export const handleStreamingResponse = async (
    response: Response,
    set: StoreApi<MessageStore>['setState']
) => {
    if (!response.body) throw new Error("No response body from API.");

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let assistantResponse = "";
    const assistantMessageId = crypto.randomUUID();

    // Add a placeholder for the assistant's message
    set(state => ({
        status: "streaming",
        messages: [...state.messages, {
            id: assistantMessageId,
            role: "assistant",
            content: "",
            timestamp: Date.now()
        }]
    }));

    // Process the stream
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        assistantResponse += decoder.decode(value, { stream: true });

        set(state => ({
            messages: state.messages.map(msg =>
                msg.id === assistantMessageId ? { ...msg, content: assistantResponse } : msg
            )
        }));
    }
};


// Finalises the conversation by updating the state and persisting the data to Firestore.
export const finaliseConversation = async (
    set: StoreApi<MessageStore>['setState'],
    get: StoreApi<MessageStore>['getState'],
    chatId: string,
    newTitle: string | false
) => {
    const finalMessages = get().messages;
    const finalDate = new Date();
    const currentUser = get().currentUser;

    set(state => ({
        status: "ready",
        abortController: null,
        chats: state.chats
            .map(c =>
                c.id === chatId
                    ? { ...c, messages: finalMessages, updatedAt: finalDate, ...(newTitle && { title: newTitle }) }
                    : c
            )
            .sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime()),
    }));

    if (!currentUser) {
        console.error("User not authenticated for final update.");
        return;
    }

    await updateConversation(chatId, currentUser.uid, {
        messages: finalMessages,
        updatedAt: finalDate,
        ...(newTitle && { title: newTitle }),
    });
};

// Handles errors that occur during message sending, including user-initiated aborts.
export const handleSendError = async (
    err: any,
    set: StoreApi<MessageStore>['setState'],
    get: StoreApi<MessageStore>['getState'],
    chatId: string,
    newTitle: string | false
) => {
    if (err.name === 'AbortError') {
        console.log('Streaming stopped by user.');
        // Still finalise to save the partial response
        await finaliseConversation(set, get, chatId, newTitle);
    } else {
        console.error(`Error sending message:`, err);
        set({ status: "error", abortController: null });
        throw err;
    }
};
