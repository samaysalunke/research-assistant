import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Loader2, MessageSquare, Send, Sparkles, FileText, List, BookOpen, Zap } from 'lucide-react';
import { supabase } from '@/services/supabase';
import toast from 'react-hot-toast';

interface ConversationMessage {
  id: string;
  userMessage: string;
  aiResponse: string;
  timestamp: string;
  confidence: number;
  sources: Array<{
    title: string;
    url: string;
    relevance: number;
    content_preview: string;
  }>;
}

interface ConversationSession {
  session_id: string;
  created_at: string;
  last_activity: string;
  message_count: number;
  conversation_summary?: string;
}

export default function ConversationalSearch() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentSession, setCurrentSession] = useState<ConversationSession | null>(null);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [responseType, setResponseType] = useState('comprehensive');
  const [sessions, setSessions] = useState<ConversationSession[]>([]);
  const [showSessions, setShowSessions] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const responseTypes = [
    { value: 'comprehensive', label: 'Comprehensive', icon: BookOpen },
    { value: 'summary', label: 'Summary', icon: FileText },
    { value: 'detailed', label: 'Detailed', icon: Zap },
    { value: 'bullet_points', label: 'Bullet Points', icon: List },
  ];

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadSessions = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/conversation/sessions`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
        },
      });

      if (response.ok) {
        const sessionsData = await response.json();
        setSessions(sessionsData);
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const startNewConversation = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/conversation/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const sessionData = await response.json();
        setCurrentSession(sessionData);
        setMessages([]);
        setShowSessions(false);
        toast.success('New conversation started!');
      }
    } catch (error) {
      console.error('Error starting conversation:', error);
      toast.error('Failed to start conversation');
    }
  };

  const sendMessage = async () => {
    if (!query.trim() || isLoading) return;

    const userMessage = query.trim();
    setQuery('');
    setIsLoading(true);

    // Add user message to UI immediately
    const tempMessage: ConversationMessage = {
      id: Date.now().toString(),
      userMessage,
      aiResponse: '',
      timestamp: new Date().toISOString(),
      confidence: 0,
      sources: [],
    };

    setMessages(prev => [...prev, tempMessage]);

    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/conversation/query`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessage,
          conversation_id: currentSession?.session_id,
          response_type: responseType,
          include_sources: true,
          max_sources: 5,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Update the message with AI response
        setMessages(prev => prev.map(msg => 
          msg.id === tempMessage.id 
            ? {
                ...msg,
                aiResponse: data.response,
                confidence: data.confidence,
                sources: data.sources || [],
              }
            : msg
        ));

        // Update current session
        if (data.conversation_id && !currentSession) {
          setCurrentSession({
            session_id: data.conversation_id,
            created_at: new Date().toISOString(),
            last_activity: new Date().toISOString(),
            message_count: 1,
          });
        }

        toast.success('Response received!');
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message');
      
      // Remove the temporary message on error
      setMessages(prev => prev.filter(msg => msg.id !== tempMessage.id));
    } finally {
      setIsLoading(false);
    }
  };

  const loadSession = async (sessionId: string) => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;

      // Get session details
      const sessionResponse = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/conversation/sessions/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
        },
      });

      if (sessionResponse.ok) {
        const sessionData = await sessionResponse.json();
        setCurrentSession(sessionData);
      }

      // Get messages
      const messagesResponse = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/conversation/sessions/${sessionId}/messages`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
        },
      });

      if (messagesResponse.ok) {
        const messagesData = await messagesResponse.json();
        setMessages(messagesData);
      }

      setShowSessions(false);
    } catch (error) {
      console.error('Error loading session:', error);
      toast.error('Failed to load conversation');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <MessageSquare className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold">Conversational Search</h1>
            <p className="text-gray-600">Ask questions and get AI-powered responses from your documents</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            onClick={() => setShowSessions(!showSessions)}
            className="flex items-center space-x-2"
          >
            <FileText className="h-4 w-4" />
            <span>History</span>
          </Button>
          <Button
            onClick={startNewConversation}
            className="flex items-center space-x-2"
          >
            <Sparkles className="h-4 w-4" />
            <span>New Chat</span>
          </Button>
        </div>
      </div>

      {/* Response Type Selector */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Response Type</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {responseTypes.map((type) => {
              const Icon = type.icon;
              return (
                <Button
                  key={type.value}
                  variant={responseType === type.value ? "default" : "outline"}
                  onClick={() => setResponseType(type.value)}
                  className="flex items-center space-x-2 h-auto p-3"
                >
                  <Icon className="h-4 w-4" />
                  <span className="text-sm">{type.label}</span>
                </Button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Sessions Panel */}
      {showSessions && (
        <Card>
          <CardHeader>
            <CardTitle>Conversation History</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-64">
              <div className="space-y-2">
                {sessions.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">No previous conversations</p>
                ) : (
                  sessions.map((session) => (
                    <div
                      key={session.session_id}
                      onClick={() => loadSession(session.session_id)}
                      className="p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium">
                            {session.conversation_summary || `Conversation ${session.session_id.slice(0, 8)}`}
                          </p>
                          <p className="text-sm text-gray-500">
                            {new Date(session.last_activity).toLocaleDateString()}
                          </p>
                        </div>
                        <Badge variant="secondary">{session.message_count} messages</Badge>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}

      {/* Messages */}
      <Card className="min-h-[500px]">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MessageSquare className="h-5 w-5" />
            <span>Conversation</span>
            {currentSession && (
              <Badge variant="outline">
                Session: {currentSession.session_id.slice(0, 8)}
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-96">
            <div className="space-y-4">
              {messages.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <MessageSquare className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>Start a conversation by asking a question</p>
                  <p className="text-sm mt-2">Try: "What is the connection between reading and writing?"</p>
                </div>
              ) : (
                messages.map((message) => (
                  <div key={message.id} className="space-y-3">
                    {/* User Message */}
                    <div className="flex justify-end">
                      <div className="bg-blue-600 text-white rounded-lg p-3 max-w-[80%]">
                        <p>{message.userMessage}</p>
                      </div>
                    </div>

                    {/* AI Response */}
                    {message.aiResponse && (
                      <div className="flex justify-start">
                        <div className="bg-gray-100 rounded-lg p-3 max-w-[80%] space-y-3">
                          <div className="flex items-center space-x-2">
                            <Sparkles className="h-4 w-4 text-green-600" />
                            <Badge variant="outline" className="text-xs">
                              Confidence: {(message.confidence * 100).toFixed(0)}%
                            </Badge>
                          </div>
                          <p className="whitespace-pre-wrap">{message.aiResponse}</p>
                          
                          {/* Sources */}
                          {message.sources && message.sources.length > 0 && (
                            <div className="mt-3 pt-3 border-t">
                              <p className="text-sm font-medium text-gray-700 mb-2">Sources:</p>
                              <div className="space-y-2">
                                {message.sources.map((source, index) => (
                                  <div key={index} className="text-sm bg-white p-2 rounded border">
                                    <p className="font-medium">{source.title}</p>
                                    <p className="text-gray-600 text-xs">
                                      Relevance: {(source.relevance * 100).toFixed(0)}%
                                    </p>
                                    {source.url && (
                                      <a
                                        href={source.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-blue-600 text-xs hover:underline"
                                      >
                                        View source
                                      </a>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Loading indicator */}
                    {!message.aiResponse && isLoading && (
                      <div className="flex justify-start">
                        <div className="bg-gray-100 rounded-lg p-3 flex items-center space-x-2">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          <span className="text-sm text-gray-600">Thinking...</span>
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Input */}
      <Card>
        <CardContent className="p-4">
          <div className="flex space-x-2">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about your documents..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button
              onClick={sendMessage}
              disabled={!query.trim() || isLoading}
              className="flex items-center space-x-2"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              <span>Send</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
