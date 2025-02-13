<template>
  <div id="app">
    <AppNavbar />
    <router-view />
  </div>
</template>

<script>
import AppNavbar from '@/components/AppNavbar.vue';
import { mapGetters } from 'vuex';

export default {
  name: 'App',
  components: {
    AppNavbar
  },
  computed: {
    ...mapGetters(['isAuthenticated'])
  },
  async created() {
    if (this.isAuthenticated) {
      try {
        await this.$store.dispatch('fetchUser');
      } catch (error) {
        console.error('Failed to fetch user on app initialization:', error);
        // Optionally handle the error, e.g., redirect to login
      }
    }
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
