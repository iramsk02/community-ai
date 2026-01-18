import { streamText } from 'ai';

import { SYSTEM_PROMPTS } from '@/app/api/chat/lib/constants';
import { Message } from '@/types/chat/types';
import { openai } from '@ai-sdk/openai';

export async function handleGeneralRequest(messages: Message[]): Promise<Response> {
    try {
        const result = streamText({
            model: openai("gpt-4o"),
            system: SYSTEM_PROMPTS.general,
            messages: messages.map(msg => ({
                role: msg.role,
                content: msg.content
            })),
        });

        return new Response(result.textStream, {
            headers: {
                'Content-Type': 'text/plain; charset=utf-8',
                'Transfer-Encoding': 'chunked',
            },
        });
    } catch (error) {
        console.error("General request error:", error);
        throw error;
    }
}
