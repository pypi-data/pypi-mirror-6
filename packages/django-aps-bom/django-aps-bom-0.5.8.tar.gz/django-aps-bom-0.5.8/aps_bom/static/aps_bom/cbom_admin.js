django.jQuery(document).ready(function() {
    $('#id_customer').on('change', function(){
        $.ajax({
            url: ddl_ajax_url
            ,data: {
                'action': 'get_epn_choices_for_customer'
                ,'obj_id': $('#id_customer').val()
            }
            ,success: function(data){
                $('[name*=-epn][name*=cbomitems-]').each(function(){
                    $(this).html(data);
                });
            }
        });
    });
});
