<template>
  <div class="quantity-control flex flex-col">
    <label :for="fieldId" class="quantity-label mb-1">
      {{ label }}
    </label>
    <div class="input-wrapper flex">
      <input
        :id="fieldId"
        v-model.number="currentValue"
        type="number"
        min="0"
        class="quantity-input flex-1 p-2 text-center"
        @input="onInput"
      />
      <div class="buttons flex flex-col">
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
.quantity-label {
  font-size: 0.85rem;
}

.input-wrapper {
  border: 1px solid var(--border-color);
  border-radius: 0.25rem;
  overflow: hidden;
  background-color: var(--input-background);
}

.quantity-input {
  border: none;
  background-color: transparent;
  outline: none;
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

.buttons {
  border-left: 1px solid var(--border-color);
}

.btn {
  width: 2rem;
  height: 1.25rem;
  font-size: 0.8rem;
}

.increment-btn {
  border-bottom: 1px solid var(--border-color);
}
</style>