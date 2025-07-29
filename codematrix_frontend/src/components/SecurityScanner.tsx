
import { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Shield, AlertTriangle, CheckCircle, XCircle, Info } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { CodeSnippet, SecurityIssue } from '../types';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

interface SecurityScannerProps {
  snippet: CodeSnippet;
  isOpen: boolean;
  onClose: () => void;
}

export const SecurityScanner = ({ snippet, isOpen, onClose }: SecurityScannerProps) => {
  const [issues, setIssues] = useState<SecurityIssue[]>([]);
  const [riskLevel, setRiskLevel] = useState<string>('');
  const [isScanning, setIsScanning] = useState(false);

  const severityColors = {
    low: 'bg-green-100 text-green-800 border-green-300',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    high: 'bg-orange-100 text-orange-800 border-orange-300',
    critical: 'bg-red-100 text-red-800 border-red-300'
  };

  const severityIcons = {
    low: CheckCircle,
    medium: Info,
    high: AlertTriangle,
    critical: XCircle
  };

  const handleScan = async () => {
    setIsScanning(true);
    try {
      const response = await apiService.securityScan(snippet.filePath);
      setIssues(response.issues);
      setRiskLevel(response.risk_level);
    } catch (error) {
      toast.error('Failed to scan for security issues');
      console.error('Security scan error:', error);
    } finally {
      setIsScanning(false);
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
              <Shield className="h-5 w-5" />
              <span>Security Scanner</span>
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
              <div>
                <div className="text-sm font-medium">File: {snippet.filePath}</div>
                {riskLevel && (
                  <Badge 
                    variant="outline" 
                    className={`mt-2 ${severityColors[riskLevel as keyof typeof severityColors]}`}
                  >
                    Risk Level: {riskLevel.toUpperCase()}
                  </Badge>
                )}
              </div>
              
              <Button
                onClick={handleScan}
                disabled={isScanning}
                variant="default"
              >
                {isScanning ? (
                  <>
                    <Shield className="h-4 w-4 mr-2 animate-pulse" />
                    Scanning...
                  </>
                ) : (
                  <>
                    <Shield className="h-4 w-4 mr-2" />
                    Scan for Issues
                  </>
                )}
              </Button>
            </div>
            
            <ScrollArea className="h-96">
              {issues.length === 0 && !isScanning && (
                <div className="text-center text-muted-foreground py-8">
                  <Shield className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Click "Scan for Issues" to analyze this code for security vulnerabilities</p>
                </div>
              )}
              
              {issues.length > 0 && (
                <div className="space-y-3">
                  {issues.map((issue, index) => {
                    const Icon = severityIcons[issue.severity];
                    return (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="border rounded-lg p-4 space-y-2"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-center space-x-2">
                            <Icon className={`h-4 w-4 ${
                              issue.severity === 'critical' ? 'text-red-500' :
                              issue.severity === 'high' ? 'text-orange-500' :
                              issue.severity === 'medium' ? 'text-yellow-500' :
                              'text-green-500'
                            }`} />
                            <div className="font-medium">{issue.type}</div>
                          </div>
                          <Badge 
                            variant="outline" 
                            className={severityColors[issue.severity]}
                          >
                            {issue.severity.toUpperCase()}
                          </Badge>
                        </div>
                        
                        <div className="text-sm text-muted-foreground">
                          Line {issue.line}
                        </div>
                        
                        <div className="text-sm">
                          {issue.description}
                        </div>
                        
                        <div className="bg-muted/50 rounded p-3 text-sm">
                          <div className="font-medium mb-1">Recommendation:</div>
                          {issue.recommendation}
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              )}
              
              {issues.length === 0 && riskLevel && !isScanning && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-center py-8"
                >
                  <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
                  <p className="text-green-600 font-medium">No security issues found!</p>
                  <p className="text-sm text-muted-foreground mt-2">
                    This code appears to be secure based on our analysis.
                  </p>
                </motion.div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};
