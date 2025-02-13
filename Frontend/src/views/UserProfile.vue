<template>
  <div class="user-profile">
    <h1>Profil</h1>
    <div v-if="user">
      <form @submit.prevent="updateProfile" class="profile-form">
        <div class="form-group">
          <label for="name">Nume:</label>
          <input type="text" id="name" v-model="user.name" required>
        </div>
        <div class="form-group">
          <label for="email">Email:</label>
          <input type="email" id="email" v-model="user.email" required>
        </div>
        <div class="form-group">
          <label for="role">Rol:</label>
          <input type="text" id="role" v-model="user.role" disabled>
        </div>
        <button type="submit">Actualizează Profilul</button>
      </form>
      <button class="delete-button" @click="deleteProfile">Șterge Profilul</button>
    </div>
    <h2>Preferințe</h2>
    <form @submit.prevent="updatePreferences" class="preferences-form">
      <div class="form-group" v-for="(value, key) in preferences" :key="key">
        <label :for="key">{{ translatedKeys[key] }}:</label>
        <input type="range" :id="key" v-model.number="preferences[key]" min="0" max="10" @input="checkTotal">
        <span>{{ preferences[key] }}</span>
      </div>
      <div v-if="totalScore > 44" class="error">Scorul total depășește 44</div>
      <button type="submit" :disabled="totalScore > 44">Actualizează Preferințele</button>
    </form>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import api from '@/services/api'; // Importă api.js

export default {
  name: 'UserProfile',
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
      totalScore: 0,
      translatedKeys: {
        rating_personal: 'Personal',
        rating_facilities: 'Facilități',
        rating_cleanliness: 'Curățenie',
        rating_comfort: 'Confort',
        rating_value_for_money: 'Raport calitate/preț',
        rating_location: 'Locație',
        rating_wifi: 'Wi-Fi'
      }
    };
  },
  computed: {
    ...mapGetters(['getUser']),
    user() {
      return this.getUser;
    }
  },
  created() {
    this.fetchUser();
    this.fetchPreferences();
  },
  methods: {
    ...mapActions(['fetchUser', 'updateUser', 'deleteUser']),
    async updateProfile() {
      try {
        await this.updateUser(this.user);
        await this.fetchUser(); // Refetch user after updating profile
      } catch (error) {
        console.error('Eroare la actualizarea profilului:', error);
      }
    },
    async deleteProfile() {
      try {
        await this.deleteUser();
        this.$router.push('/register');
      } catch (error) {
        console.error('Eroare la ștergerea profilului:', error);
      }
    },
    async fetchPreferences() {
      try {
        const response = await api.get('/user/preferences');
        this.preferences = {
          rating_personal: response.data.rating_personal,
          rating_facilities: response.data.rating_facilities,
          rating_cleanliness: response.data.rating_cleanliness,
          rating_comfort: response.data.rating_comfort,
          rating_value_for_money: response.data.rating_value_for_money,
          rating_location: response.data.rating_location,
          rating_wifi: response.data.rating_wifi
        };
        this.checkTotal();
      } catch (error) {
        console.error('Eroare la preluarea preferințelor:', error);
      }
    },
    async updatePreferences() {
      try {
        console.log('Sending preferences:', this.preferences);
        await api.put('/user/preferences', this.preferences);
        await this.fetchPreferences(); // Refetch preferences after updating
      } catch (error) {
        console.error('Eroare la actualizarea preferințelor:', error);
      }
    },
    checkTotal() {
      this.totalScore = Object.values(this.preferences).reduce((a, b) => a + b, 0);
    }
  }
};
</script>

<style scoped>
.user-profile {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 10px;
}

h1, h2 {
  text-align: center;
  margin-bottom: 20px;
}

.profile-form, .preferences-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 5px;
}

input[type="text"],
input[type="email"],
input[type="range"] {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}

input[type="range"] {
  margin-bottom: 5px;
}

button {
  padding: 10px 20px;
  background-color: #42b983;
  border: none;
  color: white;
  cursor: pointer;
  margin-top: 10px;
}

button:disabled {
  background-color: grey;
  cursor: not-allowed;
}

.delete-button {
  background-color: red;
}

.error {
  color: red;
  text-align: center;
}
</style>
