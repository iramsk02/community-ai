import { BACKEND_SERVICES, SYSTEM_PROMPTS } from '@/app/api/chat/lib/constants';
import { callBackendService, ServiceError } from '@/app/api/chat/lib/services';
import {
  createAiStream, createErrorStream,
} from '@/app/api/chat/lib/streaming';

export async function handleJiraRequest(message: string): Promise<Response> {
    try {
        const serviceResponse = await callBackendService(
            `${BACKEND_SERVICES.jira}/jira/query`,
            { query: message, use_fallback: true },
            "Jira"
        );

        const userPrompt = `Based on the Jira query "${message}", here's what I found: ${serviceResponse}`;
        return createAiStream(SYSTEM_PROMPTS.jira, userPrompt);

    } catch (error) {
        console.error("Jira integration error:", error);
        if (error instanceof ServiceError) {
            return createErrorStream(error.message);
        }
        // Re-throw other errors to be caught by the main API route handler
        throw error;
    }
}
