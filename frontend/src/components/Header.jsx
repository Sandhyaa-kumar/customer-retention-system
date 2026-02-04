import { Menu } from 'lucide-react';

function Header({ onToggleSidebar }) {
  return (
    <header className="bg-white shadow-sm h-16 flex items-center px-4 fixed top-0 left-0 right-0 z-30">
      <button
        onClick={onToggleSidebar}
        className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        aria-label="Toggle sidebar"
      >
        <Menu className="w-6 h-6 text-gray-700" />
      </button>
      <h1 className="ml-4 text-xl font-semibold text-gray-800">
        Customer Retention System
      </h1>
    </header>
  );
}

export default Header;
