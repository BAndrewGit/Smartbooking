<template>
  <div class="property-details">
    <h1 class="property-title">{{ property.name }}</h1>
    <div class="property-header">
      <!-- Property Details -->
      <div class="property-info">
        <p><strong>Address:</strong> <span>{{ property.address }}</span></p>
        <p><strong>Postal Code:</strong> <span>{{ property.postal_code }}</span></p>
        <p><strong>Country:</strong> <span>{{ property.country }}</span></p>
        <p><strong>Region:</strong> <span>{{ property.region }}</span></p>
        <p><strong>Check-in:</strong> <span>{{ property.check_in }}</span></p>
        <p><strong>Check-out:</strong> <span>{{ property.check_out }}</span></p>
        <p><strong>Stars:</strong> <span>{{ property.stars }}</span></p>
        <p><strong>Type:</strong> <span>{{ property.type }}</span></p>
        <label v-if="isAuthenticated">
          <button @click="toggleFavorite" class="favorite-button">
            {{ isFavorite ? 'Remove from Favorites' : 'Add to Favorites' }}
          </button>
        </label>
      </div>

      <!-- Property Image -->
      <div class="property-image-wrapper">
        <div class="carousel" v-if="propertyImages && propertyImages.length > 0">
          <button @click="prevImage" class="carousel-button">&lt;</button>
          <img :src="currentImage" alt="Property Image" class="carousel-image" />
          <button @click="nextImage" class="carousel-button">&gt;</button>
        </div>
        <img v-else :src="require('@/assets/default-image.png')" alt="Default Property Image" class="carousel-image" />
      </div>

      <!-- Property Ratings -->
      <div class="property-ratings">
        <p><strong>Nota Generală:</strong> <span>{{ property.nota }}</span></p>
        <p><strong>Personal:</strong> <span>{{ roundedRating(property.nota_personal) }}</span></p>
        <p><strong>Facilități:</strong> <span>{{ roundedRating(property.nota_facilităţi) }}</span></p>
        <p><strong>Curățenie:</strong> <span>{{ roundedRating(property.nota_curăţenie) }}</span></p>
        <p><strong>Confort:</strong> <span>{{ roundedRating(property.nota_confort) }}</span></p>
        <p><strong>Raport Calitate/Preț:</strong> <span>{{ roundedRating(property.nota_raport_calitate_preţ) }}</span></p>
        <p><strong>Locație:</strong> <span>{{ roundedRating(property.nota_locaţie) }}</span></p>
        <p><strong>WiFi Gratuit:</strong> <span>{{ roundedRating(property.nota_wifi_gratuit) }}</span></p>
        <p><strong> Reviews:</strong> <span>{{ property.num_reviews }}</span></p>
      </div>
    </div>

    <h2>Rooms</h2>
    <div v-for="room in rooms" :key="room.id">
      <RoomCard :room="room" />
    </div>

    <!-- Reservation Form -->
    <div>
      <h2>Book a Room</h2>
      <form @submit.prevent="handleFormSubmit">
        <div>
          <label for="check_in_date">Check-in Date:</label>
          <input type="date" v-model="reservationData.check_in_date" @change="fetchRooms" required />
        </div>
        <div>
          <label for="check_out_date">Check-out Date:</label>
          <input type="date" v-model="reservationData.check_out_date" @change="fetchRooms" required />
        </div>
        <div>
          <label for="room_ids">Select Rooms:</label>
          <div v-for="room in rooms" :key="room.id">
            <input type="checkbox" :value="room.id" v-model="reservationData.room_ids" @change="updateTotalPrice" />
            <label>{{ room.room_type }} - {{ room.price }} {{ room.currency }}</label>
          </div>
        </div>
        <p>Total Price: {{ totalPrice }} lei</p>
        <button type="submit">Book Now</button>
      </form>
    </div>

    <!-- Review Section -->
    <div v-if="isAuthenticated">
      <button @click="toggleReviewForm">
        {{ showReviewForm ? 'Cancel' : 'Add Review' }}
      </button>
      <ReviewForm 
        v-if="showReviewForm" 
        :propertyId="property.id" 
        :review="reviewToEdit" 
        @review-submitted="handleReviewSubmitted" 
      />
    </div>

    <h2>Reviews</h2>
    <div v-for="review in reviews" :key="review.id">
      <ReviewCard 
        :review="review" 
        :currentUser="currentUser" 
        :isSuperAdmin="isSuperAdmin" 
        @edit-review="editReview" 
        @review-deleted="handleReviewDeleted" 
        :showActions="isAuthenticated"
      />
    </div>
  </div>
</template>

<script>
import RoomCard from '@/components/RoomCard.vue';
import ReviewCard from '@/components/ReviewCard.vue';
import ReviewForm from '@/components/ReviewForm.vue';
import { mapGetters } from 'vuex';

