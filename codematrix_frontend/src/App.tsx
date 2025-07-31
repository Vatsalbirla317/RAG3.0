import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { useTheme } from './hooks/useTheme';
import { Header } from './components/Header';
import { RepositoryInput } from './components/RepositoryInput';
import { ChatBox } from './components/ChatBox';
import { ExplainModal } from './components/ExplainModal';
import { LivePreview } from './components/LivePreview';
import { SecurityScanner } from './components/SecurityScanner';
import { VisualizationPanel } from './components/VisualizationPanel';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Terminal, Zap } from 'lucide-react';
import { Repository, CodeSnippet } from './types';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      refetchOnWindowFocus: false,
    },
  },
});

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('App Error:', error, errorInfo);
    this.setState({ errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-background text-destructive flex items-center justify-center">
          <div className="text-center p-8 max-w-4xl">
            <h1 className="text-4xl font-bold mb-4">⚠️ Matrix Error</h1>
            <p className="text-lg mb-4">Something went wrong in the matrix</p>
            <div className="text-sm bg-muted p-4 rounded text-left overflow-auto max-h-96">
              <h3 className="font-bold mb-2">Error Details:</h3>
              <pre className="whitespace-pre-wrap">{this.state.error?.toString()}</pre>
              {this.state.errorInfo && (
                <>
                  <h3 className="font-bold mb-2 mt-4">Component Stack:</h3>
                  <pre className="whitespace-pre-wrap">{this.state.errorInfo.componentStack}</pre>
                </>
              )}
            </div>
            <button 
              onClick={() => window.location.reload()} 
              className="mt-4 px-4 py-2 bg-destructive text-destructive-foreground rounded hover:bg-destructive/80"
            >
              Reload Matrix
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

function App() {
  const [isClient, setIsClient] = useState(false);
  const [isReady, setIsReady] = useState(false);
  const { theme, toggleTheme } = useTheme();
  const [repository, setRepository] = useState<Repository | null>(null);
  const [selectedSnippet, setSelectedSnippet] = useState<CodeSnippet | null>(null);
  const [activeModal, setActiveModal] = useState<'explain' | 'preview' | 'security' | 'visualize' | null>(null);
  
  // Ensure hydration safety
  useEffect(() => {
    setIsClient(true);
    // Add a small delay to ensure everything is properly initialized
    const timer = setTimeout(() => {
      setIsReady(true);
      console.log('App ready');
    }, 100);
    
    return () => clearTimeout(timer);
  }, []);

  const handleRepositoryCloned = (repo: Repository) => {
    console.log('Repository cloned:', repo);
    setRepository(repo);
  };

  const handleSnippetAction = (snippet: CodeSnippet, action: 'explain' | 'preview' | 'security' | 'visualize') => {
    console.log('Snippet action:', action, snippet);
    setSelectedSnippet(snippet);
    setActiveModal(action);
  };

  const closeModal = () => {
    setActiveModal(null);
    setSelectedSnippet(null);
  };
  
  // Show loading screen until client-side and ready
  if (!isClient || !isReady) {
    return (
      <div className="min-h-screen bg-background text-primary flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-pulse">⚡</div>
          <h1 className="text-4xl font-bold mb-2">CodeMatrix</h1>
          <p className="animate-pulse">Initializing the Matrix...</p>
          <div className="mt-4 text-sm opacity-60">
            {!isClient ? 'Loading client...' : 'Starting systems...'}
          </div>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <div className={`min-h-screen bg-background text-foreground matrix-bg font-mono ${theme}`}>
          <Header theme={theme} onThemeToggle={toggleTheme} />
          
          {!repository ? (
            <main className="flex flex-col items-center justify-center min-h-screen w-full px-4">
              {/* Central Branding Section */}
              <div className="flex flex-col items-center mb-12">
                <div className="relative mb-6">
                  <div className="p-6 bg-card border-2 border-matrix-cyan rounded-lg shadow-[0_0_25px_rgba(0,255,255,0.4)]">
                    <Terminal size={48} className="text-matrix-cyan glow-cyan" />
                  </div>
                  <Zap size={24} className="absolute -top-2 -right-2 text-matrix-magenta animate-pulse glow-magenta" />
                </div>
                <h1 className="text-7xl font-bold text-matrix-cyan glow-text mb-4 tracking-wider">
                  CodeMatrix
                </h1>
                <p className="text-2xl text-matrix-green glow-text mb-6 tracking-wide">
                  Your Code's Digital Ghost
                </p>
                <div className="text-matrix-green font-mono text-lg flex items-center">
                  <span className="text-matrix-cyan mr-2">&gt;</span>
                  <span>Enter the matrix of your codebase</span>
                  <span className="animate-pulse ml-1 text-matrix-cyan">|</span>
                </div>
              </div>

              {/* Repository Input */}
              <div className="w-full max-w-3xl">
                <RepositoryInput onRepositoryCloned={handleRepositoryCloned} />
              </div>
            </main>
          ) : (
            <main className="container mx-auto px-4 py-6">
              <Tabs defaultValue="chat" className="w-full">
                <TabsList className="grid w-full grid-cols-5 bg-card/90 border border-matrix-green/30">
                  <TabsTrigger 
                    value="chat" 
                    className="data-[state=active]:bg-matrix-cyan/20 data-[state=active]:text-matrix-cyan text-matrix-green font-mono hover:bg-matrix-green/10"
                  >
                    Matrix Chat
                  </TabsTrigger>
                  <TabsTrigger 
                    value="security" 
                    className="data-[state=active]:bg-matrix-magenta/20 data-[state=active]:text-matrix-magenta text-matrix-green font-mono hover:bg-matrix-magenta/10"
                  >
                    Security Scan
                  </TabsTrigger>
                  <TabsTrigger 
                    value="visualize" 
                    className="data-[state=active]:bg-matrix-cyan/20 data-[state=active]:text-matrix-cyan text-matrix-green font-mono hover:bg-matrix-cyan/10"
                  >
                    Code Matrix
                  </TabsTrigger>
                  <TabsTrigger 
                    value="preview" 
                    className="data-[state=active]:bg-matrix-green/20 data-[state=active]:text-matrix-green text-matrix-green font-mono hover:bg-matrix-green/10"
                  >
                    Live Ghost
                  </TabsTrigger>
                  <TabsTrigger 
                    value="explain" 
                    className="data-[state=active]:bg-matrix-cyan/20 data-[state=active]:text-matrix-cyan text-matrix-green font-mono hover:bg-matrix-cyan/10"
                  >
                    Code Oracle
                  </TabsTrigger>
                </TabsList>
                
                <TabsContent value="chat" className="mt-6">
                  <ChatBox 
                    repository={repository} 
                    onSnippetAction={handleSnippetAction}
                  />
                </TabsContent>
                
                <TabsContent value="security" className="mt-6">
                  <SecurityScanner 
                    snippet={null}
                    isOpen={true}
                    onClose={() => {}}
                  />
                </TabsContent>
                
                <TabsContent value="visualize" className="mt-6">
                  <VisualizationPanel 
                    snippet={null}
                    isOpen={true}
                    onClose={() => {}}
                  />
                </TabsContent>
                
                <TabsContent value="preview" className="mt-6">
                  <LivePreview 
                    snippet={null}
                    isOpen={true}
                    onClose={() => {}}
                  />
                </TabsContent>
                
                <TabsContent value="explain" className="mt-6">
                  <ExplainModal 
                    snippet={null}
                    isOpen={true}
                    onClose={() => {}}
                  />
                </TabsContent>
              </Tabs>
            </main>
          )}
          
          {selectedSnippet && activeModal === 'explain' && (
            <ExplainModal
              snippet={selectedSnippet}
              isOpen={true}
              onClose={closeModal}
            />
          )}
          
          {selectedSnippet && activeModal === 'preview' && (
            <LivePreview
              snippet={selectedSnippet}
              isOpen={true}
              onClose={closeModal}
            />
          )}
          
          {selectedSnippet && activeModal === 'security' && (
            <SecurityScanner
              snippet={selectedSnippet}
              isOpen={true}
              onClose={closeModal}
            />
          )}
          
          {selectedSnippet && activeModal === 'visualize' && (
            <VisualizationPanel
              snippet={selectedSnippet}
              isOpen={true}
              onClose={closeModal}
            />
          )}
          
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: 'var(--matrix-dark)',
                color: 'var(--matrix-green)',
                border: '1px solid var(--matrix-green)',
                fontFamily: 'Fira Code, monospace',
                boxShadow: '0 0 20px rgba(0, 255, 65, 0.3)',
              },
            }}
          />
        </div>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
