import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '@/views/HomePage.vue';
import LoginUser from '@/views/LoginUser.vue';
import UserProfile from '@/views/UserProfile.vue';
import SearchProperties from '@/views/SearchProperties.vue';
import PropertyDetails from '@/views/PropertyDetails.vue';
import ManageProperties from '@/views/ManageProperties.vue';
import ManageRooms from '@/views/ManageRooms.vue';
import PropertyReservations from '@/views/PropertyReservations.vue';
import FavoritesList from '@/views/FavoritesList.vue';
import AdminRoles from '@/views/AdminRoles.vue';
import ResetPassword from '@/views/ResetPassword.vue';
import store from '@/store';

const routes = [
  { path: '/', name: 'HomePage', component: HomePage},
  { path: '/login', name: 'LoginUser', component: LoginUser, meta: { title: 'Authentication - Smart Booking' } },
  { path: '/profile', name: 'UserProfile', component: UserProfile, meta: { requiresAuth: true, title: 'Profile - Smart Booking' } },
  { path: '/search-properties', name: 'SearchProperties', component: SearchProperties, meta: { title: 'Find Properties - Smart Booking' } },
  { path: '/property-details/:id', name: 'PropertyDetails', component: PropertyDetails, meta: { title: 'Property Info - Smart Booking' } },
  { path: '/manage-properties', name: 'ManageProperties', component: ManageProperties, meta: { requiresAuth: true, title: 'Properties - Smart Booking' } },
  { path: '/manage-rooms', name: 'ManageRooms', component: ManageRooms, meta: { requiresAuth: true, title: 'Rooms - Smart Booking' } },
  { path: '/reservations', name: 'PropertyReservations', component: PropertyReservations, meta: { requiresAuth: true, title: 'Reservations - Smart Booking' } },
  { path: '/favorites', name: 'FavoritesList', component: FavoritesList, meta: { requiresAuth: true, title: 'Favorites - Smart Booking' } },
  { path: '/admin-roles', name: 'AdminRoles', component: AdminRoles, meta: { requiresAuth: true, requiresSuperadmin: true, title: 'Roles - Smart Booking' } },
  { path: '/reset-password/:token', name: 'ResetPassword', component: ResetPassword, meta: { title: 'Reset Password - Smart Booking' } }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const requiresSuperadmin = to.matched.some(record => record.meta.requiresSuperadmin);
  const isAuthenticated = store.getters.isAuthenticated;
  const userRole = store.state.user ? store.state.user.role : null;

  // Set the document title from the route meta
  if (to.meta.title) {
    document.title = to.meta.title;
  } else {
    document.title = 'Smart Booking';
  }

  if (requiresAuth && !isAuthenticated) {
    next('/login');
  } else if (requiresSuperadmin && userRole !== 'superadmin') {
    next('/');
  } else {
    next();
  }
});

export default router;
