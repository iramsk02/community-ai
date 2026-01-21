import { BACKEND_SERVICES, SYSTEM_PROMPTS } from '@/app/api/chat/lib/constants';
import { callBackendService, ServiceError } from '@/app/api/chat/lib/services';
import {
  createAiStream, createErrorStream,
} from '@/app/api/chat/lib/streaming';

export async function handleSlackRequest(message: string): Promise<Response> {
    try {
        const serviceResponse = await callBackendService(
            `${BACKEND_SERVICES.slack}/chat`,
            {
                message: message,
                conversation_id: "frontend-session"
            },
            "Slack"
        );

        const userPrompt = `Based on the Slack query "${message}", here's the information I found: ${serviceResponse}`;
        return createAiStream(SYSTEM_PROMPTS.slack, userPrompt);

    } catch (error) {
        console.error("Slack integration error:", error);
        if (error instanceof ServiceError) {
            return createErrorStream(error.message);
        }
        // Re-throw other errors to be caught by the main API route handler
        throw error;
    }
}
