import frappe

def get_user_location_from_address():
    """
    Mengambil nama wilayah dari alamat utama pengguna yang sedang login.
    """
    user = frappe.session.user
    if user == "Guest":
        return None

    try:
        # Mencari alamat utama (primary address) yang terkait dengan pengguna
        default_address = frappe.db.get_value(
            "Address", 
            {"link_doctype": "User", "link_name": user, "is_primary_address": 1},
            "name"
        )
        if default_address:
            city = frappe.db.get_value("Address", default_address, "city")
            return city
    except Exception as e:
        frappe.log_error(title="Gagal mendapatkan lokasi pengguna", message=str(e))

    return None

def filter_webshop_items(context):
    """
    Hook yang memfilter item webshop berdasarkan lokasi pembeli secara otomatis.
    """
    user_location = get_user_location_from_address()

    # Periksa apakah user_location sudah ada di Territory
    if user_location and frappe.db.exists("Territory", user_location):
        # Pastikan 'filters' ada di context
        if 'filters' not in context:
            context['filters'] = {}

        # Tambahkan filter lokasi ke query
        context['filters']['custom_lokasi_geografi'] = user_location

    return context