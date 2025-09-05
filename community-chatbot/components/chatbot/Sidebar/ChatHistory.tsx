import { Trash2 } from 'lucide-react';
import Image from 'next/image';

import { ChatHistoryItem, IntegrationMode } from '@/components/chatbot/types';
import { Button } from '@/components/ui/button';
import { SidebarGroup } from '@/components/ui/sidebar';

interface ChatHistoryProps {
	chatHistory: ChatHistoryItem[]
	switchConversation: (conversationId: string) => void
	deleteConversation: (conversationId: string, e: React.MouseEvent) => void
	integrationModes: IntegrationMode[]
	isExpanded: boolean
}

export function ChatHistory({
	chatHistory,
	switchConversation,
	isExpanded,
	deleteConversation
}: ChatHistoryProps) {
	return (
		<SidebarGroup className="space-y-4 overflow-y-auto">
			{chatHistory?.map((chat) => (
				<div
					key={chat.id}
					className={`flex items-center justify-center flex-wrap gap-3 p-3 rounded-2xl cursor-pointer transition-colors
						${chat.active
							? "bg-blue-600 text-white"
							: "hover:bg-gray-100 dark:hover:bg-gray-700"
						}`}
					onClick={() => switchConversation(chat.id)}
				>
					<div className="bg-white p-2 rounded-full">
						<Image
							src={chat.icon}
							alt={chat.title}
							width={20}
							height={20}
						/>
					</div>

					{isExpanded && (
						<div className="flex-1 px-2 min-w-0">
							<p className="font-medium truncate">{chat.title}</p>
							<p
								className={`text-sm ${chat.active
									? "text-blue-100"
									: "text-gray-500 dark:text-gray-400"
									}`}
							>
								{chat.date}
							</p>
						</div>
					)}

					{isExpanded && chatHistory.length > 1 && (
						<Button
							variant="ghost"
							size="icon"
							className={`size-6 transition
								${chat.active
									? "text-white hover:text-white hover:bg-blue-700"
									: "hover:bg-gray-200 dark:hover:bg-gray-600"
								}`}
							onClick={(e) => {
								e.stopPropagation(); // don’t trigger switchConversation
								deleteConversation(chat.id, e);
							}}
						>
							<Trash2 className="w-3 h-3" />
						</Button>
					)}
				</div>
			))}

		</SidebarGroup>
	)
}