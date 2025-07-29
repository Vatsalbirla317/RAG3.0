
import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Terminal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { apiService } from '@/services/api';
import { Repository, Message, CodeSnippet } from '@/types';
import { CodeViewer } from './CodeViewer';
import ReactMarkdown from 'react-markdown';
import { motion } from 'framer-motion';

interface ChatBoxProps {
  repository: Repository;
  onSnippetAction?: (snippet: CodeSnippet, action: 'explain' | 'preview' | 'security' | 'visualize') => void;
}

export const ChatBox = ({ repository, onSnippetAction }: ChatBoxProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [typingText, setTypingText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const typewriterEffect = (text: string, callback: () => void) => {
    let i = 0;
    const timer = setInterval(() => {
      if (i < text.length) {
        setTypingText(text.slice(0, i + 1));
        i++;
      } else {
        clearInterval(timer);
        setTypingText('');
        callback();
      }
    }, 20);
  };

  const handleSendMessage = async () => {
    if (!currentMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: currentMessage,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);

    try {
      const response = await apiService.chat(currentMessage, 5);

      // Start typewriter effect
      typewriterEffect(response.answer, () => {
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: response.answer,
          role: 'assistant',
          timestamp: new Date(),
          codeSnippets: response.retrieved_code?.map((code, index) => ({
            id: `${Date.now()}_${index}`,
            content: code,
            code: code,
            language: 'typescript',
            filename: `snippet_${index + 1}.ts`,
            filePath: `snippet_${index + 1}.ts`,
          })),
        };

        setMessages(prev => [...prev, aiMessage]);
        setIsLoading(false);
      });
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Connection to the matrix failed. Please try again.',
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="h-[calc(100vh-200px)] flex flex-col">
      <Card className="flex-1 flex flex-col bg-[#111111]/95 border-[#00FF41] border-opacity-30 shadow-2xl shadow-[#00FF41]/10">
        <CardHeader className="border-b border-[#00FF41]/20">
          <CardTitle className="flex items-center space-x-2 text-[#00FFFF] glow-text font-mono">
            <Terminal className="h-5 w-5" />
            <span>Matrix Interface: {repository.name}</span>
            <div className="ml-auto flex space-x-1">
              <div className="w-2 h-2 rounded-full bg-[#FF00FF] animate-pulse"></div>
              <div className="w-2 h-2 rounded-full bg-[#00FFFF] animate-pulse" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-2 h-2 rounded-full bg-[#00FF41] animate-pulse" style={{ animationDelay: '0.4s' }}></div>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col p-0">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-[#0a0a0a]/50">
            {messages.length === 0 ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center py-12"
              >
                <Terminal className="h-16 w-16 mx-auto mb-4 text-[#00FFFF] glow-cyan" />
                <p className="text-[#00FF41] font-mono text-lg mb-2">Matrix connection established</p>
                <p className="text-[#00FF41]/70 font-mono text-sm">
                  <span className="text-[#00FFFF]">&gt;</span> Query the digital ghost of your codebase
                </p>
              </motion.div>
            ) : (
              messages.map((message, index) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, x: message.role === 'user' ? 20 : -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-4 font-mono ${
                      message.role === 'user'
                        ? 'bg-[#00FFFF]/10 border border-[#00FFFF]/30 text-[#00FFFF]'
                        : 'bg-[#111111]/80 border border-[#00FF41]/30 text-[#00FF41]'
                    }`}
                  >
                    {message.role === 'user' && (
                      <div className="text-xs text-[#00FFFF]/70 mb-2">USER@MATRIX:~$</div>
                    )}
                    {message.role === 'assistant' && (
                      <div className="text-xs text-[#00FF41]/70 mb-2">MATRIX_AI@GHOST:~$</div>
                    )}
                    <div className="prose prose-sm max-w-none">
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                    {message.codeSnippets && message.codeSnippets.length > 0 && (
                      <div className="mt-4 space-y-2">
                        {message.codeSnippets.map((snippet) => (
                          <CodeViewer
                            key={snippet.id}
                            snippet={snippet}
                            onAction={onSnippetAction}
                          />
                        ))}
                      </div>
                    )}
                  </div>
                </motion.div>
              ))
            )}
            
            {/* Typing indicator */}
            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start"
              >
                <div className="bg-[#111111]/80 border border-[#00FF41]/30 rounded-lg p-4 font-mono">
                  <div className="text-xs text-[#00FF41]/70 mb-2">MATRIX_AI@GHOST:~$</div>
                  {typingText ? (
                    <div className="text-[#00FF41]">{typingText}<span className="animate-pulse">|</span></div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-[#00FF41] rounded-full animate-matrix-loading"></div>
                        <div className="w-2 h-2 bg-[#00FF41] rounded-full animate-matrix-loading" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-2 h-2 bg-[#00FF41] rounded-full animate-matrix-loading" style={{ animationDelay: '0.4s' }}></div>
                      </div>
                      <span className="text-[#00FF41]/70">Accessing digital ghost...</span>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-[#00FF41]/20 bg-[#111111]/80">
            <div className="flex space-x-2">
              <div className="flex-1 relative">
                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#00FFFF] font-mono text-sm">
                  &gt;
                </span>
                <Input
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Query the matrix..."
                  disabled={isLoading}
                  className="matrix-input pl-8 font-mono"
                />
              </div>
              <Button
                onClick={handleSendMessage}
                disabled={isLoading || !currentMessage.trim()}
                className="neon-button px-4"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
