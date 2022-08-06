import frappe
from frappe import enqueue
from frappe.utils.data import nowdate
from pos_sym.sym_controllers.customer_controller import sym_prepare_customer
from pos_sym.utils import sym_clear_backlogs, sym_get_pos_client

PREPARE_CONTROLLERS = [
    sym_prepare_customer
]

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
        for prepare_ctl in PREPARE_CONTROLLERS:
            prepare_ctl(pos_client_orm)

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

        pos_client_orm.save()

        return True
    except Exception as e:
        print(e)
        return False