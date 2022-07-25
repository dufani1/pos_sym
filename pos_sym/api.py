import frappe

@frappe.whitelist(allow_guest=False, methods=["GET"]) 
def get_customers():
    args = frappe.request.args
    items = []
    cond_filters = {}

    if "last_update" in args:
        cond_filters["modified"] = (">", args.get("last_update"))
        
    _items = frappe.get_all("Customer", fields="*", filters=cond_filters, order_by="modified asc")

    for item in _items:
        # append child tables data
        item["tables"] = get_child_tables_data("Customer", item.get("name"))
        items.append(item)
    return items

@frappe.whitelist(allow_guest=False, methods=["GET"]) 
def get_items():
    args = frappe.request.args
    items = []
    cond_filters = {
        "sym_publish_to_local_pos": 1
    }

    if "last_update" in args:
        cond_filters["modified"] = (">", args.get("last_update"))
        
    _items = frappe.get_all("Item", fields="*", filters=cond_filters, order_by="modified asc")

    for item in _items:
        # append child tables data
        item["tables"] = get_child_tables_data("Item", item.get("name"))
        items.append(item)
    return items


def get_child_tables_data(doctype, docname):
    meta = frappe.get_meta(doctype)
    table_fields = meta.get_table_fields()
    child_tables = [{"fieldname": d.get("fieldname"), "table": d.get("options")} for d in table_fields]
    data = []
    for table_name in child_tables:
        table_data = frappe.get_all(
            table_name.get("table"),
            fields="*",
            filters={
                "parent": docname
            },
            order_by="modified asc"
        )

        data.append(
            {
                table_name.get("table"): table_data
            }
        )
    print(data)
    return data


