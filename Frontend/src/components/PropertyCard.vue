<template>
  <div class="property-card">
    <div class="property-info">
      <h3>{{ property.name }}</h3>
      <p>{{ property.region }}</p>
      <p>{{ property.address }}</p>
      <p>Stars: {{ property.stars }}</p>
      <p>Type: {{ property.type }}</p>
      <div v-if="property.rooms && property.rooms.length">
        <div v-for="room in property.rooms" :key="room.room_type">
          <p>{{ room.room_type }}: {{ room.price }} {{ room.currency }} ({{ room.persons }} persons)</p>
        </div>
      </div>
      <p v-if="property.total_price">Total Price: {{ property.total_price }} {{ property.rooms[0].currency }}</p>
      <button @click="viewDetails">View Details</button>
      <button v-if="isManageMode && !isSuperAdmin" @click="editProperty" class="edit-button">Edit</button>
      <button v-if="isManageMode" @click="deleteProperty" class="delete-button">Delete</button>
      <button v-if="!isManageMode" @click="toggleFavorite">
        {{ isFavorite ? 'Remove from Favorites' : 'Add to Favorites' }}
      </button>
    </div>
    <div class="carousel">
      <button @click="prevImage" class="carousel-button">&lt;</button>
      <img :src="currentImage" alt="Property Image" class="property-image">
      <button @click="nextImage" class="carousel-button">&gt;</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    property: {
      type: Object,
      required: true
    },
    isManageMode: {
      type: Boolean,
      default: false
    },
    showDetailsButton: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      isFavorite: false,
      defaultImage: require('@/assets/default-image.png'), // Default image
      isToggling: false,
      currentImageIndex: 0
    };
  },
  computed: {
    isAuthenticated() {
      return this.$store.getters.isAuthenticated;
    },
    isSuperAdmin() {
      return this.$store.getters.userRole === 'superadmin';
    },
    currentImage() {
      let images = [];
      try {
        images = typeof this.property.images === 'string' ? JSON.parse(this.property.images) : this.property.images;
      } catch (error) {
        console.error('Error parsing property images:', error);
      }
      return images && images.length > 0 ? `data:image/jpeg;base64,${images[this.currentImageIndex]}` : this.defaultImage;
    }
  },
  async created() {
    if (this.isAuthenticated) {
      await this.checkIfFavorite();
    }
  },
  methods: {
    viewDetails() {
      this.$router.push({ name: 'PropertyDetails', params: { id: this.property.id } });
    },
    editProperty() {
      this.$emit('edit-property', this.property);
    },
    async deleteProperty() {
      if (confirm('Are you sure you want to delete this property?')) {
        try {
          await axios.delete(`http://127.0.0.1:5000/properties/${this.property.id}`, {
            headers: {
              Authorization: `Bearer ${this.$store.state.token}`
            }
          });
          this.$emit('property-deleted', this.property.id);
          this.$emit('refresh-properties'); // Emit event to refresh properties
          alert('Property deleted successfully!');
        } catch (error) {
          console.error('Failed to delete property:', error.response ? error.response.data : error.message);
          alert('Failed to delete property. Please try again.');
        }
      }
    },
    async toggleFavorite() {
      if (!this.isAuthenticated) {
        alert('You must be logged in to manage favorites');
        return;
      }
      if (this.isToggling) {
        return;
      }
      this.isToggling = true;
      try {
        if (this.isFavorite) {
          const favorite = this.$store.state.favorites.find(fav => fav.property_id === this.property.id);
          if (favorite) {
            await this.$store.dispatch('deleteFavorite', favorite.id);
            this.isFavorite = false;
            this.$emit('favorite-removed', this.property);
          }
        } else {
          await this.$store.dispatch('createFavorite', { property_id: this.property.id });
          this.isFavorite = true;
          this.$emit('favorite-added', this.property);
        }
        await this.$store.dispatch('fetchFavorites');
        await this.checkIfFavorite();
      } catch (error) {
        console.error('Failed to toggle favorite:', error);
      } finally {
        this.isToggling = false;
      }
    },
    async checkIfFavorite() {
      try {
        await this.$store.dispatch('fetchFavorites');
        this.isFavorite = this.$store.state.favorites.some(favorite => favorite.property_id === this.property.id);
      } catch (error) {
        console.error('Failed to check if property is favorite:', error);
      }
    },
    prevImage() {
      let images = [];
      try {
        images = typeof this.property.images === 'string' ? JSON.parse(this.property.images) : this.property.images;
      } catch (error) {
        console.error('Error parsing property images:', error);
      }

      if (images.length > 0) {
        this.currentImageIndex = (this.currentImageIndex - 1 + images.length) % images.length;
      }
    },
    nextImage() {
      let images = [];
      try {
        images = typeof this.property.images === 'string' ? JSON.parse(this.property.images) : this.property.images;
      } catch (error) {
        console.error('Error parsing property images:', error);
      }

      if (images.length > 0) {
        this.currentImageIndex = (this.currentImageIndex + 1) % images.length;
      }
    }
  }
};
</script>

<style scoped>
.property-card {
  display: flex;
  border: 1px solid #ddd;
  padding: 16px;
  margin: 16px;
  border-radius: 5px;
  justify-content: space-between;
}
.property-info {
  flex: 1;
}
.carousel {
  position: relative;
  display: flex;
  align-items: center;
}
.property-card img {
  width: 400px;
  height: 300px;
  object-fit: cover;
  margin-left: 20px;
  margin-top: 5px;
}
.carousel-button {
  background-color: transparent;
  border: none;
  font-size: 24px;
  cursor: pointer;
  position: absolute;
}
.carousel-button:focus {
  outline: none;
}
.carousel-button:nth-of-type(1) {
  left: 0;
}
.carousel-button:nth-of-type(2) {
  right: 0;
}
button {
  margin-top: 10px;
  background-color: #42b983;
  color: white;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
}
button:hover {
  background-color: #369971;
}
button:disabled {
  background-color: #bbb;
  cursor: not-allowed;
}
.edit-button {
  background-color: #007BFF;
}
.edit-button:hover {
  background-color: #0056b3;
}
.delete-button {
  background-color: #dc3545;
}
.delete-button:hover {
  background-color: #c82333;
}
</style>
