<template>
  <div>
    <div>
      <button @click="toggleForm('login')">Login</button>
      <button @click="toggleForm('register')">Register</button>
    </div>
    <div v-if="currentForm === 'login'">
      <h2>Login</h2>
      <form @submit.prevent="performLogin">
        <div>
          <label for="loginEmail">Email:</label>
          <input type="email" id="loginEmail" v-model="email" required>
        </div>
        <div>
          <label for="loginPassword">Password:</label>
          <input type="password" id="loginPassword" v-model="password" required>
        </div>
        <button type="submit">Login</button>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
      <div>
        <p>Forgot your password? <a @click="showResetPassword = !showResetPassword">Reset it here</a></p>
        <form v-if="showResetPassword" @submit.prevent="handleForgotPassword">
          <div>
            <label for="resetEmail">Email:</label>
            <input type="email" id="resetEmail" v-model="resetEmail" required>
          </div>
          <button type="submit">Send Reset Link</button>
        </form>
      </div>
    </div>
    <div v-if="currentForm === 'register'">
      <h2>Register</h2>
      <form @submit.prevent="performRegister">
        <div>
          <label for="registerName">Name:</label>
          <input type="text" id="registerName" v-model="name" required>
        </div>
        <div>
          <label for="registerEmail">Email:</label>
          <input type="email" id="registerEmail" v-model="email" required>
        </div>
        <div>
          <label for="registerPassword">Password:</label>
          <input type="password" id="registerPassword" v-model="password" required>
        </div>
        <button type="submit">Register</button>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'LoginUser',
  data() {
    return {
      currentForm: 'login', 
      email: '',
      password: '',
      name: '',
      resetEmail: '',
      showResetPassword: false,
      error: ''
    };
  },
  methods: {
    ...mapActions(['login', 'register', 'forgotPassword']),
    toggleForm(form) {
      this.currentForm = form;
      this.error = ''; 
    },
    async performLogin() {
      try {
        await this.login({ email: this.email, password: this.password });
        this.$router.push('/');
      } catch (error) {
        if (error.response && error.response.data) {
          this.error = error.response.data.message || 'Failed to login';
        } else {
          this.error = 'Failed to login';
        }
        console.error('Failed to login:', error);
      }
    },
    async performRegister() {
      this.error = '';
      try {
        await this.register({ name: this.name, email: this.email, password: this.password });
        this.$router.push('/login');
      } catch (error) {
        if (error.response && error.response.data) {
          this.error = error.response.data.message || 'Failed to register';
        } else {
          this.error = 'Failed to register';
        }
        console.error('Failed to register:', error);
      }
    },
    async handleForgotPassword() {
      try {
        console.log('Sending reset link to:', this.resetEmail);
        await this.forgotPassword(this.resetEmail); 
        alert('If your email is registered, you will receive a password reset link');
      } catch (error) {
        console.error('Failed to send reset link:', error);
      }
    }
  }
};
</script>

<style scoped>
button {
  margin: 10px;
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
}

button:hover {
  background-color: #369971;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>
