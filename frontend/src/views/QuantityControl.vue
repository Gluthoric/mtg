<template>
  <div class="quantity-control">
    <label :for="fieldId" class="quantity-label">
      {{ label }}
    </label>
    <div class="input-wrapper">
      <input
        :id="fieldId"
        v-model.number="currentValue"
        type="number"
        min="0"
        class="quantity-input"
        @input="onInput"
      />
      <div class="buttons">
        <button
          @click="increment"
          class="btn increment-btn"
          aria-label="Increment"
        >
          ▲
        </button>
        <button
          @click="decrement"
          class="btn decrement-btn"
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
.quantity-control {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.quantity-label {
  font-size: 0.85rem;
  color: #a0aec0;
}

.input-wrapper {
  display: flex;
  align-items: center;
  border: 1px solid #4a5568;
  border-radius: 0.25rem;
  overflow: hidden;
  background-color: #2d3748;
}

.quantity-input {
  flex: 1;
  padding: 0.5rem;
  border: none;
  text-align: center;
  font-size: 1rem;
  background-color: transparent;
  outline: none;
  color: #e2e8f0;
}

.quantity-input::-webkit-inner-spin-button,
.quantity-input::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.quantity-input {
  -moz-appearance: textfield;
}

.buttons {
  display: flex;
  flex-direction: column;
  border-left: 1px solid #4a5568;
}

.btn {
  width: 2rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #4a5568;
  border: none;
  cursor: pointer;
  font-size: 0.8rem;
  color: #e2e8f0;
  transition: background-color 0.2s, color 0.2s;
}

.btn:hover:not(:disabled) {
  background-color: #718096;
}

.btn:disabled {
  background-color: #2d3748;
  color: #718096;
  cursor: not-allowed;
}

.increment-btn {
  border-bottom: 1px solid #4a5568;
}
</style>