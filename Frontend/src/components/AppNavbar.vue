<template>
  <nav>
    <ul>
      <li><router-link to="/">Home</router-link></li>
      <li v-if="!isAuthenticated"><router-link to="/login">Login</router-link></li>
      <li v-if="isAuthenticated"><router-link to="/profile">Profile</router-link></li>
      <li><router-link to="/search-properties">Search Properties</router-link></li>
      <li v-if="isOwnerOrSuperAdmin"><router-link to="/manage-properties">Manage Properties</router-link></li>
      <li v-if="isOwner"><router-link to="/manage-rooms">Manage Rooms</router-link></li>
      <li v-if="isAuthenticated"><router-link to="/reservations">Reservations</router-link></li>
      <li v-if="isAuthenticated"><router-link to="/favorites">Favorites</router-link></li>
      <li v-if="isSuperAdmin"><router-link to="/admin-roles">Admin</router-link></li>
      <li v-if="isAuthenticated"><button @click="logout">Logout</button></li>
    </ul>
  </nav>
</template>

<script>
export default {
  computed: {
    isAuthenticated() {
      return this.$store.getters.isAuthenticated;
    },
    isSuperAdmin() {
      return this.$store.getters.userRole === 'superadmin';
    },
    isOwner() {
      return this.$store.getters.userRole === 'owner';
    },
    isOwnerOrSuperAdmin() {
      const role = this.$store.getters.userRole;
      return role === 'owner' || role === 'superadmin';
    }
  },
  methods: {
    logout() {
      this.$store.dispatch('logout').then(() => {
        this.$router.push('/');
        // Refetch the user and update the state
        this.$store.dispatch('fetchUser').catch(() => {
          this.$store.commit('SET_USER', null);
        });
      });
    }
  }
};
</script>

<style scoped>
nav ul {
  list-style-type: none;
  padding: 0;
}

nav ul li {
  display: inline;
  margin: 0 10px;
}

nav ul li a,
nav ul li button {
  text-decoration: none;
  color: #42b983;
}

nav ul li button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

nav ul li a:hover,
nav ul li button:hover {
  text-decoration: underline;
}
</style>
