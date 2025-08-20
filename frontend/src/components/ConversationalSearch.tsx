import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Send, 
  Bot, 
  User, 
  Loader2, 
  RefreshCw, 
  MessageSquare,
  Search,
  FileText,
  ExternalLink
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Source[];
}

interface Source {
  id: string;
  title: string;
  url?: string;
  content: string;
  similarity: number;
}

interface ConversationState {
  messages: Message[];
  isLoading: boolean;
  sessionId?: string;
}

const ConversationalSearch: React.FC = () => {
  const { session } = useAuth();
  const [conversation, setConversation] = useState<ConversationState>({
    messages: [],
    isLoading: false
  });
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation.messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || conversation.isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    };

    setConversation(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true
    }));

    setInputMessage('');

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/search/conversational/chat`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          session_id: conversation.sessionId,
          conversation_history: conversation.messages.map(msg => ({
            role: msg.role,
            content: msg.content
          }))
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.response,
          timestamp: new Date(),
          sources: data.sources || []
        };

        setConversation(prev => ({
          ...prev,
          messages: [...prev.messages, assistantMessage],
          isLoading: false,
          sessionId: data.session_id || prev.sessionId
        }));
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Chat error:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your request. Please try again.',
        timestamp: new Date()
      };

      setConversation(prev => ({
        ...prev,
        messages: [...prev.messages, errorMessage],
        isLoading: false
      }));
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const startNewConversation = () => {
    setConversation({
      messages: [],
      isLoading: false
    });
  };

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <MessageSquare className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold">Conversational Search</h1>
            <p className="text-gray-600">Chat with your documents using AI</p>
          </div>
        </div>
        <Button
          variant="outline"
          onClick={startNewConversation}
          className="flex items-center space-x-2"
        >
          <RefreshCw className="h-4 w-4" />
          <span>New Chat</span>
        </Button>
      </div>

      {/* Chat Interface */}
      <Card className="h-[600px] flex flex-col">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Bot className="h-5 w-5" />
            <span>AI Assistant</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col p-0">
          {/* Messages Area */}
          <ScrollArea className="flex-1 p-6">
            {conversation.messages.length === 0 ? (
              <div className="text-center py-12">
                <Bot className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Start a conversation</h3>
                <p className="text-gray-500">
                  Ask questions about your documents and get AI-powered answers
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {conversation.messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-4 ${
                        message.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <div className="flex items-start space-x-2 mb-2">
                        {message.role === 'user' ? (
                          <User className="h-4 w-4 mt-1 flex-shrink-0" />
                        ) : (
                          <Bot className="h-4 w-4 mt-1 flex-shrink-0" />
                        )}
                        <div className="flex-1">
                          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                          
                          {/* Sources */}
                          {message.sources && message.sources.length > 0 && (
                            <div className="mt-4 pt-4 border-t border-gray-200">
                              <p className="text-xs font-medium mb-2">Sources:</p>
                              <div className="space-y-2">
                                {message.sources.map((source) => (
                                  <div key={source.id} className="text-xs bg-white rounded p-2">
                                    <div className="flex items-start justify-between">
                                      <div className="flex-1">
                                        <p className="font-medium">{source.title}</p>
                                        <p className="text-gray-600 line-clamp-2">{source.content}</p>
                                        <Badge variant="outline" className="mt-1">
                                          {Math.round(source.similarity * 100)}% match
                                        </Badge>
                                      </div>
                                      {source.url && (
                                        <a
                                          href={source.url}
                                          target="_blank"
                                          rel="noopener noreferrer"
                                          className="ml-2 text-blue-600 hover:text-blue-700"
                                        >
                                          <ExternalLink className="h-3 w-3" />
                                        </a>
                                      )}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="text-xs opacity-70">
                        {formatTimestamp(message.timestamp)}
                      </div>
                    </div>
                  </div>
                ))}
                
                {/* Loading indicator */}
                {conversation.isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 rounded-lg p-4 max-w-[80%]">
                      <div className="flex items-center space-x-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="text-sm text-gray-600">AI is thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>
            )}
          </ScrollArea>

          {/* Input Area */}
          <div className="border-t p-4">
            <div className="flex space-x-2">
              <Input
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a question about your documents..."
                disabled={conversation.isLoading}
                className="flex-1"
              />
              <Button
                onClick={sendMessage}
                disabled={!inputMessage.trim() || conversation.isLoading}
                className="flex items-center space-x-2"
              >
                {conversation.isLoading ? (
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
  );
};

export default ConversationalSearch;
