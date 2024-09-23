<!-- QuantityControl.vue -->
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
    onInput(val) {
      this.currentValue = val;
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
  color: #555;
}

.input-wrapper {
  display: flex;
  align-items: center;
  border: 1px solid #ccc;
  border-radius: 5px;
  overflow: hidden;
  background-color: #fff;
}

.quantity-input {
  flex: 1;
  padding: 0.5rem;
  border: none;
  text-align: center;
  font-size: 1rem;
  background-color: transparent;
  outline: none;
  color: #333;
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
  border-left: 1px solid #ccc;
}

.btn {
  width: 2.5rem;
  height: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
  border: none;
  cursor: pointer;
  font-size: 0.8rem;
  color: #333;
  transition: background-color 0.2s, color 0.2s;
}

.btn:hover:not(:disabled) {
  background-color: #e0e0e0;
  color: #000;
}

.btn:disabled {
  background-color: #f9f9f9;
  color: #999;
  cursor: not-allowed;
}

.increment-btn {
  border-bottom: 1px solid #ccc;
}

.decrement-btn {
  /* No additional border needed as it's the last button */
}
</style>
