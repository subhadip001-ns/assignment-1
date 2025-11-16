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
  Wrench,
  Trash2,
} from 'lucide-react'
import { aiApi } from '@/lib/api'
import { cn } from '@/lib/utils'
import DOMPurify from 'dompurify'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  toolCalls?: Array<{ name: string; args: any; id: string }>
}

const examplePrompts = [
  { icon: BookOpen, text: 'Tell me about available courses', label: 'Courses' },
  { icon: User, text: 'Enroll me into the course with ID 1', label: 'Enroll' },
  { icon: MessageCircle, text: 'Show all courses where i m enrolled in', label: 'Enrolled Courses' },
]

export function AIChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [isLoadingHistory, setIsLoadingHistory] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isStreaming])

  // Load chat history on mount
  useEffect(() => {
    const loadChatHistory = async () => {
      try {
        setIsLoadingHistory(true)
        const response = await aiApi.getChatHistory()
        const historyMessages: Message[] = response.data.messages.map((msg, idx) => ({
          id: `history-${idx}-${Date.now()}`,
          role: msg.role as 'user' | 'assistant',
          content: msg.content,
          timestamp: new Date(msg.timestamp)
        }))
        setMessages(historyMessages)
      } catch (error) {
        console.error('Failed to load chat history:', error)
        // Don't show error to user, just start with empty chat
      } finally {
        setIsLoadingHistory(false)
      }
    }

    loadChatHistory()
  }, [])

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

      // Don't send chat_history - backend will fetch it automatically
      await aiApi.streamChat(
        messageToSend,
        [], // Backend will fetch chat history from database
        (chunk: string) => {
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessageId
                ? { ...msg, content: msg.content + chunk }
                : msg
            )
          )
        },
        (toolCalls: Array<{ name: string; args: any; id: string }>) => {
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessageId
                ? { ...msg, toolCalls }
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

  const handleClearChat = async () => {
    if (!confirm('Are you sure you want to clear all chat history? This action cannot be undone.')) {
      return
    }

    try {
      setIsLoading(true)
      await aiApi.clearChatHistory()
      setMessages([])
    } catch (error) {
      console.error('Failed to clear chat history:', error)
      alert('Failed to clear chat history. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] w-full">
      <div className="flex flex-col h-full">
        {/* Header with Clear Chat Button */}
        {messages.length > 0 && !isLoadingHistory && (
          <div className="flex items-center justify-between px-6 py-3 border-b border-gray-200 dark:border-gray-800">
            <h2 className="text-lg font-semibold">Chat</h2>
            <button
              onClick={handleClearChat}
              disabled={isLoading}
              className="flex items-center gap-2 px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground hover:bg-accent rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Clear chat history"
            >
              <Trash2 className="w-4 h-4" />
              <span>Clear Chat</span>
            </button>
          </div>
        )}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Messages Area */}
          <ScrollArea className="flex-1">
            <div className="p-6 space-y-6">
              {isLoadingHistory ? (
                <div className="flex items-center justify-center py-12">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    <span>Loading chat history...</span>
                  </div>
                </div>
              ) : messages.length === 0 ? (
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
                              ? 'bg-gray-700 text-white rounded-br-md'
                              : 'bg-gray-50 text-foreground rounded-bl-md border border-gray-200 dark:border-gray-800'
                          )}
                        >
                          {isUser ? (
                            <div className="prose prose-sm max-w-none dark:prose-invert">
                              <p className="whitespace-pre-wrap m-0 leading-relaxed">
                                {message.content}
                              </p>
                            </div>
                          ) : (
                            <div className="prose prose-sm max-w-none dark:prose-invert 
                              prose-headings:mt-0 prose-headings:mb-3 prose-headings:font-semibold
                              prose-h1:text-2xl prose-h2:text-xl prose-h3:text-lg
                              prose-p:my-2 prose-p:leading-relaxed prose-p:text-foreground
                              prose-ul:my-2 prose-ol:my-2 prose-li:my-1 prose-li:leading-relaxed
                              prose-code:text-sm prose-code:bg-gray-100 prose-code:dark:bg-gray-800 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:font-mono
                              prose-pre:bg-gray-100 prose-pre:dark:bg-gray-800 prose-pre:p-4 prose-pre:rounded-lg prose-pre:overflow-x-auto prose-pre:my-3
                              prose-strong:font-semibold prose-strong:text-foreground
                              prose-table:w-full prose-table:border-collapse prose-table:my-4 prose-table:shadow-sm prose-table:rounded-lg prose-table:overflow-hidden prose-table:border prose-table:border-gray-200 prose-table:dark:border-gray-700
                              prose-thead:bg-gradient-to-r prose-thead:from-gray-50 prose-thead:to-gray-100 prose-thead:dark:from-gray-800 prose-thead:dark:to-gray-900
                              prose-th:border prose-th:border-gray-200 prose-th:dark:border-gray-700 prose-th:bg-transparent prose-th:px-4 prose-th:py-3 prose-th:text-left prose-th:font-semibold prose-th:text-sm prose-th:text-gray-900 prose-th:dark:text-gray-100 prose-th:uppercase prose-th:tracking-wider
                              prose-tbody:bg-white prose-tbody:dark:bg-gray-900
                              prose-td:border prose-td:border-gray-200 prose-td:dark:border-gray-700 prose-td:px-4 prose-td:py-3 prose-td:text-sm prose-td:text-gray-700 prose-td:dark:text-gray-300
                              prose-tr:border-b prose-tr:border-gray-200 prose-tr:dark:border-gray-700 prose-tr:transition-colors prose-tr:duration-150
                              prose-tr:hover:bg-gray-50 prose-tr:dark:hover:bg-gray-800/50 prose-tr:last:border-b-0">
                              {message.content ? (
                                <div 
                                  dangerouslySetInnerHTML={{ 
                                    __html: DOMPurify.sanitize(message.content, {
                                      ALLOWED_TAGS: ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'code', 'pre', 'blockquote', 'a', 'div', 'span'],
                                      ALLOWED_ATTR: ['href', 'class', 'id', 'style']
                                    })
                                  }}
                                  className="html-content [&_table]:w-full [&_table]:border-collapse [&_table]:my-4 [&_table]:shadow-sm [&_table]:rounded-lg [&_table]:overflow-hidden [&_table]:border [&_table]:border-gray-200 dark:[&_table]:border-gray-700 [&_table]:bg-white dark:[&_table]:bg-gray-900 [&_thead]:bg-gradient-to-r [&_thead]:from-gray-50 [&_thead]:to-gray-100 dark:[&_thead]:from-gray-800 dark:[&_thead]:to-gray-900 [&_th]:px-4 [&_th]:py-3 [&_th]:text-left [&_th]:font-semibold [&_th]:text-sm [&_th]:text-gray-900 dark:[&_th]:text-gray-100 [&_th]:uppercase [&_th]:tracking-wider [&_th]:border-b [&_th]:border-gray-200 dark:[&_th]:border-gray-700 [&_td]:px-4 [&_td]:py-3 [&_td]:text-sm [&_td]:text-gray-700 dark:[&_td]:text-gray-300 [&_td]:border-b [&_td]:border-gray-100 dark:[&_td]:border-gray-800 [&_tr]:transition-colors [&_tr]:duration-150 [&_tr:hover]:bg-gray-50 dark:[&_tr:hover]:bg-gray-800/50"
                                />
                              ) : (
                                <span className="text-muted-foreground italic">Thinking...</span>
                              )}
                            </div>
                          )}
                          {message.toolCalls && message.toolCalls.length > 0 && (
                            <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                              <div className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground mb-2">
                                <Wrench className="w-3 h-3" />
                                <span>Tools Used:</span>
                              </div>
                              <div className="space-y-2">
                                {message.toolCalls.map((toolCall, idx) => (
                                  <div
                                    key={toolCall.id || idx}
                                    className="bg-gray-100 dark:bg-gray-800 rounded-md p-2.5 text-xs border border-gray-200 dark:border-gray-700"
                                  >
                                    <div className="flex items-center gap-2 mb-1.5">
                                      <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                                      <span className="font-medium text-primary">
                                        {toolCall.name}
                                      </span>
                                    </div>
                                    <div className="text-muted-foreground font-mono text-[10px] bg-gray-50 dark:bg-gray-900 rounded p-1.5 overflow-x-auto">
                                      <pre className="whitespace-pre-wrap break-words">
                                        {JSON.stringify(toolCall.args, null, 2)}
                                      </pre>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
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
                    <div className="bg-gray-50 rounded-2xl rounded-bl-md px-4 py-3 inline-block border border-gray-200 dark:border-gray-800">
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
