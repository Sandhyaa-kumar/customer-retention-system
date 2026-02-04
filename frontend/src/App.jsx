import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard'; 
import Customers from './pages/Customers';
import Analytics from './pages/Analytics';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-100">
        <Header onToggleSidebar={toggleSidebar} />
        <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />

        <main className="pt-16 px-4 md:px-6 lg:px-8 py-8">
          <div className="max-w-7xl mx-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/customers" element={<Customers />} />
              <Route path="/analytics" element={<Analytics />} />
            </Routes>
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
