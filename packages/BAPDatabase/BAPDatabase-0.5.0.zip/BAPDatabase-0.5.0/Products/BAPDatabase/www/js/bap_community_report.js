$(document).ready(function(){
    /**
     * Hide all objectives` content if Javascript Enabled
     */
    hideItems();
    if(window.location.hash) {
        var hashed = $(normalize_id(window.location.hash));
        hashed.siblings().show();
        hashed.parents().slideDown();        
    }
    $('.bap-objective-title a').click(function(e){
        e.preventDefault();
        update_links('/bap');

        if($(this).parent().next('.bap-objective').is(':visible')){
            $(this).attr("class", "active");
        }else {
            $(this).attr("class", "inactive");
        }

        $(this).parent().next('.bap-objective').slideToggle();
    });

    $('.bap-objective-title a').click(function(e){
        update_links('/bap');
        objective_id = $(this).text();
        setCookie('BAPObjective', objective_id, 60);
	deleteCookie('BAPTarget');
	deleteCookie('BAPAction');
        toggle_objective($(this).closest('span'));
    });


    $('.bap-objective-title span').click(function(e){
        update_links('/bap');
        objective_id = $(this).parent().children('a').text();
        setCookie('BAPObjective', objective_id, 60);
	deleteCookie('BAPTarget');
	deleteCookie('BAPAction');
        toggle_objective($(this));
    });

    $('.bap-objective .bap-targets .bap-target span a.target-link').click(function(){
        update_links('/bap');
        target_id = $(this).attr('href').split('?id=')[1];
        setCookie('BAPTarget', target_id, 60);
        toggle_target($(this));
        return false;
    });

    $('.action-link').click(function(){
        update_links('/bap');
        action_id = $(this).attr('href').split('?id=')[1];
        setCookie('BAPAction', action_id, 60);
        toggle_action($(this));
        return false;
    });

	$('.target-link').each(function(){
    $this = $(this);
    if( $this.closest('.bap-actions').is(':visible') ) {
        $this.removeClass('expand').addClass('collapse');
    }else {
        $this.removeClass('collapse').addClass('expand');
    }
    });

    $('.action-link').each(function(){
    $this = $(this);
    if( $this.closest('.bap-mop-content').is(':visible') ) {
        $this.removeClass('expand').addClass('collapse');
    }else {
        $this.removeClass('collapse').addClass('expand');
    }
    });

    $('.goto-action').live('click', function(){
        var href = $(this).attr('href');
        href = normalize_id(href);
        $(href).parents().show();
        toggle_action($(href));
    });

    $('.bap-action span span').each(function(){
        $(this).html(replace_actions($(this).html()));
    });
    
    console.log(getCookie('BAPObjective'));
    console.log(getCookie('BAPTarget'));
    console.log(getCookie('BAPAction'));
    
    var action_id = getCookie('BAPAction');
    if ((action_id !== 'None') && (action_id !== undefined))
    {
	console.log('action');
        update_links('/bap');
        var Action = $('.action-link[id='+action_id+']');
        var Target = Action.parents('.bap-target').find('.target-link');
        var objective = Action.parents('.bap-objectives').find('.bap-objective-title span');
        if (Action.length>0)
        {
            toggle_objective(objective);
            toggle_target(Target);
            toggle_action(Action);
        }
    }
    else{
        var target_id = getCookie('BAPTarget');
        if ((target_id !== 'None') && (target_id !== undefined))
        {
		console.log('target');
            update_links('/bap');
            var Target = $('.bap-objective .bap-targets .bap-target span a.target-link[id='+target_id+']');
            var objective = Target.parents('.bap-objectives').find('.bap-objective-title span');
            if (Target.length>0)
            {
                toggle_objective(objective);
                toggle_target(Target);
            }
        }
        else{
            var objective_id = getCookie('BAPObjective');
            if ((objective_id !== 'None') && (objective_id !== undefined))
            {
                update_links('/bap');
                var objective = $('.bap-objective-title a:contains('+objective_id+'):first')
                if (objective.length>0)
                {
                    toggle_objective(objective);
                }
            }
        }
    }
});


