// Real-time invoice calculation - FIXED VERSION
function calculateTotals() {
    console.log('Calculating totals...');
    let subtotal = 0;

    // Calculate line totals for each item
    $('.item-row').each(function() {
        const $row = $(this);
        const isDeleted = $row.find('input[type="checkbox"][name*="DELETE"]').is(':checked');
        
        if (!isDeleted) {
            // Find inputs by name attribute pattern
            const $qtyInput = $row.find('input[name*="quantity"]');
            const $priceInput = $row.find('input[name*="unit_price"]');
            
            const quantity = parseFloat($qtyInput.val()) || 0;
            const unitPrice = parseFloat($priceInput.val()) || 0;
            const lineTotal = quantity * unitPrice;
            
            console.log('Row - Qty:', quantity, 'Price:', unitPrice, 'Total:', lineTotal);
            
            $row.find('.line-total').val(lineTotal.toFixed(2));
            subtotal += lineTotal;
        } else {
            $row.find('.line-total').val('0.00');
        }
    });

    // Get tax rate and discount
    const taxRate = parseFloat($('#id_tax_rate').val()) || 0;
    const discountAmount = parseFloat($('#id_discount_amount').val()) || 0;

    // Calculate tax amount
    const taxAmount = (subtotal * taxRate) / 100;

    // Calculate total
    const total = subtotal + taxAmount - discountAmount;

    console.log('Subtotal:', subtotal, 'Tax:', taxAmount, 'Discount:', discountAmount, 'Total:', total);

    // Update display
    $('#subtotal-display').text(subtotal.toFixed(2));
    $('#tax-display').text(taxAmount.toFixed(2));
    $('#discount-display').text(discountAmount.toFixed(2));
    $('#total-display').text(total.toFixed(2));
}

$(document).ready(function() {
    console.log('Invoice form loaded');
    
    // Attach calculation events - using attribute selectors for Django form names
    $(document).on('input', 'input[name*="quantity"], input[name*="unit_price"], #id_tax_rate, #id_discount_amount', function() {
        console.log('Input detected:', $(this).attr('name'), '=', $(this).val());
        calculateTotals();
    });
    
    $(document).on('change', 'input[type="checkbox"][name*="DELETE"]', function() {
        if ($(this).is(':checked')) {
            $(this).closest('.item-row').addClass('text-muted');
        } else {
            $(this).closest('.item-row').removeClass('text-muted');
        }
        calculateTotals();
    });
    
    // Get current form count
    let formCount = parseInt($('#id_items-TOTAL_FORMS').val()) || 1;
    console.log('Initial form count:', formCount);
    
    // Add item button handler
    $('#add-item-btn').on('click', function(e) {
        e.preventDefault();
        console.log('Add item clicked! Current count:', formCount);
        
        const $container = $('#item-formset');
        const $template = $('.item-row:first').clone();
        
        // Clear all input values
        $template.find('input:not([type="hidden"]), select, textarea').val('');
        $template.find('input[type="checkbox"]').prop('checked', false);
        $template.find('.line-total').val('0.00');
        $template.removeClass('text-muted');
        
        // Update all name and id attributes with new index
        $template.find('input, select, textarea').each(function() {
            ['name', 'id'].forEach(attr => {
                const val = $(this).attr(attr);
                if (val) {
                    // Replace items-0- with items-{formCount}-
                    $(this).attr(attr, val.replace(/-\d+-/, `-${formCount}-`));
                }
            });
        });
        
        // Update label for attributes
        $template.find('label').each(function() {
            const forAttr = $(this).attr('for');
            if (forAttr) {
                $(this).attr('for', forAttr.replace(/-\d+-/, `-${formCount}-`));
            }
        });
        
        // Append new form
        $container.append($template);
        
        // Increment counter
        formCount++;
        $('#id_items-TOTAL_FORMS').val(formCount);
        
        console.log('New form added! New count:', formCount);
        calculateTotals();
    });
    
    // Initial calculation after page load
    setTimeout(function() {
        console.log('Running initial calculation...');
        calculateTotals();
    }, 500);
});