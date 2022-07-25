import frappe

def on_update(doc, method):
    if doc.sym_publish_to_local_pos:
        item_prices = frappe.get_all("Item Price",
                fields=["name"],
                filters={
                    "item_code": doc.item_code,
                    "selling": True
                })
        if len(item_prices) == 0:
            frappe.throw(frappe._(f"SYM: Cant publish to local POS, Item {doc.item_name} has no <a target='_blank' href='/app/item-price'>item sell price</a>"))