import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { ChatAvatar } from '@/components/agent/Mode/Chat/Panel/ChatAvatar';
import { Message } from '@/types/chat/types';

interface MessageListProps {
  messages: Message[]
}

export function MessageList({ messages }: MessageListProps) {
  return (
    <>
      {messages.map((message) => (
        <div key={message.id} className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}>
          {message.role === "assistant" && <ChatAvatar role="assistant" />}
          <div
            className={`max-w-[80%] rounded-lg px-4 py-3 
              overflow-hidden break-words
              ${message.role === "user"
                ? "bg-blue-600 text-white ml-auto"
                : "bg-white dark:bg-gray-700 shadow-sm border dark:border-gray-600"
              }`}
          >
           
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                pre: ({ children }) => (
                  <pre className="whitespace-pre-wrap break-words overflow-hidden">
                    {children}
                  </pre>
                ),
                code: ({ inline, children }: any) => (
                  <code
                    className={`${inline
                      ? "whitespace-pre-wrap break-words"
                      : "block whitespace-pre-wrap break-words"
                      }`}
                  >
                    {children}
                  </code>
                ),
                a: ({ children }) => (
                  <span className="break-all">{children}</span>
                ),
                table: ({ children }) => (
                  <div className="overflow-hidden">{children}</div>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
            
          </div>
          {message.role === "user" && <ChatAvatar role="user" />}
        </div>
      ))}
    </>
  );
}
