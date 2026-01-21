import { ModelMessage, streamText } from 'ai';

import { openai } from '@ai-sdk/openai';

// Creates a streaming text response from the AI.
export function createAiStream(systemPrompt: string, userPrompt: string): Response {
    const messages: ModelMessage[] = [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt },
    ];

    const result = streamText({
        model: openai("gpt-4o"),
        messages,
    });

    return new Response(result.textStream, {
        headers: {
            'Content-Type': 'text/plain; charset=utf-8',
            'Transfer-Encoding': 'chunked',
        },
    });
}

// Creates a streaming error message response from the AI.
export function createErrorStream(errorMessage: string): Response {
    const result = streamText({
        model: openai("gpt-4o"),
        messages: [
            {
                role: "system",
                content: "You are a helpful assistant explaining a service connection issue. Be empathetic and provide actionable advice.",
            },
            {
                role: "user",
                content: `${errorMessage} You can try again later or switch to the General Assistant mode for other questions.`,
            },
        ],
    });

    return new Response(result.textStream, {
        headers: {
            'Content-Type': 'text/plain; charset=utf-8',
            'Transfer-Encoding': 'chunked',
        },
    });
}
