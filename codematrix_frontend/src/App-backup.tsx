// Backup of original App
import { useState } from 'react';
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

const queryClient = new QueryClient();

function App() {
  const { theme, toggleTheme } = useTheme();
  const [repository, setRepository] = useState<Repository | null>(null);
  const [selectedSnippet, setSelectedSnippet] = useState<CodeSnippet | null>(null);
  const [activeModal, setActiveModal] = useState<'explain' | 'preview' | 'security' | 'visualize' | null>(null);

  const handleRepositoryCloned = (repo: Repository) => {
    setRepository(repo);
  };

  const handleSnippetAction = (snippet: CodeSnippet, action: 'explain' | 'preview' | 'security' | 'visualize') => {
    setSelectedSnippet(snippet);
    setActiveModal(action);
  };

  const closeModal = () => {
    setActiveModal(null);
    setSelectedSnippet(null);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-[#111111] text-[#00FF41] matrix-bg font-mono">
        <Header theme={theme} onThemeToggle={toggleTheme} />
        
        {!repository ? (
          <main className="flex flex-col items-center justify-center min-h-screen w-full px-4">
            {/* Central Branding Section */}
            <div className="flex flex-col items-center mb-12">
              <div className="relative mb-6">
                <div className="p-6 bg-[#0a0a0a] border-2 border-[#00FFFF] rounded-lg shadow-[0_0_25px_rgba(0,255,255,0.4)]">
                  <Terminal size={48} className="text-[#00FFFF] glow-cyan" />
                </div>
                <Zap size={24} className="absolute -top-2 -right-2 text-[#FF00FF] animate-pulse glow-magenta" />
              </div>
              <h1 className="text-7xl font-bold text-[#00FFFF] glow-text mb-4 tracking-wider">
                CodeMatrix
              </h1>
              <p className="text-2xl text-[#00FF41] glow-text mb-6 tracking-wide">
                Your Code's Digital Ghost
              </p>
              <div className="text-[#00FF41] font-mono text-lg flex items-center">
                <span className="text-[#00FFFF] mr-2">&gt;</span>
                <span>Enter the matrix of your codebase</span>
                <span className="animate-pulse ml-1 text-[#00FFFF]">|</span>
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
              <TabsList className="grid w-full grid-cols-5 bg-[#111111]/90 border border-[#00FF41]/30">
                <TabsTrigger 
                  value="chat" 
                  className="data-[state=active]:bg-[#00FFFF]/20 data-[state=active]:text-[#00FFFF] text-[#00FF41] font-mono hover:bg-[#00FF41]/10"
                >
                  Matrix Chat
                </TabsTrigger>
                <TabsTrigger 
                  value="security" 
                  className="data-[state=active]:bg-[#FF00FF]/20 data-[state=active]:text-[#FF00FF] text-[#00FF41] font-mono hover:bg-[#FF00FF]/10"
                >
                  Security Scan
                </TabsTrigger>
                <TabsTrigger 
                  value="visualize" 
                  className="data-[state=active]:bg-[#00FFFF]/20 data-[state=active]:text-[#00FFFF] text-[#00FF41] font-mono hover:bg-[#00FFFF]/10"
                >
                  Code Matrix
                </TabsTrigger>
                <TabsTrigger 
                  value="preview" 
                  className="data-[state=active]:bg-[#00FF41]/20 data-[state=active]:text-[#00FF41] text-[#00FF41] font-mono hover:bg-[#00FF41]/10"
                >
                  Live Ghost
                </TabsTrigger>
                <TabsTrigger 
                  value="explain" 
                  className="data-[state=active]:bg-[#00FFFF]/20 data-[state=active]:text-[#00FFFF] text-[#00FF41] font-mono hover:bg-[#00FFFF]/10"
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
              background: '#0a0a0a',
              color: '#00FF41',
              border: '1px solid #00FF41',
              fontFamily: 'Fira Code, monospace',
              boxShadow: '0 0 20px rgba(0, 255, 65, 0.3)',
            },
          }}
        />
      </div>
    </QueryClientProvider>
  );
}

export default App;
