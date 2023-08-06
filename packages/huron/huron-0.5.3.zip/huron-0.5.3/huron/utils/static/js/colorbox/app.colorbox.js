django.jQuery(document).ready(function() {
    django.jQuery(".colorbox").colorbox({rel:'gal'});
    django.jQuery(".colorbox-iframe-r").colorbox({iframe:true,
                                                 width:"80%",
                                                 height:"80%",
                                                 onClosed: function() {
                                                     location.reload();
                                                 }});
});