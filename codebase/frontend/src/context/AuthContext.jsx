import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedMember, setSelectedMember] = useState(null);
  const [members, setMembers] = useState([]);

  useEffect(() => {
    api.loadTokens();
    const token = localStorage.getItem('accessToken');
    if (token && !api.isTokenExpired()) {
      setUser({ email: 'user@tenmission.com' });
    } else {
      api.clearTokens();
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (email) => {
    const data = await api.login(email);
    api.setTokens(data.access_token, data.expires_in);
    setUser({ email });
    return data;
  }, []);

  const logout = useCallback(() => {
    api.clearTokens();
    setUser(null);
    setSelectedMember(null);
  }, []);

  const fetchMembers = useCallback(async () => {
    try {
      const data = await api.getMembers({ page_size: 100 });
      const memberList = data.items.map(item => ({
        id: item.id,
        full_name: item.full_name,
        username: item.username,
      }));
      setMembers(memberList);
      if (!selectedMember && memberList.length > 0) {
        setSelectedMember(memberList[0]);
      }
    } catch (error) {
      console.error('Failed to fetch members:', error);
    }
  }, [selectedMember]);

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        selectedMember,
        setSelectedMember,
        members,
        fetchMembers,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}