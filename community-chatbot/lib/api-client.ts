// API client utilities for backend services
export class BackendAPIClient {
  private baseUrls = {
    slack: process.env.NEXT_PUBLIC_FASTAPI_URL || "http://localhost:8000",
    jira: "http://localhost:8001",
    github: "http://localhost:8003",
  }

  async checkServiceHealth(service: keyof typeof this.baseUrls): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrls[service]}/health`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      })
      return response.ok
    } catch (error) {
      console.error(`Health check failed for ${service}:`, error)
      return false
    }
  }

  async sendSlackMessage(message: string, conversationId = "default") {
    const response = await fetch(`${this.baseUrls.slack}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    })

    if (!response.ok) {
      throw new Error(`Slack API error: ${response.status}`)
    }

    return response.json()
  }

  async sendJiraQuery(query: string, useFallback = true) {
    const response = await fetch(`${this.baseUrls.jira}/jira/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query,
        use_fallback: useFallback,
      }),
    })

    if (!response.ok) {
      throw new Error(`Jira API error: ${response.status}`)
    }

    return response.json()
  }

  async sendGitHubMessage(message: string, sessionId = "default") {
    const response = await fetch(`${this.baseUrls.github}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    })

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.status}`)
    }

    return response.json()
  }
}

export const apiClient = new BackendAPIClient()
