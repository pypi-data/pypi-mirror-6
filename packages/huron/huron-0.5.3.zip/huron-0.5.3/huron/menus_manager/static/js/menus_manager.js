jQuery(function($) {
    $('a.expands').click(function() {
        $(this).next().next().next().next().toggle();
        $(this).next().next().next().toggle();
        return false;
    });
    $("#item-list, #item-list ul" ).sortable({
      connectWith: ".connected-sortable",
      update: function(event, ui) {
          //change order, maybe parent. So call Ajax helper to record that
          //firstly, find the li.menu-item parent, if exists
          var parent = $(ui.item).closest('ul').closest('li.menu-item').attr('data-pk');
          var sorting = $('li', $(ui.item).parent('ul')).index(ui.item);
          //alert(ui.offset.top+' '+ui.originalPosition.top);
          if($(ui.item).attr('data-sorting') != sorting || $(ui.item).attr('data-parent') != parent) {
              $(ui.item).attr('data-sorting', sorting);
              $(ui.item).attr('data-parent', parent);
              var values = {}
              values['item-pk'] = $(ui.item).attr('data-pk');
              values['parent'] = parent;
              values['sorting'] = sorting;
              values['csrfmiddlewaretoken'] = $('form[name=add-item] input[name=csrfmiddlewaretoken]').val();
              $.ajax({
                    type: "POST",
                    dataType: "json",
                    url: '/api-menu/sort/item/',
                    data: values,
                    success: function(data, textStatus) {
                        var data = $.parseJSON(data);
                        if(data.status == 'ok') {
                            $('#edit-message').html('Élément correctement trié.');
                        }
                        else {
                            $('#edit-message').html('Erreur lors de l\'enregistrement du tri.');
                        }
                    },
                    error: function(errorObj, textStatus, errorThrown) {
                        $('#edit-message').html('Erreur lors du tri de l\'élément.');
                    },
                });
          }
      }
    }).disableSelection();
    $("form[name=add-item]").submit(function() {
        var values = {};
        values['menu-pk'] = $('#menu-pk_new').val();
        values['nav_title'] = $('#nav_title_new').val();
        values['url'] = $('#url_new').val();
        values['css_class'] = $('#css_class_new').val();
        values['target_blank'] = $('#target_blank_new').attr('checked');
        values['html_title'] = $('#html_title_new').val();
        values['description'] = $('#description_new').val();
        values['csrfmiddlewaretoken'] = $('form[name=add-item] input[name=csrfmiddlewaretoken]').val();
        $.ajax({
                type: "POST",
                dataType: "json",
                url: '/api-menu/add/item/',
                data: values,
                success: function(data, textStatus) {
                    var data = $.parseJSON(data);
                    if(data.status == 'ok') {
                        $('#add-message').html('Élément correctement ajouté.');
                        location.reload();
                    }
                    else {
                        $('#add-message').html('Erreur lors de l\'enregistrement de l\'élément.');
                    }
                },
                error: function(errorObj, textStatus, errorThrown) {
                    $('#add-message').html('Erreur lors de l\'ajout de l\'élément.');
                },
            });
        return false;
    });
    $("form[name=update-item]").submit(function() {
        var values = {};
        values['item-pk'] = $('input[name=pk]', this).val();
        values['nav_title'] = $('input[name=nav_title]', this).val();
        values['url'] = $('input[name=url]', this).val();
        values['css_class'] = $('input[name=css_class]', this).val();
        values['target_blank'] = $('input[name=target_blank]', this).attr('checked');
        values['html_title'] = $('input[name=html_title]', this).val();
        values['description'] = $('textarea[name="description"]', this).val();
        values['csrfmiddlewaretoken'] = $('form[name=add-item] input[name=csrfmiddlewaretoken]').val();
        $.ajax({
                type: "POST",
                dataType: "json",
                url: '/api-menu/edit/item/',
                data: values,
                success: function(data, textStatus) {
                    var data = $.parseJSON(data);
                    if(data.status == 'ok') {
                        $('#edit-message').html('Élément correctement modifié.');
                        location.reload();
                    }
                    else {
                        $('#edit-message').html('Erreur lors de l\'enregistrement de l\'élément.');
                    }
                },
                error: function(errorObj, textStatus, errorThrown) {
                    $('#edit-message').html('Erreur lors de l\'ajout de l\'élément.');
                },
            });
        return false;
    });
    $('.delete-node').click(function() {
        var values = {};
        values['item-pk'] = $(this).attr('data-id');
        values['csrfmiddlewaretoken'] = $('form[name=add-item] input[name=csrfmiddlewaretoken]').val();
        $.ajax({
                type: "POST",
                dataType: "json",
                url: '/api-menu/del/item/',
                data: values,
                success: function(data, textStatus) {
                    var data = $.parseJSON(data);
                    if(data.status == 'ok') {
                        $('#edit-message').html('Élément correctement supprimé.');
                        location.reload();
                    }
                    else {
                        $('#edit-message').html('Erreur lors de l\'enregistrement de l\'élément.');
                    }
                },
                error: function(errorObj, textStatus, errorThrown) {
                    $('#edit-message').html('Erreur lors de l\'ajout de l\'élément.');
                },
            });
        return false;
    })
});