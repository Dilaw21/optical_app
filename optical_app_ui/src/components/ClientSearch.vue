<script setup>
import { ref } from "vue"
import { createListResource, createResource } from "frappe-ui"

const selectedCustomer = ref(null)

// CUSTOMER INPUT
const customerName = ref("")
const phone = ref("")
const addressLine = ref("")

// LIST customers
const customers = createListResource({
  doctype: "Customer",
  fields: ["name", "customer_name"],
  auto: true,
})

// CREATE CUSTOMER
const createCustomer = createResource({
  url: "frappe.client.insert",
})

// CREATE ADDRESS
const createAddress = createResource({
  url: "frappe.client.insert",
})

async function addCustomerWithAddress() {
  if (!customerName.value) return

  // 1. Create Customer
  const customer = await createCustomer.submit({
    doc: {
      doctype: "Customer",
      customer_name: customerName.value,
      customer_type: "Individual",
      customer_group: "Individual",
      territory: "Algeria",
    },
  })

  // 2. Create Address linked to Customer
  if (addressLine.value || phone.value) {
    await createAddress.submit({
      doc: {
        doctype: "Address",

        address_title: customerName.value,
        address_type: "Shipping",

        address_line1: addressLine.value || "N/A",
        city: "Algiers",
        country: "Algeria",

        phone: phone.value,

        links: [
          {
            link_doctype: "Customer",
            link_name: customer.name,
          },
        ],
      },
    })
  }

  selectedCustomer.value = customer

  // reset
  customerName.value = ""
  phone.value = ""
  addressLine.value = ""

  customers.reload()
}
</script>

<template>
  <div class="space-y-3">

    <!-- SELECTED -->
    <div v-if="selectedCustomer" class="p-2 bg-green-100">
      Selected: {{ selectedCustomer.customer_name }}
    </div>

    <!-- FORM -->
    <div class="border p-3 space-y-2">
      <h3 class="font-bold">New Customer + Address</h3>

      <input
        v-model="customerName"
        placeholder="Customer name"
        class="border p-2 w-full"
      />

      <input
        v-model="phone"
        placeholder="Phone number"
        class="border p-2 w-full"
      />

      <input
        v-model="addressLine"
        placeholder="Address"
        class="border p-2 w-full"
      />

      <button
        class="bg-blue-500 text-white p-2 w-full"
        @click="addCustomerWithAddress"
      >
        Save Customer
      </button>
    </div>

    <!-- LIST -->
    <div class="border">
      <div
        v-for="c in customers.data"
        :key="c.name"
        class="p-2 border-b cursor-pointer"
        @click="selectedCustomer = c"
      >
        {{ c.customer_name }}
      </div>
    </div>

  </div>
</template>