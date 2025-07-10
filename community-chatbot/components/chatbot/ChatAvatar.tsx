import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Bot, User } from "lucide-react"

interface ChatAvatarProps {
  role: "user" | "assistant"
}

export function ChatAvatar({ role }: ChatAvatarProps) {
  if (role === "user") {
    return (
      <Avatar className="h-8 w-8">
        <AvatarFallback className="bg-gray-600 text-white">
          <User className="h-4 w-4" />
        </AvatarFallback>
      </Avatar>
    )
  }

  return (
    <Avatar className="h-8 w-8">
      <AvatarFallback className="bg-blue-600 text-white">
        <Bot className="h-4 w-4" />
      </AvatarFallback>
    </Avatar>
  )
}
