import { createStore } from 'vuex';
import api from '@/services/api';

const state = {
  token: localStorage.getItem('token') || '',
  refreshToken: localStorage.getItem('refreshToken') || '',
  user: null,
  properties: [],
  propertyDetails: {},
  recommendations: [],
  rooms: [],
  reservations: [],
  reviews: [],
  favorites: [],
  loading: false,
  error: null
};

const mutations = {
  SET_TOKEN(state, token) {
    state.token = token;
    localStorage.setItem('token', token);
  },
  SET_REFRESH_TOKEN(state, refreshToken) {
    state.refreshToken = refreshToken;
    localStorage.setItem('refreshToken', refreshToken);
  },
  LOGOUT(state) {
    state.token = '';
    state.refreshToken = '';
    state.user = null;
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  },
  SET_USER(state, user) {
    state.user = user;
  },
  SET_PROPERTIES(state, properties) {
    state.properties = properties;
  },
  SET_PROPERTY_DETAILS(state, property) {
    state.propertyDetails = property;
  },
  SET_ROOMS(state, rooms) {
    state.rooms = rooms;
  },
  SET_RESERVATIONS(state, reservations) {
    state.reservations = reservations;
  },
  SET_REVIEWS(state, reviews) {
    state.reviews = reviews;
  },
  SET_FAVORITES(state, favorites) {
    state.favorites = favorites;
  },
  SET_LOADING(state, loading) {
    state.loading = loading;
  },
  SET_ERROR(state, error) {
    state.error = error;
  },
  SET_RECOMMENDATIONS(state, recommendations) {
    state.recommendations = recommendations;
  },
  ADD_PROPERTY(state, property) {
    state.properties.push(property);
  },
  UPDATE_PROPERTY(state, updatedProperty) {
    const index = state.properties.findIndex(property => property.id === updatedProperty.id);
    if (index !== -1) {
      state.properties.splice(index, 1, updatedProperty);
    }
  },
  DELETE_PROPERTY(state, propertyId) {
    state.properties = state.properties.filter(property => property.id !== propertyId);
  },
  ADD_ROOM(state, room) {
    state.rooms.push(room);
  },
  UPDATE_ROOM(state, updatedRoom) {
    const index = state.rooms.findIndex(room => room.id === updatedRoom.id);
    if (index !== -1) {
      state.rooms.splice(index, 1, updatedRoom);
    }
  },
  DELETE_ROOM(state, roomId) {
    state.rooms = state.rooms.filter(room => room.id !== roomId);
  },
  ADD_RESERVATION(state, reservation) {
    state.reservations.push(reservation);
  },
  ADD_FAVORITE(state, favorite) {
    state.favorites.push(favorite);
  },
  REMOVE_FAVORITE(state, favoriteId) {
    state.favorites = state.favorites.filter(favorite => favorite.id !== favoriteId);
  }
};

