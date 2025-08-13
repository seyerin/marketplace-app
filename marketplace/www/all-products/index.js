$(() => {
	class ProductListing {
		constructor() {
			let me = this;
			let is_item_group_page = $(".item-group-content").data("item-group");
			this.item_group = is_item_group_page || null;

			let view_type = localStorage.getItem("product_view") || "List View";

			// Render Product Views, Filters & Search
			new webshop.ProductView({
				view_type: view_type,
				products_section: $('#product-listing'),
				item_group: me.item_group
			});

			this.bind_card_actions();
			this.bind_price_slider();
		}

		bind_card_actions() {
			webshop.webshop.shopping_cart.bind_add_to_cart_action();
			webshop.webshop.wishlist.bind_wishlist_action();
		}

  		bind_price_slider() {
            let minInput = $('#min-price');
            let maxInput = $('#max-price');

            const updateProducts = () => {
                let params = frappe.utils.get_query_params();
                params.min_price = minInput.val();
                params.max_price = maxInput.val();

                fetch(window.location.pathname + '?' + frappe.utils.get_url_from_dict(params))
                    .then(res => res.text())
                    .then(html => {
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(html, "text/html");
                        const newProducts = doc.querySelector("#product-listing").innerHTML;
                        $("#product-listing").html(newProducts);
                    });
            };

            minInput.on('input change', updateProducts);
            maxInput.on('input change', updateProducts);
        }
	}

	new ProductListing();
});
