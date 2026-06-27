import { useEffect, useRef, useState } from 'react'
import { Send, ChevronDown, ChevronUp, Bot, User } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { createSession, getSession, askQuestion } from '@/api/client'
import type { Message, Source } from '@/types'

interface Props {
  collectionId: string
}

export default function ChatPanel({ collectionId }: Props) {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  // Auto-create a session when the panel mounts
  useEffect(() => {
    const init = async () => {
      try {
        const session = await createSession(collectionId)
        setSessionId(session.id)
        setMessages(session.messages)
      } catch {
        setError('Failed to start chat session.')
      }
    }
    init()
  }, [collectionId])

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendMessage = async () => {
    if (!input.trim() || !sessionId || loading) return
    const question = input.trim()
    setInput('')
    setError('')

    // Optimistically add user message
    const tempUserMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: question,
      sources: [],
      created_at: new Date().toISOString(),
    }
    setMessages(prev => [...prev, tempUserMsg])
    setLoading(true)

    try {
      const assistantMsg = await askQuestion(collectionId, sessionId, question)
      setMessages(prev => [...prev, assistantMsg])
    } catch (e: any) {
      const msg = e?.response?.data?.error || 'Something went wrong. Please try again.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      <h2 className="font-semibold text-sm uppercase tracking-wide text-muted-foreground mb-4">
        Chat
      </h2>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1">
        {messages.length === 0 && !loading && (
          <div className="text-center text-muted-foreground text-sm py-10">
            Ask a question about the documents in this collection.
          </div>
        )}

        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {/* Thinking animation */}
        {loading && <ThinkingBubble />}

        {error && (
          <p className="text-xs text-destructive text-center">{error}</p>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="pt-4 border-t mt-4">
        <div className="flex gap-2 items-end">
          <Textarea
            placeholder="Ask a question about your documents..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                sendMessage()
              }
            }}
            rows={2}
            className="resize-none"
            disabled={loading}
          />
          <Button
            size="icon"
            onClick={sendMessage}
            disabled={loading || !input.trim()}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-xs text-muted-foreground mt-1">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  )
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user'
  const [sourcesOpen, setSourcesOpen] = useState(false)

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div className={`h-7 w-7 rounded-full flex items-center justify-center shrink-0 mt-1
        ${isUser ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
        {isUser
          ? <User className="h-3.5 w-3.5" />
          : <Bot className="h-3.5 w-3.5" />
        }
      </div>

      {/* Bubble */}
      <div className={`max-w-[80%] space-y-2 ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        <div className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap
          ${isUser
            ? 'bg-primary text-primary-foreground rounded-tr-sm'
            : 'bg-muted rounded-tl-sm'
          }`}>
          {message.content}
        </div>

        {/* Sources */}
        {!isUser && message.sources?.length > 0 && (
          <div className="w-full">
            <button
              onClick={() => setSourcesOpen(o => !o)}
              className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              {sourcesOpen ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
              {message.sources.length} source{message.sources.length > 1 ? 's' : ''} used
            </button>
            {sourcesOpen && (
              <div className="mt-2 space-y-2">
                {message.sources.map((src: Source, i: number) => (
                  <div key={i} className="text-xs bg-background border rounded-lg p-3 text-muted-foreground leading-relaxed">
                    <span className="font-medium text-foreground">Chunk {src.chunk_index + 1}</span>
                    <p className="mt-1 line-clamp-3">{src.text}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function ThinkingBubble() {
  return (
    <div className="flex gap-3">
      <div className="h-7 w-7 rounded-full bg-muted flex items-center justify-center shrink-0 mt-1">
        <Bot className="h-3.5 w-3.5" />
      </div>
      <div className="bg-muted rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1">
        <span className="h-2 w-2 rounded-full bg-foreground/40 animate-bounce [animation-delay:0ms]" />
        <span className="h-2 w-2 rounded-full bg-foreground/40 animate-bounce [animation-delay:150ms]" />
        <span className="h-2 w-2 rounded-full bg-foreground/40 animate-bounce [animation-delay:300ms]" />
      </div>
    </div>
  )
}