const actions = {
  async login({ commit, dispatch }, credentials) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      const response = await api.post('/auth/login', credentials);
      commit('SET_TOKEN', response.data.access_token);
      commit('SET_REFRESH_TOKEN', response.data.refresh_token);
      await dispatch('fetchUser');
    } catch (error) {
      const errorMessage = error.response && error.response.data && error.response.data.message
        ? error.response.data.message
        : 'Failed to login';
      commit('SET_ERROR', errorMessage);
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async register({ commit }, user) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      await api.post('/auth/register', user);
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to register');
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async logout({ commit }) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      await api.post('/auth/logout');
      commit('LOGOUT');
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to logout');
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async forgotPassword({ commit }, email) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      await api.post('/auth/forgot_password', { email: email });
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to send reset link');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async refreshToken({ commit }) {
    try {
      const response = await api.post('/auth/refresh', {}, {
        headers: {
          'Authorization': `Bearer ${state.refreshToken}`
        }
      });
      commit('SET_TOKEN', response.data.access_token);
      api.defaults.headers.common['Authorization'] = `Bearer ${state.token}`;
    } catch (error) {
      commit('LOGOUT');
      throw error;
    }
  },
  async fetchUser({ commit }) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      const response = await api.get('/user');
      commit('SET_USER', response.data);
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to fetch user');
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async updateUser({ commit }, user) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      const response = await api.put('/user', user);
      commit('SET_USER', response.data);
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to update user');
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async deleteUser({ commit }) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      await api.delete('/user');
      commit('LOGOUT');
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to delete user');
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async fetchProperties({ commit }, params) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      const response = await api.get('/filter_properties', { params });
      commit('SET_PROPERTIES', response.data.available_properties);
      commit('SET_RECOMMENDATIONS', response.data.recommendations);
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to fetch properties');
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async fetchRooms({ commit }, params = {}) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      const response = await api.get('/rooms', { params });
      commit('SET_ROOMS', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to fetch rooms');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async fetchOwnerProperties({ commit }) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      const response = await api.get('/properties/owner');
      commit('SET_PROPERTIES', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to fetch owner properties');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async fetchReservations({ commit }) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      const response = await api.get('/reservations');
      commit('SET_RESERVATIONS', response.data);
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to fetch reservations');
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async viewReservation({ commit }, reservationId) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      const response = await api.get(`/reservations/${reservationId}`);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to fetch reservation details');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async cancelReservation({ commit }, reservationId) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      const response = await api.post(`/cancel_reservation/${reservationId}`);
      commit('SET_RESERVATIONS', state.reservations.map(r => r.id === reservationId ? { ...r, status: 'cancelled' } : r));
      return response.data;
    } catch (error) {
      const errorMessage = error.response && error.response.data && error.response.data.message
        ? error.response.data.message
        : 'Failed to cancel reservation';
      commit('SET_ERROR', errorMessage);
      throw new Error(errorMessage);
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async fetchFavorites({ commit }) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      const response = await api.get('/favorites');
      commit('SET_FAVORITES', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to fetch favorites');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async fetchPropertyDetails({ commit }, propertyId) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      const response = await api.get(`/properties/${propertyId}`);
      commit('SET_PROPERTY_DETAILS', response.data); // Stochează detaliile proprietății în state
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to fetch property details');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async createFavorite({ commit }, favorite) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      const response = await api.post('/favorites', favorite);
      commit('ADD_FAVORITE', response.data);
      return response.data;
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to add favorite');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async deleteFavorite({ commit }, favoriteId) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      await api.delete(`/favorites/${favoriteId}`);
      commit('REMOVE_FAVORITE', favoriteId);
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to delete favorite');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async createProperty({ commit, state }, property) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      const formData = new FormData();
      for (const key in property) {
        if (key !== 'images') {
          formData.append(key, property[key]);
        }
      }
      formData.append('availability', true); // Set availability to true
      property.images.forEach((file) => {
        formData.append('images', file);
      });

      console.log('Creating property with data:', formData);
      const response = await api.post('/properties', formData, {
        headers: {
          Authorization: `Bearer ${state.token}`,
          'Content-Type': 'multipart/form-data',
        },
      });
      commit('ADD_PROPERTY', response.data);
    } catch (error) {
      console.error('Error creating property:', error.response ? error.response.data : error.message);
      commit('SET_ERROR', error.response ? error.response.data.message : 'Failed to add property');
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async updateProperty({ commit, state }, property) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      const formData = new FormData();
      for (const key in property) {
        if (key !== 'images') {
          formData.append(key, property[key]);
        }
      }
      property.images.forEach((file) => {
        formData.append('images', file);
      });

      console.log(`Updating property ${property.id} with data:`, formData);
      const response = await api.put(`/properties/${property.id}`, formData, {
        headers: {
          Authorization: `Bearer ${state.token}`,
          'Content-Type': 'multipart/form-data',
        },
      });
      commit('UPDATE_PROPERTY', response.data);
    } catch (error) {
      console.error('Error updating property:', error.response ? error.response.data : error.message);
      commit('SET_ERROR', error.response ? error.response.data.message : 'Failed to update property');
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async deleteProperty({ commit, state }, propertyId) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      console.log(`Deleting property with id: ${propertyId}`);
      await api.delete(`/properties/${propertyId}`, {
        headers: {
          Authorization: `Bearer ${state.token}`,
        },
      });
      commit('DELETE_PROPERTY', propertyId);
    } catch (error) {
      console.error('Error deleting property:', error.response ? error.response.data : error.message);
      commit('SET_ERROR', error.response.data.message || 'Failed to delete property');
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async createRoom({ commit }, room) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      const response = await api.post('/rooms', room);
      commit('ADD_ROOM', response.data);
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to add room');
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async updateRoom({ commit }, room) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      const response = await api.put(`/rooms/${room.id}`, room);
      commit('UPDATE_ROOM', response.data);
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to update room');
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async deleteRoom({ commit }, roomId) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      await api.delete(`/rooms/${roomId}`);
      commit('DELETE_ROOM', roomId);
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to delete room');
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async createReservation({ commit }, reservation) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      console.log('Dispatching reservation data:', reservation);
      const response = await api.post('/reservations', reservation);
      commit('ADD_RESERVATION', response.data);
      return response.data; // Return the response data
    } catch (error) {
      console.error('Error in createReservation action:', error);
      commit('SET_ERROR', error.response.data.message || 'Failed to add reservation');
      throw error; // Rethrow the error to handle it in the component
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async createReview({ commit }, review) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      await api.post('/reviews', review);
      await this.dispatch('fetchReviews', review.property_id);
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to add review');
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async fetchReviews({ commit }, propertyId) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      const response = await api.get(`/properties/${propertyId}/reviews`);
      commit('SET_REVIEWS', response.data);
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to fetch reviews');
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async updateReview({ commit, dispatch }, review) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      await api.put(`/reviews/${review.id}`, review);
      await dispatch('fetchReviews', review.property_id);
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to update review');
    } finally {
      commit('SET_LOADING', false);
    }
  },
  async deleteReview({ commit }, review) {
    commit('SET_LOADING', true);
    commit('SET_ERROR', null);
    try {
      await api.delete(`/reviews/${review.id}`);
      await this.dispatch('fetchReviews', review.property_id);
    } catch (error) {
      commit('SET_ERROR', error.response.data.message || 'Failed to delete review');
    } finally {
      commit('SET_LOADING', false);
    }
  }
};

const getters = {
  isAuthenticated: state => !!state.token,
  userRole: state => (state.user ? state.user.role : null),
  userProperties: state => state.properties.filter(property => property.owner_id === state.user.id),
  getUser: state => state.user,
  getPreferences: state => state.preferences,
  getProperties: state => state.properties,
  getPropertyDetails: state => state.propertyDetails,
  getRecommendations: state => state.recommendations,
  getRooms: state => state.rooms,
  getReservations: state => state.reservations,
  getReviews: state => state.reviews,
  getFavorites: state => state.favorites,
  isLoading: state => state.loading,
  getError: state => state.error
};

export default createStore({
  state,
  mutations,
  actions,
  getters
});
