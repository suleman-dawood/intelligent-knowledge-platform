export default function AboutPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-6">About Intelligent Knowledge Platform</h1>
        
        <div className="prose prose-lg max-w-none">
          <p className="text-xl text-gray-600 mb-8">
            A comprehensive multi-agent system for gathering, processing, analyzing, and visualizing knowledge from diverse sources using advanced AI capabilities.
          </p>
          
          <div className="grid md:grid-cols-2 gap-8 mb-12">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h2 className="text-2xl font-semibold mb-4 text-blue-600">🔍 Intelligent Search</h2>
              <p className="text-gray-600">
                Advanced semantic search capabilities powered by AI to find relevant knowledge across all your content sources.
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h2 className="text-2xl font-semibold mb-4 text-green-600">📚 Multi-Source Aggregation</h2>
              <p className="text-gray-600">
                Automatically gather and process content from PDFs, academic papers, web articles, and more.
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h2 className="text-2xl font-semibold mb-4 text-purple-600">🧠 Knowledge Graphs</h2>
              <p className="text-gray-600">
                Visualize relationships between concepts, entities, and ideas through interactive knowledge graphs.
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h2 className="text-2xl font-semibold mb-4 text-orange-600">🤖 AI-Powered Analysis</h2>
              <p className="text-gray-600">
                Leverage advanced AI models for entity extraction, sentiment analysis, and content summarization.
              </p>
            </div>
          </div>
          
          <div className="bg-gray-50 p-8 rounded-lg mb-8">
            <h2 className="text-2xl font-semibold mb-4">How It Works</h2>
            <div className="space-y-4">
              <div className="flex items-start">
                <div className="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-4 mt-1">1</div>
                <div>
                  <h3 className="font-semibold">Content Ingestion</h3>
                  <p className="text-gray-600">Upload documents, add URLs, or input text directly into the platform.</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <div className="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-4 mt-1">2</div>
                <div>
                  <h3 className="font-semibold">AI Processing</h3>
                  <p className="text-gray-600">Our AI agents extract entities, analyze sentiment, and identify key relationships.</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <div className="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-4 mt-1">3</div>
                <div>
                  <h3 className="font-semibold">Knowledge Graph Construction</h3>
                  <p className="text-gray-600">Information is organized into an interconnected knowledge graph.</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <div className="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-4 mt-1">4</div>
                <div>
                  <h3 className="font-semibold">Intelligent Search & Discovery</h3>
                  <p className="text-gray-600">Find relevant information through semantic search and visual exploration.</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="text-center">
            <h2 className="text-2xl font-semibold mb-4">Powered by Advanced AI</h2>
            <p className="text-gray-600 mb-6">
              Built with DeepSeek AI models, modern databases (MongoDB, Neo4j, Redis), 
              and a scalable microservices architecture.
            </p>
            <div className="flex justify-center space-x-4 text-sm text-gray-500">
              <span>• Multi-Agent System</span>
              <span>• Real-time Processing</span>
              <span>• Scalable Architecture</span>
              <span>• Open Source</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 