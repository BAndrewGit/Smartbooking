<template>
  <div v-if="userRole !== 'superadmin'" class="property-form">
    <h2>{{ isEditMode ? 'Edit Property' : 'Add New Property' }}</h2>
    <form @submit.prevent="handleSubmit" class="form-container">
      <div class="form-group full-width">
        <label for="name">Name</label>
        <input type="text" id="name" v-model="localProperty.name" required />
      </div>
      <div class="form-group">
        <label for="address">Address</label>
        <input type="text" id="address" v-model="localProperty.address" required />
      </div>
      <div class="form-group">
        <label for="postal_code">Postal Code</label>
        <input type="text" id="postal_code" v-model="localProperty.postal_code" />
      </div>
      <div class="form-group">
        <label for="country">Country</label>
        <input type="text" id="country" v-model="localProperty.country" />
      </div>
      <div class="form-group">
        <label for="region">Region</label>
        <input type="text" id="region" v-model="localProperty.region" />
      </div>
      <div class="form-group">
        <label for="latitude">Latitude</label>
        <input type="number" step="0.0001" id="latitude" v-model="localProperty.latitude" />
      </div>
      <div class="form-group">
        <label for="longitude">Longitude</label>
        <input type="number" step="0.0001" id="longitude" v-model="localProperty.longitude" />
      </div>
      <div class="form-group">
        <label for="check_in">Check In</label>
        <input type="text" id="check_in" v-model="localProperty.check_in" />
      </div>
      <div class="form-group">
        <label for="check_out">Check Out</label>
        <input type="text" id="check_out" v-model="localProperty.check_out" />
      </div>
      <div class="form-group">
        <label for="stars">Stars</label>
        <input type="number" id="stars" max="5" v-model="localProperty.stars" />
      </div>
      <div class="form-group">
        <label for="type">Type</label>
        <select id="type" v-model="localProperty.type">
          <option v-for="(label, value) in propertyTypes" :key="value" :value="value">
            {{ label }}
          </option>
        </select>
      </div>
      <div class="form-group full-width">
        <label for="description">Description</label>
        <textarea id="description" v-model="localProperty.description"></textarea>
      </div>
      <div class="form-group full-width">
        <label for="images">Images</label>
        <input type="file" id="images" ref="imagesInput" @change="handleImageUpload" multiple />
        <div class="image-preview" v-if="imagePreviews.length">
          <div v-for="(image, index) in imagePreviews" :key="index" class="image-thumbnail">
            <img :src="image" alt="Property Image" />
            <button @click="removeImage(index)">Remove</button>
          </div>
        </div>
      </div>
      <div class="button-container">
        <button type="submit">{{ isEditMode ? 'Update Property' : 'Add Property' }}</button>
        <button v-if="isEditMode" type="button" class="cancel-button" @click="cancelEdit">Cancel</button>
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    propertyData: {
      type: Object,
      default: () => ({}),
    },
    isEditMode: {
      type: Boolean,
      default: false,
    },
    userRole: {
      type: String,
      required: true
    },
  },
  data() {
    return {
      localProperty: {
        name: '',
        address: '',
        postal_code: '',
        country: '',
        region: '',
        latitude: null,
        longitude: null,
        check_in: '',
        check_out: '',
        stars: null,
        type: '',
        description: '',
        images: [],
      },
      propertyTypes: {
        hotel: 'Hotel',
        apartment: 'Apartment',
        guest_house: 'Guest House',
        bed_and_breakfast: 'Bed and Breakfast',
        aparthotel: 'Aparthotel',
        holiday_home: 'Holiday Home',
        lodge: 'Lodge',
        camping: 'Camping',
        homestay: 'Homestay',
        villa: 'Villa',
        country_house: 'Country House',
        resort: 'Resort',
        chalet: 'Chalet',
        motel: 'Motel',
        holiday_park: 'Holiday Park',
        capsule_hotel: 'Capsule Hotel',
        inn: 'Inn',
        boat: 'Boat',
        farm_holiday: 'Farm Holiday',
        hostel: 'Hostel',
        camp: 'Camp',
      },
      imageFiles: [],
      imagePreviews: [],
    };
  },
  mounted() {
    if (this.isEditMode && this.propertyData) {
      this.localProperty = { ...this.propertyData };
      this.imagePreviews = Array.isArray(this.localProperty.images) ? this.localProperty.images.map(image => `data:image/jpeg;base64,${image}`) : [];
    }
  },
  methods: {
    async handleSubmit() {
      const propertyData = { ...this.localProperty };

      // Convert images to base64 strings
      const imageBase64Strings = await Promise.all(this.imageFiles.map(file => this.convertToBase64(file)));
      propertyData.images = imageBase64Strings;

      try {
        const url = this.isEditMode 
          ? `http://127.0.0.1:5000/properties/${this.localProperty.id}` 
          : 'http://127.0.0.1:5000/properties';

        const method = this.isEditMode ? 'put' : 'post';

        console.log(`Making ${method.toUpperCase()} request to ${url} with data:`, propertyData);

        await axios({
          method: method,
          url: url,
          data: propertyData,
          headers: {
            Authorization: `Bearer ${this.$store.state.token}`,
            'Content-Type': 'application/json',
          },
        });

        this.isEditMode 
          ? this.$emit('property-updated')
          : this.$emit('property-added');

        alert('Property saved successfully!');
        this.resetForm(); // Reset the form after submission
      } catch (error) {
        console.error('Error saving property:', error.response ? error.response.data : error.message);
        alert('Error saving property. Please try again.');
      }
    },
    async convertToBase64(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = error => reject(error);
        reader.readAsDataURL(file);
      });
    },
    handleImageUpload(event) {
      const files = Array.from(event.target.files);
      this.imageFiles.push(...files);
      files.forEach((file) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.imagePreviews.push(e.target.result);
        };
        reader.readAsDataURL(file);
      });
    },
    removeImage(index) {
      this.imagePreviews.splice(index, 1);
      this.imageFiles.splice(index, 1);
    },
    cancelEdit() {
      this.$emit('cancel-edit');
      this.resetForm(); // Reset the form when canceling edit
    },
    resetForm() {
      this.localProperty = {
        name: '',
        address: '',
        postal_code: '',
        country: '',
        region: '',
        latitude: null,
        longitude: null,
        check_in: '',
        check_out: '',
        stars: null,
        type: '',
        description: '',
        images: [],
      };
      this.imageFiles = [];
      this.imagePreviews = [];
      if (this.$refs.imagesInput) {
        this.$refs.imagesInput.value = null; // Reset file input
      }
    }
  },
  watch: {
    propertyData(newPropertyData) {
      this.localProperty = { ...newPropertyData };
      this.imagePreviews = Array.isArray(this.localProperty.images) ? this.localProperty.images.map(image => `data:image/jpeg;base64,${image}`) : [];
    }
  }
};
</script>

<style scoped>
.property-form {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 10px;
  max-width: 800px;
  margin: 20px auto;
}

h2 {
  text-align: center;
  margin-bottom: 20px;
}

.form-container {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
}

.form-group {
  flex: 1 1 45%;
  min-width: 200px;
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
}

.full-width {
  flex: 1 1 100%;
}

.button-container {
  display: flex;
  justify-content: space-between;
  width: 100%;
}

button {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  border-radius: 5px;
  margin-top: 20px;
}

button:hover {
  background-color: #369971;
}

.cancel-button {
  background-color: #dc3545;
}

.cancel-button:hover {
  background-color: #c82333;
}

.image-preview {
  display: flex;
  flex-wrap: wrap;
}

.image-thumbnail {
  position: relative;
  margin-right: 10px;
}

.image-thumbnail img {
  width: 100px;
  height: 100px;
  object-fit: cover;
}

.image-thumbnail button {
  position: absolute;
  top: 0;
  right: 0;
  background: red;
  color: white;
  border: none;
  cursor: pointer;
}
</style>
