<template>
  <div class="room-form">
    <h2>{{ isEditMode ? 'Edit Room' : 'Add New Room' }}</h2>
    <form @submit.prevent="submitForm" class="form-container">
      <div class="form-group">
        <label for="property">Property</label>
        <select id="property" v-model="localRoomData.property_id">
          <option v-for="property in properties" :key="property.id" :value="property.id">
            {{ property.name }}
          </option>
        </select>
      </div>
      <div class="form-group">
        <label for="room_type">Room Type</label>
        <input type="text" id="room_type" v-model="localRoomData.room_type" required />
      </div>
      <div class="form-group">
        <label for="persons">Persons</label>
        <input type="number" id="persons" v-model="localRoomData.persons" required />
      </div>
      <div class="form-group">
        <label for="price">Price</label>
        <input type="number" id="price" v-model="localRoomData.price" required />
      </div>
      <div class="form-group">
        <label for="currency">Currency</label>
        <input type="text" id="currency" v-model="localRoomData.currency" required />
      </div>
      <div class="form-group facilities-group">
        <h3>Facilities</h3>
        <div class="facilities-grid">
          <div v-for="facility in facilities" :key="facility" class="facility-item">
            <input type="checkbox" :id="facility" v-model="localRoomData[facility]" />
            <label :for="facility">{{ facilityNames[facility] }}</label>
          </div>
        </div>
      </div>
      <div class="button-container">
        <button type="submit" :disabled="loading">{{ isEditMode ? 'Update Room' : 'Add Room' }}</button>
      </div>
    </form>
    <LoadingSpinner :loading="loading" />
  </div>
</template>

<script>
import LoadingSpinner from '@/components/LoadingSpinner.vue';

