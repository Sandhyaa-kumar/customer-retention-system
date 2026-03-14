import { Menu, LogOut } from "lucide-react";
import { useAuth } from "../context/AuthContext";

function Header({ onToggleSidebar }) {
  const { user, isAuthenticated, logout } = useAuth();

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
      {isAuthenticated && (
        <div className="ml-auto flex items-center gap-3">
          <span className="text-sm text-gray-600 hidden sm:block">
            {user?.username}
          </span>
          <button
            onClick={logout}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600
                       hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            aria-label="Sign out"
          >
            <LogOut className="w-4 h-4" />
            <span className="hidden sm:block">Sign out</span>
          </button>
        </div>
      )}
    </header>
  );
}

export default Header;
