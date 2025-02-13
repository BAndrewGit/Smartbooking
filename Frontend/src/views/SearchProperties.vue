<template>
  <div>
    <h1>Search Properties</h1>
    <SearchFilter @search="performSearch" />
    <div v-if="recommendations.length > 0">
      <h2>Recommendations</h2>
      <div class="properties-grid">
        <div v-for="property in recommendations" :key="property.id">
          <PropertyCard :property="property" />
        </div>
      </div>
    </div>
    <div v-if="searchResults.length > 0">
      <h2>Search Results</h2>
      <div class="properties-grid">
        <div v-for="property in searchResults" :key="property.id">
          <PropertyCard :property="property" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SearchFilter from '@/components/SearchFilter.vue';
import PropertyCard from '@/components/PropertyCard.vue';
import api from '@/services/api';

export default {
  components: {
    SearchFilter,
    PropertyCard
  },
  data() {
    return {
      recommendations: [],
      searchResults: []
    };
  },
  async created() {
    this.performSearch(this.$route.query);
  },
  methods: {
    async performSearch(filters) {
      try {
        const response = await api.get('/filter_properties', { params: filters });
        this.recommendations = response.data.recommendations || [];
        this.searchResults = response.data.available_properties || [];
      } catch (error) {
        console.error('Error searching properties:', error);
      }
    }
  },
  watch: {
    '$route.query': 'performSearch'
  }
};
</script>

<style scoped>
.properties-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
</style>
