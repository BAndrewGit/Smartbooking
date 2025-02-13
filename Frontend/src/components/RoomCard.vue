<template>
  <div class="room-card">
    <h3>{{ room.room_type }} - {{ room.persons }} persoane</h3>
    <p>Preț: {{ room.price }} {{ room.currency }}</p>
    <p :class="priceRatingClass">{{ room.price_rating }}</p>

    <ul class="facilities-list">
      <li v-if="room.vedere_la_oras">Vedere la oraș</li>
      <li v-if="room.menaj_zilnic">Menaj zilnic</li>
      <li v-if="room.canale_prin_satelit">Canale prin satelit</li>
      <li v-if="room.zona_de_luat_masa_in_aer_liber">Zonă de luat masa în aer liber</li>
      <li v-if="room.cada">Cadă</li>
      <li v-if="room.facilitati_de_calcat">Facilități de călcat</li>
      <li v-if="room.izolare_fonica">Izolare fonică</li>
      <li v-if="room.terasa_la_soare">Terasă la soare</li>
      <li v-if="room.pardoseala_de_gresie_marmura">Pardoseală de gresie/marmură</li>
      <li v-if="room.papuci_de_casa">Papuci de casă</li>
      <li v-if="room.uscator_de_rufe">Uscător de rufe</li>
      <li v-if="room.animale_de_companie">Animale de companie permise</li>
      <li v-if="room.incalzire">Încălzire</li>
      <li v-if="room.birou">Birou</li>
      <li v-if="room.mobilier_exterior">Mobilier exterior</li>
      <li v-if="room.alarma_de_fum">Alarmă de fum</li>
      <li v-if="room.vedere_la_gradina">Vedere la grădină</li>
      <li v-if="room.cuptor">Cuptor</li>
      <li v-if="room.cuptor_cu_microunde">Cuptor cu microunde</li>
      <li v-if="room.zona_de_relaxare">Zonă de relaxare</li>
      <li v-if="room.canapea">Canapea</li>
      <li v-if="room.intrare_privata">Intrare privată</li>
      <li v-if="room.fier_de_calcat">Fier de călcat</li>
      <li v-if="room.masina_de_cafea">Mașină de cafea</li>
      <li v-if="room.plita_de_gatit">Plită de gătit</li>
      <li v-if="room.extinctoare">Extinctoare</li>
      <li v-if="room.cana_fierbator">Cană fierbător</li>
      <li v-if="room.gradina">Grădină</li>
      <li v-if="room.ustensile_de_bucatarie">Ustensile de bucătărie</li>
      <li v-if="room.masina_de_spalat">Mașină de spălat</li>
      <li v-if="room.balcon">Balcon</li>
      <li v-if="room.pardoseala_de_lemn_sau_parchet">Pardoseală de lemn sau parchet</li>
      <li v-if="room.aparat_pentru_prepararea_de_ceai_cafea">Aparat pentru prepararea de ceai/cafea</li>
      <li v-if="room.zona_de_luat_masa">Zonă de luat masa</li>
      <li v-if="room.canale_prin_cablu">Canale prin cablu</li>
      <li v-if="room.aer_conditionat">Aer condiționat</li>
      <li v-if="room.masa">Masă</li>
      <li v-if="room.suport_de_haine">Suport de haine</li>
      <li v-if="room.cada_sau_dus">Cadă sau duș</li>
      <li v-if="room.frigider">Frigider</li>
      <li v-if="room.mic_dejun">Mic dejun inclus</li>
    </ul>

    <div v-if="isManageMode">
      <button @click="editRoom" class="edit-button">Edit</button>
      <button @click="deleteRoom" class="delete-button">Delete</button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    room: {
      type: Object,
      required: true
    },
    isManageMode: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    priceRatingClass() {
      switch (this.room.price_rating) {
        case 'Very good price':
          return 'price-very-good';
        case 'Good price':
          return 'price-good';
        case 'Fair price':
          return 'price-fair';
        case 'Increased price':
          return 'price-increased';
        case 'High price':
          return 'price-high';
        default:
          return '';
      }
    }
  },
  methods: {
    editRoom() {
      this.$emit('edit-room', this.room);
    },
    deleteRoom() {
      this.$emit('delete-room', this.room.id);
    }
  }
};
</script>

<style scoped>
.room-card {
  border: 1px solid #ccc;
  padding: 20px;
  margin-bottom: 10px;
  font-family: Arial, sans-serif;
}

.price-very-good {
  color: green;
  background-color: #eaffea;
  padding: 5px;
}

.price-good {
  color: lightgreen;
  background-color: #f0fff0;
  padding: 5px;
}

.price-fair {
  color: rgb(232, 202, 5);
  background-color: #ffffe1;
  padding: 5px;
}

.price-increased {
  color: orange;
  background-color: #fff5e0;
  padding: 5px;
}

.price-high {
  color: red;
  background-color: #ffeaea;
  padding: 5px;
}

.facilities-list {
  column-count: 2;
  column-gap: 20px;
  list-style-type: none;
  padding: 0;
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
