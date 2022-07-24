import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from frappe.event_streaming.doctype.event_update_log.event_update_log import get_update
from frappe.utils import random_string

STATE_HASH_FIELDNAME = "sync_state_hash4"

# Generate state hash for all doctype entries
def gen_doc_state_hashes(doctype: str):
    frappe.set_user("administrator")
    doctype_has_state_hash = frappe.db.sql(f"""
        SHOW COLUMNS FROM `tab{doctype}` LIKE '{STATE_HASH_FIELDNAME}'
    """, as_dict=True)
    new_hash = random_string(20)

    # doc has no state hash
    if len(doctype_has_state_hash) == 0:
        # todo make hidden
        df = dict(
            fieldname=STATE_HASH_FIELDNAME,
            label="Sync State hash",
            fieldtype="Data",
            read_only=1,
            hidden = 0,
            print_hide=1,
            is_custom_field=1
        )
        create_custom_field(doctype, df)
        # todo set all entries using sql
        doc_entries = frappe.get_all(doctype)

        for entry in doc_entries:
            frappe.db.set_value(doctype, entry.name, STATE_HASH_FIELDNAME, new_hash)

# Generate state hash for a doc
def gen_doc_state_hash(doc):
    new_hash = random_string(20)
    doc.sync_state_hash4 = new_hash

def get_sync_docs(doctype: str, state_hash) -> list:
    sync_docs = frappe.get_all(
        doctype,
        fields=["name", STATE_HASH_FIELDNAME, "item_group"],
        filters={STATE_HASH_FIELDNAME: ("!=", state_hash)}
    )

    return sync_docs


@frappe.whitelist(allow_guest=True, methods=["GET"]) 
def main():
    # item_sync_docs = get_sync_docs("Item", state_hash)
    pass


@frappe.whitelist(allow_guest=False, methods=["GET"]) 
def get_items_for_sync():
    args = frappe.request.args
    items = []
    cond_filters = {}


    if "last_update" in args:
        cond_filters["modified"] = (">", args.get("last_update"))
        
    _items = frappe.get_all("Item", fields="*", filters=cond_filters, order_by="modified asc")

    for item in _items:
        items.append(item)
    return items



def get_doc_tables(docname: str) -> list:
    meta = frappe.get_meta(docname)
    table_fields = meta.get_table_fields()

    # for df in table_fields:
    #     child_table = doc.get(df.fieldname)
    #     for entry in child_table:
    #         child_doc = frappe.get_doc(entry.doctype, entry.name)
    #         if child_doc:
    #             # child_doc = frappe._dict(child_doc)
    #             child_doc_links = frappe.get_meta(entry.doctype).get_link_fields()
    #             set_dependencies(child_doc, child_doc_links)
    return table_fields

# def before_insert(doc, method):
#     if doc.doctype == "Item":
#         print(doc)

# generate state hash on any doc change
def notify_change(doc, event):
    if doc.doctype == "Item":
        
        if event == "after_insert":
            new_update = frappe.get_doc(
                {
                    "doctype": "SYM Update Logs",
                    "update_type": "Update",
                    "ref_doctype": doc.doctype,
                    "docname": doc.name,
                    "data": frappe.as_json(new_update)
                }
            )
            new_update.insert(ignore_permissions=True)
        elif event == "on_update":
            diff = get_update(doc.get_doc_before_save(), doc)
            new_update = frappe.get_doc(
                {
                    "doctype": "SYM Update Logs",
                    "update_type": "Update",
                    "ref_doctype": doc.doctype,
                    "docname": doc.name,
                    "data": frappe.as_json(diff["changed"])
                }
            )
            new_update.insert(ignore_permissions=True)
            
        elif event == "on_trash":
            pass

            # frappe.throw("a")

def get_last_update():
	"""get the creation timestamp of last update consumed"""
	updates = frappe.get_list(
		"Event Update Log", "creation", ignore_permissions=True, limit=1, order_by="creation desc"
	)
	if updates:
		return updates[0].creation
	return frappe.utils.now_datetime()


def get_dependencies(doc):
    document = frappe.get_doc("Item", doc)
    dependencies = {document: True}
    deps = []
    def check_doc_has_dependencies(doc):
        """Sync child table link fields first,
        then sync link fields,
        then dynamic links"""
        meta = frappe.get_meta(doc.doctype)
        table_fields = meta.get_table_fields()
        link_fields = meta.get_link_fields()
        dl_fields = meta.get_dynamic_link_fields()
        if table_fields:
            sync_child_table_dependencies(doc, table_fields)
        if link_fields:
            sync_link_dependencies(doc, link_fields)
        if dl_fields:
            sync_dynamic_link_dependencies(doc, dl_fields)

    def sync_child_table_dependencies(doc, table_fields):
        for df in table_fields:
            child_table = doc.get(df.fieldname)
            for entry in child_table:
                child_doc = frappe.get_doc(entry.doctype, entry.name)
                if child_doc:
                    # child_doc = frappe._dict(child_doc)
                    child_doc_links = frappe.get_meta(entry.doctype).get_link_fields()
                    set_dependencies(child_doc, child_doc_links)

    def sync_link_dependencies(doc, link_fields):
        set_dependencies(doc, link_fields)

    def sync_dynamic_link_dependencies(doc, dl_fields):
        for df in dl_fields:
            docname = doc.get(df.fieldname)
            linked_doctype = doc.get(df.options)
            # if docname and not check_dependency_fulfilled(linked_doctype, docname):
                # master_doc = producer_site.get_doc(linked_doctype, docname)
                # frappe.get_doc(master_doc).insert(set_name=docname)

    def set_dependencies(doc, link_fields):
        print(f"Main Doctype: {document.name} depends on:")
        for df in link_fields:
            docname = doc.get(df.fieldname)
            linked_doctype = df.get_link_doctype()
            if docname:
                master_doc = frappe.get_doc(linked_doctype, docname)
                try:
                    master_doc = frappe.get_doc(master_doc)
                    deps.append({"doctype": linked_doctype.name, "value": master_doc.name})
                    # print(f"""
                    #     Doctype: {master_doc.doctype} entry: {master_doc.name}
                    #     DocField: {df.label} {df.fieldname} {df.fieldtype}
                    #     """ )
                    # master_doc.insert(set_name=docname)
                    # frappe.db.commit()

                # for dependency inside a dependency
                except Exception as e:
                    tb = frappe.get_traceback()
                    print(tb)
                    dependencies[master_doc] = True

    # def check_dependency_fulfilled(linked_doctype, docname):
    #     return frappe.db.exists(linked_doctype, docname)

    while dependencies[document]:
        # find the first non synced dependency
        for item in reversed(list(dependencies.keys())):
            if dependencies[item]:
                dependency = item
                break

        check_doc_has_dependencies(dependency)

        # mark synced for nested dependency
        if dependency != document:
            dependencies[dependency] = False
            # dependency.insert()

        # no more dependencies left to be synced, the main doc is ready to be synced
        # end the dependency loop
        if not any(list(dependencies.values())[1:]):
            dependencies[document] = False
            print(deps)