import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './components';
import { LoginPage } from './pages/LoginPage';
import { ActionPage } from './pages/ActionPage';
import { InventoryPage } from './pages/InventoryPage';
import { BookingsPage } from './pages/BookingsPage';
import { CreateBookingPage } from './pages/CreateBookingPage';

function ProtectedRoute({ children }) {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" replace />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/action"
        element={
          <ProtectedRoute>
            <ActionPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/inventory"
        element={
          <ProtectedRoute>
            <InventoryPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/bookings"
        element={
          <ProtectedRoute>
            <BookingsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/create-booking"
        element={
          <ProtectedRoute>
            <CreateBookingPage />
          </ProtectedRoute>
        }
      />
      <Route path="/" element={<Navigate to="/action" replace />} />
      <Route path="*" element={<Navigate to="/action" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <AppRoutes />
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;