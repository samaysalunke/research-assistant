import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { MessageCircle, Send, History, Sparkles, Loader2, X, RefreshCw } from 'lucide-react';

interface ConversationMessage {
  id: string;
  query: string;
  response: string;
  timestamp: string;
  sources?: Array<{
    id: string;
    title: string;
    url?: string;
  }>;
  confidence?: number;
}

interface ConversationSession {
  session_id: string;
  user_id: string;
  created_at: string;
  last_activity: string;
  title?: string;
  message_count: number;
}

interface ConversationalResponse {
  response: string;
  conversation_id: string;
  sources: Array<{
    id: string;
    title: string;
    url?: string;
  }>;
  confidence: number;
  suggestions: string[];
  response_type: string;
  metadata: any;
  query_analysis: any;
}

const ConversationalSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [currentSession, setCurrentSession] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sessions, setSessions] = useState<ConversationSession[]>([]);
  const [showSessions, setShowSessions] = useState(false);
  const [responseType, setResponseType] = useState('comprehensive');
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/conversation/sessions`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions || []);
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const startNewConversation = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/conversation/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setCurrentSession(data.conversation_id);
        setMessages([]);
        await loadSessions();
      }
    } catch (error) {
      console.error('Failed to start conversation:', error);
    }
  };

  const sendMessage = async () => {
    if (!query.trim() || isLoading) return;

    const userMessage: ConversationMessage = {
      id: Date.now().toString(),
      query: query,
      response: '',
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setQuery('');
    setIsLoading(true);
    setProgress(0);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setProgress(prev => Math.min(prev + 10, 90));
    }, 200);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/conversation/query`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessage.query,
          conversation_id: currentSession,
          response_type: responseType,
          include_sources: true,
          max_sources: 5,
        }),
      });

      clearInterval(progressInterval);
      setProgress(100);

      if (response.ok) {
        const data: ConversationalResponse = await response.json();
        
        const aiMessage: ConversationMessage = {
          id: (Date.now() + 1).toString(),
          query: '',
          response: data.response,
          timestamp: new Date().toISOString(),
          sources: data.sources,
          confidence: data.confidence,
        };

        setMessages(prev => prev.map(msg => 
          msg.id === userMessage.id ? { ...msg, response: data.response } : msg
        ).concat(aiMessage));

        if (!currentSession) {
          setCurrentSession(data.conversation_id);
        }
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages(prev => prev.map(msg => 
        msg.id === userMessage.id ? { ...msg, response: 'Sorry, I encountered an error. Please try again.' } : msg
      ));
    } finally {
      setIsLoading(false);
      setProgress(0);
    }
  };

  const loadSession = async (sessionId: string) => {
    try {
      const sessionResponse = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/conversation/sessions/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`,
          'Content-Type': 'application/json',
        },
      });
      
      const messagesResponse = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/conversation/sessions/${sessionId}/messages`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (sessionResponse.ok && messagesResponse.ok) {
        const sessionData = await sessionResponse.json();
        const messagesData = await messagesResponse.json();
        
        setCurrentSession(sessionId);
        setMessages(messagesData.messages || []);
      }
    } catch (error) {
      console.error('Failed to load session:', error);
    }
  };

  const deleteSession = async (sessionId: string) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/conversation/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase.auth.token')}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        await loadSessions();
        if (currentSession === sessionId) {
          setCurrentSession(null);
          setMessages([]);
        }
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <MessageCircle className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold">Conversational Search</h1>
            <p className="text-gray-600">Ask questions and get AI-powered responses from your documents</p>
          </div>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            onClick={() => setShowSessions(!showSessions)}
            className="flex items-center space-x-2"
          >
            <History className="h-4 w-4" />
            <span>Sessions</span>
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
          <Select value={responseType} onValueChange={setResponseType}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select response type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="comprehensive">Comprehensive</SelectItem>
              <SelectItem value="concise">Concise</SelectItem>
              <SelectItem value="detailed">Detailed</SelectItem>
              <SelectItem value="summary">Summary</SelectItem>
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {/* Sessions Panel */}
      {showSessions && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Previous Conversations</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-64">
              <div className="space-y-2">
                {sessions.map((session) => (
                  <div
                    key={session.session_id}
                    className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex-1">
                      <div className="font-medium">
                        {session.title || `Conversation ${session.session_id.slice(0, 8)}`}
                      </div>
                      <div className="text-sm text-gray-500">
                        {formatTimestamp(session.created_at)} • {session.message_count} messages
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => loadSession(session.session_id)}
                      >
                        Load
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => deleteSession(session.session_id)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}

      {/* Messages */}
      <Card className="min-h-[500px]">
        <CardHeader>
          <CardTitle className="text-lg">Conversation</CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-96">
            <div className="space-y-4">
              {messages.length === 0 && !isLoading && (
                <div className="text-center text-gray-500 py-8">
                  <MessageCircle className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>Start a conversation by asking a question</p>
                </div>
              )}
              
              {messages.map((message) => (
                <div key={message.id} className="space-y-2">
                  {message.query && (
                    <div className="flex justify-end">
                      <div className="bg-blue-600 text-white rounded-lg p-3 max-w-[80%]">
                        <p>{message.query}</p>
                      </div>
                    </div>
                  )}
                  
                  {message.response && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 rounded-lg p-3 max-w-[80%]">
                        <p className="whitespace-pre-wrap">{message.response}</p>
                        
                        {message.sources && message.sources.length > 0 && (
                          <div className="mt-3 pt-3 border-t">
                            <p className="text-sm font-medium text-gray-700 mb-2">Sources:</p>
                            <div className="space-y-1">
                              {message.sources.map((source) => (
                                <div key={source.id} className="text-sm text-blue-600">
                                  {source.title}
                                  {source.url && (
                                    <a href={source.url} target="_blank" rel="noopener noreferrer" className="ml-2 underline">
                                      View
                                    </a>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {message.confidence && (
                          <div className="mt-2 text-xs text-gray-500">
                            Confidence: {Math.round(message.confidence * 100)}%
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg p-3 max-w-[80%]">
                    <div className="flex items-center space-x-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Thinking...</span>
                    </div>
                    {progress > 0 && (
                      <div className="mt-2">
                        <Progress value={progress} className="h-2" />
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Input */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex space-x-2">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask a question about your documents..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button
              onClick={sendMessage}
              disabled={!query.trim() || isLoading}
              className="flex items-center space-x-2"
            >
              <Send className="h-4 w-4" />
              <span>Send</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ConversationalSearch;
