import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Eye, Mail, X, AlertCircle, Target, TrendingDown, CheckCircle, Info } from 'lucide-react';
import { customers } from '../data/mockData';

function Customers() {
  const location = useLocation();
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [sortBy, setSortBy] = useState('name');

  useEffect(() => {
    if (location.state?.selectedCustomerId) {
      const customer = customers.find(c => c.id === location.state.selectedCustomerId);
      if (customer) {
        setSelectedCustomer(customer);
      }
    }
  }, [location]);

  const getStatusBadgeColor = (status) => {
    return status === 'Active'
      ? 'bg-green-100 text-green-800'
      : 'bg-red-100 text-red-800';
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

  const getHealthScoreBgColor = (score) => {
    if (score >= 7.5) return 'bg-green-50';
    if (score >= 5) return 'bg-yellow-50';
    return 'bg-red-50';
  };

  const getHealthScoreColor = (score) => {
    if (score >= 7.5) return 'text-green-600';
    if (score >= 5) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRiskReasons = (customer) => {
    const reasons = [];
    if (customer.healthScore < 5) reasons.push('Low health score');
    if (customer.riskLevel === 'High') reasons.push('High inactivity');
    if (customer.lastActivity.includes('ago') && parseInt(customer.lastActivity) > 7) {
      reasons.push('Limited recent engagement');
    }
    return reasons.length > 0 ? reasons : ['Monitor for changes'];
  };

  const getRecommendedAction = (customer) => {
    if (customer.healthScore < 3) return 'Send win-back email';
    if (customer.riskLevel === 'High') return 'Send re-engagement email';
    if (customer.riskLevel === 'Medium') return 'Offer special discount';
    return 'Schedule support follow-up';
  };

  const handleSendEmail = () => {
    const action = getRecommendedAction(selectedCustomer);
    alert(`${action} would be sent to ${selectedCustomer.email}`);
  };

  const sortedCustomers = [...customers].sort((a, b) => {
    if (sortBy === 'health') return b.healthScore - a.healthScore;
    if (sortBy === 'login') return new Date(b.lastLogin) - new Date(a.lastLogin);
    return a.name.localeCompare(b.name);
  });

  const getRiskTag = (customer) => {
    if (customer.riskLevel === 'High' && customer.healthScore < 5) return 'High Risk';
    if (customer.riskLevel === 'High') return 'High Risk';
    if (customer.status === 'Churned') return 'Churned';
    const daysSinceLogin = Math.floor(Math.random() * 60) + 1;
    if (daysSinceLogin > 30) return 'Inactive';
    return null;
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-1">Customers</h2>
        <p className="text-gray-600 text-sm">Manage and analyze customer retention metrics</p>
      </div>

      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => setSortBy('name')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            sortBy === 'name'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Sort by Name
        </button>
        <button
          onClick={() => setSortBy('health')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            sortBy === 'health'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Sort by Health Score
        </button>
        <button
          onClick={() => setSortBy('login')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            sortBy === 'login'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Sort by Last Login
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className={`${selectedCustomer ? 'lg:col-span-2' : 'lg:col-span-3'}`}>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Health Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Last Login
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {sortedCustomers.map((customer) => {
                    const riskTag = getRiskTag(customer);
                    return (
                      <tr
                        key={customer.id}
                        className={`hover:bg-gray-50 transition-colors ${
                          selectedCustomer?.id === customer.id ? 'bg-blue-50' : ''
                        }`}
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center gap-2">
                            <div className="text-sm font-medium text-gray-900">{customer.name}</div>
                            {riskTag && (
                              <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${
                                riskTag === 'High Risk' ? 'bg-red-100 text-red-800' :
                                riskTag === 'Churned' ? 'bg-gray-100 text-gray-800' :
                                'bg-yellow-100 text-yellow-800'
                              }`}>
                                {riskTag}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-500">{customer.email}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeColor(customer.status)}`}>
                            {customer.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className={`${getHealthScoreBgColor(customer.healthScore)} px-3 py-1.5 rounded-lg inline-block`}>
                            <span className={`text-sm font-bold ${getHealthScoreColor(customer.healthScore)}`}>
                              {customer.healthScore}/10
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {customer.lastLogin}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <button
                            onClick={() => setSelectedCustomer(customer)}
                            className="text-blue-600 hover:text-blue-800 font-medium transition-colors"
                          >
                            View
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {selectedCustomer && (
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6 sticky top-20 max-h-[calc(100vh-100px)] overflow-y-auto animate-in slide-in-from-right">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-800">Customer Details</h3>
                <button
                  onClick={() => setSelectedCustomer(null)}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <h4 className="text-xl font-bold text-gray-800">{selectedCustomer.name}</h4>
                  <p className="text-sm text-gray-500">{selectedCustomer.email}</p>
                </div>

                <div className="flex items-center gap-2 flex-wrap">
                  <span className={`px-3 py-1 text-sm font-semibold rounded-full ${getStatusBadgeColor(selectedCustomer.status)}`}>
                    {selectedCustomer.status}
                  </span>
                  <span className={`px-3 py-1 text-sm font-semibold rounded-full ${getRiskBadgeColor(selectedCustomer.riskLevel)}`}>
                    {selectedCustomer.riskLevel} Risk
                  </span>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <div>
                    <p className="text-xs text-gray-500 uppercase font-semibold mb-1">Customer Overview</p>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs text-gray-500">Health Score</p>
                        <div className={`${getHealthScoreBgColor(selectedCustomer.healthScore)} px-2 py-1.5 rounded mt-1 inline-block`}>
                          <p className={`text-sm font-bold ${getHealthScoreColor(selectedCustomer.healthScore)}`}>
                            {selectedCustomer.healthScore}/10
                          </p>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">Engagement + Activity + Support</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Last Login</p>
                        <p className="text-sm font-medium text-gray-800 mt-1">{selectedCustomer.lastLogin}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <p className="text-xs text-gray-500 uppercase font-semibold mb-2">Risk Assessment</p>
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <div className="flex gap-2 mb-2">
                      <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
                      <p className="text-sm font-semibold text-red-800">Risk Factors</p>
                    </div>
                    <ul className="space-y-1">
                      {getRiskReasons(selectedCustomer).map((reason, idx) => (
                        <li key={idx} className="text-xs text-red-700 flex items-start gap-2">
                          <span className="mt-1">•</span>
                          <span>{reason}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <p className="text-xs text-gray-500 uppercase font-semibold mb-2">Recent Activity Timeline</p>
                  <div className="space-y-3 max-h-40 overflow-y-auto">
                    {selectedCustomer.activities.map((activity, index) => (
                      <div key={index} className="flex gap-3">
                        <div className="flex-shrink-0">
                          <div className="w-2 h-2 mt-2 rounded-full bg-blue-500" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-semibold text-gray-800">{activity.type}</p>
                          <p className="text-xs text-gray-600 leading-relaxed">{activity.detail}</p>
                          <p className="text-xs text-gray-400 mt-1">{activity.date}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <p className="text-xs text-gray-500 uppercase font-semibold mb-3">Recommended Action</p>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-3">
                    <div className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="text-sm font-semibold text-green-800">{getRecommendedAction(selectedCustomer)}</p>
                        <p className="text-xs text-green-700 mt-1">This action may help improve retention</p>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={handleSendEmail}
                    className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                  >
                    <Mail className="w-4 h-4" />
                    {getRecommendedAction(selectedCustomer)}
                  </button>
                  <p className="text-xs text-gray-500 mt-2 text-center">UI only – backend integration planned</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Customers;
