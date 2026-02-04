import { useNavigate } from 'react-router-dom';
import { TrendingDown, TrendingUp, Users, Heart, DollarSign, AlertTriangle, AlertCircle, Mail } from 'lucide-react';
import { kpiMetrics, retentionData, churnReasons, topRiskCustomers } from '../data/mockData';

function Dashboard() {
  const navigate = useNavigate();

  const kpiCards = [
    {
      label: 'Churn Rate',
      value: kpiMetrics.churnRate,
      subtitle: 'Percentage of customers lost this month',
      icon: TrendingDown,
      color: 'text-red-600',
      trend: '↓ Improved from last month',
      trendType: 'positive'
    },
    {
      label: 'Retention Rate',
      value: kpiMetrics.retentionRate,
      subtitle: 'Percentage of customers retained',
      icon: TrendingUp,
      color: 'text-green-600',
      trend: '↑ Up from last month',
      trendType: 'positive'
    },
    {
      label: 'Active Users',
      value: kpiMetrics.activeUsers,
      subtitle: 'Customers actively using product',
      icon: Users,
      color: 'text-blue-600',
      trend: '→ Stable from last month',
      trendType: 'neutral'
    },
    {
      label: 'Health Score',
      value: kpiMetrics.healthScore,
      subtitle: 'Overall customer wellness',
      icon: Heart,
      color: 'text-pink-600',
      trend: '↑ Improved from last month',
      trendType: 'positive'
    },
    {
      label: 'Loss Due to Churn',
      value: kpiMetrics.lossFromChurn,
      subtitle: 'Revenue at risk from churn',
      icon: DollarSign,
      color: 'text-orange-600',
      trend: '↓ Decreased from last month',
      trendType: 'positive'
    }
  ];

  const handleRiskCustomerClick = (customerId) => {
    navigate('/customers', { state: { selectedCustomerId: customerId } });
  };

  const getRiskBadgeColor = (riskLevel) => {
    switch (riskLevel) {
      case 'High':
        return 'bg-red-100 text-red-800';
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'Low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Dashboard</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {kpiCards.map((kpi, index) => {
          const Icon = kpi.icon;
          return (
            <div key={index} className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-gray-600">{kpi.label}</span>
                <Icon className={`w-5 h-5 ${kpi.color}`} />
              </div>
              <p className="text-2xl font-bold text-gray-800 mb-2">{kpi.value}</p>
              <p className="text-xs text-gray-500 mb-2">{kpi.subtitle}</p>
              <p className={`text-xs font-medium ${kpi.trendType === 'positive' ? 'text-green-600' : kpi.trendType === 'negative' ? 'text-red-600' : 'text-gray-600'}`}>
                {kpi.trend}
              </p>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Retention Curve</h3>
            <p className="text-sm text-gray-500 mt-1">Customer retention trend over the last 6 months</p>
          </div>
          <div className="h-64 flex items-end justify-between gap-2">
            {retentionData.map((data, index) => {
              const isBiggestDrop = index > 0 && retentionData[index - 1].retention - data.retention > 3;
              return (
                <div key={index} className="flex-1 flex flex-col items-center">
                  <div className={`w-full rounded-t-lg relative transition-all ${isBiggestDrop ? 'bg-red-500' : 'bg-blue-500'}`} style={{ height: `${data.retention * 2.4}px` }}>
                    {isBiggestDrop && <AlertCircle className="absolute -top-6 right-0 w-4 h-4 text-red-500" />}
                    <span className="absolute -top-6 left-1/2 transform -translate-x-1/2 text-xs font-semibold text-gray-700">
                      {data.retention}%
                    </span>
                  </div>
                  <span className="text-xs text-gray-600 mt-2">{data.month}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Churn Reasons</h3>
            <p className="text-sm text-gray-500 mt-1">Distribution of customer churn factors</p>
          </div>
          <div className="flex items-center justify-center h-48">
            <div className="relative w-48 h-48">
              <svg viewBox="0 0 100 100" className="transform -rotate-90">
                {churnReasons.reduce((acc, reason, index) => {
                  const previousTotal = churnReasons.slice(0, index).reduce((sum, r) => sum + r.value, 0);
                  const offset = (previousTotal / 100) * 314;
                  const strokeDasharray = `${(reason.value / 100) * 314} 314`;

                  acc.push(
                    <circle
                      key={index}
                      cx="50"
                      cy="50"
                      r="50"
                      fill="none"
                      stroke={reason.color}
                      strokeWidth="100"
                      strokeDasharray={strokeDasharray}
                      strokeDashoffset={-offset}
                    />
                  );
                  return acc;
                }, [])}
              </svg>
            </div>
          </div>
          <div className="mt-4 space-y-2">
            {churnReasons.map((reason, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: reason.color }} />
                  <span className="text-sm text-gray-700">{reason.reason}</span>
                </div>
                <span className="text-sm font-semibold text-gray-800">{reason.value}%</span>
              </div>
            ))}
          </div>
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-xs text-gray-600 leading-relaxed">
              Price and low usage together account for over 60% of churn, indicating that customers primarily leave due to perceived value misalignment or insufficient product adoption.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <h3 className="text-lg font-semibold text-gray-800">Top Risk Customers</h3>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Customer Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risk Level
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Activity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Action
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {topRiskCustomers.map((customer) => {
                const daysSinceActivity = Math.floor(Math.random() * 40) + 5;
                return (
                  <tr
                    key={customer.id}
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{customer.name}</div>
                          <div className="text-sm text-gray-500">{customer.email}</div>
                        </div>
                        {daysSinceActivity > 30 && (
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                            Inactive {daysSinceActivity}d
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getRiskBadgeColor(customer.riskLevel)}`}>
                        {customer.riskLevel}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {customer.lastActivity}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => handleRiskCustomerClick(customer.id)}
                        className="text-blue-600 hover:text-blue-800 font-medium transition-colors flex items-center gap-1"
                        title="View customer details"
                      >
                        <Mail className="w-4 h-4" />
                        Engage
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg shadow p-6 border border-blue-200">
        <div className="flex gap-4">
          <AlertCircle className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">ML-Based Insight Summary</h3>
            <ul className="space-y-2">
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold mt-0.5">•</span>
                <span className="text-gray-700 text-sm">Customers inactive for more than 30 days have a <strong>2.3x higher churn risk</strong> compared to active users.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold mt-0.5">•</span>
                <span className="text-gray-700 text-sm"><strong>Low health score is the strongest churn predictor</strong> — customers below 4.0 have an 85% probability of churning within 60 days.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold mt-0.5">•</span>
                <span className="text-gray-700 text-sm"><strong>Early engagement significantly improves retention</strong> — customers engaged in the first week are 3x more likely to remain active.</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
