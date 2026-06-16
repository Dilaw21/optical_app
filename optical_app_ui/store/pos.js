import { reactive } from "vue"

export const cart = reactive({
  items: [],

  add(item) {
    this.items.push({
      ...item,
      qty: 1,
    })
  },

  total() {
    return this.items.reduce(
      (sum, i) => sum + i.price * i.qty,
      0
    )
  },
})