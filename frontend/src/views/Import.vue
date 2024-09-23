<template>
  <div class="container">
    <h1 class="text-center mb-4">Import Cards</h1>

    <div class="card mb-4">
      <h2 class="mb-2">Import Single Card</h2>
      <form @submit.prevent="importSingleCard" class="grid grid-cols-1 gap-2">
        <div>
          <label for="scryfallId" class="block mb-1">Scryfall ID:</label>
          <input v-model="singleCard.scryfallId" id="scryfallId" required class="w-full">
        </div>
        <div>
          <label for="quantity" class="block mb-1">Quantity:</label>
          <input v-model.number="singleCard.quantity" id="quantity" type="number" min="1" required class="w-full">
        </div>
        <div class="flex items-center">
          <input v-model="singleCard.foil" id="foil" type="checkbox" class="mr-2">
          <label for="foil">Foil</label>
        </div>
        <div>
          <label for="destination" class="block mb-1">Destination:</label>
          <select v-model="singleCard.destination" id="destination" required class="w-full">
            <option value="collection">Collection</option>
            <option value="kiosk">Kiosk</option>
          </select>
        </div>
        <button type="submit" class="mt-2">Import Card</button>
      </form>
    </div>

    <div class="card mb-4">
      <h2 class="mb-2">CSV Import Guidelines</h2>
      <p class="mb-2">Please ensure your CSV follows the format below:</p>
      <pre class="bg-secondary p-2 mb-2 overflow-auto text-sm font-mono whitespace-pre-wrap break-words">
Name,Edition,Edition code,Collector's number,Price,Foil,Currency,Scryfall ID,Quantity
"Saw","Duskmourn: House of Horror","DSK","254","$0.21","Foil","USD","603c3ef4-4ef1-4db8-9ed2-e2b0926269d5","2"
      </pre>
      <a href="/static/csv_template.csv" download="csv_template.csv" class="text-primary hover:underline">Download CSV Template</a>
    </div>

    <div class="card mb-4">
      <h2 class="mb-2">Import from CSV</h2>
      <form @submit.prevent="importFromCSV" class="grid grid-cols-1 gap-2">
        <div>
          <label for="csvFile" class="block mb-1">CSV File:</label>
          <input type="file" id="csvFile" @change="handleFileUpload" accept=".csv" required class="w-full">
        </div>
        <button type="submit" class="mt-2">Import CSV</button>
      </form>
    </div>

    <div v-if="message" :class="['message', messageType, 'p-2 rounded']">
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