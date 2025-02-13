<template>
  <div>
    <h2>{{ isEditMode ? 'Edit Review' : 'Add a Review' }}</h2>
    <form @submit.prevent="submitReview">
      <div>
        <label for="reviewText">Review:</label>
        <textarea id="reviewText" v-model="localReview.review_text" required></textarea>
      </div>
      <div>
        <label for="ratingPersonal">Personal Rating:</label>
        <input type="number" id="ratingPersonal" v-model="localReview.rating_personal" min="0" max="10" required>
      </div>
      <div>
        <label for="ratingFacilities">Facilities Rating:</label>
        <input type="number" id="ratingFacilities" v-model="localReview.rating_facilities" min="0" max="10" required>
      </div>
      <div>
        <label for="ratingCleanliness">Cleanliness Rating:</label>
        <input type="number" id="ratingCleanliness" v-model="localReview.rating_cleanliness" min="0" max="10" required>
      </div>
      <div>
        <label for="ratingComfort">Comfort Rating:</label>
        <input type="number" id="ratingComfort" v-model="localReview.rating_comfort" min="0" max="10" required>
      </div>
      <div>
        <label for="ratingValueForMoney">Value for Money Rating:</label>
        <input type="number" id="ratingValueForMoney" v-model="localReview.rating_value_for_money" min="0" max="10" required>
      </div>
      <div>
        <label for="ratingLocation">Location Rating:</label>
        <input type="number" id="ratingLocation" v-model="localReview.rating_location" min="0" max="10" required>
      </div>
      <div>
        <label for="ratingWifi">Wi-Fi Rating:</label>
        <input type="number" id="ratingWifi" v-model="localReview.rating_wifi" min="0" max="10" required>
      </div>
      <button type="submit">{{ isEditMode ? 'Update Review' : 'Submit Review' }}</button>
    </form>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  props: {
    propertyId: {
      type: Number,
      required: true
    },
    review: {
      type: Object,
      default: () => ({
        review_text: '',
        rating_personal: 0,
        rating_facilities: 0,
        rating_cleanliness: 0,
        rating_comfort: 0,
        rating_value_for_money: 0,
        rating_location: 0,
        rating_wifi: 0
      })
    }
  },
  data() {
    return {
      isEditMode: !!this.review?.id,
      localReview: {
        review_text: this.review?.review_text || '',
        rating_personal: this.review?.rating_personal || 0,
        rating_facilities: this.review?.rating_facilities || 0,
        rating_cleanliness: this.review?.rating_cleanliness || 0,
        rating_comfort: this.review?.rating_comfort || 0,
        rating_value_for_money: this.review?.rating_value_for_money || 0,
        rating_location: this.review?.rating_location || 0,
        rating_wifi: this.review?.rating_wifi || 0,
        property_id: this.propertyId
      }
    };
  },
  methods: {
    async submitReview() {
      try {
        if (this.isEditMode) {
          await api.put(`/reviews/${this.review.id}`, this.localReview);
        } else {
          await api.post('/reviews', this.localReview);
        }
        this.$emit('review-submitted');
        this.clearForm();
      } catch (error) {
        console.error('Error submitting review:', error);
      }
    },
    clearForm() {
      this.localReview = {
        review_text: '',
        rating_personal: 0,
        rating_facilities: 0,
        rating_cleanliness: 0,
        rating_comfort: 0,
        rating_value_for_money: 0,
        rating_location: 0,
        rating_wifi: 0,
        property_id: this.propertyId
      };
    }
  },
  watch: {
    review(newReview) {
      this.localReview = {
        review_text: newReview?.review_text || '',
        rating_personal: newReview?.rating_personal || 0,
        rating_facilities: newReview?.rating_facilities || 0,
        rating_cleanliness: newReview?.rating_cleanliness || 0,
        rating_comfort: newReview?.rating_comfort || 0,
        rating_value_for_money: newReview?.rating_value_for_money || 0,
        rating_location: newReview?.rating_location || 0,
        rating_wifi: newReview?.rating_wifi || 0,
        property_id: this.propertyId
      };
      this.isEditMode = !!newReview?.id;
    }
  }
};
</script>

<style scoped>
/* Add your styles here */
</style>
