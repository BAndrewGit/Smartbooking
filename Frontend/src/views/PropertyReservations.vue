<template>
  <div>
    <h1>Reservations</h1>
    <div v-if="isOwner || isSuperAdmin">
      <label for="propertyFilter">Filter by Property:</label>
      <select v-model="selectedPropertyId" @change="filterReservations">
        <option value="">All Properties</option>
        <option v-for="property in properties" :key="property.id" :value="property.id">
          {{ property.name }}
        </option>
      </select>
    </div>
    <div v-if="filteredReservations.length">
      <div v-for="reservation in filteredReservations" :key="reservation.id" class="reservation-card">
        <h3>Property: {{ reservation.property_name }}</h3>
        <p>Check-in Date: {{ formatDate(reservation.check_in_date) }}</p>
        <p>Check-out Date: {{ formatDate(reservation.check_out_date) }}</p>
        <p>Status: {{ reservation.status }}</p>
        <h4>Rooms:</h4>
        <ul class="room-list">
          <li v-for="room in reservation.rooms" :key="room.id">
            {{ room.room_type }} - {{ room.price }} {{ room.currency }} ({{ room.persons }} persons)
          </li>
        </ul>
        <p><strong>Total Price: {{ reservation.total_price }} {{ reservation.rooms[0]?.currency || 'Currency' }}</strong></p>
        <button v-if="reservation.status !== 'cancelled' && !isOwner && !isSuperAdmin" @click="cancelReservation(reservation.id)">Cancel Reservation</button>
      </div>
    </div>
    <div v-else>
      <p>No reservations found.</p>
    </div>
    <div v-if="error">
      <p class="error-message">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  data() {
    return {
      selectedPropertyId: '',
      properties: [],
      filteredReservations: []
    };
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'userRole', 'getUser', 'getReservations', 'getError']),
    isSuperAdmin() {
      return this.userRole === 'superadmin';
    },
    isOwner() {
      return this.userRole === 'owner';
    },
    currentUser() {
      return this.getUser;
    },
    reservations() {
      return this.getReservations;
    },
    error() {
      return this.getError;
    }
  },
  watch: {
    reservations() {
      this.filterReservations();
    }
  },
  async created() {
    if (this.isSuperAdmin || this.isOwner) {
      await this.$store.dispatch('fetchReservations');
      await this.fetchProperties();
    } else {
      await this.$store.dispatch('fetchReservations');
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
    filterReservations() {
      if (this.selectedPropertyId) {
        this.filteredReservations = this.reservations.filter(reservation => reservation.property_id === parseInt(this.selectedPropertyId));
      } else {
        this.filteredReservations = this.reservations;
      }
      // Sort reservations by check-out date in descending order
      this.filteredReservations.sort((a, b) => new Date(b.check_out_date) - new Date(a.check_out_date));
    },
    async cancelReservation(reservationId) {
      if (confirm('Are you sure you want to cancel this reservation?')) {
        try {
          const response = await this.$store.dispatch('cancelReservation', reservationId);
          alert(response.message);
          await this.$store.dispatch('fetchReservations');
          this.$store.dispatch('clearError'); // Clear error after handling
        } catch (error) {
          console.error('Failed to cancel reservation:', error);
          alert(error.message || 'Failed to cancel reservation');
          this.$store.dispatch('clearError'); // Clear error after handling
        }
      }
    },
    formatDate(date) {
      return new Date(date).toLocaleDateString();
    }
  }
};
</script>

<style scoped>
.reservation-card {
  border: 1px solid #ddd;
  padding: 20px;
  margin-bottom: 10px;
  border-radius: 5px;
  background-color: #f9f9f9;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
button {
  margin-top: 10px;
  background-color: #ff9800; /* Orange color */
  color: white;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  border-radius: 5px;
}
button:hover {
  background-color: #e68a00;
}
.room-list {
  list-style: none;
  padding: 0;
}
.error-message {
  color: red;
}
</style>
