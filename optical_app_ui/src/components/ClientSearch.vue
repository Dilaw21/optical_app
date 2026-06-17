<script setup>
import { ref, watch } from "vue"
import { createListResource, createResource } from "frappe-ui"

const selectedCustomer = ref(null)
const selectedCustomerVisits = ref([])

// Index pour la navigation et état de la modale
const currentVisitIndex = ref(0)
const showHistoryModal = ref(false)

// CUSTOMER BASIC INPUTS
const customerName = ref("")
const phone = ref("")
const addressLine = ref("")

// OPTICAL VISIT FORM INPUTS
const visitDate = ref(new Date().toISOString().split('T')[0])
const noFacture = ref("")
const ageCategory = ref("Adulte")
const dateActe = ref("")

const dateOrdo = ref("")
const prescripteur = ref("")
const nomPresc = ref("")
const noFinessAm = ref("")
const numericField = ref(0)
const specialite = ref("")

// Eye Measurements (Right Eye / OD)
const odSph = ref("")
const odCyl = ref("")
const odAxe = ref("")
const odAdd = ref("")
const odPrisme = ref("")
const odBase = ref("")
const odAc = ref("")

// Eye Measurements (Left Eye / OG)
const ogSph = ref("")
const ogCyl = ref("")
const ogAxe = ref("")
const ogAdd = ref("")
const ogPrisme = ref("")
const ogBase = ref("")
const ogAc = ref("")

// LIST CUSTOMERS
const customers = createListResource({
  doctype: "Customer",
  fields: ["name", "customer_name"],
  auto: true,
})

// CREATE CUSTOMER RESOURCE
const createCustomer = createResource({
  url: "frappe.client.insert",
})

// RECOURS API SÉCURISÉ
const appendVisitResource = createResource({
  url: "optical_app.create.append_optical_visit",
})

// CREATE ADDRESS RESOURCE
const createAddress = createResource({
  url: "frappe.client.insert",
})

// DETAIL FETCH RESOURCE FOR HISTORIQUE
const customerDetail = createResource({
  url: "frappe.client.get",
})

// Surveiller la sélection d'un client dans le registre
watch(selectedCustomer, async (newCustomer) => {
  if (newCustomer && newCustomer.name) {
    try {
      const res = await customerDetail.submit({
        doctype: "Customer",
        name: newCustomer.name,
      })
      selectedCustomerVisits.value = res.visites || []
      currentVisitIndex.value = selectedCustomerVisits.value.length > 0 ? selectedCustomerVisits.value.length - 1 : 0
      customerName.value = res.customer_name
    } catch (error) {
      console.error("Error loading visits:", error)
      selectedCustomerVisits.value = []
      currentVisitIndex.value = 0
    }
  } else {
    selectedCustomerVisits.value = []
    currentVisitIndex.value = 0
  }
})

function prevVisit() {
  if (currentVisitIndex.value > 0) {
    currentVisitIndex.value--
  }
}

function nextVisit() {
  if (currentVisitIndex.value < selectedCustomerVisits.value.length - 1) {
    currentVisitIndex.value++
  }
}

// Sélectionner une visite spécifique depuis la liste globale de la modale
function selectVisitFromModal(index) {
  currentVisitIndex.value = index
  showHistoryModal.value = false // Ferme la modale
}

