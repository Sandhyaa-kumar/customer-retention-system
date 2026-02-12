import { useState, useEffect } from "react";
import {
  AlertTriangle,
  TrendingDown,
  Clock,
  CreditCard,
  MessageSquare,
  Activity,
  Zap,
  Calendar,
  CheckCircle,
  Mail,
  Gift,
  BookOpen,
  AlertCircle,
  Loader2,
} from "lucide-react";

function Analytics() {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch analytics from backend - recalculates from DB every time
  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const response = await fetch("http://127.0.0.1:5000/api/analytics");

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to fetch analytics`);
        }

        const data = await response.json();
        setAnalyticsData(data);
        setError(null);
      } catch (err) {
        console.error("Error fetching analytics:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();

    // Optional: Refresh analytics every 30 seconds for near-real-time updates
    const intervalId = setInterval(fetchAnalytics, 30000);

    return () => clearInterval(intervalId);
  }, []);

  const churnDriversConfig = [
    {
      icon: TrendingDown,
      color: "text-red-600",
    },
    {
      icon: Clock,
      color: "text-orange-600",
    },
    {
      icon: CreditCard,
      color: "text-yellow-600",
    },
    {
      icon: MessageSquare,
      color: "text-blue-600",
    },
  ];

  const predictiveInsightsConfig = [
    {
      icon: Activity,
    },
    {
      icon: Zap,
    },
    {
      icon: Calendar,
    },
  ];

  const recommendedActionsConfig = [
    {
      icon: Mail,
    },
    {
      icon: Gift,
    },
    {
      icon: BookOpen,
    },
    {
      icon: AlertCircle,
    },
  ];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <p className="text-red-800">Error loading analytics: {error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-800">Analytics</h2>
        <p className="text-gray-600 mt-1">
          Business insights and churn analysis derived from customer behavior
        </p>
      </div>

      <div className="bg-orange-50 border-l-4 border-orange-500 rounded-lg p-6">
        <div className="flex items-start gap-4">
          <AlertTriangle className="w-6 h-6 text-orange-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              Current Churn Risk Overview
            </h3>
            <p className="text-gray-700 leading-relaxed">
              {analyticsData?.churnRiskOverview?.description || "Loading..."}
            </p>
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-xl font-bold text-gray-800 mb-4">
          Top Churn Drivers
        </h3>
        <div className="space-y-3">
          {analyticsData?.churnDrivers?.map((driver, index) => {
            const Icon = churnDriversConfig[index]?.icon || TrendingDown;
            const color = churnDriversConfig[index]?.color || "text-gray-600";
            return (
              <div
                key={driver.rank}
                className="bg-white rounded-lg shadow p-5 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                      <span className="text-sm font-bold text-gray-700">
                        {driver.rank}
                      </span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <Icon className={`w-5 h-5 ${color}`} />
                      <h4 className="text-base font-semibold text-gray-800">
                        {driver.title}
                      </h4>
                    </div>
                    <p className="text-sm text-gray-600 mt-2 leading-relaxed">
                      {driver.description}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div>
        <h3 className="text-xl font-bold text-gray-800 mb-4">
          Predictive Insights (ML Analysis)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {analyticsData?.predictiveInsights?.map((insight, index) => {
            const Icon = predictiveInsightsConfig[index]?.icon || Activity;
            return (
              <div
                key={index}
                className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center gap-3 mb-3">
                  <Icon className="w-5 h-5 text-blue-600" />
                  <h4 className="text-base font-semibold text-gray-800">
                    {insight.title}
                  </h4>
                </div>
                <p className="text-sm text-gray-600 leading-relaxed">
                  {insight.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      <div>
        <h3 className="text-xl font-bold text-gray-800 mb-4">
          Recommended Retention Actions
        </h3>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="space-y-4">
            {analyticsData?.recommendedActions?.map((action, index) => {
              const Icon = recommendedActionsConfig[index]?.icon || Mail;
              return (
                <div
                  key={index}
                  className="flex items-start gap-4 pb-4 last:pb-0 border-b border-gray-200 last:border-b-0"
                >
                  <div className="flex-shrink-0 mt-1">
                    <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center">
                      <Icon className="w-4 h-4 text-green-600" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <p className="text-base text-gray-700 font-medium">
                      {action.title}
                    </p>
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
