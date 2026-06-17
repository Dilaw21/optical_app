import frappe

# ==========================================
# FONCTION API ACCESSIBLE DEPUIS LE FRONTEND
# ==========================================
@frappe.whitelist()
def append_optical_visit(customer_name, visit_data):
    """
    Ajoute de manière sécurisée et atomique une nouvelle visite à un client existant
    sans risquer de conflit de timestamp (TimestampMismatchError).
    """
    if isinstance(visit_data, str):
        import json
        visit_data = json.loads(visit_data)
        
    doc = frappe.get_doc("Customer", customer_name)
    doc.append("visites", visit_data)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    
    return doc.name


# ==========================================
# SCRIPT INITIAL DE CONFIGURATION DES DOCTYPES
# ==========================================
def setup_customer_visit_with_prescription():
    # 1. Structure du DocType Enfant 'Customer Visit'
    visit_fields = [
        # === LEFT SECTION: Vente / Acte ===
        {"fieldname": "vente_section", "fieldtype": "Section Break", "label": "Vente n° / Acte"},
        {"fieldname": "date", "fieldtype": "Date", "label": "Date", "reqd": 1, "in_list_view": 1},
        {"fieldname": "no_facture", "fieldtype": "Data", "label": "N° Facture", "in_list_view": 1},
        {"fieldname": "age_category", "fieldtype": "Select", "label": "Age Category", "options": "Adulte\nEnfant", "default": "Adulte"},
        {"fieldname": "date_acte", "fieldtype": "Date", "label": "Date d'acte"},

        # === RIGHT SECTION: Ordonnance ===
        {"fieldname": "ordonnance_column", "fieldtype": "Column Break", "label": "Ordonnance"},
        {"fieldname": "date_ordo", "fieldtype": "Date", "label": "Date Ordo."},
        {"fieldname": "prescripteur", "fieldtype": "Data", "label": "Prescripteur"},
        {"fieldname": "nom_presc", "fieldtype": "Data", "label": "Nom Presc."},
        {"fieldname": "no_finess_am", "fieldtype": "Data", "label": "N° FINESS/AM"},
        {"fieldname": "numeric_field", "fieldtype": "Int", "label": "Numeric field", "default": "0"},
        {"fieldname": "specialite", "fieldtype": "Data", "label": "Spé..."},

        # === ŒIL DROIT (Right Eye) Row ===
        {"fieldname": "od_section", "fieldtype": "Section Break", "label": "Œil Droit (Right Eye)"},
        {"fieldname": "od_sph", "fieldtype": "Data", "label": "Sph.", "columns": 1},
        {"fieldname": "od_cyl", "fieldtype": "Data", "label": "Cyl.", "columns": 1},
        {"fieldname": "od_axe", "fieldtype": "Data", "label": "Axe", "columns": 1},
        {"fieldname": "od_add", "fieldtype": "Data", "label": "Add.", "columns": 1},
        {"fieldname": "od_prisme", "fieldtype": "Data", "label": "Prisme", "columns": 1},
        {"fieldname": "od_base", "fieldtype": "Data", "label": "Base", "columns": 1},
        {"fieldname": "od_ac", "fieldtype": "Data", "label": "Ac.", "columns": 1},

        # === ŒIL GAUCHE (Left Eye) Row ===
        {"fieldname": "og_section", "fieldtype": "Section Break", "label": "Œil Gauche (Left Eye)"},
        {"fieldname": "og_sph", "fieldtype": "Data", "label": "Sph.", "columns": 1},
        {"fieldname": "og_cyl", "fieldtype": "Data", "label": "Cyl.", "columns": 1},
        {"fieldname": "og_axe", "fieldtype": "Data", "label": "Axe", "columns": 1},
        {"fieldname": "og_add", "fieldtype": "Data", "label": "Add.", "columns": 1},
        {"fieldname": "og_prisme", "fieldtype": "Data", "label": "Prisme", "columns": 1},
        {"fieldname": "og_base", "fieldtype": "Data", "label": "Base", "columns": 1},
        {"fieldname": "og_ac", "fieldtype": "Data", "label": "Ac.", "columns": 1},
    ]

    # 2. Vérification / Création / Mise à jour propre du DocType enfant
    if not frappe.db.exists("DocType", "Customer Visit"):
        visit_dt = frappe.get_doc({
            "doctype": "DocType",
            "name": "Customer Visit",
            "module": "Contacts",
            "custom": 1,
            "istable": 1,          # Table Enfant
            "fields": visit_fields
        })
        visit_dt.insert(ignore_permissions=True)
        print("Child Table 'Customer Visit' created successfully.")
    else:
        doc = frappe.get_doc("DocType", "Customer Visit")
        
        # CORRECTION ICI : On vide et on réinjecte proprement via append pour convertir en DocField objets
        doc.set("fields", []) 
        for field in visit_fields:
            doc.append("fields", field)
            
        doc.save(ignore_permissions=True)
        print("Existing 'Customer Visit' schema updated successfully.")

    # 3. Injection de la table dans le DocType Customer principal
    if not frappe.db.exists("Custom Field", {"dt": "Customer", "fieldname": "visites"}):
        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Customer",
            "fieldname": "visites",
            "label": "Visites",
            "fieldtype": "Table",
            "options": "Customer Visit",
            "insert_after": "customer_details"
        }).insert(ignore_permissions=True)
        print("Attached 'visites' table onto Customer DocType!")
    else:
        print("'visites' table connection already established on Customer.")

    # Nettoyage global du cache métadonnées
    frappe.clear_cache(doctype="Customer")
    frappe.clear_cache(doctype="Customer Visit")
    frappe.db.commit()

if __name__ == "__main__":
    setup_customer_visit_with_prescription()