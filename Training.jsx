import { useState, useEffect } from 'react'
import { 
  Zap, 
  Play, 
  Pause, 
  Square, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  FileText,
  Settings,
  TrendingUp,
  BarChart3
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'

export default function Training() {
  const [trainingJobs, setTrainingJobs] = useState([
    {
      id: 'train_001',
      name: 'Legal Expert v2',
      status: 'completed',
      progress: 100,
      model: 'microsoft/DialoGPT-medium',
      dataFiles: 3,
      startTime: '2024-06-15 10:30',
      endTime: '2024-06-15 14:45',
      accuracy: 92.5,
      loss: 0.23
    },
    {
      id: 'train_002',
      name: 'Medical Assistant',
      status: 'running',
      progress: 67,
      model: 'microsoft/DialoGPT-medium',
      dataFiles: 5,
      startTime: '2024-06-16 09:15',
      endTime: null,
      accuracy: 88.2,
      loss: 0.31
    },
    {
      id: 'train_003',
      name: 'Finance Bot',
      status: 'queued',
      progress: 0,
      model: 'microsoft/DialoGPT-small',
      dataFiles: 2,
      startTime: null,
      endTime: null,
      accuracy: null,
      loss: null
    }
  ])

  const [showNewTrainingDialog, setShowNewTrainingDialog] = useState(false)
  const [newTraining, setNewTraining] = useState({
    name: '',
    model: 'microsoft/DialoGPT-medium',
    dataFiles: [],
    maxLength: 512,
    loraR: 16,
    loraAlpha: 32,
    loraDropout: 0.1,
    validationSplit: 0.1
  })

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'running':
        return <Play className="h-4 w-4 text-blue-500" />
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      case 'queued':
        return <Clock className="h-4 w-4 text-yellow-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'running':
        return 'bg-blue-100 text-blue-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      case 'queued':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const handleStartTraining = () => {
    const newJob = {
      id: `train_${Date.now()}`,
      name: newTraining.name,
      status: 'queued',
      progress: 0,
      model: newTraining.model,
      dataFiles: newTraining.dataFiles.length,
      startTime: null,
      endTime: null,
      accuracy: null,
      loss: null
    }

    setTrainingJobs(prev => [...prev, newJob])
    setShowNewTrainingDialog(false)
    setNewTraining({
      name: '',
      model: 'microsoft/DialoGPT-medium',
      dataFiles: [],
      maxLength: 512,
      loraR: 16,
      loraAlpha: 32,
      loraDropout: 0.1,
      validationSplit: 0.1
    })
  }

  const handleStopTraining = (jobId) => {
    setTrainingJobs(prev => 
      prev.map(job => 
        job.id === jobId ? { ...job, status: 'stopped' } : job
      )
    )
  }

  const formatDuration = (start, end) => {
    if (!start || !end) return 'N/A'
    const startTime = new Date(start)
    const endTime = new Date(end)
    const duration = Math.round((endTime - startTime) / (1000 * 60)) // minutes
    return `${duration} min`
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Training</h1>
          <p className="text-gray-600 mt-2">Train custom models on your domain-specific data</p>
        </div>
        <Dialog open={showNewTrainingDialog} onOpenChange={setShowNewTrainingDialog}>
          <DialogTrigger asChild>
            <Button>
              <Zap className="h-4 w-4 mr-2" />
              Start Training
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Start New Training</DialogTitle>
              <DialogDescription>
                Configure and start a new model training job
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="training-name">Training Name</Label>
                  <Input
                    id="training-name"
                    value={newTraining.name}
                    onChange={(e) => setNewTraining(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="e.g., Legal Expert v3"
                  />
                </div>
                <div>
                  <Label htmlFor="base-model">Base Model</Label>
                  <Select value={newTraining.model} onValueChange={(value) => setNewTraining(prev => ({ ...prev, model: value }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="microsoft/DialoGPT-small">DialoGPT Small (117M)</SelectItem>
                      <SelectItem value="microsoft/DialoGPT-medium">DialoGPT Medium (345M)</SelectItem>
                      <SelectItem value="microsoft/DialoGPT-large">DialoGPT Large (762M)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label htmlFor="data-files">Training Data Files</Label>
                <Textarea
                  id="data-files"
                  placeholder="Enter file paths, one per line..."
                  className="h-24"
                  value={newTraining.dataFiles.join('\n')}
                  onChange={(e) => setNewTraining(prev => ({ ...prev, dataFiles: e.target.value.split('\n').filter(f => f.trim()) }))}
                />
                <p className="text-xs text-gray-500 mt-1">
                  {newTraining.dataFiles.length} files selected
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Max Sequence Length: {newTraining.maxLength}</Label>
                  <Slider
                    value={[newTraining.maxLength]}
                    onValueChange={(value) => setNewTraining(prev => ({ ...prev, maxLength: value[0] }))}
                    max={1024}
                    min={128}
                    step={64}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label>Validation Split: {newTraining.validationSplit}</Label>
                  <Slider
                    value={[newTraining.validationSplit]}
                    onValueChange={(value) => setNewTraining(prev => ({ ...prev, validationSplit: value[0] }))}
                    max={0.3}
                    min={0.05}
                    step={0.05}
                    className="mt-2"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label>LoRA Rank: {newTraining.loraR}</Label>
                  <Slider
                    value={[newTraining.loraR]}
                    onValueChange={(value) => setNewTraining(prev => ({ ...prev, loraR: value[0] }))}
                    max={64}
                    min={8}
                    step={8}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label>LoRA Alpha: {newTraining.loraAlpha}</Label>
                  <Slider
                    value={[newTraining.loraAlpha]}
                    onValueChange={(value) => setNewTraining(prev => ({ ...prev, loraAlpha: value[0] }))}
                    max={128}
                    min={16}
                    step={16}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label>LoRA Dropout: {newTraining.loraDropout}</Label>
                  <Slider
                    value={[newTraining.loraDropout]}
                    onValueChange={(value) => setNewTraining(prev => ({ ...prev, loraDropout: value[0] }))}
                    max={0.3}
                    min={0.05}
                    step={0.05}
                    className="mt-2"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setShowNewTrainingDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={handleStartTraining} disabled={!newTraining.name || newTraining.dataFiles.length === 0}>
                  Start Training
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Training Jobs */}
      <div className="space-y-6">
        {trainingJobs.map((job) => (
          <Card key={job.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(job.status)}
                  <div>
                    <CardTitle className="text-lg">{job.name}</CardTitle>
                    <CardDescription>
                      {job.model} • {job.dataFiles} data files
                    </CardDescription>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge className={getStatusColor(job.status)}>
                    {job.status}
                  </Badge>
                  {job.status === 'running' && (
                    <Button size="sm" variant="outline" onClick={() => handleStopTraining(job.id)}>
                      <Square className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              {/* Progress */}
              {job.status === 'running' && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Training Progress</span>
                    <span>{job.progress}%</span>
                  </div>
                  <Progress value={job.progress} className="h-2" />
                </div>
              )}

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Start Time:</span>
                  <p className="font-medium">{job.startTime || 'Not started'}</p>
                </div>
                <div>
                  <span className="text-gray-500">Duration:</span>
                  <p className="font-medium">{formatDuration(job.startTime, job.endTime)}</p>
                </div>
                <div>
                  <span className="text-gray-500">Accuracy:</span>
                  <p className="font-medium">{job.accuracy ? `${job.accuracy}%` : 'N/A'}</p>
                </div>
                <div>
                  <span className="text-gray-500">Loss:</span>
                  <p className="font-medium">{job.loss || 'N/A'}</p>
                </div>
              </div>

              {/* Training Metrics Chart */}
              {job.status === 'running' || job.status === 'completed' ? (
                <div className="mt-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <BarChart3 className="h-4 w-4 text-gray-500" />
                    <span className="text-sm font-medium">Training Metrics</span>
                  </div>
                  <div className="h-32 bg-gray-50 rounded-lg flex items-center justify-center">
                    <p className="text-gray-500 text-sm">Training metrics visualization would appear here</p>
                  </div>
                </div>
              ) : null}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Training Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Jobs</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{trainingJobs.length}</div>
            <p className="text-xs text-muted-foreground">
              {trainingJobs.filter(j => j.status === 'completed').length} completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.round((trainingJobs.filter(j => j.status === 'completed').length / trainingJobs.length) * 100)}%
            </div>
            <p className="text-xs text-muted-foreground">
              Based on completed jobs
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg. Accuracy</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.round(trainingJobs.filter(j => j.accuracy).reduce((acc, j) => acc + j.accuracy, 0) / trainingJobs.filter(j => j.accuracy).length)}%
            </div>
            <p className="text-xs text-muted-foreground">
              Across all models
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

import { Zap, Plus, Play, Pause, RotateCcw } from 'lucide-react'

const Training = () => {
  const [trainingData, setTrainingData] = useState('');
  const [modelName, setModelName] = useState('');
  const [isTraining, setIsTraining] = useState(false);
  const [trainingResult, setTrainingResult] = useState(null);
  const [trainingProgress, setTrainingProgress] = useState(null);
  const [hyperparameters, setHyperparameters] = useState({});
  const [dataAnalysis, setDataAnalysis] = useState(null);
  const [trainingType, setTrainingType] = useState('general');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const optimizeHyperparameters = async () => {
    try {
      const response = await fetch('/api/training/hyperparameters', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ training_type: trainingType })
      });

      const result = await response.json();
      if (result.status === 'success') {
        setHyperparameters(result.suggestions);
      }
    } catch (error) {
      console.error('Hyperparameter optimization error:', error);
    }
  };

  const analyzeData = async () => {
    if (!trainingData.trim()) return;

    try {
      const response = await fetch('/api/training/datasets/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: trainingData })
      });

      const result = await response.json();
      setDataAnalysis(result);
    } catch (error) {
      console.error('Data analysis error:', error);
    }
  };

  const handleTraining = async () => {
    if (!trainingData.trim() || !modelName.trim()) {
      alert('Please provide both training data and model name');
      return;
    }

    setIsTraining(true);
    setTrainingResult(null);
    setTrainingProgress(null);

    try {
      // Start training
      const response = await fetch('/api/train', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data: trainingData,
          model_name: modelName,
          hyperparameters: hyperparameters
        })
      });

      const result = await response.json();
      setTrainingResult(result);

      // Simulate progress tracking
      if (result.status === 'success') {
        const progressInterval = setInterval(async () => {
          try {
            const progressResponse = await fetch(`/api/training/progress/${result.model_id}`);
            const progress = await progressResponse.json();
            setTrainingProgress(progress);

            if (progress.status === 'completed') {
              clearInterval(progressInterval);
            }
          } catch (error) {
            console.error('Progress tracking error:', error);
          }
        }, 2000);
      }
    } catch (error) {
      console.error('Training error:', error);
      setTrainingResult({ error: 'Training failed' });
    } finally {
      setIsTraining(false);
    }
  };

return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Advanced Model Training</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Training Configuration */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Training Configuration</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Model Name
              </label>
              <input
                type="text"
                value={modelName}
                onChange={(e) => setModelName(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                placeholder="Enter model name..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Training Type
              </label>
              <select
                value={trainingType}
                onChange={(e) => setTrainingType(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              >
                <option value="general">General Purpose</option>
                <option value="conversational">Conversational AI</option>
                <option value="technical">Technical Documentation</option>
              </select>
            </div>
          </div>

          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <label className="block text-sm font-medium text-gray-700">
                Training Data
              </label>
              <button
                onClick={analyzeData}
                className="px-3 py-1 bg-green-100 text-green-700 rounded-md text-sm hover:bg-green-200"
              >
                Analyze Data
              </button>
            </div>
            <textarea
              value={trainingData}
              onChange={(e) => setTrainingData(e.target.value)}
              className="w-full h-48 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your training data here..."
            />
          </div>

          <div className="flex space-x-4">
            <button
              onClick={optimizeHyperparameters}
              className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
            >
              Optimize Hyperparameters
            </button>

            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
            >
              {showAdvanced ? 'Hide' : 'Show'} Advanced Settings
            </button>
          </div>

          {showAdvanced && hyperparameters.learning_rate && (
            <div className="mt-4 p-4 bg-gray-50 rounded-md">
              <h3 className="font-semibold mb-3">Hyperparameters</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                <div>
                  <span className="font-medium">Learning Rate:</span> {hyperparameters.learning_rate}
                </div>
                <div>
                  <span className="font-medium">Batch Size:</span> {hyperparameters.batch_size}
                </div>
                <div>
                  <span className="font-medium">Epochs:</span> {hyperparameters.epochs}
                </div>
                <div>
                  <span className="font-medium">Weight Decay:</span> {hyperparameters.weight_decay}
                </div>
                <div>
                  <span className="font-medium">Optimizer:</span> {hyperparameters.optimizer}
                </div>
                <div>
                  <span className="font-medium">Scheduler:</span> {hyperparameters.scheduler}
                </div>
              </div>
            </div>
          )}

          <button
            onClick={handleTraining}
            disabled={isTraining}
            className="w-full mt-4 bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          >
            {isTraining ? 'Training in Progress...' : 'Start Advanced Training'}
          </button>
        </div>

        {/* Data Analysis Panel */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Data Insights</h2>

          {dataAnalysis ? (
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-sm text-gray-700">Dataset Statistics</h3>
                <div className="text-sm space-y-1">
                  <div>Total Tokens: {dataAnalysis.total_tokens?.toLocaleString()}</div>
                  <div>Lines: {dataAnalysis.total_lines?.toLocaleString()}</div>
                  <div>Avg Length: {dataAnalysis.average_line_length}</div>
                </div>
              </div>

              <div>
                <h3 className="font-semibold text-sm text-gray-700">Quality Score</h3>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full" 
                    style={{width: `${(dataAnalysis.quality_score || 0) * 100}%`}}
                  ></div>
                </div>
                <span className="text-sm text-gray-600">
                  {((dataAnalysis.quality_score || 0) * 100).toFixed(1)}%
                </span>
              </div>

              <div>
                <h3 className="font-semibold text-sm text-gray-700">Content Types</h3>
                {dataAnalysis.content_types && Object.entries(dataAnalysis.content_types).map(([type, ratio]) => (
                  <div key={type} className="flex justify-between text-sm">
                    <span className="capitalize">{type}:</span>
                    <span>{(ratio * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>

              <div>
                <h3 className="font-semibold text-sm text-gray-700">Recommendations</h3>
                <ul className="text-xs space-y-1">
                  {dataAnalysis.recommendations?.map((rec, idx) => (
                    <li key={idx} className="text-gray-600">• {rec}</li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">
              Add training data and click "Analyze Data" to see insights
            </div>
          )}
        </div>
      </div>

      {/* Training Progress */}
      {isTraining && trainingProgress && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Training Progress</h2>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {trainingProgress.epoch}/{trainingProgress.total_epochs}
              </div>
              <div className="text-sm text-gray-600">Epochs</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {trainingProgress.loss?.toFixed(3)}
              </div>
              <div className="text-sm text-gray-600">Loss</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {(trainingProgress.accuracy * 100)?.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Accuracy</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {trainingProgress.eta_minutes}m
              </div>
              <div className="text-sm text-gray-600">ETA</div>
            </div>
          </div>

          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-blue-600 h-3 rounded-full transition-all duration-300" 
              style={{
                width: `${(trainingProgress.samples_processed / trainingProgress.total_samples) * 100}%`
              }}
            ></div>
          </div>
          <div className="text-sm text-gray-600 mt-2">
            {trainingProgress.samples_processed?.toLocaleString()} / {trainingProgress.total_samples?.toLocaleString()} samples
          </div>
        </div>
      )}

      {/* Training Results */}
      {trainingResult && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Training Results</h2>

          {trainingResult.status === 'success' ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-green-50 p-3 rounded-md">
                  <div className="font-semibold text-green-800">Training Time</div>
                  <div className="text-green-600">{trainingResult.training_time}</div>
                </div>
                <div className="bg-blue-50 p-3 rounded-md">
                  <div className="font-semibold text-blue-800">Final Loss</div>
                  <div className="text-blue-600">{trainingResult.metrics?.final_loss}</div>
                </div>
                <div className="bg-purple-50 p-3 rounded-md">
                  <div className="font-semibold text-purple-800">Epochs</div>
                  <div className="text-purple-600">{trainingResult.metrics?.epochs_completed}</div>
                </div>
                <div className="bg-orange-50 p-3 rounded-md">
                  <div className="font-semibold text-orange-800">Samples</div>
                  <div className="text-orange-600">{trainingResult.metrics?.samples_processed}</div>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-md">
                <pre className="text-sm overflow-auto">
                  {JSON.stringify(trainingResult, null, 2)}
                </pre>
              </div>
            </div>
          ) : (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="text-red-800 font-semibold">Training Failed</div>
              <div className="text-red-600">{trainingResult.error}</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Training