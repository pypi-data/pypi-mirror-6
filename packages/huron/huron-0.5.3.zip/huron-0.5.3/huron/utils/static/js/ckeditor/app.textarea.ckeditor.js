django.jQuery(function()
{
    var config = {
        language : 'fr',
        //contentsCss : '/static/css/style.css',
        bodyId : 'page-ckeditor',
        filebrowserBrowseUrl : '/admin/browser/browse/type/all',
        filebrowserImageBrowseUrl : '/admin/browser/browse/type/image',
        filebrowserWindowWidth  : 1000,
        enterMode : CKEDITOR.ENTER_P,
        ignoreEmptyParagraph : true,
        skin : 'moono-dark',
        toolbar : 'Cms',
        toolbar_Cms : [
            ['Source'],
            ['Cut','Copy','Paste','PasteText','PasteFromWord'],
            ['Undo','Redo','-','SelectAll','RemoveFormat'],
            ['Bold','Italic','-','Subscript','Superscript'],
            ['NumberedList','BulletedList','-','Outdent','Indent','Blockquote'],
            ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
            ['Link','Unlink','Anchor'],
            ['Image','Table','SpecialChar'],
            '/',
            ['Styles','Format','FontSize'],
            ['TextColor'],
            ['Maximize', 'ShowBlocks']
        ],
    };
    CKEDITOR.addStylesSet('default',[
        { name: 'Aucun', element: 'p' },
        { name: 'Titre niveau 1', element: 'h1'},
        { name: 'Titre niveau 2', element: 'h2'},
        { name: 'Titre niveau 3', element: 'h3'},
        { name: 'Titre niveau 4', element: 'h4'},
        { name: 'Titre niveau 5', element: 'h5'},
        { name: 'Titre niveau 6', element: 'h6'},
        { name: 'Image alignée à droite', element: 'p', attributes: { 'class': 'alignright' } },
        { name: 'Image alignée à gauche', element: 'p', attributes: { 'class': 'alignleft' } },
        { name: 'Image centrée', element: 'p', attributes: { 'class': 'aligncenter' } },
    ]);

    django.jQuery('textarea.rich-text').ckeditor(config);
});
