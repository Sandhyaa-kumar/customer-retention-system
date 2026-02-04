import { AlertTriangle, TrendingDown, Clock, CreditCard, MessageSquare, Activity, Zap, Calendar, CheckCircle, Mail, Gift, BookOpen, AlertCircle } from 'lucide-react';

function Analytics() {
  const churnDrivers = [
    {
      rank: 1,
      icon: TrendingDown,
      title: 'Low Engagement',
      description: 'Customers who stop using core features early are more likely to churn.',
      color: 'text-red-600'
    },
    {
      rank: 2,
      icon: Clock,
      title: 'Long Inactivity',
      description: 'Inactivity beyond 14 days strongly increases churn probability.',
      color: 'text-orange-600'
    },
    {
      rank: 3,
      icon: CreditCard,
      title: 'Payment Issues',
      description: 'Failed or delayed payments lead to higher customer drop-offs.',
      color: 'text-yellow-600'
    },
    {
      rank: 4,
      icon: MessageSquare,
      title: 'Support Complaints',
      description: 'Repeated unresolved issues reduce customer trust and retention.',
      color: 'text-blue-600'
    }
  ];

  const predictiveInsights = [
    {
      icon: Activity,
      title: 'Health Score Threshold',
      description: 'Customers with a health score below 40 have the highest churn probability.'
    },
    {
      icon: Zap,
      title: 'Early Warning Signal',
      description: 'Sudden drops in usage often predict churn before account cancellation.'
    },
    {
      icon: Calendar,
      title: 'Critical Retention Window',
      description: 'The first 7 days of customer activity strongly influence long-term retention.'
    }
  ];

  const recommendedActions = [
    {
      icon: Mail,
      title: 'Re-engage customers inactive for more than 7 days'
    },
    {
      icon: Gift,
      title: 'Provide offers or discounts to high-risk users'
    },
    {
      icon: BookOpen,
      title: 'Improve onboarding during the first week'
    },
    {
      icon: AlertCircle,
      title: 'Monitor and resolve payment failures early'
    }
  ];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-800">Analytics</h2>
        <p className="text-gray-600 mt-1">Business insights and churn analysis derived from customer behavior</p>
      </div>

      <div className="bg-orange-50 border-l-4 border-orange-500 rounded-lg p-6">
        <div className="flex items-start gap-4">
          <AlertTriangle className="w-6 h-6 text-orange-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Current Churn Risk Overview</h3>
            <p className="text-gray-700 leading-relaxed">18% of active customers are currently at high risk of churn due to low engagement and prolonged inactivity. Immediate retention efforts are recommended for this segment.</p>
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-xl font-bold text-gray-800 mb-4">Top Churn Drivers</h3>
        <div className="space-y-3">
          {churnDrivers.map((driver) => {
            const Icon = driver.icon;
            return (
              <div key={driver.rank} className="bg-white rounded-lg shadow p-5 hover:shadow-md transition-shadow">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                      <span className="text-sm font-bold text-gray-700">{driver.rank}</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <Icon className={`w-5 h-5 ${driver.color}`} />
                      <h4 className="text-base font-semibold text-gray-800">{driver.title}</h4>
                    </div>
                    <p className="text-sm text-gray-600 mt-2 leading-relaxed">{driver.description}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div>
        <h3 className="text-xl font-bold text-gray-800 mb-4">Predictive Insights (ML Analysis)</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {predictiveInsights.map((insight, index) => {
            const Icon = insight.icon;
            return (
              <div key={index} className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
                <div className="flex items-center gap-3 mb-3">
                  <Icon className="w-5 h-5 text-blue-600" />
                  <h4 className="text-base font-semibold text-gray-800">{insight.title}</h4>
                </div>
                <p className="text-sm text-gray-600 leading-relaxed">{insight.description}</p>
              </div>
            );
          })}
        </div>
      </div>

      <div>
        <h3 className="text-xl font-bold text-gray-800 mb-4">Recommended Retention Actions</h3>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="space-y-4">
            {recommendedActions.map((action, index) => {
              const Icon = action.icon;
              return (
                <div key={index} className="flex items-start gap-4 pb-4 last:pb-0 border-b border-gray-200 last:border-b-0">
                  <div className="flex-shrink-0 mt-1">
                    <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center">
                      <Icon className="w-4 h-4 text-green-600" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <p className="text-base text-gray-700 font-medium">{action.title}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Analytics;
