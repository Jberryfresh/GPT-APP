import { useState, useEffect } from 'react'
import { 
  Brain, 
  Upload, 
  Download, 
  Trash2, 
  Play, 
  Pause, 
  Settings,
  Info,
  CheckCircle,
  AlertCircle,
  Clock,
  HardDrive
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'

export default function Models() {
  const [models, setModels] = useState([
    {
      id: 'default',
      name: 'Default Model',
      type: 'base',
      status: 'active',
      size: '2.3 GB',
      parameters: '7B',
      created: '2024-06-01',
      description: 'General purpose conversational model',
      performance: {
        accuracy: 85,
        speed: 'Fast',
        memory: '4.2 GB'
      }
    },
    {
      id: 'legal-expert',
      name: 'Legal Expert',
      type: 'fine_tuned',
      status: 'active',
      size: '2.5 GB',
      parameters: '7B + LoRA',
      created: '2024-06-10',
      description: 'Specialized model for legal document analysis and advice',
      performance: {
        accuracy: 92,
        speed: 'Fast',
        memory: '4.5 GB'
      }
    },
    {
      id: 'medical-assistant',
      name: 'Medical Assistant',
      type: 'fine_tuned',
      status: 'training',
      size: '2.4 GB',
      parameters: '7B + LoRA',
      created: '2024-06-15',
      description: 'Medical knowledge and patient interaction assistant',
      performance: {
        accuracy: 88,
        speed: 'Medium',
        memory: '4.3 GB'
      }
    }
  ])
  const [selectedModel, setSelectedModel] = useState(null)
  const [showLoadDialog, setShowLoadDialog] = useState(false)
  const [loadModelPath, setLoadModelPath] = useState('')

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'training':
        return <Clock className="h-4 w-4 text-yellow-500" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'training':
        return 'bg-yellow-100 text-yellow-800'
      case 'error':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const handleLoadModel = () => {
    // Simulate loading a model
    const newModel = {
      id: `model-${Date.now()}`,
      name: 'Loaded Model',
      type: 'fine_tuned',
      status: 'active',
      size: '2.1 GB',
      parameters: '7B + LoRA',
      created: new Date().toISOString().split('T')[0],
      description: 'Newly loaded custom model',
      performance: {
        accuracy: 90,
        speed: 'Fast',
        memory: '4.0 GB'
      }
    }
    setModels(prev => [...prev, newModel])
    setShowLoadDialog(false)
    setLoadModelPath('')
  }

  const handleUnloadModel = (modelId) => {
    setModels(prev => prev.filter(model => model.id !== modelId))
  }

  const handleSetDefault = (modelId) => {
    // In a real app, this would make an API call
    console.log(`Setting ${modelId} as default model`)
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Models</h1>
          <p className="text-gray-600 mt-2">Manage your AI models and their configurations</p>
        </div>
        <div className="flex space-x-4">
          <Dialog open={showLoadDialog} onOpenChange={setShowLoadDialog}>
            <DialogTrigger asChild>
              <Button>
                <Upload className="h-4 w-4 mr-2" />
                Load Model
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Load New Model</DialogTitle>
                <DialogDescription>
                  Load a model from a local path or URL
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="model-path">Model Path</Label>
                  <Input
                    id="model-path"
                    value={loadModelPath}
                    onChange={(e) => setLoadModelPath(e.target.value)}
                    placeholder="/path/to/model or https://..."
                  />
                </div>
                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setShowLoadDialog(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleLoadModel} disabled={!loadModelPath}>
                    Load Model
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Discover Models
          </Button>
        </div>
      </div>

      {/* Models Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {models.map((model) => (
          <Card key={model.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-2">
                  <Brain className="h-5 w-5 text-indigo-600" />
                  <CardTitle className="text-lg">{model.name}</CardTitle>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(model.status)}
                  <Badge className={getStatusColor(model.status)}>
                    {model.status}
                  </Badge>
                </div>
              </div>
              <CardDescription>{model.description}</CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-4">
              {/* Model Info */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Type:</span>
                  <p className="font-medium">{model.type}</p>
                </div>
                <div>
                  <span className="text-gray-500">Size:</span>
                  <p className="font-medium">{model.size}</p>
                </div>
                <div>
                  <span className="text-gray-500">Parameters:</span>
                  <p className="font-medium">{model.parameters}</p>
                </div>
                <div>
                  <span className="text-gray-500">Created:</span>
                  <p className="font-medium">{model.created}</p>
                </div>
              </div>

              {/* Performance Metrics */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Accuracy</span>
                  <span className="font-medium">{model.performance.accuracy}%</span>
                </div>
                <Progress value={model.performance.accuracy} className="h-2" />
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Speed:</span>
                  <p className="font-medium">{model.performance.speed}</p>
                </div>
                <div>
                  <span className="text-gray-500">Memory:</span>
                  <p className="font-medium">{model.performance.memory}</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex space-x-2 pt-4">
                {model.status === 'active' ? (
                  <>
                    <Button size="sm" variant="outline" onClick={() => handleSetDefault(model.id)}>
                      Set Default
                    </Button>
                    <Button size="sm" variant="outline">
                      <Settings className="h-4 w-4" />
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline" 
                      onClick={() => handleUnloadModel(model.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </>
                ) : model.status === 'training' ? (
                  <Button size="sm" variant="outline" disabled>
                    <Clock className="h-4 w-4 mr-2" />
                    Training...
                  </Button>
                ) : (
                  <Button size="sm">
                    <Play className="h-4 w-4 mr-2" />
                    Load
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Model Details Panel */}
      {selectedModel && (
        <Card>
          <CardHeader>
            <CardTitle>Model Details: {selectedModel.name}</CardTitle>
            <CardDescription>
              Detailed information and configuration options
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Basic Info */}
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900">Basic Information</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Model ID:</span>
                    <span className="font-mono">{selectedModel.id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Type:</span>
                    <span>{selectedModel.type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Status:</span>
                    <Badge className={getStatusColor(selectedModel.status)}>
                      {selectedModel.status}
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Performance */}
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900">Performance</h3>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Accuracy</span>
                      <span>{selectedModel.performance.accuracy}%</span>
                    </div>
                    <Progress value={selectedModel.performance.accuracy} className="h-2" />
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Inference Speed:</span>
                    <span>{selectedModel.performance.speed}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Memory Usage:</span>
                    <span>{selectedModel.performance.memory}</span>
                  </div>
                </div>
              </div>

              {/* Configuration */}
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900">Configuration</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Parameters:</span>
                    <span>{selectedModel.parameters}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Model Size:</span>
                    <span>{selectedModel.size}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Created:</span>
                    <span>{selectedModel.created}</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* System Resources */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <HardDrive className="h-5 w-5" />
            <span>System Resources</span>
          </CardTitle>
          <CardDescription>
            Current system resource usage and availability
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>GPU Memory</span>
                <span>6.2 / 8.0 GB</span>
              </div>
              <Progress value={77.5} className="h-2" />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>System RAM</span>
                <span>12.4 / 16.0 GB</span>
              </div>
              <Progress value={77.5} className="h-2" />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Storage</span>
                <span>45.2 / 100.0 GB</span>
              </div>
              <Progress value={45.2} className="h-2" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}


