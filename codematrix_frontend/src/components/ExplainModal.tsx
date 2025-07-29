
import { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Eye, BookOpen, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CodeSnippet } from '../types';
import { apiService } from '../services/api';
import ReactMarkdown from 'react-markdown';
import toast from 'react-hot-toast';

interface ExplainModalProps {
  snippet: CodeSnippet;
  isOpen: boolean;
  onClose: () => void;
}

export const ExplainModal = ({ snippet, isOpen, onClose }: ExplainModalProps) => {
  const [complexity, setComplexity] = useState<string>('adult');
  const [explanation, setExplanation] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const handleExplain = async () => {
    setIsLoading(true);
    try {
      const response = await apiService.explainCode(snippet.code, complexity);
      setExplanation(response.explanation);
    } catch (error) {
      toast.error('Failed to generate explanation');
      console.error('Explanation error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getComplexityIcon = () => {
    switch (complexity) {
      case '5-year-old':
        return '🧒';
      case '10-year-old':
        return '👦';
      case 'teenager':
        return '🧑';
      case 'adult':
        return '👨‍💻';
      default:
        return '💻';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-4xl max-h-[90vh] bg-background rounded-lg shadow-xl"
      >
        <Card className="h-full">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
            <CardTitle className="flex items-center space-x-2">
              <Eye className="h-5 w-5" />
              <span>Explain Like I'm...</span>
              <span className="text-2xl">{getComplexityIcon()}</span>
            </CardTitle>
            
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-8 w-8"
            >
              <X className="h-4 w-4" />
            </Button>
          </CardHeader>
          
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                File: {snippet.filePath}
              </div>
              
              <div className="flex items-center space-x-2">
                <Select value={complexity} onValueChange={setComplexity}>
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="5-year-old">🧒 5 Year Old</SelectItem>
                    <SelectItem value="10-year-old">👦 10 Year Old</SelectItem>
                    <SelectItem value="teenager">🧑 Teenager</SelectItem>
                    <SelectItem value="adult">👨‍💻 Adult</SelectItem>
                  </SelectContent>
                </Select>
                
                <Button
                  onClick={handleExplain}
                  disabled={isLoading}
                  variant="default"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Explaining...
                    </>
                  ) : (
                    <>
                      <BookOpen className="h-4 w-4 mr-2" />
                      Explain Code
                    </>
                  )}
                </Button>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 h-96">
              <div className="space-y-2">
                <h3 className="font-medium text-sm">Original Code:</h3>
                <div className="border rounded-lg p-3 bg-muted font-mono text-sm overflow-auto h-full">
                  <pre className="whitespace-pre-wrap">{snippet.code}</pre>
                </div>
              </div>
              
              <div className="space-y-2">
                <h3 className="font-medium text-sm">Explanation:</h3>
                <div className="border rounded-lg p-3 bg-background overflow-auto h-full">
                  {!explanation && !isLoading && (
                    <div className="text-center text-muted-foreground h-full flex items-center justify-center">
                      <div>
                        <BookOpen className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p>Click "Explain Code" to get an explanation</p>
                      </div>
                    </div>
                  )}
                  
                  {isLoading && (
                    <div className="text-center text-muted-foreground h-full flex items-center justify-center">
                      <div>
                        <Loader2 className="h-8 w-8 mx-auto mb-2 animate-spin" />
                        <p>AI is analyzing your code...</p>
                      </div>
                    </div>
                  )}
                  
                  {explanation && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="prose prose-sm max-w-none dark:prose-invert"
                    >
                      <ReactMarkdown>
                        {explanation}
                      </ReactMarkdown>
                    </motion.div>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};
