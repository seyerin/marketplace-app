import frappe
from frappe.exceptions import ValidationError, PermissionError

@frappe.whitelist()
def create_amended_proposal(name, new_price):
    try:
        # Get the original document
        original_doc = frappe.get_doc("Supplier Product Proposal", name)

        # --- PERBAIKAN UTAMA DIMULAI DI SINI ---
        # Logika pembatalan dipindahkan ke awal
        # agar dokumen lama dibatalkan terlebih dahulu.
        if original_doc.docstatus == 1:
            # Temporarily switch to the Administrator user to perform the cancellation
            current_user = frappe.session.user
            frappe.set_user("Administrator")
            
            try:
                # Get the doc again in the context of the new user session
                doc_to_cancel = frappe.get_doc("Supplier Product Proposal", name)
                doc_to_cancel.cancel()
                frappe.db.commit() # Commit the cancellation
            finally:
                # Always switch back to the original user
                frappe.set_user(current_user)

        # Reload the document to get its new state (cancelled)
        original_doc.reload()

        # Check if cancellation was successful
        if original_doc.docstatus != 2: # docstatus 2 means cancelled
             frappe.throw("Proposal tidak dapat dibatalkan. Silakan hubungi Administrator.", title="Pembatalan Gagal")
        
        # --- PERBAIKAN UTAMA BERAKHIR DI SINI ---

        # Create the new amended document from the cancelled original
        new_doc = frappe.copy_doc(original_doc)
        
        # Secara eksplisit reset docstatus dan stat ke status awal (Draft)
        new_doc.docstatus = 0
        new_doc.stat = "Draft"
        
        # Set the 'amended_from' field
        new_doc.amended_from = name
        
        # Update the price
        new_doc.supplier_price = new_price
        
        # Insert the new document with the current user's permissions. It will start as Draft.
        new_doc.insert()

        # Setelah dokumen dibuat sebagai Draft, kita ubah statusnya menjadi Pending
        # dan simpan untuk memicu transisi workflow.
        new_doc.stat = "Pending"
        new_doc.save()
        
        return new_doc.name

    except PermissionError as e:
        frappe.throw("Anda tidak memiliki izin untuk melakukan tindakan ini.", title="Izin Ditolak")
    except ValidationError as e:
        frappe.throw(str(e), title="Amendment Tidak Diizinkan")
    except Exception as e:
        # Log the full traceback for better debugging
        frappe.log_error(title="Kesalahan saat membuat amandemen", message=frappe.get_traceback())
        frappe.throw("Terjadi kesalahan yang tidak terduga. Mohon hubungi Administrator.", title="Kesalahan Sistem")
