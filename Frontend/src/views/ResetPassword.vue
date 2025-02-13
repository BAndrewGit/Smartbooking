<template>
  <div>
    <h2>Reset Password</h2>
    <form @submit.prevent="resetPassword">
      <div>
        <label for="password">New Password:</label>
        <input type="password" v-model="password" required>
      </div>
      <button type="submit">Reset Password</button>
    </form>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'ResetPassword',
  components: {},
  data() {
    return {
      password: ''
    };
  },
  methods: {
    async resetPassword() {
      const token = this.$route.params.token;
      try {
        await api.post(`/reset_password/${token}`, { password: this.password });
        alert('Password updated successfully');
        this.$router.push('/login');
      } catch (error) {
        console.error('Failed to reset password:', error);
        alert('The reset link is invalid or has expired');
      }
    }
  }
};
</script>

<style scoped>
/* Adaugă stilurile tale aici */
</style>
