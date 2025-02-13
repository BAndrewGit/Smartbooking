<template>
  <div class="review-card">
    <div class="review-content">
      <div class="review-text">
        <p>{{ review.review_text }}</p>
      </div>
      <div class="review-ratings">
        <p><strong>Personal:</strong> <span>{{ review.rating_personal }}</span></p>
        <p><strong>Facilities:</strong> <span>{{ review.rating_facilities }}</span></p>
        <p><strong>Cleanliness:</strong> <span>{{ review.rating_cleanliness }}</span></p>
        <p><strong>Comfort:</strong> <span>{{ review.rating_comfort }}</span></p>
        <p><strong>Value for Money:</strong> <span>{{ review.rating_value_for_money }}</span></p>
        <p><strong>Location:</strong> <span>{{ review.rating_location }}</span></p>
        <p><strong>Wi-Fi:</strong> <span>{{ review.rating_wifi }}</span></p>
      </div>
      <div class="review-user">
        <p><strong>Posted by:</strong> {{ review.user_name }}</p>
        <div v-if="showActions" class="review-actions">
          <button v-if="canEdit" @click="$emit('edit-review', review)" class="edit-button">Edit</button>
          <button v-if="canDelete" @click="deleteReview" class="delete-button">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import api from '@/services/api';

export default {
  props: {
    review: {
      type: Object,
      required: true
    },
    showActions: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    ...mapGetters(['userRole', 'getUser']),
    userId() {
      return this.getUser ? this.getUser.id : null;
    },
    canEdit() {
      return this.review.user_id === this.userId;
    },
    canDelete() {
      return this.review.user_id === this.userId || this.userRole === 'superadmin';
    }
  },
  methods: {
    async deleteReview() {
      try {
        await api.delete(`/reviews/${this.review.id}`);
        this.$emit('review-deleted');
      } catch (error) {
        console.error('Error deleting review:', error);
      }
    }
  }
};
</script>

<style scoped>
.review-card {
  border: 1px solid #ddd;
  padding: 16px;
  margin: 16px 0;
  display: flex;
  flex-direction: column;
  font-family: Arial, sans-serif;
}

.review-content {
  display: flex;
  justify-content: space-between;
}

.review-text {
  flex: 1;
  margin-right: 20px;
}

.review-ratings {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.review-ratings p {
  margin: 2px 0;
}

.review-user {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.review-actions {
  display: flex;
  flex-direction: column;
  margin-top: 10px;
}

button {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  margin-right: 10px;
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
  margin-bottom: 5px;
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
