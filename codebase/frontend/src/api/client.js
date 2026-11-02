const API_BASE = '/api';

class ApiClient {
  constructor() {
    this.accessToken = null;
  }

  setTokens(accessToken, expiresIn) {
    this.accessToken = accessToken;
    if (accessToken) {
      localStorage.setItem('accessToken', accessToken);
      if (expiresIn) {
        const expiration = Date.now() + expiresIn * 1000;
        localStorage.setItem('tokenExpiration', String(expiration));
      }
    } else {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('tokenExpiration');
    }
  }

  loadTokens() {
    this.accessToken = localStorage.getItem('accessToken');
  }

  isTokenExpired() {
    const expiration = localStorage.getItem('tokenExpiration');
    if (!expiration) return true;
    return Date.now() > parseInt(expiration, 10);
  }

  clearTokens() {
    this.accessToken = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('tokenExpiration');
  }

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || 'Request failed');
    }

    return response.json();
  }

  // Auth
  login(email) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  }

  // Inventory
  getInventory(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/inventory?${query}`);
  }

  getInventoryItem(id) {
    return this.request(`/inventory/${id}`);
  }

  // Bookings
  bookInventory(booking) {
    return this.request('/bookings/book', {
      method: 'POST',
      body: JSON.stringify(booking),
    });
  }

  cancelBooking(bookingReference) {
    return this.request('/bookings/cancel', {
      method: 'POST',
      body: JSON.stringify({ booking_reference: bookingReference }),
    });
  }

  getBookings(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/bookings?${query}`);
  }

  // Members
  getMembers(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/members?${query}`);
  }

  // Inventory for member (available to book)
  getAvailableForMember(memberId, params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/members/${memberId}/available-inventory?${query}`);
  }
}

export const api = new ApiClient();