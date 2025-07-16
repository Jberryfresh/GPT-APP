import { useState, useEffect, useRef } from 'react'
import { 
  Send, 
  Bot, 
  User, 
  Loader2, 
  RefreshCw, 
  Settings,
  MessageSquare,
  Trash2
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Label } from '@/components/ui/label'

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: 'Hello! I\'m your custom GPT assistant. How can I help you today?',
      timestamp: new Date()
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedModel, setSelectedModel] = useState('default')
  const [models, setModels] = useState([
    { id: 'default', name: 'Default Model', status: 'active' },
    { id: 'legal-expert', name: 'Legal Expert', status: 'active' },
    { id: 'medical-assistant', name: 'Medical Assistant', status: 'training' }
  ])
  const [chatSettings, setChatSettings] = useState({
    temperature: 0.7,
    maxTokens: 256,
    streaming: true
  })
  const [showSettings, setShowSettings] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    const currentInput = inputMessage;
    setInputMessage('');

    try {
      const response = await fetch('/api/v1/chat/simple', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          message: currentInput,
          max_tokens: chatSettings.maxTokens,
          temperature: chatSettings.temperature
        })
      });

      const data = await response.json();

      if (data.success) {
        const botMessage = { 
          id: Date.now() + 1,
          role: 'assistant', 
          content: data.response,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, botMessage]);
      } else {
        const errorMessage = { 
          id: Date.now() + 1,
          role: 'assistant', 
          content: `Error: ${data.error || 'Unknown error occurred'}`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = { 
        id: Date.now() + 1,
        role: 'assistant', 
        content: 'Sorry, there was an error connecting to the API. Please check your connection and try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const clearChat = () => {
    setMessages([
      {
        id: 1,
        role: 'assistant',
        content: 'Hello! I\'m your custom GPT assistant. How can I help you today?',
        timestamp: new Date()
      }
    ])
  }

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex gap-6">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        <Card className="flex-1 flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <MessageSquare className="h-5 w-5" />
                <span>Chat with {models.find(m => m.id === selectedModel)?.name}</span>
              </CardTitle>
              <CardDescription>
                Interact with your custom GPT model
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowSettings(!showSettings)}
              >
                <Settings className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={clearChat}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>

          <CardContent className="flex-1 flex flex-col p-0">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-4 ${
                      message.role === 'user'
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div className="flex items-start space-x-2">
                      {message.role === 'assistant' && (
                        <Bot className="h-5 w-5 mt-0.5 text-indigo-600" />
                      )}
                      {message.role === 'user' && (
                        <User className="h-5 w-5 mt-0.5 text-white" />
                      )}
                      <div className="flex-1">
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        <p className={`text-xs mt-2 ${
                          message.role === 'user' ? 'text-indigo-200' : 'text-gray-500'
                        }`}>
                          {formatTime(message.timestamp)}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg p-4">
                    <div className="flex items-center space-x-2">
                      <Bot className="h-5 w-5 text-indigo-600" />
                      <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
                      <span className="text-sm text-gray-500">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t p-6">
              <div className="flex space-x-4">
                <div className="flex-1">
                  <Input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message..."
                    disabled={isLoading}
                    className="w-full"
                  />
                </div>
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || isLoading}
                  className="px-6"
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sidebar */}
      <div className="w-80 space-y-6">
        {/* Model Selection */}
        <Card>
          <CardHeader>
            <CardTitle>Model Selection</CardTitle>
            <CardDescription>
              Choose which model to chat with
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Select value={selectedModel} onValueChange={setSelectedModel}>
              <SelectTrigger>
                <SelectValue placeholder="Select a model" />
              </SelectTrigger>
              <SelectContent>
                {models.map((model) => (
                  <SelectItem key={model.id} value={model.id} disabled={model.status !== 'active'}>
                    <div className="flex items-center justify-between w-full">
                      <span>{model.name}</span>
                      <Badge variant={model.status === 'active' ? 'default' : 'secondary'}>
                        {model.status}
                      </Badge>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CardContent>
        </Card>

        {/* Chat Settings */}
        {showSettings && (
          <Card>
            <CardHeader>
              <CardTitle>Chat Settings</CardTitle>
              <CardDescription>
                Adjust model parameters
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label>Temperature: {chatSettings.temperature}</Label>
                <Slider
                  value={[chatSettings.temperature]}
                  onValueChange={(value) => setChatSettings(prev => ({ ...prev, temperature: value[0] }))}
                  max={1}
                  min={0}
                  step={0.1}
                  className="w-full"
                />
                <p className="text-xs text-gray-500">
                  Higher values make output more random
                </p>
              </div>

              <div className="space-y-2">
                <Label>Max Tokens: {chatSettings.maxTokens}</Label>
                <Slider
                  value={[chatSettings.maxTokens]}
                  onValueChange={(value) => setChatSettings(prev => ({ ...prev, maxTokens: value[0] }))}
                  max={512}
                  min={50}
                  step={10}
                  className="w-full"
                />
                <p className="text-xs text-gray-500">
                  Maximum length of the response
                </p>
              </div>

              <div className="flex items-center justify-between">
                <Label>Streaming</Label>
                <Button
                  variant={chatSettings.streaming ? "default" : "outline"}
                  size="sm"
                  onClick={() => setChatSettings(prev => ({ ...prev, streaming: !prev.streaming }))}
                >
                  {chatSettings.streaming ? "On" : "Off"}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Chat Statistics */}
        <Card>
          <CardHeader>
            <CardTitle>Session Stats</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Messages</span>
              <span className="text-sm font-medium">{messages.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Model</span>
              <span className="text-sm font-medium">{selectedModel}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Tokens Used</span>
              <span className="text-sm font-medium">~{messages.length * 20}</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}