import { useState, useEffect } from 'react'
import { 
  Settings as SettingsIcon, 
  User, 
  Key, 
  Database, 
  Bell, 
  Shield, 
  CreditCard,
  Save,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Eye,
  EyeOff
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'

export default function Settings() {
  const [settings, setSettings] = useState({
    profile: {
      name: 'Demo User',
      email: 'demo@example.com',
      organization: 'Demo Organization',
      timezone: 'UTC'
    },
    api: {
      defaultModel: 'microsoft/DialoGPT-medium',
      maxTokens: 256,
      temperature: 0.7,
      rateLimitPerMinute: 60,
      enableCors: true
    },
    notifications: {
      trainingComplete: true,
      modelErrors: true,
      systemAlerts: true,
      weeklyReports: false,
      emailNotifications: true
    },
    security: {
      twoFactorAuth: false,
      sessionTimeout: 24,
      apiKeyRotation: 30,
      allowedIPs: ''
    },
    billing: {
      plan: 'Professional',
      monthlyUsage: 45000,
      monthlyLimit: 500000,
      autoRenewal: true
    }
  })

  const [showApiKey, setShowApiKey] = useState(false)
  const [apiKey] = useState('sk-demo-1234567890abcdef1234567890abcdef')
  const [unsavedChanges, setUnsavedChanges] = useState(false)

  const updateSetting = (section, key, value) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }))
    setUnsavedChanges(true)
  }

  const handleSave = () => {
    // In a real app, this would make an API call
    console.log('Saving settings:', settings)
    setUnsavedChanges(false)
  }

  const handleReset = () => {
    // Reset to default values
    setUnsavedChanges(false)
  }

  const generateNewApiKey = () => {
    // In a real app, this would make an API call
    console.log('Generating new API key')
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600 mt-2">Manage your account and system preferences</p>
        </div>
        <div className="flex space-x-4">
          {unsavedChanges && (
            <div className="flex items-center space-x-2 text-amber-600">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">Unsaved changes</span>
            </div>
          )}
          <Button variant="outline" onClick={handleReset} disabled={!unsavedChanges}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Reset
          </Button>
          <Button onClick={handleSave} disabled={!unsavedChanges}>
            <Save className="h-4 w-4 mr-2" />
            Save Changes
          </Button>
        </div>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="api">API</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="billing">Billing</TabsTrigger>
        </TabsList>

        {/* Profile Settings */}
        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <User className="h-5 w-5" />
                <span>Profile Information</span>
              </CardTitle>
              <CardDescription>
                Update your personal information and preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="name">Full Name</Label>
                  <Input
                    id="name"
                    value={settings.profile.name}
                    onChange={(e) => updateSetting('profile', 'name', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    value={settings.profile.email}
                    onChange={(e) => updateSetting('profile', 'email', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="organization">Organization</Label>
                  <Input
                    id="organization"
                    value={settings.profile.organization}
                    onChange={(e) => updateSetting('profile', 'organization', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="timezone">Timezone</Label>
                  <Select value={settings.profile.timezone} onValueChange={(value) => updateSetting('profile', 'timezone', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="UTC">UTC</SelectItem>
                      <SelectItem value="America/New_York">Eastern Time</SelectItem>
                      <SelectItem value="America/Chicago">Central Time</SelectItem>
                      <SelectItem value="America/Denver">Mountain Time</SelectItem>
                      <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                      <SelectItem value="Europe/London">London</SelectItem>
                      <SelectItem value="Europe/Paris">Paris</SelectItem>
                      <SelectItem value="Asia/Tokyo">Tokyo</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Settings */}
        <TabsContent value="api">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Key className="h-5 w-5" />
                  <span>API Configuration</span>
                </CardTitle>
                <CardDescription>
                  Configure API defaults and access credentials
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <Label htmlFor="default-model">Default Model</Label>
                    <Select value={settings.api.defaultModel} onValueChange={(value) => updateSetting('api', 'defaultModel', value)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="microsoft/DialoGPT-small">DialoGPT Small</SelectItem>
                        <SelectItem value="microsoft/DialoGPT-medium">DialoGPT Medium</SelectItem>
                        <SelectItem value="microsoft/DialoGPT-large">DialoGPT Large</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="max-tokens">Max Tokens</Label>
                    <Input
                      id="max-tokens"
                      type="number"
                      value={settings.api.maxTokens}
                      onChange={(e) => updateSetting('api', 'maxTokens', parseInt(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="temperature">Temperature</Label>
                    <Input
                      id="temperature"
                      type="number"
                      step="0.1"
                      min="0"
                      max="1"
                      value={settings.api.temperature}
                      onChange={(e) => updateSetting('api', 'temperature', parseFloat(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="rate-limit">Rate Limit (per minute)</Label>
                    <Input
                      id="rate-limit"
                      type="number"
                      value={settings.api.rateLimitPerMinute}
                      onChange={(e) => updateSetting('api', 'rateLimitPerMinute', parseInt(e.target.value))}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="enable-cors">Enable CORS</Label>
                    <p className="text-sm text-gray-500">Allow cross-origin requests to your API</p>
                  </div>
                  <Switch
                    id="enable-cors"
                    checked={settings.api.enableCors}
                    onCheckedChange={(checked) => updateSetting('api', 'enableCors', checked)}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>API Key Management</CardTitle>
                <CardDescription>
                  Manage your API access credentials
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="api-key">Current API Key</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="api-key"
                      type={showApiKey ? "text" : "password"}
                      value={apiKey}
                      readOnly
                      className="font-mono"
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowApiKey(!showApiKey)}
                    >
                      {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                    <Button variant="outline" size="sm" onClick={generateNewApiKey}>
                      Generate New
                    </Button>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Keep your API key secure and never share it publicly
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Notifications */}
        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Bell className="h-5 w-5" />
                <span>Notification Preferences</span>
              </CardTitle>
              <CardDescription>
                Choose what notifications you want to receive
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="training-complete">Training Complete</Label>
                    <p className="text-sm text-gray-500">Get notified when model training finishes</p>
                  </div>
                  <Switch
                    id="training-complete"
                    checked={settings.notifications.trainingComplete}
                    onCheckedChange={(checked) => updateSetting('notifications', 'trainingComplete', checked)}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="model-errors">Model Errors</Label>
                    <p className="text-sm text-gray-500">Get notified about model loading or inference errors</p>
                  </div>
                  <Switch
                    id="model-errors"
                    checked={settings.notifications.modelErrors}
                    onCheckedChange={(checked) => updateSetting('notifications', 'modelErrors', checked)}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="system-alerts">System Alerts</Label>
                    <p className="text-sm text-gray-500">Get notified about system maintenance and updates</p>
                  </div>
                  <Switch
                    id="system-alerts"
                    checked={settings.notifications.systemAlerts}
                    onCheckedChange={(checked) => updateSetting('notifications', 'systemAlerts', checked)}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="weekly-reports">Weekly Reports</Label>
                    <p className="text-sm text-gray-500">Receive weekly usage and performance reports</p>
                  </div>
                  <Switch
                    id="weekly-reports"
                    checked={settings.notifications.weeklyReports}
                    onCheckedChange={(checked) => updateSetting('notifications', 'weeklyReports', checked)}
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="email-notifications">Email Notifications</Label>
                    <p className="text-sm text-gray-500">Send notifications to your email address</p>
                  </div>
                  <Switch
                    id="email-notifications"
                    checked={settings.notifications.emailNotifications}
                    onCheckedChange={(checked) => updateSetting('notifications', 'emailNotifications', checked)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security */}
        <TabsContent value="security">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5" />
                <span>Security Settings</span>
              </CardTitle>
              <CardDescription>
                Configure security and access controls
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="two-factor">Two-Factor Authentication</Label>
                  <p className="text-sm text-gray-500">Add an extra layer of security to your account</p>
                </div>
                <Switch
                  id="two-factor"
                  checked={settings.security.twoFactorAuth}
                  onCheckedChange={(checked) => updateSetting('security', 'twoFactorAuth', checked)}
                />
              </div>

              <Separator />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="session-timeout">Session Timeout (hours)</Label>
                  <Input
                    id="session-timeout"
                    type="number"
                    value={settings.security.sessionTimeout}
                    onChange={(e) => updateSetting('security', 'sessionTimeout', parseInt(e.target.value))}
                  />
                </div>
                <div>
                  <Label htmlFor="api-key-rotation">API Key Rotation (days)</Label>
                  <Input
                    id="api-key-rotation"
                    type="number"
                    value={settings.security.apiKeyRotation}
                    onChange={(e) => updateSetting('security', 'apiKeyRotation', parseInt(e.target.value))}
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="allowed-ips">Allowed IP Addresses</Label>
                <Textarea
                  id="allowed-ips"
                  placeholder="Enter IP addresses or ranges, one per line (leave empty to allow all)"
                  value={settings.security.allowedIPs}
                  onChange={(e) => updateSetting('security', 'allowedIPs', e.target.value)}
                  className="h-24"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Example: 192.168.1.0/24 or 203.0.113.1
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Billing */}
        <TabsContent value="billing">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <CreditCard className="h-5 w-5" />
                  <span>Billing Information</span>
                </CardTitle>
                <CardDescription>
                  Manage your subscription and usage
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium">Current Plan</h3>
                    <p className="text-sm text-gray-500">Professional Plan</p>
                  </div>
                  <Badge variant="default" className="bg-green-100 text-green-800">
                    Active
                  </Badge>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900">{settings.billing.monthlyUsage.toLocaleString()}</div>
                    <div className="text-sm text-gray-500">Tokens Used</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900">{settings.billing.monthlyLimit.toLocaleString()}</div>
                    <div className="text-sm text-gray-500">Monthly Limit</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900">
                      {Math.round((settings.billing.monthlyUsage / settings.billing.monthlyLimit) * 100)}%
                    </div>
                    <div className="text-sm text-gray-500">Usage</div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="auto-renewal">Auto Renewal</Label>
                    <p className="text-sm text-gray-500">Automatically renew your subscription</p>
                  </div>
                  <Switch
                    id="auto-renewal"
                    checked={settings.billing.autoRenewal}
                    onCheckedChange={(checked) => updateSetting('billing', 'autoRenewal', checked)}
                  />
                </div>

                <div className="flex space-x-4">
                  <Button variant="outline">
                    View Usage Details
                  </Button>
                  <Button variant="outline">
                    Download Invoice
                  </Button>
                  <Button>
                    Upgrade Plan
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Usage Statistics</CardTitle>
                <CardDescription>
                  Your usage over the past 30 days
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                  <p className="text-gray-500">Usage chart would appear here</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

  const [settings, setSettings] = useState({
    email: 'admin@example.com',
    firstName: 'Admin',
    lastName: 'User',
    timezone: 'UTC',
    notifications: {
      email: true,
      training: true,
      api: false
    },
    apiKey: 'fb8d58f3f79448ebb16ef76dfd145b72'
  })

  const handleSave = () => {
    alert('Settings saved successfully!')
  }

  const generateNewApiKey = () => {
    const newKey = Math.random().toString(36).substring(2, 34)
    setSettings(prev => ({
      ...prev,
      apiKey: newKey
    }))
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-2">Manage your account and preferences</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar */}
        <div className="lg:w-64">
          <nav className="space-y-1">
            {[
              { id: 'profile', name: 'Profile', icon: User },
              { id: 'api', name: 'API Keys', icon: Key },
              { id: 'notifications', name: 'Notifications', icon: Bell },
              { id: 'security', name: 'Security', icon: Shield }
            ].map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center space-x-3 px-3 py-2 text-left rounded-lg transition-colors ${
                    activeTab === tab.id
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{tab.name}</span>
                </button>
              )
            })}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1">
          <div className="bg-white rounded-lg shadow-md p-6">
            {activeTab === 'profile' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900">Profile Information</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email Address
                    </label>
                    <input
                      type="email"
                      value={settings.email}
                      onChange={(e) => setSettings(prev => ({ ...prev, email: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      First Name
                    </label>
                    <input
                      type="text"
                      value={settings.firstName}
                      onChange={(e) => setSettings(prev => ({ ...prev, firstName: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Last Name
                    </label>
                    <input
                      type="text"
                      value={settings.lastName}
                      onChange={(e) => setSettings(prev => ({ ...prev, lastName: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Timezone
                    </label>
                    <select
                      value={settings.timezone}
                      onChange={(e) => setSettings(prev => ({ ...prev, timezone: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="UTC">UTC</option>
                      <option value="America/New_York">Eastern Time</option>
                      <option value="America/Chicago">Central Time</option>
                      <option value="America/Denver">Mountain Time</option>
                      <option value="America/Los_Angeles">Pacific Time</option>
                    </select>
                  </div>
                </div>
                
                <button
                  onClick={handleSave}
                  className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <Save className="h-4 w-4" />
                  <span>Save Changes</span>
                </button>
              </div>
            )}

            {activeTab === 'api' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900">API Keys</h2>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <label className="block text-sm font-medium text-gray-700">
                      Current API Key
                    </label>
                    <button
                      onClick={generateNewApiKey}
                      className="text-sm text-indigo-600 hover:text-indigo-500"
                    >
                      Generate New
                    </button>
                  </div>
                  <div className="flex items-center space-x-2">
                    <code className="flex-1 px-3 py-2 bg-white border border-gray-300 rounded-md text-sm font-mono">
                      {settings.apiKey}
                    </code>
                    <button
                      onClick={() => navigator.clipboard.writeText(settings.apiKey)}
                      className="px-3 py-2 text-sm text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
                    >
                      Copy
                    </button>
                  </div>
                </div>
                
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-yellow-800 mb-2">Important Security Notice</h3>
                  <p className="text-sm text-yellow-700">
                    Keep your API key secure and never share it publicly. If you suspect it has been compromised, 
                    generate a new one immediately.
                  </p>
                </div>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900">Notification Preferences</h2>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">Email Notifications</h3>
                      <p className="text-sm text-gray-500">Receive notifications via email</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.notifications.email}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        notifications: { ...prev.notifications, email: e.target.checked }
                      }))}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">Training Completion</h3>
                      <p className="text-sm text-gray-500">Notify when training jobs complete</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.notifications.training}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        notifications: { ...prev.notifications, training: e.target.checked }
                      }))}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">API Usage Alerts</h3>
                      <p className="text-sm text-gray-500">Alert when approaching usage limits</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.notifications.api}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        notifications: { ...prev.notifications, api: e.target.checked }
                      }))}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                  </div>
                </div>
                
                <button
                  onClick={handleSave}
                  className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <Save className="h-4 w-4" />
                  <span>Save Preferences</span>
                </button>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900">Security Settings</h2>
                
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Change Password</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Current Password
                        </label>
                        <input
                          type="password"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          New Password
                        </label>
                        <input
                          type="password"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Confirm New Password
                        </label>
                        <input
                          type="password"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                        />
                      </div>
                      <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
                        Update Password
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
