import imp
import frappe
from frappe.model.document import Document
from frappe.utils.data import nowdate

def sym_get_pos_client():
    """ Get POS Client from the current request """
    client_id = frappe.form_dict["client_id"]

    pos_client_name = frappe.db.get_value(
        doctype="POS Client",
        filters={
            "client_id": client_id
        },
        fieldname="name"
    )
    pos_client = frappe.get_doc("POS Client", pos_client_name)
    
    return pos_client

def sym_get_pos_clients() -> "list[Document]":
    pos_clients_orms = []
    pos_clients = frappe.db.get_all(
        doctype="POS Client",
        fields=["name"]
    )
    for pos_client in pos_clients:
        pos_clients_orms.append(
            frappe.get_doc("POS Client", pos_client.get("name"))
        )
    
    if len(pos_clients_orms) > 0:
        return pos_clients_orms
    else:
        return None


def sym_create_backlog(pos_client_orm, doctype, docname, data, event_type, status="Pending"):
    new_backlog = frappe.get_doc(
        {
            "doctype": "POS SYNC Backlog",
            "pos_client": pos_client_orm.name,
            "client_id": pos_client_orm.client_id,
            "ref_doctype": doctype,
            "ref_docname": docname,
            "data": data,
            "event": event_type,
            "status": status,
            "date": nowdate()
        }
    )

    new_backlog.insert()

def sym_clear_backlogs(pos_client_name):

    # TODO: delete records using sql
    _entries = frappe.get_all(
        "POS SYNC Backlog",
        fields=["name"]
    )
    for entry in _entries:
        frappe.db.delete(
            "POS SYNC Backlog",
            filters={
                "name": entry.name,
                "pos_client": pos_client_name
            }
        )

# def get_child_tables_data(doctype_dict):
#     meta = frappe.get_meta(doctype_dict["doctype"])
#     table_fields = meta.get_table_fields()

#     child_tables = [{"fieldname": d.get("fieldname"), "table": d.get("options")} for d in table_fields]
#     data = []
    
#     for table_name in child_tables:
#         table_data = frappe.get_all(
#             table_name.get("table"),
#             fields="*",
#             filters={
#                 "parent": doctype_dict["name"]
#             },
#             order_by="modified asc"
#         )
#         doctype_dict[table_name.get("fieldname")] = table_data
#         # data.append(
#         #     {
#         #         table_name.get("table"): table_data
#         #     }
#         # )
#     print(data)
#     # return data


# def sym_create_backlog(client_id, ):
#     pos_client = sym_get_pos_client()
    
#     new_backlog = frappe.get_doc(
#         {
#             "doctype": "POS SYNC Backlog",
#             "pos_client": 
#         }
#     )
