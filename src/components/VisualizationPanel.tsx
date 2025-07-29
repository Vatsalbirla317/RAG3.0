
import { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Network, Download, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CodeSnippet } from '../types';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

interface VisualizationPanelProps {
  snippet: CodeSnippet;
  isOpen: boolean;
  onClose: () => void;
}

export const VisualizationPanel = ({ snippet, isOpen, onClose }: VisualizationPanelProps) => {
  const [graphData, setGraphData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [zoom, setZoom] = useState(1);

  const handleVisualize = async () => {
    setIsLoading(true);
    try {
      const response = await apiService.visualizeCode(snippet.filePath);
      setGraphData(response.graph_data);
    } catch (error) {
      toast.error('Failed to generate visualization');
      console.error('Visualization error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.1, 3));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.1, 0.5));
  const handleReset = () => setZoom(1);

  const exportGraph = () => {
    // This would export the graph as PNG/SVG
    toast.success('Graph exported!');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-6xl max-h-[90vh] bg-background rounded-lg shadow-xl"
      >
        <Card className="h-full">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
            <CardTitle className="flex items-center space-x-2">
              <Network className="h-5 w-5" />
              <span>Code Flow Visualization</span>
            </CardTitle>
            
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleZoomOut}
                disabled={zoom <= 0.5}
              >
                <ZoomOut className="h-4 w-4" />
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={handleReset}
              >
                <RotateCcw className="h-4 w-4" />
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={handleZoomIn}
                disabled={zoom >= 3}
              >
                <ZoomIn className="h-4 w-4" />
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={exportGraph}
                disabled={!graphData}
              >
                <Download className="h-4 w-4" />
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
          
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                File: {snippet.filePath}
              </div>
              
              <Button
                onClick={handleVisualize}
                disabled={isLoading}
                variant="default"
              >
                {isLoading ? (
                  <>
                    <Network className="h-4 w-4 mr-2 animate-pulse" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Network className="h-4 w-4 mr-2" />
                    Generate Visualization
                  </>
                )}
              </Button>
            </div>
            
            <div className="border rounded-lg h-96 bg-muted/30 flex items-center justify-center">
              {!graphData && !isLoading && (
                <div className="text-center text-muted-foreground">
                  <Network className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Click "Generate Visualization" to create an interactive code flow diagram</p>
                </div>
              )}
              
              {isLoading && (
                <div className="text-center text-muted-foreground">
                  <Network className="h-12 w-12 mx-auto mb-4 animate-pulse" />
                  <p>Analyzing code structure...</p>
                </div>
              )}
              
              {graphData && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="w-full h-full relative"
                  style={{ transform: `scale(${zoom})` }}
                >
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="bg-blue-100 text-blue-800 p-4 rounded-lg">
                      Interactive visualization would be rendered here
                      <br />
                      (Integration with React Flow or D3.js)
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};
