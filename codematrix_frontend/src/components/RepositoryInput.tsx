
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Download, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { apiService } from '../services/api';
import { Repository, StatusResponse } from '../types';
import toast from 'react-hot-toast';

interface RepositoryInputProps {
  onRepositoryCloned: (repo: Repository) => void;
}

export const RepositoryInput = ({ onRepositoryCloned }: RepositoryInputProps) => {
  const [repoUrl, setRepoUrl] = useState('');
  const [isCloning, setIsCloning] = useState(false);
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [currentRepo, setCurrentRepo] = useState<Repository | null>(null);

  const isValidGitHubUrl = (url: string) => {
    // More robust GitHub URL validation
    const pattern = /^https:\/\/github\.com\/[a-zA-Z0-9._-]+\/[a-zA-Z0-9._-]+\/?$/;
    return pattern.test(url.trim()) && url.length > 0;
  };

  const pollStatus = async () => {
    try {
      const statusResponse = await apiService.getStatus();
      setStatus(statusResponse);
      
      if (statusResponse.status === 'ready') {
        // Don't set isCloning to false - let parent component handle unmounting
        const repo: Repository = {
          name: currentRepo?.name || repoUrl.split('/').pop() || 'Unknown',
          url: currentRepo?.url || repoUrl,
          path: currentRepo?.path || '',
          status: 'ready' as const
        };
        
        if (currentRepo) {
          const updatedRepo = { ...currentRepo, status: 'ready' as const };
          setCurrentRepo(updatedRepo);
        }
        
        // Always call the callback when ready
        onRepositoryCloned(repo);
        
        toast.success('Matrix connection established!', {
          style: {
            background: '#0a0a0a',
            color: '#00FF41',
            border: '1px solid #00FF41',
            boxShadow: '0 0 20px rgba(0, 255, 65, 0.3)',
          },
        });
      } else if (statusResponse.status === 'error') {
        // Only set isCloning to false on error so user can retry
        setIsCloning(false);
        toast.error('Matrix connection failed', {
          style: {
            background: '#0a0a0a',
            color: '#FF00FF',
            border: '1px solid #FF00FF',
            boxShadow: '0 0 20px rgba(255, 0, 255, 0.3)',
          },
        });
      } else if (statusResponse.status === 'idle') {
        // If we get idle status while cloning, something went wrong
        setIsCloning(false);
      }
    } catch (error) {
      console.error('Error polling status:', error);
      setIsCloning(false); // Stop polling on error
    }
  };

  useEffect(() => {
    let interval: NodeJS.Timeout | undefined;
    if (isCloning) {
      interval = setInterval(pollStatus, 1000);
    }
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [isCloning]);

  const handleClone = async () => {
    // Prevent multiple clicks
    if (isCloning) {
      return;
    }

    if (!isValidGitHubUrl(repoUrl)) {
      toast.error('Please enter a valid GitHub repository URL', {
        style: {
          background: '#0a0a0a',
          color: '#FF00FF',
          border: '1px solid #FF00FF',
          boxShadow: '0 0 20px rgba(255, 0, 255, 0.3)',
        },
      });
      return;
    }

    setIsCloning(true);
    
    try {
      const response = await apiService.cloneRepository(repoUrl);
      
      if (response.success) {
        const repo: Repository = {
          name: repoUrl.split('/').pop() || 'Unknown',
          url: repoUrl,
          path: response.repo_path,
          status: 'cloning'
        };
        
        setCurrentRepo(repo);
        toast.success('Initiating matrix connection...', {
          style: {
            background: '#0a0a0a',
            color: '#00FFFF',
            border: '1px solid #00FFFF',
            boxShadow: '0 0 20px rgba(0, 255, 255, 0.3)',
          },
        });
      } else {
        setIsCloning(false);
        toast.error(response.message || 'Failed to establish connection');
      }
    } catch (error) {
      setIsCloning(false);
      toast.error('Matrix connection error');
      console.error('Clone error:', error);
    }
  };

  const getStatusIcon = () => {
    if (!status) return null;
    
    switch (status.status) {
      case 'cloning':
        return <Download className="h-4 w-4 animate-pulse text-[#00FFFF]" />;
      case 'indexing':
        return <Loader2 className="h-4 w-4 animate-spin text-[#00FF41]" />;
      case 'ready':
        return <CheckCircle className="h-4 w-4 text-[#00FF41] glow-green" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-[#FF00FF] glow-magenta" />;
      default:
        return null;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="w-full"
    >
      <Card className="bg-[#0a0a0a]/70 border-2 border-[#00FFFF] rounded-lg shadow-[0_0_30px_rgba(0,255,255,0.3)] backdrop-blur">
        <CardHeader className="pb-4">
          <CardTitle className="text-[#00FF41] flex items-center gap-2 font-mono text-lg">
            <span className="text-[#00FFFF]">&gt;</span>
            <span className="glow-text">Initialize Matrix Connection</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-3">
            <Input
              type="text"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/user/repo"
              disabled={isCloning}
              className="flex-grow matrix-input font-mono text-[#00FF41] bg-[#111111]/80 border-2 border-[#00FFFF]/50 focus:border-[#00FF41] focus:shadow-[0_0_15px_rgba(0,255,65,0.3)] placeholder:text-[#00FF41]/50"
              onKeyPress={(e) => e.key === 'Enter' && !isCloning && handleClone()}
            />
            <Button
              onClick={handleClone}
              disabled={isCloning || !repoUrl}
              className="bg-[#00FF41] text-[#0a0a0a] font-bold hover:bg-[#00FF41]/80 border-2 border-[#00FF41] hover:shadow-[0_0_20px_rgba(0,255,65,0.5)] transition-all duration-300 font-mono px-6"
            >
              {isCloning ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Connecting...
                </>
              ) : (
                <>
                  <Download className="mr-2 h-4 w-4" />
                  Enter Matrix
                </>
              )}
            </Button>
          </div>

          {status && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="border-t border-[#00FFFF]/20 pt-4 space-y-3"
            >
              <div className="flex items-center gap-3 text-sm font-mono">
                {getStatusIcon()}
                <span className="text-[#00FFFF] uppercase tracking-wider font-bold">
                  {status.status}
                </span>
                <span className="text-[#00FF41]/50">•</span>
                <span className="text-[#00FF41]/80">{status.message}</span>
              </div>
              
              {status.progress > 0 && (
                <div className="space-y-2">
                  <Progress 
                    value={status.progress} 
                    className="h-2 bg-[#111111] border border-[#00FF41]/30" 
                  />
                  <div className="text-xs text-[#00FF41]/70 text-right font-mono">
                    {status.progress}% digital integration complete
                  </div>
                </div>
              )}
              
              {isCloning && (
                <div className="flex justify-center py-2">
                  <div className="text-[#00FF41] font-mono text-xs opacity-60 animate-pulse">
                    01110000 01110010 01101111 01100011 01100101 01110011 01110011 01101001 01101110 01100111
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {currentRepo && currentRepo.status === 'ready' && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex items-center gap-3 p-4 bg-[#111111]/50 rounded-lg border border-[#00FF41]/50 shadow-[0_0_15px_rgba(0,255,65,0.2)]"
            >
              <CheckCircle className="h-5 w-5 text-[#00FF41] glow-green" />
              <div className="font-mono">
                <div className="font-bold text-[#00FFFF] glow-text">
                  Connection Established
                </div>
                <div className="text-sm text-[#00FF41]">
                  {currentRepo.name} integrated into the matrix
                </div>
              </div>
            </motion.div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};
