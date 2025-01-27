define(['jquery', 'bootstrap'], function ($) {
    $(document).ready(function () {
        console.log("chargement JS ajax-adhesion.js OK");



 
        $('.adh_select').on('click', function (event) {
            
            let data_id = $(this).attr("data_id");
            $("#adh_id").val(data_id);
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
 
            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'data_id': data_id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    url: "ajax_remboursement",
                    success: function (data) {
                        console.log(data.remb) ;
                        $('#remb').html("").html(data.remb);
                        $('#jour').html("").html(data.jour);
                    }
                }
            )
        }); 


        $('.validate_renewal').attr("disabled",true); 
        var liste = [] ;
 
        $('form').on('click', '.renewal_user_class' ,  function (event) { 

            let data_user_id = $(this).attr("data_user_id");
            let data_name = $(this).attr("data_name");
            let data_id = $(this).attr("data_id");
            let level = $("#level"+data_user_id).val();
            levels = ["Cours Préparatoire", "Cours Elémentaire 1", "Cours Elémentaire 2","Cours Moyen 1","Cours Moyen 2","Sixième", "Cinquième", "Quatrième","Troisième","Seconde","Première","Terminale","Classe Prépa PCSI","Maternelle"]

            let engagement = $("input[name='engagement"+data_user_id+"']:checked").val() ;
                            
            construct_user("Enfant",data_name, levels[level-1] ,data_id , engagement ) ; 
         
        });    



        function construct_user(statut,name,level,id, engagement ){

                let nb_child = $("#nb_child").val();

                tab_eng = engagement.split("-")


                nb =  parseInt(nb_child);
                var div = "<div class='renewal_user selector' id="+id+"><div>"+ name +"<br/> "+ level + "<br/> "+ tab_eng[1] +" mois<br/> "+tab_eng[0]+"€ </div></div>" ;


                if ( document.getElementById(id) !== null ) {
                    $("#"+id).remove() ;
                }

                $("#show_confirm_renewal").append(div) ;



                liste.push(id); 
                $('#renewal'+id).parent().parent().addClass("selector") ;

                if (nb ==  parseInt(liste.length)) {  
                    $('.renewal_user').hide();
                    $('.selector').show();
                    }

                $('.validate_renewal').attr("disabled",false); 

            }



        $('.cancel_user_class').on('click', function (event) { 

            let data_user_id = $(this).attr("data_user_id");
 
            if ( document.getElementById("renewal"+data_user_id) !== null ) {
                    $("#renewal"+data_user_id).remove() ;
                }
            $("input[name='engagement"+data_user_id+"']").prop('checked', false );

        });  

 


            $("#id_username").on('change', function () {
 
                let username = $("#id_username").val();
                let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
     
                $.ajax({
                    url: '/account/ajax/userinfo/',
                    type: "POST",
                    data: {
                        'username': username,
                        csrfmiddlewaretoken: csrf_token,    
                    },
                    dataType: 'json',
                    success: function (data) {
                        $("#ajaxresult"+i).html(data["html"]);

                         $("#div_username").show();
                         $("#verif_username").html( $("#id_username").val() );

                        
                    } 

                }); 

            });

 
            $("#id_password1").on('change', function () {
                    $("#id_save").show();
            });
     



            $("#id_last_name").on('change', function () {
                $("#div_display").show() 
                $("#div_last_name").show();
                $("#verif_last_name").html( $("#id_last_name").val() );

            });


            $("#id_first_name").on('change', function () {
                $("#div_display").show() 
                $("#div_first_name").show();
                $("#verif_first_name").html( $("#id_first_name").val() );

            });
 


            $("#id_level").on('change', function () {
                $("#div_display").show() 
                $("#div_level").show();

                levels = ["", "Cours Préparatoire", "Cours Elémentaire 1", "Cours Elémentaire 2","Cours Moyen 1","Cours Moyen 2","Sixième", "Cinquième", "Quatrième","Troisième","Seconde","Première","Terminale","Classe Prépa PCSI","Maternelle"]

                $("#verif_level").html( levels [ $("#id_level").val() ]  );

            });


            $("#id_email").on('change', function () {
                $("#div_display").show() 
                $("#div_email").show();
                $("#verif_email").html( $("#id_email").val() );

            });
 


            $("#id_username").on('change', function () {
                $("#div_display").show() 
                $("#div_username").show();
                $("#verif_username").html( $("#id_username").val() );

            });


            $("#formule_id").on('change', function () {
                $("#div_display").show() 
                $("#div_formule").show();
                if ( $("#formule_id").val() == 1) { f = "Autonomie"}
                else if ( $("#formule_id").val() == 2) {f = "IA"}
                else if ( $("#formule_id").val() == 3) {f = "Suivi"}
                else  {f = "Personnalisé"}


                $("#verif_formule").html( f );
            });





 
        $('.formule').on('change', function (event) {
            let formule_id = $(this).val();
            let csrf_token = $("input[name='csrfmiddlewaretoken']").val();
            let student_id = $(this).data("user");


            $.ajax(
                {
                    type: "POST",
                    dataType: "json",
                    data: {
                        'formule_id': formule_id,
                        'student_id': student_id,
                        csrfmiddlewaretoken: csrf_token
                    },
                    url: "ajax_prices_formule",
                    success: function (data) {
                        $('#engage'+student_id).html("");
                        // Remplir la liste des choix avec le résultat de l'appel Ajax
                        let prices = data["prices"];
                        for (let i = 0; i < prices.length; i++) {

                            let price_id   = prices[i].price;
                            let price_name =  prices[i].nb_month;

                            $('#engage'+student_id).append('<label for="engagement'+student_id+'"><input type="radio" id="engagement'+student_id+'" name="engagement'+student_id+'" value="'+ price_id +'-'+price_name+'" /> '+price_name+' mois - '+ price_id +'€</label><br/>')
                                
 
                        }
                    }
                }
            )
        }); 
  
    });

});

