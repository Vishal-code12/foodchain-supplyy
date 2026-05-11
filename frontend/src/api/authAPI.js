import API from './axiosConfig';

export const authAPI = {
  login: (email, password) => 
    API.post('/api/auth/login', { email, password }),

  register: (userData) => 
    API.post('/api/auth/register', userData),

  loginWithMetaMask: (walletAddress, signature, role) =>
    API.post('/api/auth/metamask-login', { walletAddress, signature, role }),

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userData');
  }
};