export default {
  components: {
    LoadingSpinner
  },
  props: {
    roomData: {
      type: Object,
      default: () => ({
        property_id: '',
        room_type: '',
        persons: 1,
        price: 0,
        currency: '',
        vedere_la_oras: false,
        menaj_zilnic: false,
        canale_prin_satelit: false,
        zona_de_luat_masa_in_aer_liber: false,
        cada: false,
        facilitati_de_calcat: false,
        izolare_fonica: false,
        terasa_la_soare: false,
        pardoseala_de_gresie_marmura: false,
        papuci_de_casa: false,
        uscator_de_rufe: false,
        animale_de_companie: false,
        incalzire: false,
        birou: false,
        mobilier_exterior: false,
        alarma_de_fum: false,
        vedere_la_gradina: false,
        cuptor: false,
        cuptor_cu_microunde: false,
        zona_de_relaxare: false,
        canapea: false,
        intrare_privata: false,
        fier_de_calcat: false,
        masina_de_cafea: false,
        plita_de_gatit: false,
        extinctoare: false,
        cana_fierbator: false,
        gradina: false,
        ustensile_de_bucatarie: false,
        masina_de_spalat: false,
        balcon: false,
        pardoseala_de_lemn_sau_parchet: false,
        aparat_pentru_prepararea_de_ceai_cafea: false,
        zona_de_luat_masa: false,
        canale_prin_cablu: false,
        aer_conditionat: false,
        masa: false,
        suport_de_haine: false,
        cada_sau_dus: false,
        frigider: false,
        mic_dejun: false,
      }),
    },
    isEditMode: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      localRoomData: { ...this.roomData },
      facilities: [
        'vedere_la_oras', 'menaj_zilnic', 'canale_prin_satelit', 'zona_de_luat_masa_in_aer_liber',
        'cada', 'facilitati_de_calcat', 'izolare_fonica', 'terasa_la_soare',
        'pardoseala_de_gresie_marmura', 'papuci_de_casa', 'uscator_de_rufe', 'animale_de_companie',
        'incalzire', 'birou', 'mobilier_exterior', 'alarma_de_fum', 'vedere_la_gradina', 'cuptor',
        'cuptor_cu_microunde', 'zona_de_relaxare', 'canapea', 'intrare_privata', 'fier_de_calcat',
        'masina_de_cafea', 'plita_de_gatit', 'extinctoare', 'cana_fierbator', 'gradina',
        'ustensile_de_bucatarie', 'masina_de_spalat', 'balcon', 'pardoseala_de_lemn_sau_parchet',
        'aparat_pentru_prepararea_de_ceai_cafea', 'zona_de_luat_masa', 'canale_prin_cablu',
        'aer_conditionat', 'masa', 'suport_de_haine', 'cada_sau_dus', 'frigider', 'mic_dejun'
      ],
      facilityNames: {
        vedere_la_oras: 'Vedere la oraș',
        menaj_zilnic: 'Menaj zilnic',
        canale_prin_satelit: 'Canale prin satelit',
        zona_de_luat_masa_in_aer_liber: 'Zonă de luat masa în aer liber',
        cada: 'Cadă',
        facilitati_de_calcat: 'Facilități de călcat',
        izolare_fonica: 'Izolare fonică',
        terasa_la_soare: 'Terasă la soare',
        pardoseala_de_gresie_marmura: 'Pardoseală de gresie/marmură',
        papuci_de_casa: 'Papuci de casă',
        uscator_de_rufe: 'Uscător de rufe',
        animale_de_companie: 'Animale de companie',
        incalzire: 'Încălzire',
        birou: 'Birou',
        mobilier_exterior: 'Mobilier exterior',
        alarma_de_fum: 'Alarmă de fum',
        vedere_la_gradina: 'Vedere la grădină',
        cuptor: 'Cuptor',
        cuptor_cu_microunde: 'Cuptor cu microunde',
        zona_de_relaxare: 'Zonă de relaxare',
        canapea: 'Canapea',
        intrare_privata: 'Intrare privată',
        fier_de_calcat: 'Fier de călcat',
        masina_de_cafea: 'Mașină de cafea',
        plita_de_gatit: 'Plită de gătit',
        extinctoare: 'Extinctoare',
        cana_fierbator: 'Cană fierbător',
        gradina: 'Grădină',
        ustensile_de_bucatarie: 'Ustensile de bucătărie',
        masina_de_spalat: 'Mașină de spălat',
        balcon: 'Balcon',
        pardoseala_de_lemn_sau_parchet: 'Pardoseală de lemn sau parchet',
        aparat_pentru_prepararea_de_ceai_cafea: 'Aparat pentru prepararea de ceai/cafea',
        zona_de_luat_masa: 'Zonă de luat masa',
        canale_prin_cablu: 'Canale prin cablu',
        aer_conditionat: 'Aer condiționat',
        masa: 'Masă',
        suport_de_haine: 'Suport de haine',
        cada_sau_dus: 'Cadă sau duș',
        frigider: 'Frigider',
        mic_dejun: 'Mic dejun'
      },
      properties: [],
      loading: false,
    };
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
    async submitForm() {
      this.loading = true;
      try {
        if (this.isEditMode) {
          await this.$store.dispatch('updateRoom', this.localRoomData);
        } else {
          await this.$store.dispatch('createRoom', this.localRoomData);
        }
        this.$emit('room-saved');
      } catch (error) {
        console.error('Error saving room:', error);
      } finally {
        this.loading = false;
      }
    },
  },
  async created() {
    await this.fetchProperties();
  },
  watch: {
    roomData(newRoomData) {
      this.localRoomData = { ...newRoomData };
    }
  }
};
</script>

<style scoped>
.room-form {
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

.facilities-group {
  flex: 1 1 100%;
}

.facilities-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  padding: 10px;
}

.facility-item {
  display: flex;
  align-items: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.facility-item input {
  margin-right: 10px;
}

.button-container {
  display: flex;
  justify-content: center;
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

button:disabled {
  background-color: #bbb;
  cursor: not-allowed;
}
</style>
