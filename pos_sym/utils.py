import imp
import frappe
from frappe.model.document import Document
from frappe.utils.data import nowdate

def sym_get_backlogs(pos_client):
    # we send only Pending backlogs
    backlogs = []
    _backlogs = frappe.get_all(
        "SYM Backlog",
        fields="*",
        filters={
            "pos_client": pos_client.name
        },
        order_by="modified asc"
    )

    for bl in _backlogs:
        if bl.status == "Success":
            continue
        if bl.status == "Failed":
            break
        
        backlogs.append(
            bl
        )
    return backlogs

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
            "doctype": "SYM Backlog",
            "pos_client": pos_client_orm.name,
            "client_id": pos_client_orm.client_id,
            "ref_doctype": doctype,
            "ref_docname": docname,
            "data": data,
            "event": event_type,
            "status": status,
            "create": nowdate()
        }
    )

    new_backlog.insert()

def sym_clear_backlogs(pos_client_name):

    # TODO: delete records using sql
    _entries = frappe.get_all(
        "SYM Backlog",
        fields=["name"],
        filters={
            "pos_client": pos_client_name
        }
    )
    for entry in _entries:
        frappe.db.delete(
            "SYM Backlog",
            filters={
                "name": entry.name
            }
        )

def sym_clear_pull_logs(pos_client_name):

    # TODO: delete records using sql
    _entries = frappe.get_all(
        "SYM Pull Log",
        fields=["name"],
        filters={
            "pos_client": pos_client_name
        }
    )
    for entry in _entries:
        frappe.db.delete(
            "SYM Pull Log",
            filters={
                "name": entry.name
            }
        )
    
def sym_create_pull_log(pos_client_orm, syc_backlog_name, event_type, status, doctype=None, docname=None, data=None):
    try:
        pull_log_exist = frappe.get_all(
            "SYM Pull Log",
            filters={
                "syc_backlog_name": syc_backlog_name
            }
        )
        if len(pull_log_exist) == 0:
            new_backlog = frappe.get_doc(
                {
                    "doctype": "SYM Pull Log",
                    "syc_backlog_name": syc_backlog_name,
                    "pos_client": pos_client_orm.name,
                    "client_id": pos_client_orm.client_id,
                    "event": event_type,
                    "status": status,
                    "ref_doctype": doctype,
                    "ref_docname": docname,
                    "data": data,
                    "create": nowdate()
                }
            )

            new_backlog.insert()
    except Exception as e:
        print("SYC Error", e)

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
#             "doctype": "SYM Backlog",
#             "pos_client": 
#         }
#     )
