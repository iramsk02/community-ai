import { usePathname } from 'next/navigation';

import { useToast } from '@/hooks/use-toast';
import { useAgentStore } from '@/lib/store/agent/agentStore';

export const useSendMessage = () => {
    const { toast } = useToast();
    const pathname = usePathname();
    const [_, mode, chatId] = pathname.split('/');
    const { input, sendMessage, setInput } = useAgentStore();

    const handleSendMessage = async () => {
        const text = input.trim();
        if (!text) {
            toast({ title: "Please enter a message." });
            return;
        }

        try {
            setInput('');
            await sendMessage(chatId, mode, text);
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : "An unknown error occurred.";
            toast({
                variant: "destructive",
                title: "Error sending message",
                description: errorMessage,
            });
            // Restore input on error
            setInput(text);
        }
    };

    return { handleSendMessage };
};