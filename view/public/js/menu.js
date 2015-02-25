
(function() {
    var $body = document.body
    , $menu_trigger = $body.getElementsByClassName('menu-trigger')[0];

    //Slidemenu
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

    // Search

    function searchTerm (term) {
    if (philosophers.indexOf(person) >= 0) {
        console.log(person + " is a philosopher.");
    } else {
        console.log(person + " is NOT a philosopher.");
    }
}
    $('#search-submit').click(function(event){
        event.preventDefault();
        var search = $("#search").val();
        if (search.indexOf('tag=') == -1){
            search = "term="+search;
        }
        window.location.href='search?'+search;
    });
}).call(this);