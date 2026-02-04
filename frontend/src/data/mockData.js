export const kpiMetrics = {
  churnRate: '12.5%',
  retentionRate: '87.5%',
  activeUsers: '8,450',
  healthScore: '7.8/10',
  lossFromChurn: '$142,000'
};

export const retentionData = [
  { month: 'Jan', retention: 100 },
  { month: 'Feb', retention: 92 },
  { month: 'Mar', retention: 87 },
  { month: 'Apr', retention: 83 },
  { month: 'May', retention: 79 },
  { month: 'Jun', retention: 76 }
];

export const churnReasons = [
  { reason: 'Price', value: 35, color: '#3B82F6' },
  { reason: 'Low Usage', value: 28, color: '#60A5FA' },
  { reason: 'Poor Support', value: 22, color: '#93C5FD' },
  { reason: 'Competition', value: 15, color: '#DBEAFE' }
];

export const customers = [
  {
    id: 1,
    name: 'Sarah Johnson',
    email: 'sarah.j@company.com',
    status: 'Active',
    healthScore: 8.5,
    lastLogin: '2024-02-01',
    riskLevel: 'Low',
    lastActivity: '2 hours ago',
    activities: [
      { type: 'Login', date: '2024-02-01', detail: 'Logged in from Chrome' },
      { type: 'Usage', date: '2024-01-30', detail: 'Used feature X for 45 minutes' },
      { type: 'Support', date: '2024-01-28', detail: 'Contacted support about billing' }
    ]
  },
  {
    id: 2,
    name: 'Michael Chen',
    email: 'michael.c@startup.io',
    status: 'Active',
    healthScore: 7.2,
    lastLogin: '2024-01-28',
    riskLevel: 'Medium',
    lastActivity: '4 days ago',
    activities: [
      { type: 'Login', date: '2024-01-28', detail: 'Logged in from Mobile' },
      { type: 'Usage', date: '2024-01-25', detail: 'Usage decreased by 40%' },
      { type: 'Support', date: '2024-01-20', detail: 'Reported technical issue' }
    ]
  },
  {
    id: 3,
    name: 'Emily Rodriguez',
    email: 'emily.r@enterprise.com',
    status: 'Active',
    healthScore: 3.8,
    lastLogin: '2024-01-15',
    riskLevel: 'High',
    lastActivity: '18 days ago',
    activities: [
      { type: 'Login', date: '2024-01-15', detail: 'Last login 18 days ago' },
      { type: 'Support', date: '2024-01-10', detail: 'Multiple unresolved tickets' },
      { type: 'Usage', date: '2024-01-08', detail: 'No activity recorded' }
    ]
  },
  {
    id: 4,
    name: 'James Wilson',
    email: 'james.w@tech.com',
    status: 'Active',
    healthScore: 4.5,
    lastLogin: '2024-01-20',
    riskLevel: 'High',
    lastActivity: '14 days ago',
    activities: [
      { type: 'Login', date: '2024-01-20', detail: 'Logged in briefly' },
      { type: 'Support', date: '2024-01-18', detail: 'Complained about pricing' },
      { type: 'Usage', date: '2024-01-15', detail: 'Very low engagement' }
    ]
  },
  {
    id: 5,
    name: 'Lisa Anderson',
    email: 'lisa.a@business.com',
    status: 'Active',
    healthScore: 6.8,
    lastLogin: '2024-01-30',
    riskLevel: 'Medium',
    lastActivity: '4 days ago',
    activities: [
      { type: 'Login', date: '2024-01-30', detail: 'Regular user' },
      { type: 'Usage', date: '2024-01-29', detail: 'Moderate usage pattern' },
      { type: 'Support', date: '2024-01-25', detail: 'Asked about new features' }
    ]
  },
  {
    id: 6,
    name: 'David Kim',
    email: 'david.k@corp.com',
    status: 'Active',
    healthScore: 9.1,
    lastLogin: '2024-02-03',
    riskLevel: 'Low',
    lastActivity: '1 hour ago',
    activities: [
      { type: 'Login', date: '2024-02-03', detail: 'Active daily user' },
      { type: 'Usage', date: '2024-02-03', detail: 'High engagement score' },
      { type: 'Support', date: '2024-01-28', detail: 'Positive feedback submitted' }
    ]
  },
  {
    id: 7,
    name: 'Rachel Green',
    email: 'rachel.g@solutions.com',
    status: 'Churned',
    healthScore: 2.1,
    lastLogin: '2023-12-15',
    riskLevel: 'High',
    lastActivity: '50 days ago',
    activities: [
      { type: 'Churn', date: '2024-01-05', detail: 'Account cancelled' },
      { type: 'Support', date: '2023-12-20', detail: 'Unresolved complaints' },
      { type: 'Login', date: '2023-12-15', detail: 'Final login before churn' }
    ]
  },
  {
    id: 8,
    name: 'Tom Harris',
    email: 'tom.h@digital.com',
    status: 'Active',
    healthScore: 5.2,
    lastLogin: '2024-01-25',
    riskLevel: 'High',
    lastActivity: '9 days ago',
    activities: [
      { type: 'Login', date: '2024-01-25', detail: 'Infrequent logins' },
      { type: 'Usage', date: '2024-01-22', detail: 'Usage dropped significantly' },
      { type: 'Support', date: '2024-01-20', detail: 'Payment issues reported' }
    ]
  },
  {
    id: 9,
    name: 'Nina Patel',
    email: 'nina.p@services.com',
    status: 'Active',
    healthScore: 7.9,
    lastLogin: '2024-02-02',
    riskLevel: 'Low',
    lastActivity: '1 day ago',
    activities: [
      { type: 'Login', date: '2024-02-02', detail: 'Regular usage pattern' },
      { type: 'Usage', date: '2024-02-01', detail: 'Consistent engagement' },
      { type: 'Support', date: '2024-01-30', detail: 'Quick question resolved' }
    ]
  },
  {
    id: 10,
    name: 'Chris Martin',
    email: 'chris.m@ventures.com',
    status: 'Active',
    healthScore: 4.9,
    lastLogin: '2024-01-22',
    riskLevel: 'High',
    lastActivity: '12 days ago',
    activities: [
      { type: 'Login', date: '2024-01-22', detail: 'Decreasing login frequency' },
      { type: 'Support', date: '2024-01-18', detail: 'Considering alternatives' },
      { type: 'Usage', date: '2024-01-15', detail: 'Minimal feature usage' }
    ]
  },
  {
    id: 11,
    name: 'Amanda White',
    email: 'amanda.w@group.com',
    status: 'Active',
    healthScore: 8.2,
    lastLogin: '2024-02-02',
    riskLevel: 'Low',
    lastActivity: '1 day ago',
    activities: [
      { type: 'Login', date: '2024-02-02', detail: 'Power user' },
      { type: 'Usage', date: '2024-02-02', detail: 'Heavy feature usage' },
      { type: 'Support', date: '2024-01-29', detail: 'Feature request submitted' }
    ]
  },
  {
    id: 12,
    name: 'Kevin Brown',
    email: 'kevin.b@agency.com',
    status: 'Churned',
    healthScore: 1.8,
    lastLogin: '2023-12-10',
    riskLevel: 'High',
    lastActivity: '55 days ago',
    activities: [
      { type: 'Churn', date: '2023-12-28', detail: 'Subscription cancelled' },
      { type: 'Support', date: '2023-12-15', detail: 'Price concerns raised' },
      { type: 'Login', date: '2023-12-10', detail: 'Last activity before churn' }
    ]
  }
];

export const topRiskCustomers = customers
  .filter(c => c.riskLevel === 'High')
  .sort((a, b) => a.healthScore - b.healthScore)
  .slice(0, 10);
