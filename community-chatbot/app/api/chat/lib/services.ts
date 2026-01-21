import { maxDuration } from '@/app/api/chat/lib/constants';

// A custom error class for service-related failures
export class ServiceError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'ServiceError';
    }
}

export async function callBackendService(
    serviceUrl: string,
    requestBody: object,
    serviceName: string
): Promise<string> {
    const controller = new AbortController();
    // 120-second timeout
    const timeoutId = setTimeout(() => controller.abort(), 1000 * maxDuration);

    try {
        const response = await fetch(serviceUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestBody),
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new ServiceError(`${serviceName} API error: ${response.status} - ${response.statusText}`);
        }

        const data = await response.json();

        if (!data || typeof data.response !== 'string') {
            throw new ServiceError(`Invalid response format from ${serviceName} service`);
        }

        return data.response;
    } catch (error) {
        clearTimeout(timeoutId);
        if (error instanceof Error && error.name === 'AbortError') {
            throw new ServiceError(`The ${serviceName} service is taking too long to respond. Please try again.`);
        }
        // Re-throw other errors to be caught by the handler
        throw error;
    }
}
