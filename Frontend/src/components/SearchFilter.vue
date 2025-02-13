<template>
  <div class="search-filter">
    <form @submit.prevent="searchProperties" class="search-form">
      <div class="form-group">
        <label for="checkIn">Check-In:</label>
        <input type="date" id="checkIn" v-model="filters.check_in" required>
      </div>
      <div class="form-group">
        <label for="checkOut">Check-Out:</label>
        <input type="date" id="checkOut" v-model="filters.check_out" required>
      </div>
      <div class="form-group">
        <label for="numPersons">Number of Persons:</label>
        <input type="number" id="numPersons" v-model="filters.num_persons" required min="1">
      </div>
      <div class="form-group">
        <label for="region">Region:</label>
        <input type="text" id="region" v-model="filters.region">
      </div>
      <div class="form-group">
        <label for="priceMax">Maximum Price:</label>
        <input type="number" id="priceMax" v-model="filters.price_max" step="50" min="0">
      </div>
      <div class="form-group">
        <label for="sortBy">Sort By:</label>
        <select id="sortBy" v-model="filters.sort_by">
          <option value="default">Default</option>
          <option value="price_asc">Price: Low to High</option>
          <option value="price_desc">Price: High to Low</option>
          <option value="rating_avg">Rating</option>
        </select>
      </div>
      <div class="form-group">
        <label>Facilities:</label>
        <div class="dropdown">
          <button type="button" class="dropbtn">Select Facilities</button>
          <div class="dropdown-content">
            <div class="facilities-grid">
              <div v-for="facility in getSortedFacilities()" :key="facility" class="facility-item">
                <input type="checkbox" :id="facility" :value="facility" v-model="filters.facilities">
                <label :for="facility">{{ facilityNames[facility] }}</label>
              </div>
            </div>
          </div>
        </div>
      </div>
      <button type="submit">Search</button>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      filters: {
        check_in: '',
        check_out: '',
        num_persons: 1,
        region: '',
        price_max: null,
        sort_by: 'default',
        facilities: []
      },
      facilities: [
        'vedere_la_oras', 'menaj_zilnic', 'canale_prin_satelit', 'zona_de_luat_masa_in_aer_liber', 'cada', 'facilitati_de_calcat',
        'izolare_fonica', 'terasa_la_soare', 'pardoseala_de_gresie_marmura', 'papuci_de_casa', 'uscator_de_rufe', 'animale_de_companie',
        'incalzire', 'birou', 'mobilier_exterior', 'alarma_de_fum', 'vedere_la_gradina', 'cuptor', 'cuptor_cu_microunde', 'zona_de_relaxare',
        'canapea', 'intrare_privata', 'fier_de_calcat', 'masina_de_cafea', 'plita_de_gatit', 'extinctoare', 'cana_fierbator', 'gradina',
        'ustensile_de_bucatarie', 'masina_de_spalat', 'balcon', 'pardoseala_de_lemn_sau_parchet', 'aparat_pentru_prepararea_de_ceai_cafea',
        'zona_de_luat_masa', 'canale_prin_cablu', 'aer_conditionat', 'masa', 'suport_de_haine', 'cada_sau_dus', 'frigider', 'mic_dejun'
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
      }
    };
  },
  methods: {
    getSortedFacilities() {
      return this.facilities.slice().sort((a, b) => this.facilityNames[a].localeCompare(this.facilityNames[b]));
    },
    formatDateToBackend(date) {
      if (!date) return '';
      const [year, month, day] = date.split('-');
      return `${day}-${month}-${year}`;
    },
    parseDateFromBackend(date) {
      if (!date) return '';
      const [day, month, year] = date.split('-');
      return `${year}-${month}-${day}`;
    },
    searchProperties() {
      // Filtrăm facilitățile pentru a elimina elementele goale
      const filteredFacilities = this.filters.facilities.filter(facility => facility.trim() !== '');

      this.$router.push({
        name: 'SearchProperties',
        query: {
          check_in: this.formatDateToBackend(this.filters.check_in),
          check_out: this.formatDateToBackend(this.filters.check_out),
          num_persons: this.filters.num_persons,
          region: this.filters.region,
          price_max: this.filters.price_max,
          sort_by: this.filters.sort_by,
          facilities: filteredFacilities.join(',')
        }
      });
    }
  },
  watch: {
    '$route.query': {
      handler(newQuery) {
        if (newQuery.check_in) {
          this.filters.check_in = this.parseDateFromBackend(newQuery.check_in);
        }
        if (newQuery.check_out) {
          this.filters.check_out = this.parseDateFromBackend(newQuery.check_out);
        }
        if (newQuery.num_persons) {
          this.filters.num_persons = parseInt(newQuery.num_persons, 10);
        }
        if (newQuery.region) {
          this.filters.region = newQuery.region;
        }
        if (newQuery.price_max) {
          this.filters.price_max = parseFloat(newQuery.price_max);
        }
        if (newQuery.sort_by) {
          this.filters.sort_by = newQuery.sort_by;
        }
        if (newQuery.facilities) {
          this.filters.facilities = newQuery.facilities.split(',');
        }
      },
      immediate: true
    }
  }
};
</script>

<style scoped>
.search-filter {
  width: 98%;
  padding: 20px;
  background-color: #f9f9f9;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
}

.form-group {
  flex: 1;
  min-width: 150px;
  margin: 10px;
  display: flex;
  flex-direction: column;
}

input, select, button {
  width: 100%;
  padding: 10px;
  box-sizing: border-box;
}

button {
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
  margin-top: 10px;
}

button:hover {
  background-color: #369971;
}

.dropdown {
  position: relative;
  display: inline-block;
  width: 100%;
}

.dropbtn {
  background-color: #42b983;
  color: white;
  padding: 10px;
  border: none;
  cursor: pointer;
  width: 100%;
}

.dropdown-content {
  display: none;
  position: absolute;
  background-color: #f9f9f9;
  box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
  z-index: 1;
  width: 400%;
  left: -300%;
}

.dropdown:hover .dropdown-content {
  display: block;
}

.facilities-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
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
</style>
