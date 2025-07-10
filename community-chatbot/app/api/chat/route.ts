import { streamText } from "ai"
import { openai } from "@ai-sdk/openai"

// Allow streaming responses up to 30 seconds
export const maxDuration = 30

// Backend service URLs - update these to match your deployment
const BACKEND_SERVICES = {
  slack: process.env.NEXT_PUBLIC_FASTAPI_URL || "http://localhost:8000",
  jira: "http://localhost:8001",
  github: "http://localhost:8003",
}

interface ChatRequest {
  messages: Array<{
    id: string
    role: "user" | "assistant"
    content: string
  }>
  mode?: string
}

export async function POST(req: Request) {
  try {
    const { messages, mode = "general" }: ChatRequest = await req.json()

    // Get the latest user message
    const lastMessage = messages[messages.length - 1]

    if (!lastMessage || lastMessage.role !== "user") {
      return new Response("Invalid message format", { status: 400 })
    }

    // Handle different integration modes
    switch (mode) {
      case "slack":
        return await handleSlackRequest(lastMessage.content, messages)

      case "jira":
        return await handleJiraRequest(lastMessage.content, messages)

      case "github":
        return await handleGitHubRequest(lastMessage.content, messages)

      default:
        return await handleGeneralRequest(messages)
    }
  } catch (error) {
    console.error("Chat API error:", error)
    return new Response("Internal Server Error", { status: 500 })
  }
}

async function handleSlackRequest(message: string, messages: any[]) {
  try {
    const response = await fetch(`${BACKEND_SERVICES.slack}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: message,
        conversation_id: "frontend-session",
      }),
    })

    if (!response.ok) {
      throw new Error(`Slack API error: ${response.status}`)
    }

    const data = await response.json()

    // Return a streaming response with the Slack agent's response
    return streamText({
      model: openai("gpt-4o"),
      messages: [
        {
          role: "system",
          content: "You are relaying a response from a Slack assistant. Present the information clearly and helpfully.",
        },
        {
          role: "user",
          content: `The Slack assistant responded: ${data.response}`,
        },
      ],
    }).toDataStreamResponse()
  } catch (error) {
    console.error("Slack integration error:", error)
    return streamText({
      model: openai("gpt-4o"),
      messages: [
        {
          role: "system",
          content: "You are a helpful assistant explaining that there's a connection issue.",
        },
        {
          role: "user",
          content: `There was an error connecting to the Slack service: ${error}. Please try again later or contact support.`,
        },
      ],
    }).toDataStreamResponse()
  }
}

async function handleJiraRequest(message: string, messages: any[]) {
  try {
    const response = await fetch(`${BACKEND_SERVICES.jira}/jira/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: message,
        use_fallback: true,
      }),
    })

    if (!response.ok) {
      throw new Error(`Jira API error: ${response.status}`)
    }

    const data = await response.json()

    return streamText({
      model: openai("gpt-4o"),
      messages: [
        {
          role: "system",
          content: "You are relaying a response from a Jira assistant. Present the information clearly and helpfully.",
        },
        {
          role: "user",
          content: `The Jira assistant responded: ${data.response}`,
        },
      ],
    }).toDataStreamResponse()
  } catch (error) {
    console.error("Jira integration error:", error)
    return streamText({
      model: openai("gpt-4o"),
      messages: [
        {
          role: "system",
          content: "You are a helpful assistant explaining service availability.",
        },
        {
          role: "user",
          content:
            "The Jira integration service is currently unavailable. Please ensure the Jira backend is running on port 8001 or contact your administrator.",
        },
      ],
    }).toDataStreamResponse()
  }
}

async function handleGitHubRequest(message: string, messages: any[]) {
  try {
    const response = await fetch(`${BACKEND_SERVICES.github}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: message,
        session_id: "frontend-session",
      }),
    })

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.status}`)
    }

    const data = await response.json()

    return streamText({
      model: openai("gpt-4o"),
      messages: [
        {
          role: "system",
          content:
            "You are relaying a response from a GitHub assistant. Present the information clearly and helpfully.",
        },
        {
          role: "user",
          content: `The GitHub assistant responded: ${data.response}`,
        },
      ],
    }).toDataStreamResponse()
  } catch (error) {
    console.error("GitHub integration error:", error)
    return streamText({
      model: openai("gpt-4o"),
      messages: [
        {
          role: "system",
          content: "You are a helpful assistant explaining service availability.",
        },
        {
          role: "user",
          content:
            "The GitHub integration service is currently unavailable. Please ensure the GitHub backend is running on port 8003 or contact your administrator.",
        },
      ],
    }).toDataStreamResponse()
  }
}

async function handleGeneralRequest(messages: any[]) {
  return streamText({
    model: openai("gpt-4o"),
    system: `You are a helpful Mifos Community assistant. You can help with general questions about Mifos features, documentation, and community support. 
    
    You can also guide users to use the specialized assistants:
    - Slack Assistant: For Slack channel management, user details, and message searches
    - Jira Assistant: For ticket status, issue creation, and project reports  
    - GitHub Assistant: For PR reviews, issue tracking, and repository management
    
    If a user asks about Slack, Jira, or GitHub specific tasks, suggest they use the appropriate specialized assistant mode.`,
    messages,
  }).toDataStreamResponse()
}
