import { useState, useEffect } from 'react'
import { 
  CreditCard, 
  Crown, 
  Check, 
  X, 
  TrendingUp, 
  Users, 
  Zap,
  Shield,
  Star,
  Download,
  Calendar,
  AlertCircle
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function Subscription() {
  const [currentSubscription, setCurrentSubscription] = useState({
    plan: 'professional',
    status: 'active',
    tokens_used: 45000,
    tokens_limit: 500000,
    current_period_end: '2024-07-16',
    auto_renew: true
  })

  const [plans, setPlans] = useState({
    free: {
      name: 'Free',
      price: 0,
      monthly_tokens: 1000,
      features: ['Basic models', 'Community support'],
      max_models: 1,
      max_training_jobs: 1
    },
    individual: {
      name: 'Individual',
      price: 999,
      monthly_tokens: 50000,
      features: ['All models', 'Email support', 'API access'],
      max_models: 5,
      max_training_jobs: 10
    },
    professional: {
      name: 'Professional',
      price: 4999,
      monthly_tokens: 500000,
      features: ['Custom model training', 'Priority support', 'Advanced analytics'],
      max_models: 20,
      max_training_jobs: 50
    },
    enterprise: {
      name: 'Enterprise',
      price: 19999,
      monthly_tokens: -1,
      features: ['Unlimited tokens', 'Dedicated infrastructure', 'Phone support', 'Custom SLA'],
      max_models: -1,
      max_training_jobs: -1
    }
  })

  const [invoices, setInvoices] = useState([
    {
      id: 'inv_001',
      date: '2024-06-01',
      amount: 4999,
      status: 'paid',
      plan: 'Professional',
      period: 'June 2024'
    },
    {
      id: 'inv_002',
      date: '2024-05-01',
      amount: 4999,
      status: 'paid',
      plan: 'Professional',
      period: 'May 2024'
    }
  ])

  const [showUpgradeDialog, setShowUpgradeDialog] = useState(false)
  const [selectedPlan, setSelectedPlan] = useState(null)

  const formatPrice = (price) => {
    if (price === 0) return 'Free'
    return `$${(price / 100).toFixed(2)}`
  }

  const formatTokens = (tokens) => {
    if (tokens === -1) return 'Unlimited'
    return tokens.toLocaleString()
  }

  const getUsagePercentage = () => {
    if (currentSubscription.tokens_limit === -1) return 0
    return (currentSubscription.tokens_used / currentSubscription.tokens_limit) * 100
  }

  const getPlanIcon = (planKey) => {
    switch (planKey) {
      case 'free':
        return <Users className="h-5 w-5" />
      case 'individual':
        return <User className="h-5 w-5" />
      case 'professional':
        return <Crown className="h-5 w-5" />
      case 'enterprise':
        return <Shield className="h-5 w-5" />
      default:
        return <Star className="h-5 w-5" />
    }
  }

  const getPlanColor = (planKey) => {
    switch (planKey) {
      case 'free':
        return 'border-gray-200'
      case 'individual':
        return 'border-blue-200'
      case 'professional':
        return 'border-purple-200 bg-purple-50'
      case 'enterprise':
        return 'border-gold-200 bg-gradient-to-br from-yellow-50 to-orange-50'
      default:
        return 'border-gray-200'
    }
  }

  const handleUpgrade = (planKey) => {
    setSelectedPlan(planKey)
    setShowUpgradeDialog(true)
  }

  const confirmUpgrade = () => {
    // In a real app, this would make an API call to upgrade the subscription
    console.log(`Upgrading to ${selectedPlan} plan`)
    setCurrentSubscription(prev => ({ ...prev, plan: selectedPlan }))
    setShowUpgradeDialog(false)
    setSelectedPlan(null)
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Subscription</h1>
          <p className="text-gray-600 mt-2">Manage your subscription and billing</p>
        </div>
        <Badge variant={currentSubscription.status === 'active' ? 'default' : 'secondary'} className="bg-green-100 text-green-800">
          {currentSubscription.status}
        </Badge>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="plans">Plans</TabsTrigger>
          <TabsTrigger value="billing">Billing</TabsTrigger>
          <TabsTrigger value="usage">Usage</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Current Plan */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Crown className="h-5 w-5 text-purple-600" />
                <span>Current Plan: {plans[currentSubscription.plan]?.name}</span>
              </CardTitle>
              <CardDescription>
                Your subscription renews on {currentSubscription.current_period_end}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {formatPrice(plans[currentSubscription.plan]?.price)}
                  </div>
                  <div className="text-sm text-gray-500">per month</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {formatTokens(plans[currentSubscription.plan]?.monthly_tokens)}
                  </div>
                  <div className="text-sm text-gray-500">tokens/month</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {plans[currentSubscription.plan]?.max_models === -1 ? '∞' : plans[currentSubscription.plan]?.max_models}
                  </div>
                  <div className="text-sm text-gray-500">max models</div>
                </div>
              </div>

              {/* Usage Progress */}
              {currentSubscription.tokens_limit !== -1 && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Token Usage</span>
                    <span>{currentSubscription.tokens_used.toLocaleString()} / {currentSubscription.tokens_limit.toLocaleString()}</span>
                  </div>
                  <Progress value={getUsagePercentage()} className="h-2" />
                  <p className="text-xs text-gray-500">
                    {Math.round(getUsagePercentage())}% of monthly limit used
                  </p>
                </div>
              )}

              {/* Features */}
              <div>
                <h3 className="font-medium text-gray-900 mb-3">Plan Features</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {plans[currentSubscription.plan]?.features.map((feature, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <Check className="h-4 w-4 text-green-500" />
                      <span className="text-sm text-gray-700">{feature}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex space-x-4">
                <Button onClick={() => handleUpgrade('enterprise')}>
                  Upgrade Plan
                </Button>
                <Button variant="outline">
                  Manage Billing
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">This Month</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{currentSubscription.tokens_used.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">tokens used</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">API Calls</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">1,547</div>
                <p className="text-xs text-muted-foreground">this month</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Next Billing</CardTitle>
                <Calendar className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">16</div>
                <p className="text-xs text-muted-foreground">days remaining</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Plans Tab */}
        <TabsContent value="plans">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {Object.entries(plans).map(([planKey, plan]) => (
              <Card key={planKey} className={`relative ${getPlanColor(planKey)} ${currentSubscription.plan === planKey ? 'ring-2 ring-purple-500' : ''}`}>
                {planKey === 'professional' && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-purple-600 text-white">Most Popular</Badge>
                  </div>
                )}
                <CardHeader className="text-center">
                  <div className="flex justify-center mb-2">
                    {getPlanIcon(planKey)}
                  </div>
                  <CardTitle className="text-lg">{plan.name}</CardTitle>
                  <div className="text-3xl font-bold">
                    {formatPrice(plan.price)}
                    {plan.price > 0 && <span className="text-sm font-normal text-gray-500">/month</span>}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center">
                    <div className="text-lg font-semibold">{formatTokens(plan.monthly_tokens)}</div>
                    <div className="text-sm text-gray-500">tokens/month</div>
                  </div>
                  
                  <div className="space-y-2">
                    {plan.features.map((feature, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <Check className="h-4 w-4 text-green-500" />
                        <span className="text-sm">{feature}</span>
                      </div>
                    ))}
                  </div>

                  <div className="pt-4">
                    {currentSubscription.plan === planKey ? (
                      <Button className="w-full" disabled>
                        Current Plan
                      </Button>
                    ) : (
                      <Button 
                        className="w-full" 
                        variant={planKey === 'professional' ? 'default' : 'outline'}
                        onClick={() => handleUpgrade(planKey)}
                      >
                        {plans[currentSubscription.plan]?.price < plan.price ? 'Upgrade' : 'Downgrade'}
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Billing Tab */}
        <TabsContent value="billing" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Payment Method</CardTitle>
              <CardDescription>Manage your payment information</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-4 p-4 border rounded-lg">
                <CreditCard className="h-8 w-8 text-gray-400" />
                <div className="flex-1">
                  <div className="font-medium">Visa ending in 4242</div>
                  <div className="text-sm text-gray-500">Expires 12/2025</div>
                </div>
                <Badge variant="secondary">Default</Badge>
              </div>
              <div className="mt-4 flex space-x-4">
                <Button variant="outline">Update Payment Method</Button>
                <Button variant="outline">Add Payment Method</Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Billing History</CardTitle>
              <CardDescription>Download your invoices and view payment history</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {invoices.map((invoice) => (
                  <div key={invoice.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <div className="font-medium">{invoice.period}</div>
                      <div className="text-sm text-gray-500">{invoice.date}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">{formatPrice(invoice.amount)}</div>
                      <Badge variant={invoice.status === 'paid' ? 'default' : 'secondary'}>
                        {invoice.status}
                      </Badge>
                    </div>
                    <Button variant="outline" size="sm">
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Usage Tab */}
        <TabsContent value="usage">
          <Card>
            <CardHeader>
              <CardTitle>Usage Analytics</CardTitle>
              <CardDescription>Detailed breakdown of your API usage</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                <p className="text-gray-500">Usage analytics chart would appear here</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Upgrade Dialog */}
      <Dialog open={showUpgradeDialog} onOpenChange={setShowUpgradeDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Upgrade Subscription</DialogTitle>
            <DialogDescription>
              Confirm your upgrade to the {selectedPlan && plans[selectedPlan]?.name} plan
            </DialogDescription>
          </DialogHeader>
          {selectedPlan && (
            <div className="space-y-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="font-medium">{plans[selectedPlan].name} Plan</span>
                  <span className="text-lg font-bold">{formatPrice(plans[selectedPlan].price)}/month</span>
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  {formatTokens(plans[selectedPlan].monthly_tokens)} tokens per month
                </div>
              </div>
              
              <div className="flex items-start space-x-2 p-3 bg-blue-50 rounded-lg">
                <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                <div className="text-sm text-blue-800">
                  Your subscription will be upgraded immediately and you'll be charged a prorated amount for the remainder of this billing period.
                </div>
              </div>

              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setShowUpgradeDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={confirmUpgrade}>
                  Confirm Upgrade
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

import { useState, useEffect } from 'react'
import { Crown, Check, X } from 'lucide-react'

function Subscription() {
  const [currentPlan, setCurrentPlan] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSubscription()
  }, [])

  const fetchSubscription = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/v1/subscription', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setCurrentPlan(data.subscription)
      } else {
        // Fallback demo data
        setCurrentPlan({
          tier: 'enterprise',
          status: 'active',
          monthly_token_limit: null,
          monthly_tokens_used: 1250,
          monthly_training_hours_limit: null,
          monthly_training_hours_used: 5.5
        })
      }
    } catch (error) {
      console.error('Error fetching subscription:', error)
    }
    setLoading(false)
  }

  const plans = [
    {
      name: 'Starter',
      price: '$29',
      interval: 'month',
      features: [
        '10,000 API calls/month',
        '2 hours training/month',
        '1 custom model',
        'Email support',
        'Basic analytics'
      ],
      limitations: [
        'No priority support',
        'Limited integrations'
      ]
    },
    {
      name: 'Professional',
      price: '$99',
      interval: 'month',
      popular: true,
      features: [
        '100,000 API calls/month',
        '20 hours training/month',
        '5 custom models',
        'Priority support',
        'Advanced analytics',
        'API access',
        'Custom integrations'
      ],
      limitations: []
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      interval: '',
      features: [
        'Unlimited API calls',
        'Unlimited training',
        'Unlimited models',
        '24/7 priority support',
        'Advanced analytics',
        'API access',
        'Custom integrations',
        'Dedicated account manager',
        'SLA guarantee'
      ],
      limitations: []
    }
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Subscription</h1>
        <p className="text-gray-600 mt-2">Choose the plan that's right for you</p>
      </div>

      {/* Current Plan Status */}
      {currentPlan && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Crown className="h-6 w-6 text-indigo-600" />
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Current Plan</h2>
                <p className="text-sm text-gray-500">
                  {currentPlan.tier.charAt(0).toUpperCase() + currentPlan.tier.slice(1)} Plan
                </p>
              </div>
            </div>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              currentPlan.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
            }`}>
              {currentPlan.status}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">API Usage</h3>
              <div className="bg-gray-200 rounded-full h-2 mb-2">
                <div 
                  className="bg-indigo-600 h-2 rounded-full"
                  style={{ 
                    width: currentPlan.monthly_token_limit 
                      ? `${(currentPlan.monthly_tokens_used / currentPlan.monthly_token_limit) * 100}%` 
                      : '12%' 
                  }}
                ></div>
              </div>
              <p className="text-sm text-gray-600">
                {currentPlan.monthly_tokens_used?.toLocaleString() || 0} 
                {currentPlan.monthly_token_limit ? ` / ${currentPlan.monthly_token_limit.toLocaleString()}` : ' / Unlimited'}
              </p>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Training Hours</h3>
              <div className="bg-gray-200 rounded-full h-2 mb-2">
                <div 
                  className="bg-green-600 h-2 rounded-full"
                  style={{ 
                    width: currentPlan.monthly_training_hours_limit 
                      ? `${(currentPlan.monthly_training_hours_used / currentPlan.monthly_training_hours_limit) * 100}%` 
                      : '28%' 
                  }}
                ></div>
              </div>
              <p className="text-sm text-gray-600">
                {currentPlan.monthly_training_hours_used || 0} hours
                {currentPlan.monthly_training_hours_limit ? ` / ${currentPlan.monthly_training_hours_limit}` : ' / Unlimited'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Pricing Plans */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {plans.map((plan, index) => (
          <div key={index} className={`bg-white rounded-lg shadow-md p-6 relative ${
            plan.popular ? 'ring-2 ring-indigo-500' : ''
          }`}>
            {plan.popular && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <span className="bg-indigo-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                  Most Popular
                </span>
              </div>
            )}

            <div className="text-center mb-6">
              <h3 className="text-xl font-semibold text-gray-900">{plan.name}</h3>
              <div className="mt-2">
                <span className="text-3xl font-bold text-gray-900">{plan.price}</span>
                {plan.interval && (
                  <span className="text-gray-500">/{plan.interval}</span>
                )}
              </div>
            </div>

            <ul className="space-y-3 mb-6">
              {plan.features.map((feature, featureIndex) => (
                <li key={featureIndex} className="flex items-start space-x-3">
                  <Check className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-700">{feature}</span>
                </li>
              ))}
              {plan.limitations.map((limitation, limitIndex) => (
                <li key={limitIndex} className="flex items-start space-x-3">
                  <X className="h-5 w-5 text-red-500 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-500">{limitation}</span>
                </li>
              ))}
            </ul>

            <button className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
              plan.popular
                ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
            }`}>
              {currentPlan?.tier === plan.name.toLowerCase() ? 'Current Plan' : 'Choose Plan'}
            </button>
          </div>
        ))}
      </div>

      <div className="bg-gray-50 rounded-lg p-6 text-center">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Need a custom solution?</h3>
        <p className="text-gray-600 mb-4">
          Contact our sales team for enterprise pricing and custom features.
        </p>
        <button className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
          Contact Sales
        </button>
      </div>
    </div>
  )
}

export default Subscription
