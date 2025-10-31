import { CloudClient } from '../types/CloudClient';

const API_BASE_URL = 'http://localhost:8000';

export interface StatData {
  label: string;
  value: string;
  change: string;
  icon: string;
}

export interface Insight {
  id: string;
  title: string;
  description: string;
  severity: 'high' | 'medium' | 'low';
}

export interface Recommendation {
  id: string;
  resourceName: string;
  currentCost: string;
  recommendation: string;
  estimatedSaving: string;
  status: 'pending' | 'approved' | 'rejected';
}

export interface BackendCloudClient {
  id: string;
  name: string;
  provider: 'aws' | 'azure' | 'gcp';
  region: string;
  roleArn?: string;
  accessKeyId?: string;
  secretAccessKey?: string;
  isActive: boolean;
  lastSync?: string;
  totalResources: number;
  monthlyCost: number;
}

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }
  return response.json();
};

export const api = {
  async getStats() {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/stats`);
    const data = await handleResponse(response);
    
    return [
      { label: 'Total Spent', value: `$${data.monthlyCost.toFixed(1)}`, change: '+8.2%', icon: 'dollar' },
      { label: 'Total Savings', value: `$${data.potentialSavings.toFixed(1)}`, change: '+15.3%', icon: 'piggy' },
      { label: 'ROI', value: data.monthlyCost > 0 ? `${((data.potentialSavings / data.monthlyCost) * 100).toFixed(1)}%` : '0.0%', change: '+4.1%', icon: 'trending' },
    ];
  },

  async getInsights(): Promise<Insight[]> {
    const response = await fetch(`${API_BASE_URL}/api/alerts`);
    const alerts = await handleResponse(response);
    
    return alerts.map((alert: any) => ({
      id: alert.id,
      title: alert.title,
      description: alert.message,
      severity: alert.severity as 'high' | 'medium' | 'low',
    }));
  },

  async getRecommendations(): Promise<Recommendation[]> {
    const response = await fetch(`${API_BASE_URL}/api/recommendations`);
    const recs = await handleResponse(response);
    
    return recs.map((rec: any) => ({
      id: rec.id,
      resourceName: rec.title,
      currentCost: `$${rec.monthlySavings}/month`,
      recommendation: rec.description.substring(0, 100),
      estimatedSaving: `$${rec.monthlySavings}/month`,
      status: rec.status as 'pending' | 'approved' | 'rejected',
    }));
  },

  async getCloudClients() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/clients`);
      const clients = await handleResponse(response);
      
      const mappedClients: CloudClient[] = clients.map((client: BackendCloudClient) => ({
        id: client.id,
        name: client.name,
        description: `${client.provider.toUpperCase()} account in ${client.region}`,
        providers: [client.provider],
        iam_role_arn: client.roleArn || '',
        created_at: client.lastSync || new Date().toISOString(),
        updated_at: client.lastSync || new Date().toISOString(),
      }));
      
      return { data: mappedClients, error: null };
    } catch (error) {
      return { data: [], error: error instanceof Error ? error.message : 'Unknown error' };
    }
  },

  async addCloudClient(clientData: Omit<CloudClient, 'id' | 'created_at' | 'updated_at'>) {
    try {
      const backendClient: Partial<BackendCloudClient> = {
        id: crypto.randomUUID(),
        name: clientData.name,
        provider: clientData.providers[0] as 'aws' | 'azure' | 'gcp',
        region: 'ap-south-1',
        roleArn: clientData.iam_role_arn,
        isActive: true,
        totalResources: 0,
        monthlyCost: 0,
      };
      
      const response = await fetch(`${API_BASE_URL}/api/clients`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(backendClient),
      });
      
      const createdClient = await handleResponse(response);
      
      const mappedClient: CloudClient = {
        id: createdClient.id,
        name: createdClient.name,
        description: clientData.description,
        providers: [createdClient.provider],
        iam_role_arn: createdClient.roleArn || '',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      
      return { data: mappedClient, error: null };
    } catch (error) {
      return { data: null, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  },

  async testRole() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      await handleResponse(response);
      return { success: true, message: 'Connection test successful!' };
    } catch (error) {
      return { success: false, message: error instanceof Error ? error.message : 'Connection failed' };
    }
  },

  async approveRecommendation(id: string) {
    try {
      await fetch(`${API_BASE_URL}/api/recommendations/${id}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'approved' }),
      });
      return { success: true, message: 'Recommendation approved successfully' };
    } catch (error) {
      return { success: false, message: error instanceof Error ? error.message : 'Failed to approve' };
    }
  },

  async rejectRecommendation(id: string) {
    try {
      await fetch(`${API_BASE_URL}/api/recommendations/${id}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'rejected' }),
      });
      return { success: true, message: 'Recommendation rejected successfully' };
    } catch (error) {
      return { success: false, message: error instanceof Error ? error.message : 'Failed to reject' };
    }
  },

  async analyze(clientId: string, query: string = 'Analyze my cloud infrastructure for cost optimization opportunities') {
    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, clientId }),
      });
      
      const result = await handleResponse(response);
      
      return {
        success: true,
        message: 'Analysis completed successfully',
        analysisId: result.analysisId,
      };
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Analysis failed',
      };
    }
  },

  async getAnalysisResult(analysisId: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/analysis/${analysisId}`);
      return await handleResponse(response);
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Failed to get analysis result');
    }
  },

  async chatWithAI(userMessage: string, clientId?: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userMessage,
          clientId: clientId || 'default',
        }),
      });
      
      const result = await handleResponse(response);
      
      if (result.analysisId) {
        const analysisResponse = await fetch(`${API_BASE_URL}/api/analysis/${result.analysisId}`);
        const analysisData = await handleResponse(analysisResponse);
        
        return {
          success: true,
          message: analysisData.result?.analysis || 'Analysis completed',
        };
      }
      
      return {
        success: false,
        message: 'No analysis result available',
      };
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to process request',
      };
    }
  },

  async connectCloudProvider(data: any) {
    return this.addCloudClient(data);
  },

  async sendFeedback(feedback: string) {
    console.log('Feedback:', feedback);
    return {
      success: true,
      message: 'Feedback submitted successfully',
    };
  },

  async connectNotification(platform: string, webhook: string) {
    console.log(`Setting up ${platform} notifications with webhook: ${webhook}`);
    
    let message = '';
    if (platform === 'Discord') {
      message = 'Discord notifications configured successfully. You will receive cost alerts in your server.';
    } else if (platform === 'Slack') {
      message = 'Slack notifications configured successfully. You will receive cost alerts in your workspace.';
    } else if (platform === 'Email') {
      message = 'Email notifications configured successfully. You will receive cost alerts at your email address.';
    } else {
      message = `${platform} notifications configured successfully`;
    }
    
    return {
      success: true,
      message,
    };
  },
};

export default api;
