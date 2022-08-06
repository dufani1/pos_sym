import frappe
from frappe.utils import now
from pos_sym.utils import sym_clear_backlogs, sym_create_backlog, sym_get_pos_clients

CONTROLLER_DOCTYPE = "POS Profile"

def doc_event(event_doc, event_name):
    if event_doc.doctype == CONTROLLER_DOCTYPE:
        if event_name == "validate":
            if not frappe.db.exists(event_doc.doctype, event_doc.name):
                # create doc
                create_insert_backlog(event_doc)
            else:
                # update doc
                create_update_backlog(event_doc)
        elif event_name == "on_trash":
            # trash doc
            create_delete_backlog(event_doc)

def create_insert_backlog(event_doc):
    # get pos clients
    pos_clients = sym_get_pos_clients()
     
    if pos_clients:
        # create insert backlogs for each pos client
        for pos_client in pos_clients:
            sym_create_backlog(
                pos_client=pos_client,
                doctype=CONTROLLER_DOCTYPE,
                docname=event_doc.name,
                data=event_doc.as_json(),
                event_type="Insert",
                status="Pending"
            )    

def create_update_backlog(event_doc):
    # get pos clients
    pos_clients = sym_get_pos_clients()
            
    if pos_clients:
        # create update backlogs for each pos client
        for pos_client in pos_clients:
            sym_create_backlog(
                pos_client_orm=pos_client,
                doctype=CONTROLLER_DOCTYPE,
                docname=event_doc.name,
                data=event_doc.as_json(),
                event_type="Update",
                status="Pending"
            )

def create_delete_backlog(event_doc):
    # get pos clients
    pos_clients = sym_get_pos_clients()
            
    if pos_clients:
        # create delete backlogs for each pos client
        for pos_client in pos_clients:
            sym_create_backlog(
                pos_client=pos_client,
                doctype=CONTROLLER_DOCTYPE,
                docname=event_doc.name,
                data=event_doc.as_json(),
                event_type="Delete",
                status="Pending"
            )    


def prepare(pos_client_orm):
    try:
        cond_filters = {}

        _entries = frappe.get_all(
            CONTROLLER_DOCTYPE,
            fields=["name"],
            filters=cond_filters,
            order_by="modified asc"
        )

        for entry in _entries:
            doc_orm = frappe.get_doc(CONTROLLER_DOCTYPE, entry.name)

            sym_create_backlog(
                pos_client_orm=pos_client_orm,
                doctype=doc_orm.doctype,
                docname=doc_orm.name,
                data=doc_orm.as_json(),
                event_type="Init",
                status="Pending"
            ) 
        return None
    except Exception as e:
        print(e)

