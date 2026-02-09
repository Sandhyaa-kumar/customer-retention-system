import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import {
  Mail,
  X,
  AlertCircle,
  Clock,
  Activity,
  TrendingUp,
  Loader2,
  AlertTriangle,
} from "lucide-react";

function Customers() {
  const location = useLocation();
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [sortBy, setSortBy] = useState("name");
  const [searchTerm, setSearchTerm] = useState("");

  // Fetch Real Data from Flask API
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch from Flask backend
        const response = await fetch("http://127.0.0.1:5000/api/customers");

        if (!response.ok) {
          throw new Error(
            `HTTP ${response.status}: Failed to fetch data from backend`,
          );
        }

        const data = await response.json();

        // Handle error responses from backend
        if (data.error) {
          throw new Error(data.error);
        }

        // Validate data structure
        if (!Array.isArray(data)) {
          throw new Error("Invalid data format received from API");
        }

        setCustomers(data);
        setLoading(false);
      } catch (error) {
        console.error("❌ Frontend Error:", error.message);
        setError(error.message);
        setLoading(false);
        setCustomers([]); // Reset to empty array on error
      }
    };

    fetchData();
  }, []);

  // Handle selection from Dashboard navigation
  useEffect(() => {
    if (location.state?.selectedCustomerId && customers.length > 0) {
      const customer = customers.find(
        (c) => c.customer_id === location.state.selectedCustomerId,
      );
      if (customer) setSelectedCustomer(customer);
    }
  }, [location, customers]);

  // UI Helper functions
  const getActivityBadge = (status) => {
    switch (status) {
      case "High Risk":
        return {
          color: "bg-red-50 text-red-700 border border-red-200",
          text: "High Risk",
        };
      case "Inactive":
        return {
          color: "bg-yellow-50 text-yellow-700 border border-yellow-200",
          text: "Inactive",
        };
      default:
        return null;
    }
  };

  const getStatusBadge = (status) => {
    return status === "Active"
      ? "bg-green-50 text-green-700 border border-green-200"
      : "bg-red-50 text-red-700 border border-red-200";
  };

  const getHealthScoreColor = (score) => {
    if (score >= 7) return "text-green-600";
    if (score >= 4) return "text-yellow-600";
    return "text-red-600";
  };

  // Filter and Sort Logic
  const filteredCustomers = customers
    .filter(
      (c) =>
        c.customer_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.email_address?.toLowerCase().includes(searchTerm.toLowerCase()),
    )
    .sort((a, b) => {
      if (sortBy === "health") return b.health_score - a.health_score;
      if (sortBy === "lastLogin")
        return new Date(b.last_login) - new Date(a.last_login);
      return a.customer_name?.localeCompare(b.customer_name);
    });

  // Loading State
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <Loader2 className="w-10 h-10 text-blue-600 animate-spin mb-2" />
        <p className="text-gray-500">
          Loading live ML predictions from Flask API...
        </p>
      </div>
    );
  }

  // Error State
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 bg-red-50 rounded-xl border border-red-200 p-8">
        <AlertTriangle className="w-12 h-12 text-red-600 mb-3" />
        <h3 className="text-lg font-bold text-red-800 mb-2">
          Failed to Load Customer Data
        </h3>
        <p className="text-sm text-red-600 text-center mb-4">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-bold text-gray-800">Customers</h2>
        <p className="text-sm text-gray-500">
          Manage and analyze customer retention metrics
        </p>
      </div>

      <div className="flex gap-3">
        <button
          onClick={() => setSortBy("name")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            sortBy === "name"
              ? "bg-blue-600 text-white"
              : "bg-white text-gray-700 border"
          }`}
        >
          Sort by Name
        </button>
        <button
          onClick={() => setSortBy("health")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            sortBy === "health"
              ? "bg-blue-600 text-white"
              : "bg-white text-gray-700 border"
          }`}
        >
          Sort by Health Score
        </button>
        <button
          onClick={() => setSortBy("lastLogin")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            sortBy === "lastLogin"
              ? "bg-blue-600 text-white"
              : "bg-white text-gray-700 border"
          }`}
        >
          Sort by Last Login
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className={selectedCustomer ? "lg:col-span-2" : "lg:col-span-3"}>
          <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Health Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Last Login
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredCustomers.map((customer) => {
                  const activityBadge = getActivityBadge(
                    customer.activity_status,
                  );
                  return (
                    <tr
                      key={customer.customer_id}
                      className={`hover:bg-gray-50 transition-colors ${
                        selectedCustomer?.customer_id === customer.customer_id
                          ? "bg-blue-50"
                          : ""
                      }`}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-gray-900">
                            {customer.customer_name}
                          </span>
                          {activityBadge && (
                            <span
                              className={`px-2 py-1 text-xs rounded ${activityBadge.color}`}
                            >
                              {activityBadge.text}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {customer.email_address}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-1 text-xs rounded ${getStatusBadge(customer.status)}`}
                        >
                          {customer.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`text-sm font-semibold ${getHealthScoreColor(customer.health_score)}`}
                        >
                          {(customer.health_score / 10).toFixed(1)}/10
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {customer.last_login}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button
                          onClick={() => setSelectedCustomer(customer)}
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
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

        {selectedCustomer && (
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg border p-6 sticky top-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-bold text-gray-800">
                  Customer Details
                </h3>
                <button
                  onClick={() => setSelectedCustomer(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <h4 className="text-xl font-bold text-gray-900">
                    {selectedCustomer.customer_name}
                  </h4>
                  <p className="text-sm text-gray-600">
                    {selectedCustomer.email_address}
                  </p>
                </div>

                <div className="flex gap-2">
                  <span
                    className={`px-3 py-1 text-xs rounded ${getStatusBadge(selectedCustomer.status)}`}
                  >
                    {selectedCustomer.status}
                  </span>
                  <span
                    className={`px-3 py-1 text-xs rounded ${
                      selectedCustomer.risk_score > 70
                        ? "bg-red-50 text-red-700 border border-red-200"
                        : "bg-green-50 text-green-700 border border-green-200"
                    }`}
                  >
                    {selectedCustomer.risk_level}
                  </span>
                </div>

                <div className="pt-4 border-t">
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-3">
                    Customer Overview
                  </p>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">
                        Health Score
                      </span>
                      <span
                        className={`text-sm font-bold ${getHealthScoreColor(selectedCustomer.health_score)}`}
                      >
                        {(selectedCustomer.health_score / 10).toFixed(1)}/10
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Last Login</span>
                      <span className="text-sm font-medium text-gray-900">
                        {selectedCustomer.last_login}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t">
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-3">
                    Engagement + Activity + Support
                  </p>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-blue-600" />
                      <span className="text-sm text-gray-600">Power user</span>
                    </div>
                    <p className="text-xs text-gray-500 ml-6">
                      {selectedCustomer.last_login}
                    </p>

                    <div className="flex items-center gap-2 mt-3">
                      <Activity className="w-4 h-4 text-blue-600" />
                      <span className="text-sm text-gray-600">
                        Heavy feature usage
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 ml-6">
                      {selectedCustomer.last_login}
                    </p>

                    {selectedCustomer.unresolved_tickets > 0 && (
                      <div className="flex items-center gap-2 mt-3">
                        <AlertCircle className="w-4 h-4 text-blue-600" />
                        <span className="text-sm text-gray-600">
                          Last support submitted
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="pt-4 border-t">
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-3">
                    Risk Assessment
                  </p>
                  {selectedCustomer.risk_score > 50 ? (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                      <div className="flex items-start gap-2">
                        <AlertCircle className="w-4 h-4 text-red-600 mt-0.5" />
                        <div>
                          <p className="text-sm font-semibold text-red-800">
                            Risk Factors
                          </p>
                          <p className="text-xs text-red-600 mt-1">
                            Monitor for changes
                          </p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <div className="flex items-start gap-2">
                        <TrendingUp className="w-4 h-4 text-green-600 mt-0.5" />
                        <div>
                          <p className="text-sm font-semibold text-green-800">
                            Schedule support follow-up
                          </p>
                          <p className="text-xs text-green-600 mt-1">
                            This action may help improve retention
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="pt-4">
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-3">
                    Recommended Action
                  </p>
                  <button className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-2">
                    <Mail className="w-4 h-4" />
                    Schedule support follow-up
                  </button>
                  <p className="text-xs text-gray-500 text-center mt-2">
                    UI only – backend integration planned
                  </p>
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
