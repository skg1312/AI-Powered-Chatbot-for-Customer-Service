import { useState, useEffect } from 'react';
import { Activity, CheckCircle, XCircle, AlertCircle, RefreshCw, Server, Database, Brain, Search, Shield } from 'lucide-react';

export default function APIStatus() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://medical-ai-chatbot-backend.onrender.com';

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/status`);
      const data = await response.json();
      setStatus(data);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error fetching API status:', error);
      setStatus({
        overall_status: 'error',
        error: 'Failed to connect to backend',
        services: {}
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (serviceStatus) => {
    switch (serviceStatus) {
      case 'operational':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'degraded':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (serviceStatus) => {
    switch (serviceStatus) {
      case 'operational':
        return 'border-green-200 bg-green-50';
      case 'degraded':
        return 'border-yellow-200 bg-yellow-50';
      case 'error':
        return 'border-red-200 bg-red-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const getServiceIcon = (serviceName) => {
    switch (serviceName) {
      case 'groq':
        return <Brain className="w-6 h-6 text-purple-500" />;
      case 'huggingface':
        return <Server className="w-6 h-6 text-orange-500" />;
      case 'pinecone':
        return <Database className="w-6 h-6 text-blue-500" />;
      case 'tavily':
        return <Search className="w-6 h-6 text-green-500" />;
      case 'supabase':
        return <Database className="w-6 h-6 text-emerald-500" />;
      default:
        return <Shield className="w-6 h-6 text-gray-500" />;
    }
  };

  const getServiceDisplayName = (serviceName) => {
    const names = {
      groq: 'Groq AI (LLM)',
      huggingface: 'HuggingFace (Embeddings)',
      pinecone: 'Pinecone (Vector DB)',
      tavily: 'Tavily AI (Web Search)',
      supabase: 'Supabase (Database)'
    };
    return names[serviceName] || serviceName.charAt(0).toUpperCase() + serviceName.slice(1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <Activity className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">API Status Dashboard</h1>
                <p className="text-sm text-gray-600">Real-time monitoring of all backend services</p>
              </div>
            </div>
            <button
              onClick={fetchStatus}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading && !status ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
            <span className="ml-3 text-lg text-gray-600">Loading API status...</span>
          </div>
        ) : (
          <>
            {/* Overall Status */}
            <div className={`rounded-xl border-2 p-6 mb-8 ${getStatusColor(status?.overall_status)}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(status?.overall_status)}
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">
                      Overall Status: {status?.overall_status?.charAt(0).toUpperCase() + status?.overall_status?.slice(1)}
                    </h2>
                    <p className="text-sm text-gray-600">
                      {status?.service} - {status?.timestamp && new Date(status.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
                {lastUpdated && (
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Last updated</p>
                    <p className="text-sm font-medium">{lastUpdated.toLocaleTimeString()}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Service Status Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {status?.services && Object.entries(status.services).map(([serviceName, serviceData]) => (
                <div
                  key={serviceName}
                  className={`rounded-xl border-2 p-6 ${getStatusColor(serviceData.status)}`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      {getServiceIcon(serviceName)}
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          {getServiceDisplayName(serviceName)}
                        </h3>
                        <div className="flex items-center space-x-2 mt-1">
                          {getStatusIcon(serviceData.status)}
                          <span className="text-sm font-medium capitalize">
                            {serviceData.status}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Service Details */}
                  <div className="space-y-2 text-sm">
                    {serviceData.model && (
                      <div>
                        <span className="font-medium text-gray-700">Model:</span>
                        <span className="ml-2 text-gray-600">{serviceData.model}</span>
                      </div>
                    )}
                    {serviceData.indexes !== undefined && (
                      <div>
                        <span className="font-medium text-gray-700">Indexes:</span>
                        <span className="ml-2 text-gray-600">{serviceData.indexes}</span>
                      </div>
                    )}
                    {serviceData.database_type && (
                      <div>
                        <span className="font-medium text-gray-700">Type:</span>
                        <span className="ml-2 text-gray-600">{serviceData.database_type}</span>
                      </div>
                    )}
                    {serviceData.last_check && (
                      <div>
                        <span className="font-medium text-gray-700">Last Check:</span>
                        <span className="ml-2 text-gray-600">
                          {new Date(serviceData.last_check).toLocaleTimeString()}
                        </span>
                      </div>
                    )}
                    {serviceData.error && (
                      <div className="mt-3 p-3 bg-red-100 border border-red-200 rounded-lg">
                        <span className="font-medium text-red-700">Error:</span>
                        <p className="text-red-600 text-xs mt-1">{serviceData.error}</p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Quick Actions */}
            <div className="mt-8 bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <a
                  href={`${backendUrl}/docs`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-2 p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                >
                  <Server className="w-5 h-5 text-blue-600" />
                  <span>API Documentation</span>
                </a>
                <a
                  href={`${backendUrl}/health`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-2 p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                >
                  <Activity className="w-5 h-5 text-green-600" />
                  <span>Health Check</span>
                </a>
                <a
                  href="/"
                  className="flex items-center space-x-2 p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                >
                  <Shield className="w-5 h-5 text-purple-600" />
                  <span>Main Dashboard</span>
                </a>
              </div>
            </div>

            {/* Error Message */}
            {status?.error && (
              <div className="mt-8 bg-red-50 border border-red-200 rounded-xl p-6">
                <div className="flex items-center space-x-2 mb-2">
                  <XCircle className="w-5 h-5 text-red-500" />
                  <h3 className="font-semibold text-red-900">Connection Error</h3>
                </div>
                <p className="text-red-700">{status.error}</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
