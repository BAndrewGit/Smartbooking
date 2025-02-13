<template>
  <div>
    <h1>Manage Rooms</h1>
    <div>
      <label for="propertyFilter">Filter by Property:</label>
      <select v-model="selectedPropertyId" @change="filterRooms">
        <option value="">All Properties</option>
        <option v-for="property in properties" :key="property.id" :value="property.id">
          {{ property.name }}
        </option>
      </select>
    </div>
    <div class="room-cards">
      <div v-for="room in filteredRooms" :key="room.id" class="room-card-wrapper">
        <RoomCard :room="room" isManageMode @edit-room="editRoom" @delete-room="deleteRoom" />
      </div>
    </div>
    <RoomForm v-if="isEditing" :roomData="selectedRoom" :isEditMode="true" @room-saved="handleRoomSaved" />
    <RoomForm v-if="!isEditing" :roomData="newRoomData" @room-saved="handleRoomSaved" />
  </div>
</template>

<script>
import RoomCard from '@/components/RoomCard.vue';
import RoomForm from '@/components/RoomForm.vue';

export default {
  components: {
    RoomCard,
    RoomForm
  },
  data() {
    return {
      rooms: [],
      properties: [],
      filteredRooms: [],
      isEditing: false,
      selectedRoom: null,
      newRoomData: {},
      selectedPropertyId: ''
    };
  },
  methods: {
    async fetchRooms() {
      try {
        const response = await this.$store.dispatch('fetchRooms');
        this.rooms = response;
        this.filterRooms();
      } catch (error) {
        console.error('Error fetching rooms:', error);
      }
    },
    async fetchProperties() {
      try {
        const response = await this.$store.dispatch('fetchOwnerProperties');
        this.properties = response;
      } catch (error) {
        console.error('Error fetching properties:', error);
      }
    },
    filterRooms() {
      if (this.selectedPropertyId) {
        this.filteredRooms = this.rooms.filter(room => room.property_id === parseInt(this.selectedPropertyId));
      } else {
        this.filteredRooms = this.rooms;
      }
    },
    editRoom(room) {
      this.selectedRoom = room;
      this.isEditing = true;
    },
    async deleteRoom(roomId) {
      try {
        await this.$store.dispatch('deleteRoom', roomId);
        await this.fetchRooms();
      } catch (error) {
        console.error('Error deleting room:', error);
      }
    },
    handleRoomSaved() {
      this.isEditing = false;
      this.selectedRoom = null;
      this.fetchRooms();
    }
  },
  async created() {
    await this.fetchProperties();
    await this.fetchRooms();
  }
};
</script>

<style scoped>
.room-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.room-card-wrapper {
  flex: 1 1 45%;
}
</style>
