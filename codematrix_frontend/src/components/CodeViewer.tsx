
import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Copy, 
  ChevronDown, 
  ChevronRight, 
  FileText, 
  Eye, 
  Shield, 
  Network, 
  Play 
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark, oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { CodeSnippet } from '../types';
import { useTheme } from 'next-themes';
import toast from 'react-hot-toast';

interface CodeViewerProps {
  snippet: CodeSnippet;
  onAction?: (snippet: CodeSnippet, action: 'explain' | 'preview' | 'security' | 'visualize') => void;
}

export const CodeViewer = ({ snippet, onAction }: CodeViewerProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const { theme } = useTheme();

  const copyToClipboard = () => {
    navigator.clipboard.writeText(snippet.code);
    toast.success('Code copied to clipboard!');
  };

  const getLanguageFromPath = (filePath: string) => {
    const extension = filePath.split('.').pop()?.toLowerCase();
    const langMap: { [key: string]: string } = {
      js: 'javascript',
      jsx: 'javascript',
      ts: 'typescript',
      tsx: 'typescript',
      py: 'python',
      java: 'java',
      cpp: 'cpp',
      c: 'c',
      css: 'css',
      html: 'html',
      json: 'json',
      yaml: 'yaml',
      yml: 'yaml',
      md: 'markdown',
      sql: 'sql',
      sh: 'bash',
      php: 'php',
      rb: 'ruby',
      go: 'go',
      rs: 'rust',
    };
    return langMap[extension || ''] || 'text';
  };

  const isPreviewable = (filePath: string) => {
    const extension = filePath.split('.').pop()?.toLowerCase();
    return ['html', 'css', 'js', 'jsx', 'ts', 'tsx'].includes(extension || '');
  };

  const language = getLanguageFromPath(snippet.filePath);
  const canPreview = isPreviewable(snippet.filePath);

  return (
    <Card className="w-full bg-[#111111] border-[#00FF41] border-opacity-30 shadow-lg shadow-[#00FF41]/20">
      <CardHeader className="pb-3 border-b border-[#00FF41]/20">
        <CardTitle className="flex items-center justify-between text-[#00FF41]">
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-0 h-6 w-6 text-[#00FF41] hover:bg-[#00FF41]/10"
            >
              {isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </Button>
            <FileText className="h-4 w-4 text-[#00FFFF]" />
            <span className="text-sm font-mono text-[#00FF41] glow-text">{snippet.filePath}</span>
          </div>
          
          <div className="flex items-center space-x-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onAction?.(snippet, 'explain')}
              className="h-8 px-2 text-[#00FFFF] hover:bg-[#00FFFF]/10 hover:glow-cyan"
            >
              <Eye className="h-3 w-3 mr-1" />
              Explain
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onAction?.(snippet, 'visualize')}
              className="h-8 px-2 text-[#00FFFF] hover:bg-[#00FFFF]/10 hover:glow-cyan"
            >
              <Network className="h-3 w-3 mr-1" />
              Visualize
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onAction?.(snippet, 'security')}
              className="h-8 px-2 text-[#FF00FF] hover:bg-[#FF00FF]/10 hover:glow-magenta"
            >
              <Shield className="h-3 w-3 mr-1" />
              Security
            </Button>
            
            {canPreview && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onAction?.(snippet, 'preview')}
                className="h-8 px-2 text-[#00FFFF] hover:bg-[#00FFFF]/10 hover:glow-cyan"
              >
                <Play className="h-3 w-3 mr-1" />
                Preview
              </Button>
            )}
            
            <Button
              variant="ghost"
              size="sm"
              onClick={copyToClipboard}
              className="h-8 px-2 text-[#00FF41] hover:bg-[#00FF41]/10 hover:glow-green"
            >
              <Copy className="h-3 w-3" />
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      
      {isExpanded && (
        <CardContent className="pt-0">
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="rounded-lg overflow-hidden border border-[#00FF41]/30 bg-[#0a0a0a]">
              <SyntaxHighlighter
                language={language}
                style={oneDark}
                customStyle={{
                  margin: 0,
                  background: '#0a0a0a',
                  fontSize: '14px',
                  lineHeight: '1.5',
                  fontFamily: 'Fira Code, monospace',
                }}
                showLineNumbers
                wrapLines
                wrapLongLines
              >
                {snippet.code}
              </SyntaxHighlighter>
            </div>
          </motion.div>
        </CardContent>
      )}
    </Card>
  );
};
