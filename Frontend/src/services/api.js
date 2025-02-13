import axios from 'axios';
import store from '@/store';

const api = axios.create({
  baseURL: 'http://127.0.0.1:5000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor to add JWT token to every request
api.interceptors.request.use(config => {
  const token = store.state.token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  console.log('Request URL:', config.baseURL + config.url);
  console.log('Request Headers:', config.headers);
  return config;
}, error => {
  return Promise.reject(error);
});

// Interceptor for handling errors and refreshing token
api.interceptors.response.use(response => {
  return response;
}, async error => {
  const originalRequest = error.config;

  // Check if the error is 401 Unauthorized and the original request has not been retried yet
  if (error.response && error.response.status === 401 && !originalRequest._retry) {
    originalRequest._retry = true; // Set the retry flag

    try {
      // Attempt to refresh the access token using the refresh token
      const response = await api.post('/auth/refresh', {}, {
        headers: {
          'Authorization': `Bearer ${store.state.refreshToken}`
        }
      });

      // Commit the new access token to the store
      store.commit('SET_TOKEN', response.data.access_token);

      // Update the Authorization header with the new access token
      api.defaults.headers.common['Authorization'] = `Bearer ${store.state.token}`;
      originalRequest.headers['Authorization'] = `Bearer ${store.state.token}`;

      // Retry the original request with the new access token
      return api(originalRequest);
    } catch (refreshError) {
      // If refresh fails, log out the user
      store.commit('LOGOUT');
      return Promise.reject(refreshError);
    }
  }

  // Return any other error that is not a 401
  return Promise.reject(error);
});

export default api;
