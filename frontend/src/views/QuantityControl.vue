<template>
  <div class="quantity-control flex flex-col">
    <label :for="fieldId" class="quantity-label mb-1 text-sm font-semibold">
      {{ label }}
    </label>
    <div class="input-wrapper flex border rounded-md overflow-hidden">
      <input
        :id="fieldId"
        v-model.number="currentValue"
        type="number"
        min="0"
        class="quantity-input flex-1 p-2 text-center border-none outline-none bg-gray-100"
        @input="onInput"
      />
      <div class="buttons flex flex-col bg-gray-200 border-l">
        <button
          @click="increment"
          class="btn increment-btn px-2 py-1 text-sm bg-gray-300 hover:bg-gray-400"
          aria-label="Increment"
        >
          ▲
        </button>
        <button
          @click="decrement"
          class="btn decrement-btn px-2 py-1 text-sm bg-gray-300 hover:bg-gray-400"
          aria-label="Decrement"
          :disabled="currentValue === 0"
        >
          ▼
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QuantityControl',
  props: {
    label: {
      type: String,
      required: true
    },
    value: {
      type: Number,
      required: true
    },
    fieldId: {
      type: String,
      required: true
    }
  },
  emits: ['update'],
  computed: {
    currentValue: {
      get() {
        return this.value;
      },
      set(val) {
        this.$emit('update', Math.max(0, parseInt(val) || 0));
      }
    }
  },
  methods: {
    increment() {
      this.$emit('update', this.currentValue + 1);
    },
    decrement() {
      if (this.currentValue > 0) {
        this.$emit('update', this.currentValue - 1);
      }
    },
    onInput(event) {
      this.currentValue = event.target.value;
    }
  }
}
</script>

<style scoped>
.quantity-label {
  font-size: 0.85rem;
}

.quantity-input {
  -webkit-appearance: textfield;
  -moz-appearance: textfield;
  appearance: textfield;
}

.quantity-input::-webkit-inner-spin-button,
.quantity-input::-webkit-outer-spin-button {
  -webkit-appearance: none;
  appearance: none;
  margin: 0;
}
</style>
