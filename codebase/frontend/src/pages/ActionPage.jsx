import { Link } from 'react-router-dom';
import { Package, ListChecks, Plus, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export function ActionPage() {
  const { logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/action" className="text-xl font-bold text-gray-900 hover:text-primary-600 transition-colors">
              TenMission
            </Link>
            <button
              onClick={logout}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <LogOut className="w-5 h-5" />
              <span className="text-sm font-medium">Logout</span>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">What would you like to do?</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link to="/inventory" className="card p-6 hover:shadow-lg transition-shadow group">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-primary-100 rounded-xl text-primary-600 group-hover:bg-primary-200 transition-colors">
                <Package className="w-8 h-8" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">View Inventory</h3>
                <p className="text-gray-600 mt-1">Browse all available inventory items</p>
              </div>
            </div>
            <div className="mt-4 flex items-center justify-end">
              <span className="text-primary-600 font-medium group-hover:underline flex items-center gap-1">
                View inventory
              </span>
            </div>
          </Link>

          <Link to="/create-booking" className="card p-6 hover:shadow-lg transition-shadow group">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-green-100 rounded-xl text-green-600 group-hover:bg-green-200 transition-colors">
                <Plus className="w-8 h-8" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Create Booking</h3>
                <p className="text-gray-600 mt-1">Book an available inventory item</p>
              </div>
            </div>
            <div className="mt-4 flex items-center justify-end">
              <span className="text-green-600 font-medium group-hover:underline flex items-center gap-1">
                Create booking
              </span>
            </div>
          </Link>

          <Link to="/bookings" className="card p-6 hover:shadow-lg transition-shadow group">
            <div className="flex items-start gap-4">
              <div className="p-3 bg-blue-100 rounded-xl text-blue-600 group-hover:bg-blue-200 transition-colors">
                <ListChecks className="w-8 h-8" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Manage Bookings</h3>
                <p className="text-gray-600 mt-1">View and cancel your existing bookings</p>
              </div>
            </div>
            <div className="mt-4 flex items-center justify-end">
              <span className="text-blue-600 font-medium group-hover:underline flex items-center gap-1">
                Manage bookings
              </span>
            </div>
          </Link>
        </div>
      </main>
    </div>
  );
}
