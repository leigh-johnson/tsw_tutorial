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
      header: "icon-folder",
      activeHeader: "icon-folder-open"
    };
    $( "#accordion").accordion({

      icons: icons,
      header: ".accordion-header",
      collapsible: true,
      active: false,
    });
    $('.accordion-header a').click(function(){
    	window.location = $(this).attr('href');
    	return false;
    });

}).call(this);