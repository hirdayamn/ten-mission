import { useState, useEffect, useCallback, useRef } from 'react';
import { ArrowLeft, ListChecks, Search, Loader2, LogOut } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import { MemberSelector, PageLoader } from '../components';
import { useToast } from '../components';
import { BookingCard } from '../components/BookingCard';

export function BookingsPage() {
  const { selectedMember, setSelectedMember, members, logout, fetchMembers } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterActive, setFilterActive] = useState(true);
  const cancellingRef = useRef(null);

  const fetchBookings = useCallback(async () => {
    if (!selectedMember) {
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const params = {
        member_id: selectedMember.id,
        active_only: filterActive,
        page_size: 50,
      };
      const data = await api.getBookings(params);
      setBookings(data.items);
    } catch (error) {
      addToast(error.message || 'Failed to load bookings', 'error');
    } finally {
      setLoading(false);
    }
  }, [selectedMember, filterActive, addToast]);

  useEffect(() => {
    fetchMembers();
    fetchBookings();
  }, [fetchMembers, fetchBookings]);

  const handleSearch = (query) => {
    setSearchQuery(query);
  };

  const handleCancel = async (bookingReference) => {
    if (!confirm('Are you sure you want to cancel this booking?')) return;
    cancellingRef.current = bookingReference;
    try {
      await api.cancelBooking(bookingReference);
      addToast('Booking cancelled successfully!');
      fetchBookings();
    } catch (error) {
      addToast(error.message || 'Cancellation failed', 'error');
    } finally {
      cancellingRef.current = null;
    }
  };

  const filteredBookings = bookings.filter((booking) =>
    booking.booking_reference.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
            <ListChecks className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">Select a Member</h2>
            <p className="text-gray-600">Choose a member from the dropdown above to view their bookings</p>
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
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">Your Bookings</h2>
          <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
            <input
              type="checkbox"
              checked={filterActive}
              onChange={(e) => setFilterActive(e.target.checked)}
              className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
            Active only
          </label>
        </div>

        {loading ? (
          <div className="min-h-[400px] flex items-center justify-center">
            <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
          </div>
        ) : filteredBookings.length === 0 ? (
          <div className="text-center py-12">
            <ListChecks className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No bookings</h3>
            <p className="text-gray-600">
              {searchQuery ? 'No bookings match your search' : 'You have no bookings yet'}
            </p>
            {searchQuery === '' && !filterActive && (
              <p className="text-gray-600 mt-2">You have no bookings at all.</p>
            )}
            <Link to="/create-booking" className="mt-6 btn-primary inline-flex items-center gap-2">
              Create a Booking
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredBookings.map((booking) => (
              <BookingCard
                key={booking.id}
                booking={booking}
                onCancel={handleCancel}
                loading={cancellingRef.current === booking.booking_reference}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
