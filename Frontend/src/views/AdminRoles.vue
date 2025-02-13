<template>
  <div class="admin-roles-container">
    <div class="admin-roles-content">
      <h1>Manage User Roles</h1>
      <form @submit.prevent="updateUserRole" class="admin-roles-form">
        <label for="username_or_email">Username or Email:</label>
        <input type="text" v-model="usernameOrEmail" required />

        <label for="role">New Role:</label>
        <select v-model="newRole" required>
          <option value="user">User</option>
          <option value="owner">Owner</option>
          <option value="superadmin">Superadmin</option>
        </select>

        <button type="submit">Update Role</button>
      </form>
      <p v-if="message">{{ message }}</p>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  data() {
    return {
      usernameOrEmail: '',
      newRole: 'user',
      message: '',
      error: ''
    };
  },
  methods: {
    async updateUserRole() {
      this.message = '';
      this.error = '';
      try {
        const response = await api.put('/admin/users/role', {
          username_or_email: this.usernameOrEmail,
          role: this.newRole
        });
        this.message = response.data.message;
      } catch (error) {
        this.error = error.response.data.message || 'Failed to update role';
      }
    }
  }
};
</script>

<style scoped>
.admin-roles-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  height: 100vh;
  padding-top: 50px; /* Adjust this value to move the form further down or up */
}

.admin-roles-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.admin-roles-form {
  display: flex;
  flex-direction: column;
  width: 300px;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 10px;
  background-color: #f9f9f9;
}

h1 {
  text-align: center;
  margin-bottom: 20px;
}

label {
  margin-top: 10px;
}

button {
  margin-top: 20px;
  padding: 10px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #369971;
}

.error {
  color: red;
  margin-top: 10px;
}

p {
  text-align: center;
}
</style>
