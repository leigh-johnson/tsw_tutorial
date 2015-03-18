
(function() {
    var $body = document.body
    , $menu_trigger = $body.getElementsByClassName('menu-trigger')[0];

    //Slidemenu
    if ( typeof $menu_trigger !== 'undefined' ) {
        $menu_trigger.addEventListener('click', function() {
            $body.className = ( $body.className == 'menu-active' )? '' : 'menu-active';
            $('.menu-trigger span').toggleClass('icon-th-menu-outline icon-times-outline', 600);
        });
    }

	$('.accordion .accordion-header').click(function() {
    $(".accordion-icon",this).toggleClass('icon-square-plus icon-square-minus');
    $(this).parent().toggleClass('is-expanded');
		$(this).next().toggle('fast');
		return false;
	}).next().hide()


    $('.accordion-header a').click(function(){
    	window.location = $(this).attr('href');
    	return false;
    });

    // Search

    $('#search-submit').click(function(event){
        event.preventDefault();
        var search = $("#search").val();
        if (search.indexOf('tag=') == -1){
            search = "term="+search;
        }
        window.location.href='search?'+search;
    });
}).call(this);