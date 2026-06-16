<script setup>
import { cart } from "../../store/pos"
</script>

<template>
  <div>
    <div
      v-for="(i, index) in cart.items"
      :key="index"
      class="flex justify-between border-b p-2"
    >
      <span>{{ i.item_name }}</span>
      <span>{{ i.price }}</span>
    </div>

    <div class="mt-3 font-bold">
      Total: {{ cart.total() }} DA
    </div>
  </div>
</template>