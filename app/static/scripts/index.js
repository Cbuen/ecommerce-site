$(document).ready(function() {
    $('.product-list-addtocart-button').click(function() {
        var productId = $(this).data('product-id');
        $.ajax({
            url: '/products',
            type: 'POST',
            data: JSON.stringify({'product_id': productId}),
            contentType: 'application/json',
            success: function(response) {
                alert('Product added to cart successfully!');
                console.log(this.data);
            },
            error: function(error) {
                console.log(error);
                alert('Error adding product to cart.');
            }
        });
    });
});


$(document).ready(function() {
    $('.remove-scroll-item').click(function() {
        var productId = $(this).data('product-id');
        var productQuantity = $(this).data('product-quantity')
        $.ajax({
            url: '/cart',
            type: 'POST',
            data: JSON.stringify({'product_id': productId,
                'product-quantity': productQuantity
            }),
            contentType: 'application/json',
            success: function() {
                location.reload()
            },
            error: function(error) {
                console.log(error);
                alert('Product could not be removed from cart?');
            }
        });
    });
});
