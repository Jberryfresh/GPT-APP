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
  AlertCircle,
  DollarSign,
  Clock,
  FileText,
  Plus,
  Trash2
} from 'lucide-react'

export default function Subscription() {
  const [activeTab, setActiveTab] = useState('overview')
  const [currentSubscription, setCurrentSubscription] = useState(null)
  const [billingPlans, setBillingPlans] = useState([])
  const [usage, setUsage] = useState(null)
  const [paymentMethods, setPaymentMethods] = useState([])
  const [invoices, setInvoices] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSubscriptionData()
  }, [])

  const fetchSubscriptionData = async () => {
    try {
      const token = localStorage.getItem('token')

      // Fetch subscription details
      const subResponse = await fetch('/api/billing/subscription', {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (subResponse.ok) {
        const subData = await subResponse.json()
        setCurrentSubscription(subData.subscription)
      }

      // Fetch billing plans
      const plansResponse = await fetch('/api/billing/plans')
      const plansData = await plansResponse.json()
      setBillingPlans(plansData.plans || [])

      // Fetch usage
      const usageResponse = await fetch('/api/billing/usage', {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (usageResponse.ok) {
        const usageData = await usageResponse.json()
        setUsage(usageData.usage)
      }

      // Fetch payment methods
      const paymentResponse = await fetch('/api/billing/payment-methods', {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (paymentResponse.ok) {
        const paymentData = await paymentResponse.json()
        setPaymentMethods(paymentData.payment_methods || [])
      }

      // Fetch invoices
      const invoicesResponse = await fetch('/api/billing/invoices', {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (invoicesResponse.ok) {
        const invoicesData = await invoicesResponse.json()
        setInvoices(invoicesData.invoices || [])
      }

    } catch (error) {
      console.error('Error fetching subscription data:', error)
    } finally {
      setLoading(false)
    }
  }

  const upgradePlan = async (planId) => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/billing/upgrade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ plan_id: planId })
      })

      const data = await response.json()
      if (data.success) {
        alert('Plan upgraded successfully!')
        fetchSubscriptionData()
      } else {
        alert('Error upgrading plan: ' + data.error)
      }
    } catch (error) {
      console.error('Error upgrading plan:', error)
      alert('Error upgrading plan')
    }
  }

  const addPaymentMethod = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/billing/payment-methods', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          type: 'card',
          last_four: '4242',
          brand: 'visa',
          exp_month: 12,
          exp_year: 2025,
          is_default: paymentMethods.length === 0
        })
      })

      const data = await response.json()
      if (data.success) {
        alert('Payment method added successfully!')
        fetchSubscriptionData()
      } else {
        alert('Error adding payment method: ' + data.error)
      }
    } catch (error) {
      console.error('Error adding payment method:', error)
      alert('Error adding payment method')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading subscription data...</p>
        </div>
      </div>
    )
  }

  const getUsagePercentage = () => {
    if (!usage || !usage.current_period) return 0
    const { tokens_used, tokens_limit } = usage.current_period
    if (tokens_limit === -1) return 0 // Unlimited
    return Math.min((tokens_used / tokens_limit) * 100, 100)
  }

  const formatCurrency = (cents) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(cents / 100)
  }

  const PlanCard = ({ plan, isCurrent = false }) => (
    <div className={`bg-white rounded-lg shadow-md p-6 ${isCurrent ? 'ring-2 ring-blue-500 border-blue-500' : 'border border-gray-200'}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-gray-900">{plan.name}</h3>
        {isCurrent && (
          <span className="bg-blue-100 text-blue-800 text-sm font-medium px-2.5 py-0.5 rounded">
            Current Plan
          </span>
        )}
      </div>

      <div className="mb-4">
        <span className="text-3xl font-bold text-gray-900">
          ${plan.price}
        </span>
        <span className="text-gray-600">/{plan.interval}</span>
      </div>

      <ul className="space-y-3 mb-6">
        {plan.features.map((feature, index) => (
          <li key={index} className="flex items-center">
            <Check className="h-5 w-5 text-green-500 mr-2" />
            <span className="text-sm text-gray-600">{feature}</span>
          </li>
        ))}
      </ul>

      <button
        onClick={() => !isCurrent && upgradePlan(plan.id)}
        disabled={isCurrent}
        className={`w-full py-2 px-4 rounded-md font-medium ${
          isCurrent
            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700'
        }`}
      >
        {isCurrent ? 'Current Plan' : 'Upgrade'}
      </button>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Subscription & Billing</h1>
              <p className="text-gray-600 mt-2">Manage your subscription, usage, and billing</p>
            </div>
            {currentSubscription && (
              <div className="flex items-center space-x-2">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  currentSubscription.status === 'active' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {currentSubscription.status}
                </span>
                <Crown className="h-5 w-5 text-yellow-500" />
                <span className="text-sm font-medium text-gray-900 capitalize">
                  {currentSubscription.tier}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', name: 'Overview', icon: TrendingUp },
              { id: 'plans', name: 'Plans', icon: Crown },
              { id: 'usage', name: 'Usage', icon: Zap },
              { id: 'billing', name: 'Billing', icon: CreditCard },
              { id: 'invoices', name: 'Invoices', icon: FileText }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Current Plan Overview */}
            {currentSubscription && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Current Subscription</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Plan</p>
                    <p className="text-2xl font-bold text-gray-900 capitalize">{currentSubscription.tier}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Status</p>
                    <p className={`text-2xl font-bold ${
                      currentSubscription.status === 'active' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {currentSubscription.status}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Next Billing</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {new Date(currentSubscription.current_period_end).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Usage Overview */}
            {usage && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Usage This Month</h2>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm">
                      <span>Tokens Used</span>
                      <span>
                        {usage.current_period.tokens_used.toLocaleString()} / {' '}
                        {usage.current_period.tokens_limit === -1 ? 'Unlimited' : usage.current_period.tokens_limit.toLocaleString()}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${getUsagePercentage()}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                    <div>
                      <p className="text-sm font-medium text-gray-500">Training Hours</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {usage.current_period.training_hours_used} / {' '}
                        {usage.current_period.training_hours_limit === -1 ? 'Unlimited' : usage.current_period.training_hours_limit}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">API Calls</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {usage.current_period.api_calls.toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'plans' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Choose Your Plan</h2>
              <p className="text-gray-600 mb-6">Select the plan that best fits your needs</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {billingPlans.map((plan) => (
                <PlanCard
                  key={plan.id}
                  plan={plan}
                  isCurrent={currentSubscription?.tier === plan.id}
                />
              ))}
            </div>
          </div>
        )}

        {activeTab === 'usage' && usage && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Detailed Usage</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex items-center">
                    <Zap className="h-8 w-8 text-blue-600" />
                    <div className="ml-3">
                      <p className="text-sm font-medium text-blue-600">Tokens</p>
                      <p className="text-2xl font-bold text-blue-900">
                        {usage.current_period.tokens_used.toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="flex items-center">
                    <Clock className="h-8 w-8 text-green-600" />
                    <div className="ml-3">
                      <p className="text-sm font-medium text-green-600">Training Hours</p>
                      <p className="text-2xl font-bold text-green-900">
                        {usage.current_period.training_hours_used}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="flex items-center">
                    <TrendingUp className="h-8 w-8 text-purple-600" />
                    <div className="ml-3">
                      <p className="text-sm font-medium text-purple-600">API Calls</p>
                      <p className="text-2xl font-bold text-purple-900">
                        {usage.current_period.api_calls.toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-orange-50 p-4 rounded-lg">
                  <div className="flex items-center">
                    <Calendar className="h-8 w-8 text-orange-600" />
                    <div className="ml-3">
                      <p className="text-sm font-medium text-orange-600">Period</p>
                      <p className="text-sm font-bold text-orange-900">
                        {new Date(usage.current_period.start_date).toLocaleDateString()} - {' '}
                        {new Date(usage.current_period.end_date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'billing' && (
          <div className="space-y-6">
            {/* Payment Methods */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-900">Payment Methods</h2>
                <button
                  onClick={addPaymentMethod}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center space-x-2"
                >
                  <Plus className="h-4 w-4" />
                  <span>Add Payment Method</span>
                </button>
              </div>

              {paymentMethods.length > 0 ? (
                <div className="space-y-3">
                  {paymentMethods.map((method) => (
                    <div key={method.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <CreditCard className="h-6 w-6 text-gray-400" />
                        <div>
                          <p className="font-medium text-gray-900">
                            {method.brand.toUpperCase()} ending in {method.last_four}
                          </p>
                          <p className="text-sm text-gray-500">
                            Expires {method.exp_month}/{method.exp_year}
                          </p>
                        </div>
                        {method.is_default && (
                          <span className="bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded">
                            Default
                          </span>
                        )}
                      </div>
                      <button className="text-red-600 hover:text-red-700">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <CreditCard className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No payment methods added</p>
                  <p className="text-sm text-gray-400">Add a payment method to enable automatic billing</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'invoices' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Billing History</h2>

              {invoices.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Invoice
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Amount
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Date
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {invoices.map((invoice) => (
                        <tr key={invoice.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            #{invoice.id.substring(0, 8)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatCurrency(invoice.amount_cents)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                              invoice.status === 'paid' 
                                ? 'bg-green-100 text-green-800'
                                : invoice.status === 'pending'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {invoice.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {new Date(invoice.created_at).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <button className="text-blue-600 hover:text-blue-700 flex items-center space-x-1">
                              <Download className="h-4 w-4" />
                              <span>Download</span>
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No invoices yet</p>
                  <p className="text-sm text-gray-400">Your billing history will appear here</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}