'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Brain, Send, Loader2, User, Bot, MessageCircle, X } from "lucide-react"
import { cn } from "@/lib/utils"

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  confidence?: number
  cited_data?: Array<{
    metric: string
    value: number
    date?: string
    context: string
  }>
}

interface QueryInterfaceProps {
  datasetId: string
  datasetName?: string
  isOpen: boolean
  onClose: () => void
}

export function QueryInterface({ datasetId, datasetName, isOpen, onClose }: QueryInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Auto-focus input when panel opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch(`/api/datasets/${datasetId}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          question: userMessage.content,
          conversation_history: messages.map(m => ({ role: m.role, content: m.content }))
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer || 'I apologize, but I could not process your question.',
        timestamp: new Date(),
        confidence: data.confidence,
        cited_data: data.cited_data
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Query failed:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your question. Please try again.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const suggestedQuestions = [
    "What are the main trends in this data?",
    "Which periods show the most significant anomalies?",
    "What caused the recent changes?",
    "How do different metrics correlate with each other?",
    "What patterns emerge over time?"
  ]

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <Card className="w-full max-w-4xl h-[600px] flex flex-col">
        <CardHeader className="flex-row items-center justify-between space-y-0 pb-2">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            <div>
              <CardTitle className="text-lg">Ask Questions</CardTitle>
              <CardDescription>
                {datasetName ? `Analyzing ${datasetName}` : 'Natural language queries about your data'}
              </CardDescription>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>
        
        <Separator />

        {/* Messages Area */}
        <CardContent className="flex-1 overflow-hidden p-0">
          <ScrollArea className="h-full px-6 py-4" ref={scrollAreaRef}>
            {messages.length === 0 ? (
              <div className="space-y-4">
                <div className="text-center text-muted-foreground py-8">
                  <MessageCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p className="text-lg font-medium">Ask me anything about your data</p>
                  <p className="text-sm">I can help you understand trends, anomalies, and insights</p>
                </div>
                
                <div>
                  <p className="text-sm font-medium mb-3 text-muted-foreground">Suggested questions:</p>
                  <div className="grid gap-2">
                    {suggestedQuestions.map((question, index) => (
                      <Button
                        key={index}
                        variant="outline"
                        size="sm"
                        className="justify-start text-left h-auto p-3 whitespace-normal"
                        onClick={() => setInput(question)}
                      >
                        {question}
                      </Button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={cn(
                      "flex gap-3",
                      message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                    )}
                  >
                    <div className={cn(
                      "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
                      message.role === 'user' 
                        ? 'bg-primary text-primary-foreground' 
                        : 'bg-muted text-muted-foreground'
                    )}>
                      {message.role === 'user' ? (
                        <User className="h-4 w-4" />
                      ) : (
                        <Bot className="h-4 w-4" />
                      )}
                    </div>
                    
                    <div className={cn(
                      "flex-1 space-y-2",
                      message.role === 'user' ? 'text-right' : 'text-left'
                    )}>
                      <div className={cn(
                        "inline-block max-w-[80%] p-3 rounded-lg",
                        message.role === 'user' 
                          ? 'bg-primary text-primary-foreground ml-auto' 
                          : 'bg-muted'
                      )}>
                        <p className="whitespace-pre-wrap">{message.content}</p>
                        
                        {/* Confidence and citations for assistant messages */}
                        {message.role === 'assistant' && (
                          <div className="mt-2 space-y-2">
                            {message.confidence && (
                              <div className="text-xs opacity-70">
                                Confidence: {Math.round(message.confidence * 100)}%
                              </div>
                            )}
                            
                            {message.cited_data && message.cited_data.length > 0 && (
                              <div className="text-xs space-y-1">
                                <p className="font-medium opacity-70">Referenced data:</p>
                                {message.cited_data.map((citation, index) => (
                                  <div key={index} className="opacity-60">
                                    <span className="font-medium">{citation.metric}:</span> {citation.value}
                                    {citation.date && <span className="ml-1">({citation.date})</span>}
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                      
                      <div className="text-xs text-muted-foreground">
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex gap-3">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-muted text-muted-foreground flex items-center justify-center">
                      <Bot className="h-4 w-4" />
                    </div>
                    <div className="flex-1">
                      <div className="inline-block bg-muted p-3 rounded-lg">
                        <div className="flex items-center gap-2">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          <span>Thinking...</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </ScrollArea>
        </CardContent>

        <Separator />

        {/* Input Area */}
        <div className="p-6">
          <div className="flex gap-2">
            <div className="flex-1">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a question about your data..."
                className="w-full min-h-[60px] max-h-32 p-3 border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent bg-background"
                disabled={isLoading}
              />
            </div>
            <Button 
              onClick={handleSendMessage} 
              disabled={!input.trim() || isLoading}
              size="lg"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}