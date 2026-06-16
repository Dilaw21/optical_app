<script setup>
import { cart } from "../../store/pos"
import { createResource } from "frappe-ui"

const createInvoice = createResource({
  url: "frappe.client.insert",
})

function pay() {
  createInvoice.submit({
    doc: {
      doctype: "Sales Invoice",
      customer: "CASH",
      items: cart.items.map(i => ({
        item_name: i.item_name,
        qty: i.qty,
        rate: i.price,
      })),
    },
  })
}
</script>

<template>
  <div class="mt-3">
    <button
      class="bg-green-500 text-white p-2 w-full"
      @click="pay"
    >
      Pay & Create Invoice
    </button>
  </div>
</template>