async function addCustomerWithPrescription() {
  if (!customerName.value) return

  const opticalVisitPayload = {
    doctype: "Customer Visit",
    date: visitDate.value,
    no_facture: noFacture.value,
    age_category: ageCategory.value,
    date_acte: dateActe.value || null,
    
    date_ordo: dateOrdo.value || null,
    prescripteur: prescripteur.value,
    nom_presc: nomPresc.value,
    no_finess_am: noFinessAm.value,
    numeric_field: parseInt(numericField.value) || 0,
    specialite: specialite.value,

    // OD
    od_sph: odSph.value,
    od_cyl: odCyl.value,
    od_axe: odAxe.value,
    od_add: odAdd.value,
    od_prisme: odPrisme.value,
    od_base: odBase.value,
    od_ac: odAc.value,

    // OG
    og_sph: ogSph.value,
    og_cyl: ogCyl.value,
    og_axe: ogAxe.value,
    og_add: ogAdd.value,
    og_prisme: ogPrisme.value,
    og_base: ogBase.value,
    og_ac: ogAc.value,
  }

  let finalCustomerName = null

  try {
    if (selectedCustomer.value && selectedCustomer.value.name) {
      await appendVisitResource.submit({
        customer_name: selectedCustomer.value.name,
        visit_data: opticalVisitPayload
      })
      finalCustomerName = selectedCustomer.value.name
      alert("Nouvelle visite ajoutée avec succès au dossier de ce patient !")
      
    } else {
      const newCustomer = await createCustomer.submit({
        doc: {
          doctype: "Customer",
          customer_name: customerName.value,
          customer_type: "Individual",
          customer_group: "Individual",
          territory: "Algeria",
          visites: [opticalVisitPayload]
        },
      })
      finalCustomerName = newCustomer.name

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
            links: [{ link_doctype: "Customer", link_name: finalCustomerName }],
          },
        })
      }
      alert("Nouveau patient enregistré en base de données !")
    }

    const updatedDetails = await customerDetail.submit({ doctype: "Customer", name: finalCustomerName })
    selectedCustomerVisits.value = updatedDetails.visites || []
    
    currentVisitIndex.value = selectedCustomerVisits.value.length - 1
    selectedCustomer.value = { name: updatedDetails.name, customer_name: updatedDetails.customer_name }

    resetFormFields()
    customers.reload()

  } catch (err) {
    console.error("Erreur lors de la sauvegarde :", err)
    alert("Une erreur est survenue lors de l'enregistrement.")
  }
}

function resetFormFields() {
  if (!selectedCustomer.value) {
    customerName.value = ""
  }
  phone.value = ""
  addressLine.value = ""
  noFacture.value = ""
  dateActe.value = ""
  dateOrdo.value = ""
  prescripteur.value = ""
  nomPresc.value = ""
  noFinessAm.value = ""
  numericField.value = 0
  specialite.value = ""
  
  odSph.value = ""; odCyl.value = ""; odAxe.value = ""; odAdd.value = ""; odPrisme.value = ""; odBase.value = ""; odAc.value = ""
  ogSph.value = ""; ogCyl.value = ""; ogAxe.value = ""; ogAdd.value = ""; ogPrisme.value = ""; ogBase.value = ""; ogAc.value = ""
}

function startNewPatient() {
  selectedCustomer.value = null
  selectedCustomerVisits.value = []
  currentVisitIndex.value = 0
  customerName.value = ""
  resetFormFields()
}
</script>

