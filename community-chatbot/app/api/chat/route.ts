import { handleGeneralRequest } from '@/app/api/chat/handlers/general';
import { handleGitHubRequest } from '@/app/api/chat/handlers/github';
import { handleJiraRequest } from '@/app/api/chat/handlers/jira';
import { handleSlackRequest } from '@/app/api/chat/handlers/slack';
import { maxDuration } from '@/app/api/chat/lib/constants';
import { Message } from '@/types/chat/types';

export { maxDuration };

interface ChatRequest {
  messages: Message[];
  mode: string;
}

export async function POST(req: Request) {
  try {
    const body = await req.json();

    // Validate body structure
    if (typeof body !== 'object' || body === null) {
      return new Response(
        JSON.stringify({ error: "Invalid request body format." }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const { messages, mode } = body;

    if (!Array.isArray(messages)) {
      return new Response(
        JSON.stringify({ error: "Request must contain a 'messages' array." }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    if (typeof mode !== 'string') {
      return new Response(
        JSON.stringify({ error: "Request must contain a 'mode' string." }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    // Existing validation for messages array length
    if (messages.length === 0) {
      return new Response(
        JSON.stringify({
          error: "Request must contain a non-empty messages array."
        }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    // Validate each message in the array to ensure it conforms to the Message type
    for (const msg of messages) {
      if (typeof msg !== 'object' || msg === null ||
        typeof msg.id !== 'string' ||
        !['user', 'assistant', 'system'].includes(msg.role) ||
        typeof msg.content !== 'string' ||
        typeof msg.timestamp !== 'number') {
        return new Response(
          JSON.stringify({ error: "Invalid message format in 'messages' array." }),
          { status: 400, headers: { "Content-Type": "application/json" } }
        );
      }
    }

    const lastMessage = messages[messages.length - 1];
    if (!lastMessage || lastMessage.role !== "user") {
      return new Response(
        JSON.stringify({
          error: "Invalid message sequence. The last message must be from a user.",
        }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    // Now we can safely cast to ChatRequest
    const chatRequest: ChatRequest = { messages, mode };

    try {
      switch (chatRequest.mode) {
        case "slack":
          return await handleSlackRequest(lastMessage.content);
        case "jira":
          return await handleJiraRequest(lastMessage.content);
        case "github":
          return await handleGitHubRequest(lastMessage.content);
        default:
          return await handleGeneralRequest(chatRequest.messages);
      }
    } catch (integrationError) {
      console.error(`${chatRequest.mode} integration error:`, integrationError);
      const fallbackUserMessage = {
        id: "fallback",
        role: "user" as const,
        content: `I was trying to use the ${chatRequest.mode} integration but it seems to be unavailable. Can you help me with: ${lastMessage.content}`,
        timestamp: Date.now(),
      };
      return await handleGeneralRequest([fallbackUserMessage]);
    }
  } catch (error) {
    console.error("Chat API error:", error);
    return new Response(
      JSON.stringify({
        error: "An unexpected server error occurred while processing your request. Please try again shortly.",
      }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
