
export interface Repository {
  id?: string;
  name: string;
  description?: string;
  url: string;
  path: string;
  clonedAt?: Date;
  status?: 'cloning' | 'indexing' | 'ready' | 'error';
}

export interface CodeSnippet {
  id: string;
  content: string;
  code: string;
  language: string;
  filename: string;
  filePath: string;
  lineNumbers?: boolean;
}

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  codeSnippets?: CodeSnippet[];
}

export interface ChatResponse {
  answer: string;
  retrieved_code?: string[];
}

export interface CloneResponse {
  success: boolean;
  message: string;
  repo_path: string;
}

export interface StatusResponse {
  status: string;
  message: string;
  progress: number;
}

export interface SecurityIssue {
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  line: number;
  recommendation: string;
}

export interface SecurityScanResponse {
  issues: SecurityIssue[];
  risk_level: string;
}

export interface ExplanationResponse {
  explanation: string;
}

export interface VisualizationResponse {
  graph_data: any;
}

export interface PreviewResponse {
  preview_url: string;
}

export interface RepoInfoResponse {
  repo_name: string;
  repo_description: string;
}
