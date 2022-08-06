import frappe
import importlib
import pos_sym.sym_controllers as sym_controllers
from frappe.utils.data import nowdate
from pos_sym.utils import sym_clear_backlogs, sym_clear_pull_logs, sym_create_pull_log, sym_get_backlogs, sym_get_pos_client


@frappe.whitelist(allow_guest=False, methods=["POST"]) 
def send_backlogs():
    try:
        pos_client = sym_get_pos_client()
        
        # send all non success backlogs to the syc client
        sym_backlogs = sym_get_backlogs(pos_client)
        
        return sym_backlogs
    except Exception as e:
        print(frappe.get_traceback())

@frappe.whitelist(allow_guest=False, methods=["POST"]) 
def receive_backlogs():
    try:
        pos_client_orm = sym_get_pos_client()
        backlogs = frappe.form_dict["backlogs"]
        backlogs = frappe.parse_json(backlogs)
        if backlogs:
            # syc_clear_pull_logs()

            # insert received backlogs
            for bl in backlogs:
                sym_create_pull_log(
                    pos_client_orm=pos_client_orm,
                    syc_backlog_name=bl.get("name"),
                    event_type=bl.get("event"),
                    status=bl.get("status"),
                    doctype=bl.get("ref_doctype"),
                    docname=bl.get("ref_docname"),
                    data=bl.get("data")
                )
            return sym_eval_pull_logs()
        # return client_backlogs
    except Exception as e:
        print(frappe.get_traceback())

@frappe.whitelist(allow_guest=False, methods=["POST"])
def sym_eval_pull_logs():
    pull_logs = frappe.get_all(
        "SYM Pull Log",
        fields="*",
        order_by="modified asc",
        limit_page_length=10

    )
    success_pull_logs = []

    for plog in pull_logs:
        print(f"Event: {plog.event} Status: {plog.status} Name: {plog.name}")
        if plog.status == "Success": 
            print(f"Skiping: {plog.name}")
            continue

        if plog.status == "Failed":
            print(f"Breaking due to: {plog.name}")
            break

        if plog.event == "Init" or plog.event == "Insert":
            try:
                
                parsed_log_data = frappe.parse_json(plog.data)
                parsed_log_data["doctype"] = plog.ref_doctype
                
                frappe.delete_doc_if_exists(doctype=plog.ref_doctype, name=plog.ref_docname, force=True)

                new_insert = frappe.get_doc(parsed_log_data) 
                new_insert.insert()
                frappe.db.set_value("SYM Pull Log", dn=plog.name, field="status", val="Success", update_modified=False)
                
                success_pull_logs.append(plog.syc_backlog_name)

            except Exception as e:
                frappe.db.set_value("SYM Pull Log", dn=plog.name, field="status", val="Failed", update_modified=False)
                print(e)
        elif plog.event == "Update":
            try:
                parsed_log_data = frappe.parse_json(plog.data)
                parsed_log_data["doctype"] = plog.ref_doctype
                
                frappe.delete_doc_if_exists(doctype=plog.ref_doctype, name=plog.ref_docname, force=True)

                new_insert = frappe.get_doc(parsed_log_data) 
                new_insert.insert()
                
                frappe.db.set_value("SYM Pull Log", dn=plog.name, field="status", val="Success", update_modified=False)

                success_pull_logs.append(plog.syc_backlog_name)

            except Exception as e:
                frappe.db.set_value("SYM Pull Log", dn=plog.name, field="status", val="Failed", update_modified=False)
                print(e)

    return success_pull_logs

# notify controllers of doc events
def sym_doc_event(doc, event):
    for idx, sym_ctl in enumerate(sym_controllers.__all__):
        module_spec = importlib.util.spec_from_file_location(sym_ctl[idx], sym_controllers.modules[idx])
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module) 
        module.doc_event(doc, event)

@frappe.whitelist(allow_guest=False, methods=["POST"])
def prepare():
    try:
        # pos_client_name = sym_get_pos_client().name
        # enqueue(_prepare, queue="long", is_async=True, job_name=f"SYM Prepare POS, POS Client: {pos_client_name}")
        _prepare()

        return True
    except Exception as e:
        print(e)
        return False

def _prepare():
    try:
        # Prepare the required Backlogs for this pos client
        pos_client_orm = sym_get_pos_client()
        pos_client_orm.is_prepared = 1
        pos_client_orm.preparation_date = nowdate()

        pos_client_orm.save()

        # Prepare Controllers
        # sym_prepare_customer(pos_client_orm)

         # clear previus client logs before preparing new logs
        sym_clear_backlogs(pos_client_orm.name)
        for idx, sym_ctl in enumerate(sym_controllers.__all__):
            module_spec = importlib.util.spec_from_file_location(sym_ctl[idx], sym_controllers.modules[idx])
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module) 
            module.prepare(pos_client_orm)
            
    except Exception as e:
        print(e)


@frappe.whitelist(allow_guest=False, methods=["POST"])
def revoke():
    try:
        # pos_client_name = sym_get_pos_client().name
        # frappe.enqueue(_prepare, queue="long", is_async=True, job_name=f"SYM Prepare POS, POS Client: {pos_client_name}")
        _revoke()

        return True
    except Exception as e:
        print(e)
        return False

def _revoke():
    try:
        # Revoke all POS Client preparations
        pos_client_orm = sym_get_pos_client()
        pos_client_orm.is_prepared = 0
        pos_client_orm.preparation_date = None

        # clear pos clients backlogs
        sym_clear_backlogs(pos_client_orm.name)
        sym_clear_pull_logs(pos_client_orm.name)
        
        pos_client_orm.save()

        return True
    except Exception as e:
        print(e)
        return False

@frappe.whitelist(allow_guest=False, methods=["POST"]) 
def sym_confirm_backlogs():

    """ confirm received success pull logs from syc """
    success_pull_logs = frappe.form_dict["success_pull_logs"]

    if success_pull_logs:
        for plog in frappe.parse_json(success_pull_logs):
            frappe.db.set_value(
                "SYM Backlog",
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


