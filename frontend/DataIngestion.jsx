import { useState, useEffect } from 'react'
import { 
  Database, 
  Upload, 
  FileText, 
  Globe, 
  FolderOpen, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  Download,
  Trash2,
  Eye,
  Filter
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function DataIngestion() {
  const [ingestionJobs, setIngestionJobs] = useState([
    {
      id: 'ingest_001',
      name: 'Legal Documents Batch 1',
      type: 'files',
      status: 'completed',
      progress: 100,
      itemsProcessed: 1250,
      totalItems: 1250,
      startTime: '2024-06-15 09:30',
      endTime: '2024-06-15 10:15',
      dataSize: '45.2 MB',
      errors: 0
    },
    {
      id: 'ingest_002',
      name: 'Medical Research Papers',
      type: 'web',
      status: 'running',
      progress: 73,
      itemsProcessed: 892,
      totalItems: 1220,
      startTime: '2024-06-16 08:45',
      endTime: null,
      dataSize: '67.8 MB',
      errors: 3
    },
    {
      id: 'ingest_003',
      name: 'Financial Reports Directory',
      type: 'directory',
      status: 'queued',
      progress: 0,
      itemsProcessed: 0,
      totalItems: 450,
      startTime: null,
      endTime: null,
      dataSize: '0 MB',
      errors: 0
    }
  ])

  const [showNewIngestionDialog, setShowNewIngestionDialog] = useState(false)
  const [newIngestion, setNewIngestion] = useState({
    name: '',
    type: 'files',
    sources: [],
    maxFileSize: 100,
    recursive: true,
    removeHtml: true,
    removeDuplicates: true
  })

  const [filterStatus, setFilterStatus] = useState('all')

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'running':
        return <Clock className="h-4 w-4 text-blue-500 animate-spin" />
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

  const getTypeIcon = (type) => {
    switch (type) {
      case 'files':
        return <FileText className="h-4 w-4" />
      case 'web':
        return <Globe className="h-4 w-4" />
      case 'directory':
        return <FolderOpen className="h-4 w-4" />
      default:
        return <Database className="h-4 w-4" />
    }
  }

  const handleStartIngestion = () => {
    const newJob = {
      id: `ingest_${Date.now()}`,
      name: newIngestion.name,
      type: newIngestion.type,
      status: 'queued',
      progress: 0,
      itemsProcessed: 0,
      totalItems: newIngestion.sources.length,
      startTime: null,
      endTime: null,
      dataSize: '0 MB',
      errors: 0
    }
    
    setIngestionJobs(prev => [...prev, newJob])
    setShowNewIngestionDialog(false)
    setNewIngestion({
      name: '',
      type: 'files',
      sources: [],
      maxFileSize: 100,
      recursive: true,
      removeHtml: true,
      removeDuplicates: true
    })
  }

  const filteredJobs = ingestionJobs.filter(job => 
    filterStatus === 'all' || job.status === filterStatus
  )

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
          <h1 className="text-3xl font-bold text-gray-900">Data Ingestion</h1>
          <p className="text-gray-600 mt-2">Import and process data from various sources</p>
        </div>
        <div className="flex space-x-4">
          <Select value={filterStatus} onValueChange={setFilterStatus}>
            <SelectTrigger className="w-40">
              <Filter className="h-4 w-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="running">Running</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="failed">Failed</SelectItem>
              <SelectItem value="queued">Queued</SelectItem>
            </SelectContent>
          </Select>
          <Dialog open={showNewIngestionDialog} onOpenChange={setShowNewIngestionDialog}>
            <DialogTrigger asChild>
              <Button>
                <Upload className="h-4 w-4 mr-2" />
                New Ingestion
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Start Data Ingestion</DialogTitle>
                <DialogDescription>
                  Configure and start a new data ingestion job
                </DialogDescription>
              </DialogHeader>
              <Tabs value={newIngestion.type} onValueChange={(value) => setNewIngestion(prev => ({ ...prev, type: value }))}>
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="files">Files</TabsTrigger>
                  <TabsTrigger value="web">Web URLs</TabsTrigger>
                  <TabsTrigger value="directory">Directory</TabsTrigger>
                </TabsList>
                
                <div className="space-y-6 mt-6">
                  <div>
                    <Label htmlFor="ingestion-name">Job Name</Label>
                    <Input
                      id="ingestion-name"
                      value={newIngestion.name}
                      onChange={(e) => setNewIngestion(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="e.g., Legal Documents Batch 2"
                    />
                  </div>

                  <TabsContent value="files" className="space-y-4">
                    <div>
                      <Label htmlFor="file-sources">File Paths</Label>
                      <Textarea
                        id="file-sources"
                        placeholder="Enter file paths, one per line..."
                        className="h-32"
                        value={newIngestion.sources.join('\n')}
                        onChange={(e) => setNewIngestion(prev => ({ ...prev, sources: e.target.value.split('\n').filter(f => f.trim()) }))}
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Supports: .txt, .pdf, .docx, .md, .html
                      </p>
                    </div>
                  </TabsContent>

                  <TabsContent value="web" className="space-y-4">
                    <div>
                      <Label htmlFor="web-sources">URLs</Label>
                      <Textarea
                        id="web-sources"
                        placeholder="Enter URLs, one per line..."
                        className="h-32"
                        value={newIngestion.sources.join('\n')}
                        onChange={(e) => setNewIngestion(prev => ({ ...prev, sources: e.target.value.split('\n').filter(f => f.trim()) }))}
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Will extract text content from web pages
                      </p>
                    </div>
                  </TabsContent>

                  <TabsContent value="directory" className="space-y-4">
                    <div>
                      <Label htmlFor="directory-sources">Directory Paths</Label>
                      <Textarea
                        id="directory-sources"
                        placeholder="Enter directory paths, one per line..."
                        className="h-32"
                        value={newIngestion.sources.join('\n')}
                        onChange={(e) => setNewIngestion(prev => ({ ...prev, sources: e.target.value.split('\n').filter(f => f.trim()) }))}
                      />
                      <div className="flex items-center space-x-2 mt-2">
                        <input
                          type="checkbox"
                          id="recursive"
                          checked={newIngestion.recursive}
                          onChange={(e) => setNewIngestion(prev => ({ ...prev, recursive: e.target.checked }))}
                        />
                        <Label htmlFor="recursive" className="text-sm">Recursive (include subdirectories)</Label>
                      </div>
                    </div>
                  </TabsContent>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Max File Size (MB): {newIngestion.maxFileSize}</Label>
                      <input
                        type="range"
                        min="1"
                        max="500"
                        value={newIngestion.maxFileSize}
                        onChange={(e) => setNewIngestion(prev => ({ ...prev, maxFileSize: parseInt(e.target.value) }))}
                        className="w-full mt-2"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Processing Options</Label>
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id="remove-html"
                            checked={newIngestion.removeHtml}
                            onChange={(e) => setNewIngestion(prev => ({ ...prev, removeHtml: e.target.checked }))}
                          />
                          <Label htmlFor="remove-html" className="text-sm">Remove HTML tags</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id="remove-duplicates"
                            checked={newIngestion.removeDuplicates}
                            onChange={(e) => setNewIngestion(prev => ({ ...prev, removeDuplicates: e.target.checked }))}
                          />
                          <Label htmlFor="remove-duplicates" className="text-sm">Remove duplicates</Label>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-end space-x-2">
                    <Button variant="outline" onClick={() => setShowNewIngestionDialog(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleStartIngestion} disabled={!newIngestion.name || newIngestion.sources.length === 0}>
                      Start Ingestion
                    </Button>
                  </div>
                </div>
              </Tabs>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Jobs</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{ingestionJobs.length}</div>
            <p className="text-xs text-muted-foreground">
              {ingestionJobs.filter(j => j.status === 'completed').length} completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Items Processed</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {ingestionJobs.reduce((acc, job) => acc + job.itemsProcessed, 0).toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              Across all jobs
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Data Volume</CardTitle>
            <Download className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">113 MB</div>
            <p className="text-xs text-muted-foreground">
              Total ingested
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">98.5%</div>
            <p className="text-xs text-muted-foreground">
              Items processed successfully
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Ingestion Jobs */}
      <div className="space-y-6">
        {filteredJobs.map((job) => (
          <Card key={job.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(job.status)}
                  <div className="flex items-center space-x-2">
                    {getTypeIcon(job.type)}
                    <div>
                      <CardTitle className="text-lg">{job.name}</CardTitle>
                      <CardDescription>
                        {job.type} ingestion • {job.itemsProcessed}/{job.totalItems} items
                      </CardDescription>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge className={getStatusColor(job.status)}>
                    {job.status}
                  </Badge>
                  <Button size="sm" variant="outline">
                    <Eye className="h-4 w-4" />
                  </Button>
                  {job.status === 'completed' && (
                    <Button size="sm" variant="outline">
                      <Download className="h-4 w-4" />
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
                    <span>Processing Progress</span>
                    <span>{job.progress}%</span>
                  </div>
                  <Progress value={job.progress} className="h-2" />
                </div>
              )}

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Start Time:</span>
                  <p className="font-medium">{job.startTime || 'Not started'}</p>
                </div>
                <div>
                  <span className="text-gray-500">Duration:</span>
                  <p className="font-medium">{formatDuration(job.startTime, job.endTime)}</p>
                </div>
                <div>
                  <span className="text-gray-500">Data Size:</span>
                  <p className="font-medium">{job.dataSize}</p>
                </div>
                <div>
                  <span className="text-gray-500">Errors:</span>
                  <p className={`font-medium ${job.errors > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {job.errors}
                  </p>
                </div>
                <div>
                  <span className="text-gray-500">Success Rate:</span>
                  <p className="font-medium">
                    {job.itemsProcessed > 0 ? Math.round(((job.itemsProcessed - job.errors) / job.itemsProcessed) * 100) : 0}%
                  </p>
                </div>
              </div>

              {/* Error Details */}
              {job.errors > 0 && (
                <div className="mt-4 p-3 bg-red-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <AlertCircle className="h-4 w-4 text-red-500" />
                    <span className="text-sm font-medium text-red-800">
                      {job.errors} errors encountered during processing
                    </span>
                  </div>
                  <p className="text-xs text-red-600 mt-1">
                    Click the view button to see error details
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredJobs.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No ingestion jobs found</h3>
            <p className="text-gray-500 mb-4">
              {filterStatus === 'all' 
                ? 'Start your first data ingestion job to begin processing your data.'
                : `No jobs with status "${filterStatus}" found.`
              }
            </p>
            <Button onClick={() => setShowNewIngestionDialog(true)}>
              <Upload className="h-4 w-4 mr-2" />
              Start New Ingestion
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

import { useState } from 'react'
import { Database, Upload, File, Link, Globe } from 'lucide-react'

function DataIngestion() {
  const [activeTab, setActiveTab] = useState('upload')
  const [uploading, setUploading] = useState(false)

  const handleFileUpload = async (event) => {
    const files = event.target.files
    if (!files.length) return

    setUploading(true)
    
    // Simulate upload process
    setTimeout(() => {
      setUploading(false)
      alert('Files uploaded successfully!')
    }, 2000)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Data Ingestion</h1>
        <p className="text-gray-600 mt-2">Upload and manage your training data</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'upload', name: 'File Upload', icon: Upload },
            { id: 'url', name: 'URL Import', icon: Link },
            { id: 'web', name: 'Web Scraping', icon: Globe },
            { id: 'database', name: 'Database', icon: Database }
          ].map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.name}</span>
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg shadow-md p-6">
        {activeTab === 'upload' && (
          <div className="space-y-6">
            <div className="text-center">
              <File className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Upload Files</h3>
              <p className="text-gray-500 mb-4">
                Support for PDF, TXT, CSV, JSON, and more
              </p>
            </div>
            
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-indigo-500 transition-colors">
              <input
                type="file"
                multiple
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
                accept=".pdf,.txt,.csv,.json,.docx"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer flex flex-col items-center space-y-2"
              >
                <Upload className="h-8 w-8 text-gray-400" />
                <span className="text-gray-600">
                  Click to upload or drag and drop files here
                </span>
                <span className="text-sm text-gray-500">
                  PDF, TXT, CSV, JSON up to 10MB each
                </span>
              </label>
            </div>

            {uploading && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center space-x-3">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                  <span className="text-blue-800">Uploading files...</span>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'url' && (
          <div className="space-y-6">
            <div className="text-center">
              <Link className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Import from URLs</h3>
              <p className="text-gray-500 mb-4">
                Import content from web pages, APIs, or documents
              </p>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  URLs (one per line)
                </label>
                <textarea
                  rows={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="https://example.com/page1
https://example.com/page2
https://api.example.com/data"
                />
              </div>
              <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
                Import URLs
              </button>
            </div>
          </div>
        )}

        {activeTab === 'web' && (
          <div className="space-y-6">
            <div className="text-center">
              <Globe className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Web Scraping</h3>
              <p className="text-gray-500 mb-4">
                Automatically scrape content from websites
              </p>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Website URL
                </label>
                <input
                  type="url"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="https://example.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Scraping Depth
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
                  <option value="1">1 level (current page only)</option>
                  <option value="2">2 levels</option>
                  <option value="3">3 levels</option>
                </select>
              </div>
              <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
                Start Scraping
              </button>
            </div>
          </div>
        )}

        {activeTab === 'database' && (
          <div className="space-y-6">
            <div className="text-center">
              <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Database Connection</h3>
              <p className="text-gray-500 mb-4">
                Connect to SQL databases and import data
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Database Type
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
                  <option value="postgresql">PostgreSQL</option>
                  <option value="mysql">MySQL</option>
                  <option value="sqlite">SQLite</option>
                  <option value="mongodb">MongoDB</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Host
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="localhost"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Database Name
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="my_database"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Port
                </label>
                <input
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="5432"
                />
              </div>
            </div>
            
            <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
              Test Connection
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default DataIngestion
