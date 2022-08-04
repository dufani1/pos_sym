import frappe
from pos_sym.utils import sym_get_backlogs, sym_get_pos_client

@frappe.whitelist(allow_guest=False, methods=["POST"]) 
def pull_backlogs():
    try:
        pos_client = sym_get_pos_client()
        
        # send all non success backlogs to the syc client
        client_backlogs = sym_get_backlogs(pos_client)
        
        return client_backlogs
    except Exception as e:
        print(frappe.get_traceback())


@frappe.whitelist(allow_guest=False, methods=["POST"]) 
def sym_confirm_backlogs():

    """ confirm received success pull logs from syc """
    success_pull_logs = frappe.form_dict["success_pull_logs"]

    if success_pull_logs:
        for plog in frappe.parse_json(success_pull_logs):
            frappe.db.set_value(
                "POS SYNC Backlog",
                dn=plog.get("sym_backlog_name"),
                field="status",
                val="Success",
                update_modified=False
            )

# def get_child_tables_data(doctype, docname):
#     meta = frappe.get_meta(doctype)
#     table_fields = meta.get_table_fields()
#     child_tables = [{"fieldname": d.get("fieldname"), "table": d.get("options")} for d in table_fields]
#     data = []
#     for table_name in child_tables:
#         table_data = frappe.get_all(
#             table_name.get("table"),
#             fields="*",
#             filters={
#                 "parent": docname
#             },
#             order_by="modified asc"
#         )

#         data.append(
#             {
#                 table_name.get("table"): table_data
#             }
#         )
#     print(data)
#     return data


