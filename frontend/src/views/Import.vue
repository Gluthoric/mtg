<template>
  <div class="import">
    <h1>Import Cards</h1>

    <div class="import-section">
      <h2>Import Single Card</h2>
      <form @submit.prevent="importSingleCard">
        <div>
          <label for="scryfallId">Scryfall ID:</label>
          <input v-model="singleCard.scryfallId" id="scryfallId" required>
        </div>
        <div>
          <label for="quantity">Quantity:</label>
          <input v-model.number="singleCard.quantity" id="quantity" type="number" min="1" required>
        </div>
        <div>
          <label for="foil">Foil:</label>
          <input v-model="singleCard.foil" id="foil" type="checkbox">
        </div>
        <div>
          <label for="destination">Destination:</label>
          <select v-model="singleCard.destination" id="destination" required>
            <option value="collection">Collection</option>
            <option value="kiosk">Kiosk</option>
          </select>
        </div>
        <button type="submit">Import Card</button>
      </form>
    </div>

    <div class="import-section">
      <h2>Import from CSV</h2>
      <form @submit.prevent="importFromCSV">
        <div>
          <label for="csvFile">CSV File:</label>
          <input type="file" id="csvFile" @change="handleFileUpload" accept=".csv" required>
        </div>
        <div>
          <label for="csvDestination">Destination:</label>
          <select v-model="csvImport.destination" id="csvDestination" required>
            <option value="collection">Collection</option>
            <option value="kiosk">Kiosk</option>
          </select>
        </div>
        <button type="submit">Import CSV</button>
      </form>
    </div>

    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'

export default {
  name: 'Import',
  setup() {
    const singleCard = ref({
      scryfallId: '',
      quantity: 1,
      foil: false,
      destination: 'collection'
    })

    const csvImport = ref({
      file: null,
      destination: 'collection'
    })

    const message = ref('')
    const messageType = ref('')

    const importSingleCard = async () => {
      try {
        const response = await axios.post(`/api/${singleCard.value.destination}`, {
          scryfallid: singleCard.value.scryfallId,
          quantity: singleCard.value.quantity,
          foil: singleCard.value.foil ? 1 : 0
        })
        message.value = `Card imported successfully: ${response.data.message}`
        messageType.value = 'success'
        // Reset form
        singleCard.value = { scryfallId: '', quantity: 1, foil: false, destination: 'collection' }
      } catch (error) {
        message.value = `Error importing card: ${error.response?.data?.error || error.message}`
        messageType.value = 'error'
      }
    }

    const handleFileUpload = (event) => {
      csvImport.value.file = event.target.files[0]
    }

    const importFromCSV = async () => {
      if (!csvImport.value.file) {
        message.value = 'Please select a CSV file'
        messageType.value = 'error'
        return
      }

      const formData = new FormData()
      formData.append('file', csvImport.value.file)
      formData.append('destination', csvImport.value.destination)

      try {
        const response = await axios.post('/api/import_csv', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        message.value = `CSV imported successfully: ${response.data.message}`
        messageType.value = 'success'
        // Reset form
        csvImport.value = { file: null, destination: 'collection' }
      } catch (error) {
        message.value = `Error importing CSV: ${error.response?.data?.error || error.message}`
        messageType.value = 'error'
      }
    }

    return {
      singleCard,
      csvImport,
      message,
      messageType,
      importSingleCard,
      handleFileUpload,
      importFromCSV
    }
  }
}
</script>

<style scoped>
.import-section {
  margin-bottom: 2rem;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 400px;
  margin: 0 auto;
}

label {
  font-weight: bold;
}

input[type="text"],
input[type="number"],
select {
  width: 100%;
  padding: 0.5rem;
}

button {
  padding: 0.5rem 1rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}

.message {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 4px;
}

.success {
  background-color: #dff0d8;
  color: #3c763d;
}

.error {
  background-color: #f2dede;
  color: #a94442;
}
</style>