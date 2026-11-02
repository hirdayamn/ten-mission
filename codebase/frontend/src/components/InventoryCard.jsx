import { useState } from 'react';
import { Calendar, Package, AlertTriangle, X } from 'lucide-react';

export function InventoryCard({ item }) {
  const isExpired = !item.is_active;
  const isLowStock = item.remaining_count > 0 && item.remaining_count <= 3 && item.is_active;
  const [showDetails, setShowDetails] = useState(false);

  return (
    <>
      <div className="card p-5 flex flex-col h-full">
        <div className="flex items-start justify-between mb-3">
          <h3 className="font-semibold text-gray-900 text-lg">{item.title}</h3>
          <div className="flex items-center gap-2">
            {isExpired ? (
              <span className="flex items-center gap-1 text-xs text-red-600 bg-red-50 px-2 py-1 rounded-full">
                <AlertTriangle className="w-3 h-3" />
                Expired
              </span>
            ) : item.remaining_count === 0 ? (
              <span className="flex items-center gap-1 text-xs text-gray-500 bg-gray-50 px-2 py-1 rounded-full">
                <Package className="w-3 h-3" />
                Out of stock
              </span>
            ) : isLowStock ? (
              <span className="flex items-center gap-1 text-xs text-yellow-800 bg-yellow-50 px-2 py-1 rounded-full">
                <AlertTriangle className="w-3 h-3" />
                Only {item.remaining_count} left!
              </span>
            ) : (
              <span className="flex items-center gap-1 text-xs text-gray-600 bg-gray-50 px-2 py-1 rounded-full">
                <Package className="w-3 h-3" />
                Available: {item.remaining_count}
              </span>
            )}
          </div>
        </div>
        <div className="mb-4 flex-1">
          <p className="text-gray-600 text-sm line-clamp-3">{item.description || 'No description available'}</p>
          {item.description && (
            <button
              type="button"
              onClick={() => setShowDetails(true)}
              className="text-xs text-primary-600 hover:underline mt-1 inline-block"
            >
              Show full description
            </button>
          )}
        </div>
        <div className="flex items-center gap-1 text-sm text-gray-500 pt-3 border-t border-gray-100 mt-auto">
          <Calendar className="w-4 h-4" />
          <span className={isExpired ? 'text-red-600' : ''}>
            Expires: <span className="font-medium">{new Date(item.expiration_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
          </span>
        </div>
      </div>

      {/* Item Details Dialog */}
      {showDetails && item.description && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Item Details</h3>
              <button
                onClick={() => setShowDetails(false)}
                className="text-gray-400 hover:text-gray-600 p-1"
                aria-label="Close"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500 mb-1">Title</p>
                <p className="font-medium text-gray-900">{item.title}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500 mb-1">Description</p>
                <p className="text-gray-900 whitespace-pre-wrap">{item.description}</p>
              </div>
              <div className="grid grid-cols-2 gap-4 pt-2 border-t border-gray-100">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Available</p>
                  <p className="font-medium text-gray-900">{item.remaining_count}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-1">Expires</p>
                  <p className="font-medium text-gray-900 {isExpired ? 'text-red-600' : ''}">
                    {new Date(item.expiration_date).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })}
                  </p>
                </div>
              </div>
            </div>
            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setShowDetails(false)}
                className="btn-primary px-6 py-2"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
