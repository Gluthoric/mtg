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
      <h2>CSV Import Guidelines</h2>
      <p>Please ensure your CSV follows the format below:</p>
      <pre>
Name,Edition,Edition code,Collector's number,Price,Foil,Currency,Scryfall ID,Quantity
"Saw","Duskmourn: House of Horror","DSK","254","$0.21","Foil","USD","603c3ef4-4ef1-4db8-9ed2-e2b0926269d5","2"
      </pre>
      <a href="/static/csv_template.csv" download="csv_template.csv">Download CSV Template</a>
    </div>

    <div class="import-section">
      <h2>Import from CSV</h2>
      <form @submit.prevent="importFromCSV">
        <div>
          <label for="csvFile">CSV File:</label>
          <input type="file" id="csvFile" @change="handleFileUpload" accept=".csv" required>
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
      file: null
    })

    const message = ref('')
    const messageType = ref('')

    const importSingleCard = async () => {
      try {
        const response = await axios.post(`/api/collection`, {
          scryfall_id: singleCard.value.scryfallId,
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

      try {
        const response = await axios.post('/api/collection/import_csv', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        message.value = `CSV imported successfully: ${response.data.message}`
        messageType.value = 'success'
        // Reset form
        csvImport.value = { file: null }
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

pre {
  background-color: #f4f4f4;
  border: 1px solid #ddd;
  border-left: 3px solid #4CAF50;
  color: #666;
  page-break-inside: avoid;
  font-family: monospace;
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 1.6em;
  max-width: 100%;
  overflow: auto;
  padding: 1em 1.5em;
  display: block;
  word-wrap: break-word;
}
</style>