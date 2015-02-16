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
      var icons = {
      header: "icon-plus",
      activeHeader: "icon-minus"
    };
	$('.accordion .accordion-header').click(function() {
    	$("span",this).toggleClass('icon-plus icon-minus');
		$(this).next().toggle('slow');
		return false;
	}).next().hide()
    $('.accordion-header a').click(function(){
    	window.location = $(this).attr('href');
    	return false;
    });

}).call(this);