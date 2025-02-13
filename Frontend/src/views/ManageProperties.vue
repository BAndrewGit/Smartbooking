<template>
  <div>
    <h1>Manage Properties</h1>
    <div class="properties-grid">
      <PropertyCard 
        v-for="property in properties" 
        :key="property.id" 
        :property="property" 
        :isManageMode="true" 
        :hideRooms="true"
        @edit-property="editProperty" 
        @delete-property="deleteProperty"
      />
    </div>
    <PropertyForm 
      v-if="selectedProperty" 
      :propertyData="selectedProperty" 
      :isEditMode="true" 
      @property-updated="fetchProperties"
      @cancel-edit="cancelEdit"
    />
    <PropertyForm 
      v-if="!selectedProperty && !isSuperAdmin" 
      :isEditMode="false" 
      @property-added="fetchProperties"
    />
  </div>
</template>

<script>
import PropertyCard from '@/components/PropertyCard.vue';
import PropertyForm from '@/components/PropertyForm.vue';
import { mapGetters } from 'vuex';

export default {
  components: {
    PropertyCard,
    PropertyForm
  },
  data() {
    return {
      properties: [],
      selectedProperty: null
    };
  },
  computed: {
    ...mapGetters(['userRole']),
    isSuperAdmin() {
      return this.userRole === 'superadmin';
    }
  },
  methods: {
    async fetchProperties() {
      try {
        const response = await this.$store.dispatch('fetchOwnerProperties');
        this.properties = response;
      } catch (error) {
        console.error('Error fetching properties:', error);
      }
    },
    editProperty(property) {
      this.selectedProperty = property;
    },
    async deleteProperty(property) {
      try {
        await this.$store.dispatch('deleteProperty', property.id);
        await this.fetchProperties();
      } catch (error) {
        console.error('Error deleting property:', error);
      }
    },
    cancelEdit() {
      this.selectedProperty = null;
    }
  },
  async created() {
    await this.fetchProperties();
  }
};
</script>

<style scoped>
h1 {
  text-align: center;
  margin-top: 20px;
}
.properties-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
</style>