/**
 * Hide Objectives` content from BAP content
 *
 * @author      Bogdan Tanase       Eau de Web
 * @returns     boolean             false
*/
function hideItems(){
    $(".bap-objective").each(function(){
        $(this).css({'display' : 'none'});
    });
    
    $(".bap-actions").each(function(){
        $(this).css({'display' : 'none'});
    });
    
    return false;
}
function toggle_target(Target, state){
	target_id = Target.attr('id');
    var bap_actions = Target.parent().next('.bap-actions')
        if(bap_actions.children('.bap-action').children().length == 0){
            bap_actions.append("<div class='bap-action'><div class='bap-mop-content'></div></div>");

            url = Target.attr("href");

            $("#bap-content").showLoading();

            bap_actions.children('.bap-action').children('.bap-mop-content').load('' + url + ' #mop-content', function(response, status, xhr) {
                $("#bap-content").hideLoading();
                //Also linkify text
                $(this).parent().html(Linkify($(this).html()));

                //Shorten long urls
                $('.linkified').each(function(){
                    if (!$(this).hasClass('shortened')) {
                        $(this).html($(this).html().substr(0, 50) + '...');
                        $(this).addClass('shortened')
                    }
                });

                if(status == "error"){
                    alert(xhr.status + " " + xhr.statusText);
                }
            });

		setCookie('BAPTarget', target_id, 60);

            bap_actions.slideDown();
            bap_actions.children(".bap-mop-content").slideDown();
            Target.removeClass('expand').addClass('collapse');
        }else {
            if( bap_actions.is(':visible') ){
		setCookie('BAPTarget', 'None', 60);
                bap_actions.slideUp();
                Target.removeClass('collapse').addClass('expand');
            }else {
		setCookie('BAPTarget', target_id, 60);
                bap_actions.slideDown();
                Target.removeClass('expand').addClass('collapse');
            }
       }
       
       if(state == true){
        setCookie('BAPTarget', target_id, 60);
        bap_actions.slideDown();
    Target.removeClass('expand').addClass('collapse');
    }
    
    
}

function toggle_objective(objective){
	
    if(objective.parent().next('.bap-objective').css('display') == 'block'){
	objective.parent().next('.bap-objective').slideUp();
	deleteCookie('BAPObjective');
	objective.parent().children('.bap-objective-title a').attr("class", "active");
    }else {
	objective.parent().next('.bap-objective').slideDown();
	objective.parent().children('.bap-objective-title a').attr("class", "inactive");
    }
}

function toggle_action(Action, state){
	action_id = Action.attr('id');
    if(Action.parent().next(".bap-mop-content").is(':empty') == true){
            url = Action.attr("href");

            $("#bap-content").showLoading();

            Action.parent().next(".bap-mop-content").load('' + url + ' #mop-content', function(response, status, xhr) {
            $("#bap-content").hideLoading();
            //Replace Action: A1.2. with <a href=
            $(this).html(replace_actions($(this).html()));
            //Also linkify text
            $(this).html(Linkify($(this).html()));

            //Shorten long urls
            $('.linkified').each(function(){
                if (!$(this).hasClass('shortened')) {
                $(this).html($(this).html().substr(0, 50) + '...');
                $(this).addClass('shortened')
                }
            });

            if(status == "error"){
                alert(xhr.status + " " + xhr.statusText);
            }
            });

		setCookie('BAPAction', action_id, 60);

            Action.parent().next(".bap-mop-content").slideDown();
            Action.removeClass('expand').addClass('collapse');
        }else {
            content = Action.parent().next(".bap-mop-content");
            if( content.is(':visible') ){
		setCookie('BAPAction', 'None', 60);
                content.slideUp();
                Action.removeClass('collapse').addClass('expand');
            }else {
		setCookie('BAPAction', action_id, 60);
                content.slideDown();
                Action.removeClass('expand').addClass('collapse');
            }
        }
	
	if(state == true){
        setCookie('BAPAction', action_id, 60);
        bap_mop_content.slideDown();
    Action.removeClass('expand').addClass('collapse');
    }
    
}

function setCookie(c_name,value,expires){
        // set time, it's in milliseconds
        var today = new Date();
        today.setTime( today.getTime() );
        if ( expires ){
            expires = expires * 1000 * 60 * 60 * 24;
        }
        var expires_date = new Date( today.getTime() + (expires) );
        var path = '/';
        document.cookie=c_name + "=" + escape(value) +
            ( ( expires ) ? ";expires=" + expires_date.toGMTString() : "" ) +
            ( ( path ) ? ";path=" + path : "" );
    }

    function getCookie(c_name){
        var i,x,y,ARRcookies=document.cookie.split(";");
        for (i=0;i<ARRcookies.length;i++){
            x=ARRcookies[i].substr(0,ARRcookies[i].indexOf("="));
            y=ARRcookies[i].substr(ARRcookies[i].indexOf("=")+1);
            x=x.replace(/^\s+|\s+$/g,"");
            if (x==c_name){
                return unescape(y);
            }
        }
    }

    function deleteCookie(name){
        path = '/'
        document.cookie = name + "=" +
            ( ( path ) ? ";path=" + path : "") +
            ";expires=Thu, 01-Jan-1970 00:00:01 GMT";
    }

function update_links(parameter){
        parameter = parameter || "";
        $('.sub_folder ul li a').each(function(){
            if (parameter!=""){
                old_link = $(this).attr('href').split(parameter);
                $(this).attr('href', old_link[0]+parameter);
            }
        });
    }
function normalize_id(text){
    return text.replace(/\./g, '\\.');
}
function replace_actions(html){
    return html.replace(/\b(\w{1})\s*\.?(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b/g,
        '<a class="goto-action" href="#$1$2.$3.$4">$1$2.$3.$4</a>');
}