<template>
  <div class="space-y-6 p-6 max-w-5xl mx-auto bg-gray-50 min-h-screen relative">

    <div class="flex justify-between items-center bg-white p-3 border rounded shadow-sm">
      <div>
        <span v-if="selectedCustomer" class="text-sm font-medium text-gray-700">
          Mode : <strong class="text-blue-600">Ajout d'examen pour {{ selectedCustomer.customer_name }}</strong>
        </span>
        <span v-else class="text-sm font-medium text-gray-700">
          Mode : <strong class="text-green-600">Création d'un Nouveau Patient</strong>
        </span>
      </div>
      <button 
        v-if="selectedCustomer" 
        @click="startNewPatient" 
        class="bg-gray-100 hover:bg-gray-200 text-gray-800 text-xs font-bold px-3 py-1.5 rounded transition"
      >
        ➕ Nouveau Patient Indépendant
      </button>
    </div>

    <div v-if="selectedCustomer" class="p-4 bg-white border rounded shadow-sm space-y-4">
      <div class="border-b pb-2 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
        <h2 class="text-lg font-bold text-blue-900 flex items-center gap-2">
          <span>Dossier : {{ selectedCustomer.customer_name }}</span>
          <span class="text-xs font-mono bg-blue-100 text-blue-800 px-2 py-0.5 rounded">{{ selectedCustomer.name }}</span>
        </h2>
        
        <div v-if="selectedCustomerVisits.length > 0" class="flex items-center space-x-2 bg-gray-50 p-1 rounded border">
          <button 
            @click="prevVisit" 
            :disabled="currentVisitIndex === 0"
            class="px-2.5 py-1 bg-white border rounded text-xs font-bold shadow-sm hover:bg-gray-50 disabled:opacity-40 transition"
          >
            ◀ Précédent
          </button>
          
          <span class="text-xs font-medium text-gray-700 px-1">
            Visite <strong>{{ currentVisitIndex + 1 }}</strong> / {{ selectedCustomerVisits.length }}
          </span>
          
          <button 
            @click="nextVisit" 
            :disabled="currentVisitIndex === selectedCustomerVisits.length - 1"
            class="px-2.5 py-1 bg-white border rounded text-xs font-bold shadow-sm hover:bg-gray-50 disabled:opacity-40 transition"
          >
            Suivant ▶
          </button>

          <button 
            @click="showHistoryModal = true"
            class="ml-2 px-3 py-1 bg-blue-50 text-blue-700 border border-blue-200 rounded text-xs font-bold hover:bg-blue-100 transition shadow-xs"
          >
            👁 Tout l'historique
          </button>
        </div>
      </div>

      <div>
        <div v-if="selectedCustomerVisits.length === 0" class="text-gray-400 italic text-sm py-4 text-center">
          Aucun historique d'examen trouvé pour ce patient.
        </div>

        <div v-else class="border rounded-lg p-4 bg-gray-50 shadow-inner">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3 font-semibold text-xs text-gray-600 border-b pb-3 mb-3">
            <div class="text-blue-900 font-bold flex items-center gap-1 text-sm">
              📅 Examen du : <span class="bg-blue-600 text-white px-2 py-0.5 rounded text-xs">{{ selectedCustomerVisits[currentVisitIndex].date }}</span>
            </div>
            <div>🧾 N° Facture : <span class="text-gray-900">{{ selectedCustomerVisits[currentVisitIndex].no_facture || 'N/A' }}</span></div>
            <div>👤 Catégorie : <span class="text-gray-900">{{ selectedCustomerVisits[currentVisitIndex].age_category }}</span></div>
            <div>🩺 Dr : <span class="text-gray-900">{{ selectedCustomerVisits[currentVisitIndex].nom_presc || 'N/A' }}</span></div>
          </div>

          <div class="overflow-x-auto bg-white rounded border">
            <table class="w-full text-left border-collapse text-xs">
              <thead>
                <tr class="bg-gray-100 text-gray-700 font-bold border-b">
                  <th class="p-2 border-r">Œil</th>
                  <th class="p-2 border-r text-center">Sph.</th>
                  <th class="p-2 border-r text-center">Cyl.</th>
                  <th class="p-2 border-r text-center">Axe</th>
                  <th class="p-2 border-r text-center">Add.</th>
                  <th class="p-2 border-r text-center">Prisme</th>
                  <th class="p-2 border-r text-center">Base</th>
                  <th class="p-2 text-center">Ac.</th>
                </tr>
              </thead>
              <tbody>
                <tr class="border-b">
                  <td class="p-2 border-r font-bold text-blue-600 bg-blue-50/10">Droit (OD)</td>
                  <td class="p-2 border-r text-center font-mono">{{ selectedCustomerVisits[currentVisitIndex].od_sph || '-' }}</td>
                  <td class="p-2 border-r text-center font-mono">{{ selectedCustomerVisits[currentVisitIndex].od_cyl || '-' }}</td>
                  <td class="p-2 border-r text-center font-mono">{{ selectedCustomerVisits[currentVisitIndex].od_axe || '-' }}</td>
                  <td class="p-2 border-r text-center font-mono">{{ selectedCustomerVisits[currentVisitIndex].od_add || '-' }}</td>
                  <td class="p-2 border-r text-center font-mono">{{ selectedCustomerVisits[currentVisitIndex].od_prisme || '-' }}</td>
                  <td class="p-2 border-r text-center font-mono">{{ selectedCustomerVisits[currentVisitIndex].od_base || '-' }}</td>
                  <td class="p-2 text-center font-mono bg-gray-50/50">{{ selectedCustomerVisits[currentVisitIndex].od_ac || '-' }}</td>
                </tr>
                <tr>
                  <td class="p-2 border-r font-bold text-green-600 bg-green-50/10">Gauche (OG)</td>
                  <td class="p-2 border-r text-center font-mono">{{ selectedCustomerVisits[currentVisitIndex].og_sph || '-' }}</td>
                  <td class="p-2 border-r text-center font-mono">{{ selectedCustomerVisits[currentVisitIndex].og_cyl || '-' }}</td>
                  <td class="p-2 border-r text-center font-mono">{{ selectedCustomerVisits[currentVisitIndex].og_axe || '-' }}</td>
                  <td class="p-2 border-r text-center font-mono">{{ selectedCustomerVisits[currentVisitIndex].og_add || '-' }}</td>
                  <td class="p-2 border-r text-center font-mono">{{ selectedCustomerVisits[currentVisitIndex].og_prisme || '-' }}</td>
                  <td class="p-2 border-r text-center font-mono">{{ selectedCustomerVisits[currentVisitIndex].og_base || '-' }}</td>
                  <td class="p-2 text-center font-mono bg-gray-50/50">{{ selectedCustomerVisits[currentVisitIndex].og_ac || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white border rounded shadow-sm p-4 space-y-4">
      <h3 class="font-bold text-md text-gray-800 border-b pb-2">
        {{ selectedCustomer ? 'Formulaire : Ajouter une nouvelle consultation' : 'Formulaire : Création fiche et premier examen' }}
      </h3>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <label class="text-xs font-semibold text-gray-600 w-full">Nom Complet
          <input v-model="customerName" :disabled="selectedCustomer !== null" placeholder="Nom du patient" class="border p-2 rounded text-sm w-full disabled:bg-gray-100 disabled:text-gray-500" />
        </label>
        <label class="text-xs font-semibold text-gray-600 w-full">Téléphone
          <input v-model="phone" :disabled="selectedCustomer !== null" placeholder="N° de Téléphone" class="border p-2 rounded text-sm w-full disabled:bg-gray-100" />
        </label>
        <label class="text-xs font-semibold text-gray-600 w-full">Adresse
          <input v-model="addressLine" :disabled="selectedCustomer !== null" placeholder="Adresse résidentielle" class="border p-2 rounded text-sm w-full disabled:bg-gray-100" />
        </label>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t">
        <div class="space-y-2 bg-blue-50/50 p-3 rounded border border-blue-100">
          <h4 class="font-bold text-xs text-blue-800 uppercase tracking-wider">Left Section (Vente / Acte)</h4>
          <div class="grid grid-cols-2 gap-2">
            <label class="text-xs">Date Visite: <input type="date" v-model="visitDate" class="border p-1 rounded text-xs w-full" /></label>
            <label class="text-xs">N° Facture: <input v-model="noFacture" placeholder="Facture" class="border p-1 rounded text-xs w-full" /></label>
            <label class="text-xs">Catégorie Âge: 
              <select v-model="ageCategory" class="border p-1 rounded text-xs w-full">
                <option value="Adulte">Adulte</option>
                <option value="Enfant">Enfant</option>
              </select>
            </label>
            <label class="text-xs">Date d'acte: <input type="date" v-model="dateActe" class="border p-1 rounded text-xs w-full" /></label>
          </div>
        </div>

        <div class="space-y-2 bg-purple-50/50 p-3 rounded border border-purple-100">
          <h4 class="font-bold text-xs text-purple-800 uppercase tracking-wider">Right Section (Ordonnance)</h4>
          <div class="grid grid-cols-2 gap-2">
            <label class="text-xs">Date Ordo.: <input type="date" v-model="dateOrdo" class="border p-1 rounded text-xs w-full" /></label>
            <label class="text-xs">Prescripteur ID: <input v-model="prescripteur" placeholder="Identifiant" class="border p-1 rounded text-xs w-full" /></label>
            <label class="text-xs">Nom Presc.: <input v-model="nomPresc" placeholder="Nom Médecin" class="border p-1 rounded text-xs w-full" /></label>
            <label class="text-xs">N° FINESS/AM: <input v-model="noFinessAm" placeholder="N° Agrément" class="border p-1 rounded text-xs w-full" /></label>
            <label class="text-xs">Num Field: <input type="number" v-model="numericField" class="border p-1 rounded text-xs w-full" /></label>
            <label class="text-xs">Spécialité: <input v-model="specialite" placeholder="Spécialité" class="border p-1 rounded text-xs w-full" /></label>
          </div>
        </div>
      </div>

      <div class="pt-2 border-t space-y-3">
        <h4 class="font-bold text-xs text-gray-700 uppercase tracking-wider">Valeurs de réfraction de la session</h4>
        <div class="overflow-x-auto space-y-2">
          <div class="flex items-center space-x-1 min-w-[700px] bg-gray-50 p-2 border rounded">
            <span class="w-24 text-xs font-bold text-blue-700">Œil Droit (OD)</span>
            <input v-model="odSph" placeholder="Sph." class="border p-1 text-center text-xs w-16 rounded" />
            <input v-model="odCyl" placeholder="Cyl." class="border p-1 text-center text-xs w-16 rounded" />
            <input v-model="odAxe" placeholder="Axe" class="border p-1 text-center text-xs w-16 rounded" />
            <input v-model="odAdd" placeholder="Add." class="border p-1 text-center text-xs w-16 rounded" />
            <input v-model="odPrisme" placeholder="Prisme" class="border p-1 text-center text-xs w-16 rounded" />
            <input v-model="odBase" placeholder="Base" class="border p-1 text-center text-xs w-16 rounded" />
            <input v-model="odAc" placeholder="Ac." class="border p-1 text-center text-xs w-16 rounded" />
          </div>
          <div class="flex items-center space-x-1 min-w-[700px] bg-gray-50 p-2 border rounded">
            <span class="w-24 text-xs font-bold text-green-700">Œil Gauche (OG)</span>
            <input v-model="ogSph" placeholder="Sph." class="border p-1 text-center text-xs w-16 rounded" />
            <input v-model="ogCyl" placeholder="Cyl." class="border p-1 text-center text-xs w-16 rounded" />
            <input v-model="ogAxe" placeholder="Axe" class="border p-1 text-center text-xs w-16 rounded" />
            <input v-model="ogAdd" placeholder="Add." class="border p-1 text-center text-xs w-16 rounded" />
            <input v-model="ogPrisme" placeholder="Prisme" class="border p-1 text-center text-xs w-16 rounded" />
            <input v-model="ogBase" placeholder="Base" class="border p-1 text-center text-xs w-16 rounded" />
            <input v-model="ogAc" placeholder="Ac." class="border p-1 text-center text-xs w-16 rounded" />
          </div>
        </div>
      </div>

      <button @click="addCustomerWithPrescription" class="bg-blue-600 hover:bg-blue-700 text-white font-bold p-2 text-sm w-full rounded shadow-sm transition">
        {{ selectedCustomer ? `Valider et enregistrer la visite pour ${selectedCustomer.customer_name}` : 'Créer la fiche patient et enregistrer la visite' }}
      </button>
    </div>

    <div class="border rounded bg-white overflow-hidden shadow-sm">
      <div class="p-2 bg-gray-100 font-bold border-b text-sm text-gray-700">Registre Patients (Cliquez pour charger ou ajouter un historique)</div>
      <div class="divide-y max-h-60 overflow-y-auto">
        <div
          v-for="c in customers.data"
          :key="c.name"
          class="p-3 hover:bg-blue-50/40 cursor-pointer transition flex justify-between items-center text-sm"
          :class="{'bg-blue-50 font-semibold border-l-4 border-blue-500': selectedCustomer?.name === c.name}"
          @click="selectedCustomer = c"
        >
          <span>{{ c.customer_name }}</span>
          <span class="text-xs text-gray-400 font-mono">{{ c.name }}</span>
        </div>
      </div>
    </div>

    <div v-if="showHistoryModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
      <div class="bg-white w-full max-w-4xl rounded-lg shadow-xl max-h-[85vh] flex flex-col overflow-hidden">
        
        <div class="p-4 bg-gray-900 text-white flex justify-between items-center">
          <div>
            <h3 class="text-lg font-bold">Historique complet de : {{ selectedCustomer?.customer_name }}</h3>
            <p class="text-xs text-gray-400">Total : {{ selectedCustomerVisits.length }} consultation(s) enregistrée(s)</p>
          </div>
          <button @click="showHistoryModal = false" class="text-gray-400 hover:text-white font-bold text-xl px-2">✕</button>
        </div>

        <div class="p-4 overflow-y-auto space-y-4 bg-gray-50 flex-1">
          <div 
            v-for="(v, idx) in selectedCustomerVisits" 
            :key="idx" 
            @click="selectVisitFromModal(idx)"
            class="bg-white border rounded-lg p-3 hover:border-blue-500 cursor-pointer transition shadow-xs group"
          >
            <div class="flex justify-between items-center border-b pb-2 mb-2 bg-gray-50/50 p-2 rounded">
              <span class="font-bold text-blue-900 text-sm">
                📌 N°{{ idx + 1 }} — Visite du {{ v.date }}
              </span>
              <span class="text-xs text-gray-500 group-hover:text-blue-600 font-medium">
                Cliquez pour charger cette fiche 🔍
              </span>
            </div>

            <div class="grid grid-cols-3 gap-2 text-xs text-gray-600 mb-2 px-2">
              <div><strong>🧾 Facture :</strong> {{ v.no_facture || 'N/A' }}</div>
              <div><strong>👤 Tranche :</strong> {{ v.age_category }}</div>
              <div><strong>🩺 Médecin :</strong> {{ v.nom_presc || 'N/A' }}</div>
            </div>

            <table class="w-full text-center text-xs border border-collapse bg-white">
              <tr class="bg-gray-100 text-gray-600 font-semibold">
                <th class="p-1 border text-left pl-2">Œil</th>
                <th class="p-1 border">Sph.</th>
                <th class="p-1 border">Cyl.</th>
                <th class="p-1 border">Axe</th>
                <th class="p-1 border">Add.</th>
              </tr>
              <tr>
                <td class="p-1 border text-left pl-2 font-medium text-blue-600">OD</td>
                <td class="p-1 border font-mono">{{ v.od_sph || '-' }}</td>
                <td class="p-1 border font-mono">{{ v.od_cyl || '-' }}</td>
                <td class="p-1 border font-mono">{{ v.od_axe || '-' }}</td>
                <td class="p-1 border font-mono">{{ v.od_add || '-' }}</td>
              </tr>
              <tr>
                <td class="p-1 border text-left pl-2 font-medium text-green-600">OG</td>
                <td class="p-1 border font-mono">{{ v.og_sph || '-' }}</td>
                <td class="p-1 border font-mono">{{ v.og_cyl || '-' }}</td>
                <td class="p-1 border font-mono">{{ v.og_axe || '-' }}</td>
                <td class="p-1 border font-mono">{{ v.og_add || '-' }}</td>
              </tr>
            </table>
          </div>
        </div>

        <div class="p-3 bg-gray-100 border-t flex justify-end">
          <button 
            @click="showHistoryModal = false" 
            class="px-4 py-2 bg-gray-800 text-white text-xs font-bold rounded hover:bg-gray-700 transition"
          >
            Fermer la vue d'ensemble
          </button>
        </div>

      </div>
    </div>

  </div>
</template>