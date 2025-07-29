
import { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Play, Smartphone, Tablet, Monitor, Code, Eye, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CodeSnippet } from '../types';
import { Editor } from '@monaco-editor/react';
import { useTheme } from 'next-themes';
import toast from 'react-hot-toast';

interface LivePreviewProps {
  snippet: CodeSnippet;
  isOpen: boolean;
  onClose: () => void;
}

type ViewportSize = 'mobile' | 'tablet' | 'desktop';

export const LivePreview = ({ snippet, isOpen, onClose }: LivePreviewProps) => {
  const [viewportSize, setViewportSize] = useState<ViewportSize>('desktop');
  const [htmlCode, setHtmlCode] = useState(snippet.code);
  const [cssCode, setCssCode] = useState('');
  const [jsCode, setJsCode] = useState('');
  const [activeTab, setActiveTab] = useState('html');
  const { theme } = useTheme();

  const viewportSizes = {
    mobile: { width: '375px', height: '667px', icon: Smartphone },
    tablet: { width: '768px', height: '1024px', icon: Tablet },
    desktop: { width: '100%', height: '100%', icon: Monitor }
  };

  const generatePreviewHtml = () => {
    return `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Live Preview</title>
        <style>
          body { margin: 0; padding: 20px; font-family: Arial, sans-serif; }
          ${cssCode}
        </style>
      </head>
      <body>
        ${htmlCode}
        <script>
          try {
            ${jsCode}
          } catch (error) {
            console.error('JavaScript Error:', error);
          }
        </script>
      </body>
      </html>
    `;
  };

  const downloadPreview = () => {
    const htmlContent = generatePreviewHtml();
    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'preview.html';
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Preview downloaded!');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-7xl max-h-[95vh] bg-background rounded-lg shadow-xl"
      >
        <Card className="h-full">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
            <CardTitle className="flex items-center space-x-2">
              <Play className="h-5 w-5" />
              <span>Live Preview</span>
              <span className="text-sm font-normal text-muted-foreground">
                {snippet.filePath}
              </span>
            </CardTitle>
            
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1 mr-4">
                {Object.entries(viewportSizes).map(([key, config]) => {
                  const Icon = config.icon;
                  return (
                    <Button
                      key={key}
                      variant={viewportSize === key ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setViewportSize(key as ViewportSize)}
                      className="h-8 px-2"
                    >
                      <Icon className="h-3 w-3" />
                    </Button>
                  );
                })}
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={downloadPreview}
                className="h-8 px-2"
              >
                <Download className="h-3 w-3 mr-1" />
                Download
              </Button>
              
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="h-8 w-8"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          
          <CardContent className="p-0 h-[calc(100%-80px)]">
            <div className="grid grid-cols-1 lg:grid-cols-2 h-full">
              {/* Code Editor */}
              <div className="border-r">
                <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="html" className="text-xs">
                      <Code className="h-3 w-3 mr-1" />
                      HTML
                    </TabsTrigger>
                    <TabsTrigger value="css" className="text-xs">
                      <Code className="h-3 w-3 mr-1" />
                      CSS
                    </TabsTrigger>
                    <TabsTrigger value="js" className="text-xs">
                      <Code className="h-3 w-3 mr-1" />
                      JS
                    </TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="html" className="h-[calc(100%-48px)]">
                    <Editor
                      height="100%"
                      language="html"
                      value={htmlCode}
                      onChange={(value) => setHtmlCode(value || '')}
                      theme={theme === 'dark' ? 'vs-dark' : 'vs-light'}
                      options={{
                        minimap: { enabled: false },
                        fontSize: 14,
                        lineNumbers: 'on',
                        automaticLayout: true,
                        wordWrap: 'on',
                      }}
                    />
                  </TabsContent>
                  
                  <TabsContent value="css" className="h-[calc(100%-48px)]">
                    <Editor
                      height="100%"
                      language="css"
                      value={cssCode}
                      onChange={(value) => setCssCode(value || '')}
                      theme={theme === 'dark' ? 'vs-dark' : 'vs-light'}
                      options={{
                        minimap: { enabled: false },
                        fontSize: 14,
                        lineNumbers: 'on',
                        automaticLayout: true,
                        wordWrap: 'on',
                      }}
                    />
                  </TabsContent>
                  
                  <TabsContent value="js" className="h-[calc(100%-48px)]">
                    <Editor
                      height="100%"
                      language="javascript"
                      value={jsCode}
                      onChange={(value) => setJsCode(value || '')}
                      theme={theme === 'dark' ? 'vs-dark' : 'vs-light'}
                      options={{
                        minimap: { enabled: false },
                        fontSize: 14,
                        lineNumbers: 'on',
                        automaticLayout: true,
                        wordWrap: 'on',
                      }}
                    />
                  </TabsContent>
                </Tabs>
              </div>
              
              {/* Preview Panel */}
              <div className="flex flex-col h-full">
                <div className="flex items-center justify-between p-3 border-b">
                  <div className="flex items-center space-x-2">
                    <Eye className="h-4 w-4" />
                    <span className="text-sm font-medium">Live Preview</span>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {viewportSizes[viewportSize].width} × {viewportSizes[viewportSize].height}
                  </div>
                </div>
                
                <div className="flex-1 flex items-center justify-center p-4 bg-muted/30">
                  <div
                    className="bg-white rounded-lg shadow-lg overflow-hidden"
                    style={{
                      width: viewportSizes[viewportSize].width,
                      height: viewportSizes[viewportSize].height,
                      maxWidth: '100%',
                      maxHeight: '100%',
                    }}
                  >
                    <iframe
                      srcDoc={generatePreviewHtml()}
                      className="w-full h-full border-0"
                      title="Live Preview"
                      sandbox="allow-scripts allow-same-origin"
                    />
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};
