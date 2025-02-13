<template>
  <div class="preferences-slider">
    <h2>Set Your Preferences</h2>
    <form @submit.prevent="submitPreferences">
      <div v-for="(value, key) in preferences" :key="key" class="slider-container">
        <label :for="key">{{ getLabel(key) }}</label>
        <input type="range" :id="key" v-model="preferences[key]" min="0" max="10" step="1" @input="updateTotal" />
        <span>{{ preferences[key] }}</span>
      </div>
      <p>Total Score: {{ totalScore }}</p>
      <p v-if="totalScore > 44" class="error">Total score must be less than or equal to 44.</p>
      <button type="submit" :disabled="totalScore > 44">Submit</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      preferences: {
        rating_personal: 0,
        rating_facilities: 0,
        rating_cleanliness: 0,
        rating_comfort: 0,
        rating_value_for_money: 0,
        rating_location: 0,
        rating_wifi: 0
      },
      totalScore: 0
    };
  },
  methods: {
    getLabel(key) {
      const labels = {
        rating_personal: 'Personal',
        rating_facilities: 'Facilities',
        rating_cleanliness: 'Cleanliness',
        rating_comfort: 'Comfort',
        rating_value_for_money: 'Value for Money',
        rating_location: 'Location',
        rating_wifi: 'Wi-Fi'
      };
      return labels[key];
    },
    updateTotal() {
      this.totalScore = Object.values(this.preferences).reduce((acc, val) => acc + val, 0);
    },
    async submitPreferences() {
      try {
        const response = await axios.post('/user/preferences', this.preferences, {
          headers: {
            Authorization: `Bearer ${this.$store.state.token}`
          }
        });
        alert('Preferences saved successfully!');
      } catch (error) {
        console.error('Error saving preferences:', error.response.data);
        alert('Error saving preferences. Please try again.');
      }
    }
  }
};
</script>

<style scoped>
.preferences-slider {
  padding: 20px;
}

.slider-container {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 5px;
}

input[type="range"] {
  width: 100%;
}

.error {
  color: red;
}
</style>
