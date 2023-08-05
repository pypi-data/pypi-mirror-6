$(document).ready(function(){

    /* Defaults */
    /*-----------------------------------------------------------------------------*/
    init();

    /* Dashboars */
    /*-----------------------------------------------------------------------------*/

    $("#service-filter select").select2({
        allowClear: true
    });


    $('#service-filter').bind('change', function () {
        var action = $(this).attr('action');
        var services= $('select[name=services]',this).val();

        $('#service-list').css('opacity',0.5)
        if ($("input[name=status]").is(":checked")) status = 0;
        $('.pagination').remove();
        $('#service-list').load(action + ' #service-list >* ', {services:services} , function(){
            $('#service-list').css('opacity',1);
            init();
        });

        return false;
    });


    $(document).on('click', '.service-list-status',function(){
        var container = $(this).parents('tr')
        var href = $(this).attr('href');

        $(this).html('<i class="fa fa-spinner fa-spin c-default"></i>');

        $(container).load(href + ' #service-list tr>*', {response:'list'}, function(){
            init();
        });
        return false;
    });

    

    /* Log */
    /*-----------------------------------------------------------------------------*/

    $("#log-filter select").select2({
    	allowClear: true
    });


	$('#log-filter').bind('change', function () {
		var action = $(this).attr('action');
        var services= $('select[name=services]',this).val();
        var status= 1;

        $('#log-list').css('opacity',0.5)
		if ($("input[name=status]").is(":checked")) status = 0;
		$('.pagination').remove();
    	$('#log-list').load(action, {services:services, status:status} , function(){
    		$('#log-list').css('opacity',1);
            init();
    	});

    	return false;
    });


    /* Service Manage */
    /*-----------------------------------------------------------------------------*/

    $(document).on('click', '#service-delete',function(){
        var href = $(this).attr('href');
        var container = $('#service-actions');
        $('btn-group',container).remove();
        $(container).load(href + ' #page>*', function(){
        });
        return false;
    });

    // refresh status
    $(document).on('click', '#service-manage-status',function(){
        var href = $(this).attr('href');
        var container = $('#page');

        $(this).html('<i class="fa fa-spinner fa-spin c-default"></i>');

        $(container).load(href + ' #page>*', {response: 'manage'}, function(){
            $(container).css('opacity',1);
            init();
        });
        return false;
    });

    // add POST hook
    $(document).on('click', '#add_hook',function(){
        var href = $(this).attr('href');
        var _this = $(this);
        $(this).replaceWith('<i class="fa fa-spinner fa-spin c-default"></i>');
        $.ajax({
            type: "POST",
            url: href,
            dataType: 'json',
            data:{data: 'addhook'}
        }).done(function(content) {
            $('#service-manage-status').click();
        }).fail(function(){
            $(_this).replaceWith('<i class="fa fa-times c-remove"></i>')
        });
        return false;
    });

    // skip log
    $(document).on('click', '.log-skip',function(){
        $(this).hide().next().show();
        return false;
    });

    // skip log confirmation
    $(document).on('click', '.log-skip-confirm',function(){
        var href = $(this).attr('href');
        var container = $(this).parents('tr')
        $.ajax({
            type: "POST",
            url: href
        }).done(function() {
            $(container).fadeOut()
        });
        return false;
    });


    // init restore modal box
    $(document).on('click', '#restore-init',function(){
        var href = $(this).attr('href');
        var _this = $(this);
        $(_this).button('loading');
        $.ajax({
            type: "GET",
            url: href
        }).done(function(content) {
            $(_this).button('reset');
            $('body').append(content);
            $('#restore-modal').modal('show');
            $('#restore-modal').on('hidden.bs.modal', function () {
                $('#restore-modal').remove();
            })
        });
        return false;
    });


    // restore deploys
    $(document).on('submit', '#restore-form',function(){
        var action = $(this).attr('action');
        var payload = $('input[name=payload]',this).val();

        $('#status-modal').remove()
        $.ajax({
            type: "POST",
            url: action,
            data:{payload: payload}
        }).done(function(content) {
            $('#restore-modal').modal('hide');
            $('#fail-deploys').remove();
            $('#deploy-progress').slideDown();

            $.ajax({
                type: "POST",
                url: content,
                data:{payload: payload}
            }).done(function() {
                $('#deploy-progress').hide().before('<div class="alert alert-success">Resore completed!</div>')
            }).fail(function(content) {
                $('#deploy-progress').hide().before('<div class="alert alert-danger">Resore fail!</div>')
            }).always(function(){
                $('#service-manage-status').click();
            });

        }).fail(function(content) {
            $('#restore-modal .modal-header').append('<div id="status-modal"><br/><div class="alert alert-danger"><b>Error has occurred.</b><br>Please refresh the page and try again</div></div>')
        });
        return false;
    });

    // service notification
    $(document).on('click', '#notification',function(){
        var href = $(this).attr('href');
        var _this = $(this);
        
        $.ajax({
            type: "GET",
            url: href
        }).done(function(content) {
            $('body').append(content);
            $('#notification-modal').modal('show');
            $('#notification-modal').on('hidden.bs.modal', function () {
                $('#notification-modal').remove();
            })
        });
        return false;
    });

 



    /* service add/edit form */
    /*-----------------------------------------------------------------------------*/

    $('#id_repo_source').bind('change', function () {
        var val = $(this).val()
        var action = $(this).attr('data-action');
        var options = '<option></option>';


        if (val == ''){
            $('#id_repo_name').show().next().hide();
            return false;
        }
        if(val == 'bb') data = 'respositories';
        
        $.ajax({
            type: "POST",
            url: action,
            dataType: 'json',
            data:{data: data}
        }).done(function(content) {
            content = $.parseJSON(content)
            $.each (content, function (index) {
                options += '<option value="'+content[index].name+'">'+content[index].name+'</option>';
            });
            $('#id_repo_name').hide().after('<select class="select form-control" id="id_repo_name_select" name="repo_name_select" placeholder="Select Repository">'+options+'</select>')
            $("#id_repo_name_select").select2({});
        });
    });

    $(document).on('change', '#id_repo_name_select',function(){
        var val = $(this).val();
        $('#id_repo_name').val(val).show().focus().hide();
    });

   


});

function init(){
    "Initial properties"
    $('i[data-toggle=tooltip]').tooltip({html:true,delay:300});
    $('*[data-toggle=popover]').popover({html:true,delay:0,placement:'left'}).css('cursor','pointer');
}