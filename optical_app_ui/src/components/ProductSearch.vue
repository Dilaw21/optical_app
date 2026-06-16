<script setup>
import { ref, computed } from "vue"
import { createListResource } from "frappe-ui"

const q = ref("")

const products = createListResource({
  doctype: "Optical Item",
  fields: ["name", "item_name", "price"],
  filters: computed(() =>
    q.value
      ? [["item_name", "like", `%${q.value}%`]]
      : []
  ),
})
</script>

<template>
  <input
    v-model="q"
    placeholder="Search glasses / lenses..."
    class="border p-2 w-full mb-2"
    @input="products.reload()"
  />

  <div v-if="products.data">
    <div
      v-for="p in products.data"
      :key="p.name"
      class="p-2 border-b flex justify-between"
    >
      <span>{{ p.item_name }}</span>
      <span>{{ p.price }} DA</span>
    </div>
  </div>
</template>