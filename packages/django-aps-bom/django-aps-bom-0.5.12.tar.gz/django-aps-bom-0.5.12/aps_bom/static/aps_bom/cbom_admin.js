function update_choices() {
    $.ajax({
        url: ddl_ajax_url
        ,data: {
            'action': 'get_epn_choices_for_customer'
            ,'obj_id': $('#id_customer').val()
        }
        ,success: function(data){
            $('[name*=-epn][name*=cbomitems-]').each(function(){
                var current_value = $(this).val();
                $(this).html(data);
                $(this).val(current_value);
            });
        }
    });
}
django.jQuery(document).ready(function() {
    update_choices();
    $('#id_customer').on('change', function(){
        update_choices();
    });
});
