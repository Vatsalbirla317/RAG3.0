
import axios from 'axios';
import { 
  ChatResponse, 
  CloneResponse, 
  StatusResponse, 
  ExplanationResponse, 
  VisualizationResponse, 
  SecurityScanResponse, 
  PreviewResponse 
} from '../types';

const API_BASE_URL = 'https://rag3-0.onrender.com';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  async chat(question: string, topK: number = 5): Promise<ChatResponse> {
    const response = await api.post('/chat', { question, top_k: topK });
    return response.data;
  },

  async cloneRepository(repoUrl: string): Promise<CloneResponse> {
    const response = await api.post('/clone', { repo_url: repoUrl });
    return response.data;
  },

  async getStatus(): Promise<StatusResponse> {
    const response = await api.get('/status');
    return response.data;
  },

  async getRepoInfo(): Promise<any> {
    const response = await api.get('/repo_info');
    return response.data;
  },

  async getHealth(): Promise<any> {
    const response = await api.get('/health');
    return response.data;
  },

  async explainCode(code: string, complexity: string): Promise<ExplanationResponse> {
    const response = await api.post('/explain', { code, complexity });
    return response.data;
  },

  async visualizeCode(codebasePath: string): Promise<VisualizationResponse> {
    const response = await api.post('/visualize', { codebase_path: codebasePath });
    return response.data;
  },

  async securityScan(filePath: string): Promise<SecurityScanResponse> {
    const response = await api.post('/security-scan', { file_path: filePath });
    return response.data;
  },

  async previewCode(html: string, css: string, js: string): Promise<PreviewResponse> {
    const response = await api.post('/preview', { html, css, js });
    return response.data;
  }
};
