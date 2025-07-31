import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import Head from 'next/head';

export default function ProjectPage() {
  const router = useRouter();
  const { id } = router.query;
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      // Load project data based on ID
      loadProject(id);
    }
  }, [id]);

  const loadProject = async (projectId) => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/api/projects/${projectId}/config`);
      
      if (response.ok) {
        const data = await response.json();
        setProject(data);
      } else {
        console.error('Project not found');
      }
    } catch (error) {
      console.error('Error loading project:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading project...</p>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900">Project Not Found</h1>
          <p className="text-gray-600 mt-2">The project with ID "{id}" could not be found.</p>
          <button
            onClick={() => router.push('/')}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>{project.project_id} - Medical AI Chatbot</title>
      </Head>
      
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              Project: {project.project_id}
            </h1>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h2 className="text-xl font-semibold mb-3">Bot Persona</h2>
                <p className="text-gray-700 bg-gray-50 p-4 rounded">
                  {project.bot_persona}
                </p>
              </div>
              
              <div>
                <h2 className="text-xl font-semibold mb-3">Curated Websites</h2>
                <ul className="space-y-2">
                  {project.curated_sites?.map((site, index) => (
                    <li key={index} className="text-blue-600 hover:underline">
                      <a href={`https://${site}`} target="_blank" rel="noopener noreferrer">
                        {site}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            
            <div className="mt-6">
              <h2 className="text-xl font-semibold mb-3">Knowledge Base Files</h2>
              {project.knowledge_base_files?.length > 0 ? (
                <ul className="space-y-2">
                  {project.knowledge_base_files.map((file, index) => (
                    <li key={index} className="text-gray-700">
                      📄 {file}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500">No knowledge base files uploaded yet.</p>
              )}
            </div>
            
            <div className="mt-8 flex space-x-4">
              <button
                onClick={() => router.push(`/playground?project=${id}`)}
                className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
              >
                Open Chat Playground
              </button>
              <button
                onClick={() => router.push('/admin')}
                className="bg-gray-600 text-white px-6 py-2 rounded hover:bg-gray-700"
              >
                Edit Configuration
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
