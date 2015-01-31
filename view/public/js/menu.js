$(document).ready(function(){
  $('.js-menu-trigger,.js-menu-screen').on('click touchstart',function (e) {
    $('.js-menu,.js-menu-screen').toggleClass('is-visible');
    e.preventDefault();
  });

    $('#menu-accordion').accordion();
    $('#menu-accordion').accordion( 'option', { 
    	header: '.category',
    	heightStyle: 'fill',
     	icons : {
     		'header': 'icon-chevron-small-right',
     		'activeHeader': 'icon-chevron-small-down'
     	}
    	 });
      
});