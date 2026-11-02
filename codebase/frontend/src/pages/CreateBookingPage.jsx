import { useState, useEffect, useCallback } from 'react';
import { ArrowLeft, User, Package, Loader2, CheckCircle, Plus, X, LogOut } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import { MemberSelector, PageLoader } from '../components';
import { useToast } from '../components';

export function CreateBookingPage() {
  const { selectedMember, setSelectedMember, members, logout } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const [availableItems, setAvailableItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [itemsLoading, setItemsLoading] = useState(false);
  const [confirmBooking, setConfirmBooking] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showDetails, setShowDetails] = useState(null);
  const [limitError, setLimitError] = useState(null);

  const { fetchMembers } = useAuth();

  useEffect(() => {
    fetchMembers();
  }, [fetchMembers]);

  const fetchAvailableItems = useCallback(async () => {
    if (!selectedMember) return;
    setItemsLoading(true);
    try {
      const data = await api.getAvailableForMember(selectedMember.id, {
        page: 1,
        page_size: 50,
      });
      setAvailableItems(data.items);
    } catch (error) {
      addToast(error.message || 'Failed to load available items', 'error');
    } finally {
      setItemsLoading(false);
    }
  }, [selectedMember, addToast]);

  useEffect(() => {
    fetchAvailableItems();
  }, [fetchAvailableItems]);

  const handleMemberChange = (member) => {
    setSelectedMember(member);
    setSuccess(null);
  };

  const handleBook = (item) => {
    setSelectedItem(item);
    setConfirmBooking(true);
  };

  const handleConfirmBook = async () => {
    if (!selectedItem || !selectedMember) return;
    setLoading(true);
    try {
      const booking = await api.bookInventory({
        member_id: selectedMember.id,
        inventory_id: selectedItem.id,
        quantity: 1,
      });
      setSuccess({
        member_name: booking.member_name || selectedMember.full_name,
        inventory_title: booking.inventory_title || selectedItem.title,
        booking_reference: booking.booking_reference,
        booking_date: booking.booking_date,
      });
      setConfirmBooking(false);
      setSelectedItem(null);
      // Refresh available items since this item is now booked
      fetchAvailableItems();
    } catch (error) {
      // Check if it's a max bookings limit error
      if (error.message && error.message.includes('maximum bookings limit')) {
        setConfirmBooking(false);
        setLimitError({
          message: error.message,
          member: selectedMember,
        });
      } else {
        addToast(error.message || 'Booking failed', 'error');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCancelConfirm = () => {
    setConfirmBooking(false);
    setSelectedItem(null);
  };

  if (!selectedMember) {
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
          <div className="text-center py-12">
            <User className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">Select a Member</h2>
            <p className="text-gray-600">Choose a member from the dropdown above to see available items to book</p>
          </div>
        </main>
      </div>
    );
  }

  // Success page
  if (success) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <Link to="/action" className="text-xl font-bold text-gray-900 hover:text-primary-600 transition-colors">
                TenMission
              </Link>
              <div className="flex items-center gap-4">
                <Link to="/create-booking" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
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
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Booking Created Successfully!</h2>
            <div className="card p-8 max-w-md mx-auto">
              <dl className="space-y-4">
                <div className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 items-center">
                  <dt className="text-gray-500 text-sm">Member</dt>
                  <dd className="font-medium text-gray-900 text-right">{success.member_name}</dd>
                </div>
                <div className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 items-center">
                  <dt className="text-gray-500 text-sm">Inventory Item</dt>
                  <dd className="font-medium text-gray-900 text-right">{success.inventory_title}</dd>
                </div>
                <div className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 items-center">
                  <dt className="text-gray-500 text-sm">Booking Reference</dt>
                  <dd className="text-right">
                    <code className="font-mono text-xs bg-gray-100 px-2 py-1 rounded text-gray-900">
                      {success.booking_reference}
                    </code>
                  </dd>
                </div>
                <div className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 items-center">
                  <dt className="text-gray-500 text-sm">Booking Date</dt>
                  <dd className="font-medium text-gray-900 text-right">
                    {new Date(success.booking_date).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </dd>
                </div>
              </dl>
              <div className="mt-8 flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() => setSuccess(null)}
                  className="btn-primary w-full sm:w-1/2 py-3 text-center text-sm font-medium"
                >
                  Create Another Booking
                </button>
                <Link
                  to="/action"
                  className="btn-secondary w-full sm:w-1/2 py-3 text-center text-sm font-medium inline-flex items-center justify-center"
                >
                  Back to Dashboard
                </Link>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

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
              <div className="flex items-center gap-4 w-64">
                <MemberSelector />
              </div>
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
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-2">
            Available Inventory for {selectedMember.full_name}
          </h2>
          <p className="text-gray-600">
            Select an item below to book. Each member can have up to 2 active bookings.
          </p>
        </div>

        {itemsLoading ? (
          <div className="min-h-[300px] flex items-center justify-center">
            <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
          </div>
        ) : availableItems.length === 0 ? (
          <div className="text-center py-12">
            <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No items available to book</h3>
            <p className="text-gray-600">
              All items are either already booked by you, out of stock, or expired.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {availableItems.map((item) => (
              <div key={item.id} className="card p-5 flex flex-col h-full">
                <div className="mb-3">
                  <h3 className="font-semibold text-gray-900 text-lg">{item.title}</h3>
                </div>
                <div className="mb-4 flex-1">
                  <p className="text-gray-600 text-sm line-clamp-3">
                    {item.description || 'No description available'}
                  </p>
                  {item.description && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        setShowDetails(item);
                      }}
                      className="text-xs text-primary-600 hover:underline mt-1 inline-block"
                    >
                      Show full description
                    </button>
                  )}
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-500 mb-4 pt-3 border-t border-gray-100">
                  <span className="font-medium text-gray-900">
                    Available: {item.remaining_count}
                  </span>
                  <span className="text-gray-600">
                    Expires: {new Date(item.expiration_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                  </span>
                </div>
                <button
                  onClick={() => handleBook(item)}
                  disabled={item.remaining_count === 0}
                  className="btn-primary w-full py-2 mt-auto"
                >
                  Book Item
                </button>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Confirmation Dialog */}
      {confirmBooking && selectedItem && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl">
            <div className="flex items-start gap-3 mb-4">
              <Plus className="w-6 h-6 text-blue-600 flex-shrink-0" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Confirm Booking</h3>
                <p className="text-gray-600 text-sm">
                  Are you sure you want to book <strong>{selectedItem.title}</strong>?
                </p>
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <p className="text-sm text-gray-600 mb-2"><strong>Member:</strong> {selectedMember.full_name}</p>
              <p className="text-sm text-gray-600"><strong>Item:</strong> {selectedItem.title}</p>
              <p className="text-sm text-gray-600"><strong>Available:</strong> {selectedItem.remaining_count}</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleCancelConfirm}
                className="flex-1 btn-secondary py-2"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmBook}
                disabled={loading}
                className="flex-1 btn-primary py-2"
              >
                {loading ? 'Booking...' : 'Confirm Booking'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Item Details Dialog */}
      {showDetails && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Item Details</h3>
              <button
                onClick={() => setShowDetails(null)}
                className="text-gray-400 hover:text-gray-600 p-1"
                aria-label="Close"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500 mb-1">Title</p>
                <p className="font-medium text-gray-900">{showDetails.title}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500 mb-1">Description</p>
                <p className="text-gray-900 whitespace-pre-wrap">{showDetails.description}</p>
              </div>
              <div className="grid grid-cols-2 gap-4 pt-2 border-t border-gray-100">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Available</p>
                  <p className="font-medium text-gray-900">{showDetails.remaining_count}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-1">Expires</p>
                  <p className="font-medium text-gray-900">
                    {new Date(showDetails.expiration_date).toLocaleDateString('en-US', {
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
                onClick={() => setShowDetails(null)}
                className="btn-primary px-6 py-2"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Max Bookings Limit Error Dialog */}
      {limitError && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Booking Limit Reached</h3>
            </div>
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <p className="text-red-800 text-sm">{limitError.message}</p>
            </div>
            <p className="text-gray-600 text-sm mb-6">
              You need to cancel an existing booking before creating a new one.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setLimitError(null)}
                className="flex-1 btn-secondary py-2"
              >
                Close
              </button>
              <button
                onClick={() => {
                  setSelectedMember(limitError.member);
                  setLimitError(null);
                  navigate('/bookings');
                }}
                className="flex-1 btn-primary py-2"
              >
                Manage Bookings
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