export default {
  components: {
    RoomCard,
    ReviewCard,
    ReviewForm
  },
  data() {
    return {
      rooms: [],
      reviews: [],
      reviewToEdit: null,
      showReviewForm: false,
      isFavorite: false,
      reservationData: {
        check_in_date: '',
        check_out_date: '',
        room_ids: []
      },
      totalPrice: 0,
      currentImageIndex: 0,
      isToggling: false
    };
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'userRole', 'getUser', 'getPropertyDetails', 'getReviews']),
    property() {
      return this.getPropertyDetails;
    },
    isSuperAdmin() {
      return this.userRole === 'superadmin';
    },
    currentUser() {
      return this.getUser;
    },
    propertyImages() {
      let images = [];
      try {
        images = typeof this.property.images === 'string' ? JSON.parse(this.property.images) : this.property.images;
      } catch (error) {
        console.error('Error parsing property images:', error);
      }
      return images;
    },
    currentImage() {
      return this.propertyImages && this.propertyImages.length > 0
        ? `data:image/jpeg;base64,${this.propertyImages[this.currentImageIndex]}`
        : require('@/assets/default-image.png');
    }
  },
  async created() {
    await this.fetchPropertyDetails();
    await this.fetchReviews();
    if (this.isAuthenticated) {
      await this.fetchRooms();
      await this.checkIfFavorite();
    }
  },
  methods: {
  convertDateToBackendFormat(dateString) {
    const [year, month, day] = dateString.split('-');
    return `${day}-${month}-${year}`;
  },
  alertLogin() {
    alert('You must be logged in to book a room.');
  },
  roundedRating(value) {
    return Math.floor(value);
  },
  async fetchPropertyDetails() {
    try {
      await this.$store.dispatch('fetchPropertyDetails', this.$route.params.id);
    } catch (error) {
      console.error('Failed to fetch property details:', error);
    }
  },
  async fetchRooms() {
    if (this.reservationData.check_in_date && this.reservationData.check_out_date) {
      const params = {
        property_id: this.$route.params.id,
        check_in_date: this.reservationData.check_in_date,
        check_out_date: this.reservationData.check_out_date
      };
      try {
        const response = await this.$store.dispatch('fetchRooms', params);
        this.rooms = response;
      } catch (error) {
        console.error('Failed to fetch rooms:', error);
      }
    }
  },
  async fetchReviews() {
    try {
      await this.$store.dispatch('fetchReviews', this.$route.params.id);
      this.reviews = this.$store.getters.getReviews;
    } catch (error) {
      console.error('Failed to fetch reviews:', error);
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
  editReview(review) {
    this.reviewToEdit = review;
    this.showReviewForm = true;
  },
  toggleReviewForm() {
    this.showReviewForm = !this.showReviewForm;
    this.reviewToEdit = null; // Reset reviewToEdit when toggling the form
  },
  async handleReviewSubmitted() {
    await this.fetchReviews(); // Refetch reviews after submission
    await this.fetchPropertyDetails(); // Refresh property details, including reviews
    this.toggleReviewForm(); // Hide the review form after submission
  },
  async handleReviewDeleted() {
    await this.fetchReviews(); // Refetch reviews after deletion
    await this.fetchPropertyDetails(); // Refresh property details, including reviews
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
  updateTotalPrice() {
    const numberOfDays = this.calculateNumberOfDays(
      this.reservationData.check_in_date,
      this.reservationData.check_out_date
    );
    this.totalPrice = this.rooms
      .filter(room => this.reservationData.room_ids.includes(room.id))
      .reduce((sum, room) => sum + room.price * numberOfDays, 0);
  },
  calculateNumberOfDays(checkInDate, checkOutDate) {
    const checkIn = new Date(checkInDate);
    const checkOut = new Date(checkOutDate);
    const timeDifference = checkOut - checkIn;
    const dayInMilliseconds = 1000 * 60 * 60 * 24;
    return timeDifference / dayInMilliseconds;
  },
  async handleFormSubmit() {
    if (this.isAuthenticated) {
      await this.createReservation();
    } else {
      this.alertLogin();
    }
  },
  async createReservation() {
    try {
      const formattedCheckInDate = this.convertDateToBackendFormat(this.reservationData.check_in_date);
      const formattedCheckOutDate = this.convertDateToBackendFormat(this.reservationData.check_out_date);

      console.log('Sending reservation data:', {
        user_id: this.currentUser.id,
        property_id: this.property.id,
        check_in_date: formattedCheckInDate,
        check_out_date: formattedCheckOutDate,
        room_ids: this.reservationData.room_ids
      });

      const response = await this.$store.dispatch('createReservation', {
        user_id: this.currentUser.id,
        property_id: this.property.id,
        check_in_date: formattedCheckInDate,
        check_out_date: formattedCheckOutDate,
        room_ids: this.reservationData.room_ids
      });

      console.log('Reservation response:', response);

      // Redirect to the checkout URL
      window.location.href = response.checkout_url;
    } catch (error) {
      console.error('Failed to create reservation:', error);
    }
  },
  prevImage() {
    this.currentImageIndex = (this.currentImageIndex - 1 + this.propertyImages.length) % this.propertyImages.length;
  },
  nextImage() {
    this.currentImageIndex = (this.currentImageIndex + 1) % this.propertyImages.length;
  }
}
};
</script>

<style scoped>
.property-details {
  padding: 20px;
}
.property-title {
  text-align: center;
}
.property-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}
.property-info, .property-ratings {
  flex: 1;
  padding-right: 20px;
}
.property-image-wrapper {
  position: relative;
  flex: 1;
}
.property-details h1, h2 {
  margin: 10px 0;
}
.property-details p {
  margin: 5px 0;
}
.property-details ul {
  list-style-type: none;
  padding: 0;
}
.property-details ul li {
  background-color: #f0f0f0;
  padding: 5px;
  margin: 5px 0;
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
.carousel {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}
.carousel-image {
  width: 600px; /* Set your desired width */
  height: 450px; /* Set your desired height */
  object-fit: cover;
  margin: 0 10px;
}
.carousel-button {
  background-color: transparent;
  border: none;
  font-size: 24px;
  cursor: pointer;
}
.carousel-button:focus {
  outline: none;
}
.favorite-button {
  background-color: #ff4081;
  color: white;
  padding: 5px 10px;
  border: none;
  cursor: pointer;
  margin-top: 10px;
}
.favorite-button:hover {
  background-color: #e91e63;
}
</style>
