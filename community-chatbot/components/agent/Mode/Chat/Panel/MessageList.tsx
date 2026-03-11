import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { Message } from '@/types/chat/types';
import { CopyButton } from '@/components/agent/Mode/Chat/Panel/CopyButton';

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  return (
    <div className='flex flex-col'>
      {messages.map((message) => (
        <div
          key={message.id}
          className={`group flex flex-col gap-2 ${message.role === 'user' ? 'self-end items-end' : 'flex-start items-start w-fit'
            }`}
        >
          <div
            className={`relative rounded-lg px-4 py-3 ${message.role === 'user'
              ? 'bg-blue-600 text-white'
              : 'bg-white dark:bg-gray-700 shadow-sm border dark:border-gray-600 max-w-[80%]'
              }`}
          >
            <div className="whitespace-pre-wrap">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          </div>
            <CopyButton
              textToCopy={message.content}
              className="opacity-0 group-hover:opacity-100 transition-opacity"
            />
        </div>
      ))}
    </div>
  );
}