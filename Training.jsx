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

import { useState, useEffect } from 'react'
import { Zap, Plus, Play, Pause, RotateCcw } from 'lucide-react'

function Training() {
  const [trainingJobs, setTrainingJobs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTrainingJobs()
  }, [])

  const fetchTrainingJobs = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/v1/training/jobs', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setTrainingJobs(data.jobs || [])
      } else {
        // Fallback demo data
        setTrainingJobs([])
      }
    } catch (error) {
      console.error('Error fetching training jobs:', error)
      setTrainingJobs([])
    }
    setLoading(false)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Training</h1>
          <p className="text-gray-600 mt-2">Train and fine-tune your AI models</p>
        </div>
        <button className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
          <Plus className="h-4 w-4" />
          <span>New Training Job</span>
        </button>
      </div>

      {trainingJobs.length === 0 ? (
        <div className="text-center py-12">
          <Zap className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No training jobs yet</h3>
          <p className="text-gray-500 mb-4">Start training your first custom AI model.</p>
          <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
            Start Training
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {trainingJobs.map((job) => (
            <div key={job.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <Zap className="h-8 w-8 text-indigo-600" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{job.name}</h3>
                    <p className="text-sm text-gray-500">{job.model_type}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    job.status === 'running' ? 'bg-blue-100 text-blue-800' :
                    job.status === 'completed' ? 'bg-green-100 text-green-800' :
                    job.status === 'failed' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {job.status}
                  </span>
                  <div className="flex space-x-2">
                    <button className="p-2 text-gray-600 hover:bg-gray-100 rounded transition-colors">
                      <Play className="h-4 w-4" />
                    </button>
                    <button className="p-2 text-gray-600 hover:bg-gray-100 rounded transition-colors">
                      <Pause className="h-4 w-4" />
                    </button>
                    <button className="p-2 text-gray-600 hover:bg-gray-100 rounded transition-colors">
                      <RotateCcw className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
              
              {job.progress && (
                <div className="mt-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>Progress</span>
                    <span>{job.progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-indigo-600 h-2 rounded-full transition-all"
                      style={{ width: `${job.progress}%` }}
                    ></div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Training
