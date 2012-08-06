function append_on_current_url(nova_parte){
	var url = window.location.href;
	var url_hash = "#" + window.location.hash.substring(1);
	url = url.replace(url_hash, "");
	var url_parts = url.split("/"); 
	var nova_parte_parts = nova_parte.split("/");
	url_parts = url_parts.concat(nova_parte_parts);
	var new_url = "";
	for (part_index in url_parts){
		var part = url_parts[part_index];
		if(part != "" && part != ".."){
			new_url += part + "/";
		}
		if(part == "http:" || part == "https:"){
			new_url += "/";
		}
		if(part == ".."){
			new_url = new_url.split("/").slice(0,-2).join("/") + "/";
		}
	}

	return new_url;
}

$(document).ready(function(){
	
	/*Criar listas em home.html e sublistas em listas.html*/
	
	function adicionar_nova_lista(form){
		var nova_sub_lista = $(".nova-lista", form).val();
		window.location.href = append_on_current_url(nova_sub_lista);
	}
	
	$(".adicionar-nova-lista").on("click", function(){
		adicionar_nova_lista($(this).parent());
	});
	
	$(".form-adicionar-nova-lista").on("submit", function(){
		adicionar_nova_lista($(this));
		return false;
	});
    
    /*home.html*/
    
    $(".link-with-server").each(function(){
        var servidor = window.location.href;
        var link_to = servidor + $(this).html();
        $(this).attr("href", link_to);
        $(this).html(link_to);
    });
	
	/*listas.html*/
	
	$(".lista-editar-template").hide(); // Fica escondido até precisar dele
    $(".item-editar-template").hide(); // Ficam escondidos até precisar deles

	delay_lista = 100;

    $("#lista-body .editar").on("click", function(){
    	$("#lista-body").hide(delay_lista);
    	$(".lista-editar-template").show(delay_lista);
    });
    
    function sair_edicao_lista(){
		$(".lista-editar-template").hide(delay_lista);
    	$("#lista-body").show(delay_lista);
	}
    
    $(".lista-editar-template .cancela-edicao").on("click", function(){
    	sair_edicao_lista();
    });
    
    delay_item = 100;
    
    $("#itens .editar").on("click", function(){
        var li_enclosing = $(this).parent().parent();
        $(".item-opcoes", li_enclosing).hide();
        $(".item-body", li_enclosing).hide(delay_item);
        $(".item-editar-template", li_enclosing).show(delay_item); // Mostra o form para o usuário editar o item
        $(".item-editar-template form").css({"display": "block"});
        $(".item-editar-template form .novo_valor", li_enclosing).focus();
    });
    
    function sair_edicao_item(li_item){
		$(".item-editar-template", li_item).hide(delay_item);
        $(".item-editar-template form").css({"display": "inline"});
        $(".item-body", li_item).show(delay_item);
        $(".item-opcoes", li_item).show();
	}
    
    $("#itens .cancela-edicao").on("click", function(){
        var li_enclosing = $(this).parent().parent().parent();
        sair_edicao_item(li_enclosing);
    });
    
    /*Do the HTTP PUT and DELETE submition for the form*/
    
    function call_form_action(form, callback, data){
    	if(typeof(data)==='undefined') data = {};
    	var url = form.attr("action");
    	var method = form.attr("method");
    	$.ajax({
  		  type: method,
  		  url: url,
  		  data: data,
  		  success: function(result) {
  			  callback(result);
  		  }
  		});
    }
    
    $(".lista-editar-template .form-put .botao-submit").on("click", function(){
		var form_enclosing = $(this).parent();
		var novo_valor = $(".novo_valor", form_enclosing).val();
		var data = { novo_valor:  novo_valor};
		call_form_action(form_enclosing, function(result){
			$("#lista-body h1").html(novo_valor);
			sair_edicao_lista(); // Já editou, então pode sair
		}, data);
	});
	
	$("#itens .form-put .botao-submit").on("click", function(){
		var form_enclosing = $(this).parent();
		var li_enclosing = $(this).parent().parent().parent();
		var novo_valor = $(".novo_valor", form_enclosing).val();
		var data = { novo_valor:  novo_valor};
		call_form_action(form_enclosing, function(result){
			$(".item-body b", li_enclosing).html(novo_valor);
			sair_edicao_item(li_enclosing); // Já editou, então pode sair
		}, data);
	});
    
    $("#lista-body .form-delete .botao-submit").on("click", function(){
        if(confirm("Tem certeza que deseja deletar essa lista?")){
            var form_enclosing = $(this).parent();
            call_form_action(form_enclosing, function(result){
                window.location.href = append_on_current_url("../"); // Vai pra url pai
            });
        }
	});
    
    $("#itens .form-delete-todos-itens .botao-submit").on("click", function(){
        var form_enclosing = $(this).parent();
        call_form_action(form_enclosing, function(result){
			$("#itens .row").remove();
			$("#itens hr").remove();
		});
    });
    
    $("#itens .form-delete-um-item .botao-submit").on("click", function(){
		var form_enclosing = $(this).parent();
		var id = $(this).attr("id").replace("deleta-item-", "");
		var row = $("#row-item-" + id);
        call_form_action(form_enclosing, function(result){
			row.next().remove(); // Remove o hr
			row.remove();
		});
	});
    
});
