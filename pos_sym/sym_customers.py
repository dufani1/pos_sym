import frappe
from frappe.utils import now
from pos_sym.utils import sym_clear_backlogs, sym_create_backlog, sym_get_pos_clients

EVENT_DOCS = [
    "Customer"
]


def sym_doc_event(event_doc, event_name):
    print("sym_doc_event: ", event_name, " doc: ", event_doc.doctype)
    if event_doc.doctype in EVENT_DOCS:
        if event_name == "validate":
            if not frappe.db.exists(event_doc.doctype, event_doc.name):
                # create doc
                create_customer(event_doc)
            else:
                # update doc
                update_customer(event_doc)
        elif event_name == "on_trash":
            # trash doc
            delete_customer(event_doc)

def create_customer(event_doc):
    # get pos clients
    pos_clients = sym_get_pos_clients()
     
    if pos_clients:
        # create insert backlogs for each pos client
        for pos_client in pos_clients:
            sym_create_backlog(
                pos_client=pos_client,
                doctype=event_doc.doctype,
                docname=event_doc.name,
                data=event_doc.as_json(),
                event_type="Insert",
                status="Pending"
            )    

def update_customer(event_doc):
    # get pos clients
    pos_clients = sym_get_pos_clients()
            
    if pos_clients:
        # create update backlogs for each pos client
        for pos_client in pos_clients:
            sym_create_backlog(
                pos_client_orm=pos_client,
                doctype=event_doc.doctype,
                docname=event_doc.name,
                data=event_doc.as_json(),
                event_type="Update",
                status="Pending"
            )

def delete_customer(event_doc):
    # get pos clients
    pos_clients = sym_get_pos_clients()
            
    if pos_clients:
        # create delete backlogs for each pos client
        for pos_client in pos_clients:
            sym_create_backlog(
                pos_client=pos_client,
                doctype=event_doc.doctype,
                docname=event_doc.name,
                data=event_doc.as_json(),
                event_type="Delete",
                status="Pending"
            )    


def sym_prepare_customer(pos_client_orm):
    try:
        cond_filters = {}

        # clear previus client logs
        sym_clear_backlogs(pos_client_orm.name)
        
        _entries = frappe.get_all(
            "Customer",
            fields=["name"],
            filters=cond_filters,
            order_by="modified asc"
        )

        for entry in _entries:
            doc_orm = frappe.get_doc("Customer", entry.name)

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



def validate_pos_client_criterias(event_doc, pos_client):
    """ Check if customer is in POS Profile Customer Groups Table """
    for pos_profile in pos_client.profiles:
        
        # check if current customer is in pos profile customer_groups
        customer_groups_table = frappe.get_all(
            "POS Customer Group",
            fields=["customer_group"],
            filters={
                "parent": pos_profile.pos_profile
            }
        )
        # if empty create backlog
        if len(customer_groups_table) == 0:
            return True
            break
        # else check the value exist in one of the table rows
        elif any(d["customer_group"] == event_doc.get("customer_group") for d in customer_groups_table):
            return True
            break
