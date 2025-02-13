<template>
  <div class="favorites-list">
    <h1>Favorite Properties</h1>
    <div v-if="!favorites || favorites.length === 0">No favorites found.</div>
    <div v-else class="properties-grid">
      <PropertyCard 
        v-for="favorite in favorites" 
        :key="favorite.property.id" 
        :property="favorite.property" 
        :showDetailsButton="false"
        :hideRooms="true"
        @favorite-removed="removeFavoriteFromList" 
      />
    </div>
  </div>
</template>

<script>
import PropertyCard from '@/components/PropertyCard.vue';
import api from '@/services/api';

export default {
  components: {
    PropertyCard
  },
  data() {
    return {
      favorites: []
    };
  },
  computed: {
    isAuthenticated() {
      return this.$store.getters.isAuthenticated;
    }
  },
  async created() {
    if (this.isAuthenticated) {
      await this.fetchFavorites();
    }
  },
  methods: {
    async fetchFavorites() {
      try {
        const favorites = await this.$store.dispatch('fetchFavorites');
        const propertyDetailsPromises = favorites.map(async fav => {
          const response = await api.get(`/properties/${fav.property_id}`);
          return {
            ...fav,
            property: response.data
          };
        });
        this.favorites = await Promise.all(propertyDetailsPromises);
      } catch (error) {
        console.error('Failed to fetch favorites:', error);
      }
    },
    removeFavoriteFromList(removedFavorite) {
      this.favorites = this.favorites.filter(favorite => favorite.property.id !== removedFavorite.id);
    }
  }
};
</script>

<style scoped>
.favorites-list {
  padding: 20px;
}

.properties-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
</style>
