<template>
  <div>
    <h1>{{ greetingMessage }}</h1>
    <SearchFilter @search="searchProperties" />
  </div>
</template>

<script>
import SearchFilter from '@/components/SearchFilter.vue';
import { mapGetters, mapActions } from 'vuex';

export default {
  components: {
    SearchFilter
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'getUser']),
    greetingMessage() {
      if (this.isAuthenticated && this.getUser) {
        return `Bine ai revenit ${this.getUser.name}! Unde ai dori să călătorești?`;
      } else {
        return 'Unde ai dori să călătorești?';
      }
    }
  },
  created() {
    if (this.isAuthenticated) {
      this.fetchUser();
    }
  },
  methods: {
    ...mapActions(['fetchUser']),
    searchProperties(filters) {
      const queryParams = new URLSearchParams(filters).toString();
      this.$router.push({ path: '/search', query: queryParams });
    }
  }
};
</script>

<style scoped>
/* Add your styles here */
</style>
