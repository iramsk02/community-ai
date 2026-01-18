import { BACKEND_SERVICES, SYSTEM_PROMPTS } from '@/app/api/chat/lib/constants';
import { callBackendService, ServiceError } from '@/app/api/chat/lib/services';
import {
  createAiStream, createErrorStream,
} from '@/app/api/chat/lib/streaming';

export async function handleGitHubRequest(message: string): Promise<Response> {
    try {
        const serviceResponse = await callBackendService(
            `${BACKEND_SERVICES.github}/chat`,
            { message: message, session_id: "frontend-session" },
            "GitHub"
        );

        const userPrompt = `Based on the GitHub query "${message}", here's the information: ${serviceResponse}`;
        return createAiStream(SYSTEM_PROMPTS.github, userPrompt);

    } catch (error) {
        console.error("GitHub integration error:", error);
        if (error instanceof ServiceError) {
            return createErrorStream(error.message);
        }
        // Re-throw other errors to be caught by the main API route handler
        throw error;
    }
}
