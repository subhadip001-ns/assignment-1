import { useState, useRef, useEffect } from 'react'
import { Textarea } from '@/components/ui/textarea'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
  Send,
  Bot,
  User,
  Copy,
  Check,
  Calculator,
  BookOpen,
  MessageCircle,
} from 'lucide-react'
import { aiApi } from '@/lib/api'
import { cn } from '@/lib/utils'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const examplePrompts = [
  { icon: Calculator, text: 'What is 15 + 27?', label: 'Math' },
  { icon: BookOpen, text: 'Tell me about available courses', label: 'Courses' },
  { icon: MessageCircle, text: 'Hello! How can you help me?', label: 'General' },
]

export function AIChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isStreaming])

  useEffect(() => {
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`
    }
  }, [inputMessage])

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    const messageToSend = inputMessage.trim()
    setInputMessage('')
    setIsLoading(true)

    try {
      setIsStreaming(true)

      const assistantMessageId = (Date.now() + 1).toString()
      const assistantMessage: Message = {
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
      }

      setMessages(prev => [...prev, assistantMessage])

      await aiApi.streamChat(
        messageToSend,
        messages.map(msg => ({ role: msg.role, content: msg.content })),
        (chunk: string) => {
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessageId
                ? { ...msg, content: msg.content + chunk }
                : msg
            )
          )
        }
      )
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      setIsStreaming(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleCopy = async (content: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(content)
      setCopiedId(messageId)
      setTimeout(() => setCopiedId(null), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }

  const handleExampleClick = (text: string) => {
    setInputMessage(text)
    textareaRef.current?.focus()
  }

  const formatTime = (date: Date) => {
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)

    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] w-full">
      <div className="flex flex-col h-full">
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Messages Area */}
          <ScrollArea className="flex-1">
            <div className="p-6 space-y-6">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 px-4">
                  <div className="relative mb-6">
                    <div className="absolute inset-0 bg-primary/20 rounded-full blur-xl animate-pulse" />
                    <div className="relative p-6 rounded-full bg-gradient-to-br from-primary/10 to-primary/5">
                      <Bot className="w-12 h-12 text-primary" />
                    </div>
                  </div>
                  <h3 className="text-2xl font-semibold mb-2">Welcome to AI Chat!</h3>
                  <p className="text-muted-foreground text-center mb-8 max-w-md">
                    Start a conversation by asking a question or try one of these examples:
                  </p>
                  <div className="grid gap-3 w-full max-w-md">
                    {examplePrompts.map((prompt, idx) => {
                      const Icon = prompt.icon
                      return (
                        <button
                          key={idx}
                          onClick={() => handleExampleClick(prompt.text)}
                          className="group flex items-center gap-3 p-4 rounded-lg border border-gray-200 dark:border-gray-800 bg-card hover:bg-accent transition-all text-left cursor-pointer"
                        >
                          <div className="p-2 rounded-md bg-primary/10 group-hover:bg-primary/20 transition-colors">
                            <Icon className="w-4 h-4 text-primary" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-sm font-medium">{prompt.label}</span>
                            </div>
                            <p className="text-sm text-muted-foreground truncate">
                              {prompt.text}
                            </p>
                          </div>
                        </button>
                      )
                    })}
                  </div>
                </div>
              ) : (
                messages.map((message) => {
                  const isUser = message.role === 'user'
                  return (
                    <div
                      key={message.id}
                      className={cn(
                        'flex gap-4 group',
                        isUser ? 'flex-row-reverse' : 'flex-row'
                      )}
                    >
                      <Avatar
                        className={cn(
                          'h-9 w-9 shrink-0',
                          isUser
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white'
                        )}
                      >
                        <AvatarFallback>
                          {isUser ? (
                            <User className="w-5 h-5" />
                          ) : (
                            <Bot className="w-5 h-5" />
                          )}
                        </AvatarFallback>
                      </Avatar>

                      <div className={cn('flex flex-col gap-1.5 flex-1 min-w-0', isUser ? 'items-end' : 'items-start')}>
                        <div
                          className={cn(
                            'relative group/message rounded-2xl px-4 py-3 max-w-[85%] sm:max-w-[75%]',
                            isUser
                              ? 'bg-primary text-primary-foreground rounded-br-md'
                              : 'bg-muted text-foreground rounded-bl-md'
                          )}
                        >
                          <div className="prose prose-sm max-w-none dark:prose-invert">
                            <p className="whitespace-pre-wrap m-0 leading-relaxed">
                              {message.content || (
                                <span className="text-muted-foreground italic">Thinking...</span>
                              )}
                            </p>
                          </div>
                          {message.content && (
                            <button
                              onClick={() => handleCopy(message.content, message.id)}
                              className={cn(
                                'absolute -top-2 -right-2 opacity-0 group-hover/message:opacity-100 transition-opacity p-1.5 rounded-full bg-background border border-gray-200 dark:border-gray-800 hover:bg-accent cursor-pointer',
                                isUser ? 'text-primary-foreground' : 'text-foreground'
                              )}
                              aria-label="Copy message"
                            >
                              {copiedId === message.id ? (
                                <Check className="w-3.5 h-3.5 text-green-600" />
                              ) : (
                                <Copy className="w-3.5 h-3.5" />
                              )}
                            </button>
                          )}
                        </div>
                        <span className="text-xs text-muted-foreground px-1">
                          {formatTime(message.timestamp)}
                        </span>
                      </div>
                    </div>
                  )
                })
              )}

              {isStreaming && (
                <div className="flex gap-4">
                  <Avatar className="h-9 w-9 shrink-0 bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
                    <AvatarFallback>
                      <Bot className="w-5 h-5" />
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex flex-col gap-1.5 flex-1">
                    <div className="bg-muted rounded-2xl rounded-bl-md px-4 py-3 inline-block">
                      <div className="flex items-center gap-1.5">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]" />
                          <div className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]" />
                          <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                        </div>
                        <span className="text-xs text-muted-foreground ml-2">AI is typing...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          {/* Input Area */}
          <div className="border-t border-gray-200 dark:border-gray-800 bg-background p-4">
            <div className="flex gap-2 items-end">
              <div className="flex-1 relative">
                <Textarea
                  ref={textareaRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
                  disabled={isLoading}
                  className="min-h-[44px] max-h-[120px] resize-none pr-12 border-gray-200 dark:border-gray-800"
                  rows={1}
                />
                {inputMessage.length > 0 && (
                  <div className="absolute bottom-2 right-2 text-xs text-muted-foreground">
                    {inputMessage.length}
                  </div>
                )}
              </div>
              <button
                type="button"
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
                className="h-11 w-11 shrink-0 flex items-center justify-center rounded-md bg-gray-900 hover:bg-gray-800 text-white cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                aria-label="Send message"
              >
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </button>
            </div>
            <p className="text-xs text-muted-foreground mt-2 px-1">
              AI can make mistakes. Verify important information.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
