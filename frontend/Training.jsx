
import React, { useState, useEffect, useRef } from 'react';

const Training = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [trainingData, setTrainingData] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [availableModels, setAvailableModels] = useState([]);
  const [trainingProgress, setTrainingProgress] = useState(null);
  const [isTraining, setIsTraining] = useState(false);
  const [trainingHistory, setTrainingHistory] = useState([]);
  const [hyperparameters, setHyperparameters] = useState({
    learning_rate: 0.0001,
    batch_size: 8,
    epochs: 10,
    warmup_steps: 100,
    weight_decay: 0.01,
    training_type: 'general'
  });
  const [dataAnalysis, setDataAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [optimizedParams, setOptimizedParams] = useState(null);
  const [modelVersions, setModelVersions] = useState([]);
  const [evaluationResults, setEvaluationResults] = useState(null);
  
  const fileInputRef = useRef(null);
  const progressIntervalRef = useRef(null);

  useEffect(() => {
    fetchModels();
    fetchTrainingHistory();
    return () => {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    };
  }, []);

  const fetchModels = async () => {
    try {
      const response = await fetch('/api/models');
      const data = await response.json();
      if (data.success) {
        setAvailableModels(data.models);
        if (data.models.length > 0 && !selectedModel) {
          setSelectedModel(data.models[0].id);
        }
      }
    } catch (error) {
      console.error('Error fetching models:', error);
    }
  };

  const fetchTrainingHistory = async () => {
    try {
      // Simulate training history - replace with actual API call
      const history = [
        {
          id: 1,
          model_name: 'Customer Support Bot v1.2',
          status: 'completed',
          accuracy: 0.89,
          loss: 0.23,
          training_time: '45 minutes',
          created_at: '2024-01-15T10:30:00Z'
        },
        {
          id: 2,
          model_name: 'Technical Documentation Assistant',
          status: 'completed',
          accuracy: 0.92,
          loss: 0.18,
          training_time: '52 minutes',
          created_at: '2024-01-14T14:20:00Z'
        }
      ];
      setTrainingHistory(history);
    } catch (error) {
      console.error('Error fetching training history:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    setIsUploading(true);
    
    try {
      // Simulate file processing
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const processedFiles = files.map(file => ({
        id: Date.now() + Math.random(),
        name: file.name,
        size: file.size,
        type: file.type,
        status: 'processed',
        preview: file.type.startsWith('text/') ? 'Text content preview...' : 'Binary file'
      }));
      
      setUploadedFiles(prev => [...prev, ...processedFiles]);
      
      // Auto-analyze data if text files
      if (files.some(f => f.type.startsWith('text/'))) {
        analyzeTrainingData();
      }
    } catch (error) {
      console.error('Error uploading files:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const analyzeTrainingData = async () => {
    setIsAnalyzing(true);
    try {
      const response = await fetch('/api/training/datasets/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: trainingData })
      });
      
      const analysis = await response.json();
      setDataAnalysis(analysis);
    } catch (error) {
      console.error('Error analyzing data:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const optimizeHyperparameters = async () => {
    try {
      const response = await fetch('/api/training/hyperparameters', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ training_type: hyperparameters.training_type })
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        setOptimizedParams(data.suggestions);
        setHyperparameters(prev => ({ ...prev, ...data.suggestions }));
      }
    } catch (error) {
      console.error('Error optimizing hyperparameters:', error);
    }
  };

  const startTraining = async () => {
    if (!selectedModel) {
      alert('Please select a model to train');
      return;
    }

    setIsTraining(true);
    setTrainingProgress({
      status: 'starting',
      epoch: 0,
      total_epochs: hyperparameters.epochs,
      loss: 0,
      accuracy: 0,
      eta_minutes: 0,
      samples_processed: 0,
      total_samples: 1000
    });

    try {
      const response = await fetch('/api/training/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model_id: selectedModel,
          training_data: trainingData,
          hyperparameters: hyperparameters,
          uploaded_files: uploadedFiles.map(f => f.name)
        })
      });

      if (response.ok) {
        // Start polling for progress
        progressIntervalRef.current = setInterval(fetchTrainingProgress, 2000);
      }
    } catch (error) {
      console.error('Error starting training:', error);
      setIsTraining(false);
    }
  };

  const fetchTrainingProgress = async () => {
    try {
      const response = await fetch(`/api/training/progress/${selectedModel}`);
      const progress = await response.json();
      
      setTrainingProgress(progress);
      
      if (progress.status === 'completed' || progress.status === 'failed') {
        setIsTraining(false);
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current);
        }
        fetchTrainingHistory();
        if (progress.status === 'completed') {
          fetchModelVersions();
        }
      }
    } catch (error) {
      console.error('Error fetching training progress:', error);
    }
  };

  const fetchModelVersions = async () => {
    try {
      const response = await fetch(`/api/models/${selectedModel}/versions`);
      const data = await response.json();
      setModelVersions(data.versions || []);
    } catch (error) {
      console.error('Error fetching model versions:', error);
    }
  };

  const evaluateModel = async () => {
    try {
      const response = await fetch(`/api/models/${selectedModel}/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ test_data: [] })
      });
      
      const results = await response.json();
      setEvaluationResults(results);
    } catch (error) {
      console.error('Error evaluating model:', error);
    }
  };

  const ProgressBar = ({ progress, label }) => (
    <div className="mb-4">
      <div className="flex justify-between text-sm text-gray-600 mb-1">
        <span>{label}</span>
        <span>{Math.round(progress)}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
    </div>
  );

  const MetricCard = ({ title, value, unit, trend }) => (
    <div className="bg-white p-4 rounded-lg border">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-2xl font-bold">{value}<span className="text-sm text-gray-500">{unit}</span></p>
        </div>
        {trend && (
          <div className={`text-sm ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {trend > 0 ? '↗' : '↘'} {Math.abs(trend)}%
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6 sm:mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">AI Model Training Studio</h1>
        <p className="text-sm sm:text-base text-gray-600">Train custom AI models with your data using advanced machine learning techniques</p>
      </div>

      {/* Navigation Tabs */}
      <div className="flex flex-wrap sm:flex-nowrap gap-1 bg-gray-100 p-1 rounded-lg mb-6 overflow-x-auto">
        {[
          { id: 'upload', label: 'Data Upload', icon: '📁', shortLabel: 'Upload' },
          { id: 'configure', label: 'Configuration', icon: '⚙️', shortLabel: 'Config' },
          { id: 'train', label: 'Training', icon: '🚀', shortLabel: 'Train' },
          { id: 'evaluate', label: 'Evaluation', icon: '📊', shortLabel: 'Eval' },
          { id: 'history', label: 'History', icon: '📈', shortLabel: 'History' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-2 rounded-md transition-colors whitespace-nowrap min-h-[44px] ${
              activeTab === tab.id 
                ? 'bg-white text-blue-600 shadow-sm' 
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <span>{tab.icon}</span>
            <span className="text-xs sm:text-sm">{window.innerWidth < 640 ? tab.shortLabel : tab.label}</span>
          </button>
        ))}
      </div>

      {/* Data Upload Tab */}
      {activeTab === 'upload' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-4">Training Data Upload</h2>
            
            {/* File Upload */}
            <div className="mb-6">
              <div 
                className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 transition-colors"
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  multiple
                  accept=".txt,.pdf,.docx,.csv,.json"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <div className="text-4xl text-gray-400 mb-2">📄</div>
                <p className="text-lg text-gray-600 mb-2">
                  {isUploading ? 'Processing files...' : 'Click to upload training files'}
                </p>
                <p className="text-sm text-gray-500">
                  Supports: TXT, PDF, DOCX, CSV, JSON (Max 10MB each)
                </p>
              </div>
            </div>

            {/* Text Input */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Or paste your training data directly:
              </label>
              <textarea
                value={trainingData}
                onChange={(e) => setTrainingData(e.target.value)}
                className="w-full h-40 px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your training data here..."
              />
              <div className="flex justify-between mt-2">
                <span className="text-sm text-gray-500">
                  {trainingData.length} characters
                </span>
                <button
                  onClick={analyzeTrainingData}
                  disabled={!trainingData || isAnalyzing}
                  className="text-sm text-blue-600 hover:text-blue-800 disabled:text-gray-400"
                >
                  {isAnalyzing ? 'Analyzing...' : 'Analyze Data Quality'}
                </button>
              </div>
            </div>

            {/* Uploaded Files List */}
            {uploadedFiles.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-medium mb-3">Uploaded Files</h3>
                <div className="space-y-2">
                  {uploadedFiles.map(file => (
                    <div key={file.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">📄</span>
                        <div>
                          <p className="font-medium">{file.name}</p>
                          <p className="text-sm text-gray-500">
                            {(file.size / 1024).toFixed(1)} KB • {file.status}
                          </p>
                        </div>
                      </div>
                      <button className="text-red-500 hover:text-red-700">
                        <span className="text-xl">🗑️</span>
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Data Analysis Results */}
            {dataAnalysis && (
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="text-lg font-medium text-blue-900 mb-3">Data Analysis Results</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <MetricCard title="Total Tokens" value={dataAnalysis.total_tokens?.toLocaleString()} />
                  <MetricCard title="Lines" value={dataAnalysis.total_lines?.toLocaleString()} />
                  <MetricCard title="Quality Score" value={dataAnalysis.quality_score} unit="/1.0" />
                  <MetricCard title="Est. Training Time" value={dataAnalysis.estimated_training_time} />
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium text-blue-800">Recommendations:</h4>
                  {dataAnalysis.recommendations?.map((rec, index) => (
                    <p key={index} className="text-sm text-blue-700">• {rec}</p>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Configuration Tab */}
      {activeTab === 'configure' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-4">Training Configuration</h2>
            
            {/* Model Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Base Model
              </label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select a model...</option>
                {availableModels.map(model => (
                  <option key={model.id} value={model.id}>
                    {model.name} - {model.description}
                  </option>
                ))}
              </select>
            </div>

            {/* Training Type */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Training Type
              </label>
              <select
                value={hyperparameters.training_type}
                onChange={(e) => setHyperparameters(prev => ({ ...prev, training_type: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="general">General Purpose</option>
                <option value="conversational">Conversational AI</option>
                <option value="technical">Technical Documentation</option>
                <option value="creative">Creative Writing</option>
              </select>
            </div>

            {/* Hyperparameters */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Learning Rate
                </label>
                <input
                  type="number"
                  step="0.00001"
                  value={hyperparameters.learning_rate}
                  onChange={(e) => setHyperparameters(prev => ({ ...prev, learning_rate: parseFloat(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Batch Size
                </label>
                <input
                  type="number"
                  value={hyperparameters.batch_size}
                  onChange={(e) => setHyperparameters(prev => ({ ...prev, batch_size: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Epochs
                </label>
                <input
                  type="number"
                  value={hyperparameters.epochs}
                  onChange={(e) => setHyperparameters(prev => ({ ...prev, epochs: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Weight Decay
                </label>
                <input
                  type="number"
                  step="0.001"
                  value={hyperparameters.weight_decay}
                  onChange={(e) => setHyperparameters(prev => ({ ...prev, weight_decay: parseFloat(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* Auto-optimize Button */}
            <div className="flex justify-between items-center">
              <button
                onClick={optimizeHyperparameters}
                className="px-4 py-2 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
              >
                🧠 Auto-optimize Parameters
              </button>
              
              {optimizedParams && (
                <div className="text-sm text-green-600">
                  ✅ Parameters optimized with {Math.round(optimizedParams.confidence * 100)}% confidence
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Training Tab */}
      {activeTab === 'train' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-4">Model Training</h2>
            
            {!isTraining && !trainingProgress && (
              <div className="text-center py-8">
                <div className="text-6xl text-gray-300 mb-4">🚀</div>
                <h3 className="text-xl font-medium text-gray-700 mb-2">Ready to Start Training</h3>
                <p className="text-gray-500 mb-6">
                  Your model and data are configured. Click below to begin training.
                </p>
                <button
                  onClick={startTraining}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Start Training
                </button>
              </div>
            )}

            {(isTraining || trainingProgress) && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <MetricCard 
                    title="Epoch" 
                    value={`${trainingProgress?.epoch || 0}/${trainingProgress?.total_epochs || 0}`} 
                  />
                  <MetricCard 
                    title="Loss" 
                    value={trainingProgress?.loss?.toFixed(3) || '0.000'} 
                  />
                  <MetricCard 
                    title="Accuracy" 
                    value={Math.round((trainingProgress?.accuracy || 0) * 100)} 
                    unit="%" 
                  />
                  <MetricCard 
                    title="ETA" 
                    value={trainingProgress?.eta_minutes || 0} 
                    unit=" min" 
                  />
                </div>

                <div className="space-y-4">
                  <ProgressBar 
                    progress={(trainingProgress?.epoch || 0) / (trainingProgress?.total_epochs || 1) * 100}
                    label="Training Progress"
                  />
                  <ProgressBar 
                    progress={(trainingProgress?.samples_processed || 0) / (trainingProgress?.total_samples || 1) * 100}
                    label="Current Epoch Progress"
                  />
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium mb-2">Training Log</h4>
                  <div className="text-sm font-mono text-gray-600 space-y-1">
                    <div>🔄 Status: {trainingProgress?.status || 'Unknown'}</div>
                    <div>📊 Samples processed: {trainingProgress?.samples_processed?.toLocaleString() || 0}</div>
                    <div>⏱️ Current loss: {trainingProgress?.loss?.toFixed(6) || 'N/A'}</div>
                    <div>🎯 Current accuracy: {((trainingProgress?.accuracy || 0) * 100).toFixed(2)}%</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Evaluation Tab */}
      {activeTab === 'evaluate' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg border">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Model Evaluation</h2>
              <button
                onClick={evaluateModel}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
              >
                Run Evaluation
              </button>
            </div>

            {evaluationResults && (
              <div className="space-y-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <MetricCard 
                    title="Overall Accuracy" 
                    value={Math.round(evaluationResults.metrics.accuracy * 100)} 
                    unit="%" 
                  />
                  <MetricCard 
                    title="BLEU Score" 
                    value={evaluationResults.metrics.bleu_score.toFixed(2)} 
                  />
                  <MetricCard 
                    title="Coherence" 
                    value={Math.round(evaluationResults.metrics.coherence_score * 100)} 
                    unit="%" 
                  />
                  <MetricCard 
                    title="Relevance" 
                    value={Math.round(evaluationResults.metrics.relevance_score * 100)} 
                    unit="%" 
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-medium mb-3">Performance Breakdown</h4>
                    <div className="space-y-2">
                      {Object.entries(evaluationResults.performance_breakdown).map(([task, score]) => (
                        <div key={task} className="flex justify-between">
                          <span className="capitalize">{task.replace('_', ' ')}</span>
                          <span className="font-medium">{Math.round(score * 100)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-medium mb-3">Benchmark Comparison</h4>
                    <div className="space-y-2">
                      {Object.entries(evaluationResults.benchmark_comparison).map(([benchmark, score]) => (
                        <div key={benchmark} className="flex justify-between">
                          <span className="capitalize">{benchmark.replace('_', ' ')}</span>
                          <span className="font-medium">{Math.round(score * 100)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">Recommendations</h4>
                  <div className="space-y-1">
                    {evaluationResults.recommendations.map((rec, index) => (
                      <p key={index} className="text-sm text-blue-700">• {rec}</p>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Model Versions */}
            {modelVersions.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-medium mb-3">Model Versions</h3>
                <div className="space-y-2">
                  {modelVersions.map(version => (
                    <div key={version.version} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                      <div>
                        <span className="font-medium">v{version.version}</span>
                        <span className={`ml-2 px-2 py-1 text-xs rounded ${
                          version.status === 'latest' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                        }`}>
                          {version.status}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600">
                        Accuracy: {Math.round(version.metrics.accuracy * 100)}% | 
                        Loss: {version.metrics.loss.toFixed(3)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-4">Training History</h2>
            
            {trainingHistory.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl text-gray-300 mb-2">📊</div>
                <p>No training history yet. Start your first training session!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {trainingHistory.map(session => (
                  <div key={session.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className={`w-3 h-3 rounded-full ${
                        session.status === 'completed' ? 'bg-green-500' : 
                        session.status === 'training' ? 'bg-blue-500' : 'bg-red-500'
                      }`}></div>
                      <div>
                        <h4 className="font-medium">{session.model_name}</h4>
                        <p className="text-sm text-gray-600">
                          {new Date(session.created_at).toLocaleDateString()} • {session.training_time}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-600">Accuracy: {Math.round(session.accuracy * 100)}%</p>
                      <p className="text-sm text-gray-600">Loss: {session.loss.toFixed(3)}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Training;
