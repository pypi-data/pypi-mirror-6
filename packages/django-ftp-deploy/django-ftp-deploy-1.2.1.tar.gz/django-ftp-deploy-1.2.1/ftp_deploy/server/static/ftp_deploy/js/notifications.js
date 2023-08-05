$(document).ready(function(){

    $(document).on('click', '#notification-delete',function(){
        var href = $(this).attr('href');
        var container = $(this).parents('.notification-actions');
        $('btn-group',container).remove();
        $(container).load(href + ' #page>*', function(){
        });
        return false;
    });


    //init notifications modal
    $(document).on('click', '#notifications',function(){
        var href = $(this).attr('href');
        var _this = $(this);
        $.ajax({
            type: "GET",
            url: href
        }).done(function(content) {
            $(_this).button('reset');
            $('body').append(content);
            $('#notifications-modal').modal('show');
            $('#notifications-modal').on('hidden.bs.modal', function () {
                $('#notifications-modal').remove();
            })
        });
        return false;
    });


    // add email to list
    $(document).on('click', '#notifications-form #add',function(){
        var email = $('#email').val()
        var filter = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;

        if(email != '' && filter.test(email)){
            $('#email').val('').parent().removeClass('has-error');
            $(this).parents('tr').before(
                '<tr>'+
                    '<td><input type="checkbox" name="_success" value="'+email+'" checked></td>'+
                    '<td><input type="checkbox" name="_fail" value="'+email+'" checked></td>'+
                    '<td>'+email+'</td>'+
                    '<td><a href="#" class="remove"><i class="fa fa-times c-remove"></i></a></td>'+
                '</tr>'
            );
        }else{
            $('#email').parent().addClass('has-error');
        }

        return false;
    });

    // remove email from list
    $(document).on('click', '#notifications-form .remove',function(){
        $(this).parents('tr').remove();
        return false;
    });



    //parse success and fail emails after submit notification form
    $(document).on('submit', '#notifications-form',function(){

        var action = $(this).attr('action');
        var data = $(this).serializeArray();
        var success = []; 
        var fail = []; 

        $(data).each(function(index){
            if(data[index].name == '_success') success.push(data[index].value)
            if(data[index].name == '_fail') fail.push(data[index].value)
        });

        $('input[name=success]',this).val(success.join());
        $('input[name=fail]',this).val(fail.join());

        return true;

    });

    

});

