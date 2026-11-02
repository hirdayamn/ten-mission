import { useState, useEffect, useCallback } from 'react';
import { ArrowLeft, Package, Search, LogOut } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import { SearchBar, InventoryCard, PageLoader } from '../components';
import { useToast } from '../components';
import { useAuth } from '../context/AuthContext';

export function InventoryPage() {
  const { addToast } = useToast();
  const { logout } = useAuth();

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const fetchInventory = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getInventory({
        q: searchQuery,
        page,
        page_size: pageSize,
      });
      setItems(data.items);
      setTotalItems(data.total);
      setTotalPages(Math.ceil(data.total / pageSize));
    } catch (error) {
      addToast(error.message || 'Failed to load inventory', 'error');
    } finally {
      setLoading(false);
    }
  }, [searchQuery, page, pageSize, addToast]);

  useEffect(() => {
    fetchInventory();
  }, [fetchInventory]);

  useEffect(() => {
    setPage(1);
  }, [pageSize]);

  const handleSearch = (query) => {
    setSearchQuery(query);
    setPage(1);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/action" className="text-xl font-bold text-gray-900 hover:text-primary-600 transition-colors">
              TenMission
            </Link>
            <div className="flex items-center gap-4">
              <Link to="/action" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
                <ArrowLeft className="w-5 h-5" />
                <span className="font-medium">Back</span>
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
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Available Items</h2>
            <p className="text-gray-600">
              {totalItems} item{totalItems !== 1 ? 's' : ''} found
            </p>
          </div>
          <div className="flex items-center gap-4">
            <SearchBar onSearch={handleSearch} placeholder="Search by title or description..." />
            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(parseInt(e.target.value));
                setPage(1);
              }}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value={25}>25 items</option>
              <option value={50}>50 items</option>
              <option value={100}>100 items</option>
            </select>
          </div>
        </div>

        {loading ? (
          <PageLoader />
        ) : items.length === 0 ? (
          <div className="text-center py-12">
            <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No items found</h3>
            <p className="text-gray-600">Try adjusting your search or check back later</p>
          </div>
        ) : (
          <div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {items.map((item) => (
                <InventoryCard
                  key={item.id}
                  item={item}
                />
              ))}
            </div>

            {totalPages > 1 && (
              <div className="mt-8 flex items-center justify-center gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="btn-secondary"
                >
                  Previous
                </button>
                <span className="px-4 text-sm text-gray-600">
                  Page {page} of {totalPages}
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="btn-secondary"
                >
                  Next
                </button>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
