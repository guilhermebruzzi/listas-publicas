$(document).ready(function(){
    $(".item-editar-template").hide(); // Ficam escondidos até precisar deles

    $(".editar").on("click", function(){
        var li_enclosing = $(this).parent().parent();
        $(".item-opcoes", li_enclosing).hide();
        $(".item-body", li_enclosing).hide(500);
        $(".item-editar-template", li_enclosing).show(500); // Mostra o form para o usuário editar o item
        $(".item-editar-template form").css({"display": "block"});
        $(".item-editar-template form .novo_valor", li_enclosing).focus();
    });
    
    $(".cancela-edicao").on("click", function(){
        var li_enclosing = $(this).parent().parent().parent();
        $(".item-editar-template", li_enclosing).hide(500);
        $(".item-editar-template form").css({"display": "inline"});
        $(".item-body", li_enclosing).show(500);
        $(".item-opcoes", li_enclosing).show();
    });
    
    $(".excluir").on("click", function(){
        var form_enclosing = $(this).parent();
        form.submit();
    });
});
