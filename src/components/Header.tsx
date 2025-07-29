
import { useState } from 'react';
import { Moon, Sun, Terminal, Settings, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface HeaderProps {
  theme: 'light' | 'dark';
  onThemeToggle: () => void;
}

export const Header = ({ theme, onThemeToggle }: HeaderProps) => {
  const [showSettings, setShowSettings] = useState(false);

  return (
    <header className="fixed top-0 left-0 w-full z-50 p-4 border-b border-[#00FF41]/30 bg-[#111111]/95 backdrop-blur">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <Terminal className="text-[#00FF41] glow-green" size={32} />
            <div>
              <h1 className="text-xl font-bold text-[#00FFFF] glow-text font-mono">CodeMatrix</h1>
              <p className="text-xs text-[#00FF41] font-mono opacity-80">Your Code's Digital Ghost</p>
            </div>
          </div>
          <span className="text-[#00FF41]/50">•</span>
          <p className="text-sm text-[#00FF41]/80 font-mono animate-pulse">AI-Powered Code Analysis</p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={onThemeToggle}
            className="h-9 w-9 text-[#00FF41] hover:bg-[#00FF41]/10 hover:glow-green"
          >
            {theme === 'light' ? (
              <Moon className="h-4 w-4" />
            ) : (
              <Sun className="h-4 w-4" />
            )}
          </Button>
          
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setShowSettings(!showSettings)}
            className="h-9 w-9 text-[#00FFFF] hover:bg-[#00FFFF]/10 hover:glow-cyan"
          >
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  );
};
