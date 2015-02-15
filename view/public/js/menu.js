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
    $( "#accordion-top").accordion({
    	heightStyle: "content",
      icons: icons,
      header: ".accordion-top-header",
      collapsible: true,
      active: false,
    });
    $('.accordion-top-header a').click(function(){
    	window.location = $(this).attr('href');
    	return false;
    });
    $( "#accordion-sub").accordion({
    	heightStyle: "content",
      icons: icons,
      header: ".accordion-sub-header",
      collapsible: true,
      active: false,
    });
    $('.accordion-sub-header a').click(function(){
    	window.location = $(this).attr('href');
    	return false;
    });

}).call(this);