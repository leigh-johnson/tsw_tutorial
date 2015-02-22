/*
  Slidemenu
*/
(function() {
    var $body = document.body
    , $menu_trigger = $body.getElementsByClassName('menu-trigger')[0];

    if ( typeof $menu_trigger !== 'undefined' ) {
        $menu_trigger.addEventListener('click', function() {
            $body.className = ( $body.className == 'menu-active' )? '' : 'menu-active';
        });
    }

	$('.accordion .accordion-header').click(function() {
    $(".accordion-icon",this).toggleClass('icon-plus icon-minus');
    $(this).parent().toggleClass('is-expanded');
		$(this).next().toggle('fast');
		return false;
	}).next().hide()


    $('.accordion-header a').click(function(){
    	window.location = $(this).attr('href');
    	return false;
    });

}).call(this);