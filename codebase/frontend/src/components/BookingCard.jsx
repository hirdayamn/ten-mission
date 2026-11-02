import { Calendar, Package, User, XCircle, CheckCircle, Mail } from 'lucide-react';

export function BookingCard({ booking, onCancel, loading }) {
  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="card p-5">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <span className="font-medium text-gray-900">Ref:</span>
            <code className="bg-gray-100 px-2 py-1 rounded font-mono text-xs">{booking.booking_reference}</code>
            <span className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
              booking.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
            }`}>
              {booking.is_active ? (
                <>
                  <CheckCircle className="w-3 h-3" />
                  Active
                </>
              ) : (
                <>
                  <XCircle className="w-3 h-3" />
                  Cancelled
                </>
              )}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2 text-gray-600">
              <User className="w-4 h-4" />
              <span>Member: <span className="font-medium text-gray-900">{booking.member_name || booking.member_id}</span></span>
            </div>
            <div className="flex items-center gap-2 text-gray-600">
              <Package className="w-4 h-4" />
              <span>Item: <span className="font-medium text-gray-900">{booking.inventory_title || booking.inventory_id}</span></span>
            </div>
            <div className="flex items-center gap-2 text-gray-600">
              <Calendar className="w-4 h-4" />
              <span>Booked: <span className="font-medium text-gray-900">{formatDate(booking.booking_date)}</span></span>
            </div>
            <div className="flex items-center gap-2 text-gray-600">
              <Mail className="w-4 h-4" />
              <span>Created by: <span className="font-medium text-gray-900">{booking.created_by}</span></span>
            </div>
            {!booking.is_active && booking.cancelled_by && (
              <div className="flex items-center gap-2 text-gray-600">
                <Mail className="w-4 h-4" />
                <span>Cancelled by: <span className="font-medium text-gray-900">{booking.cancelled_by}</span></span>
              </div>
            )}
          </div>
        </div>
        {booking.is_active && (
          <button
            onClick={() => onCancel(booking.booking_reference)}
            disabled={loading}
            className="btn-danger ml-4 whitespace-nowrap"
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  );
}