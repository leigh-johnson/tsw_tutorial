$(document).ready(function(){
  $('.js-menu-trigger,.js-menu-screen').on('click touchstart',function (e) {
    $('.js-menu,.js-menu-screen').toggleClass('is-visible');
    e.preventDefault();
  });

    $('#menu-accordion').accordion();
    $('#menu-accordion').accordion( 'option', { 
    	header: '.category-item',
    	heightStyle: 'fill',
     	icons : {
     		'header': 'icon-folder',
     		'activeHeader': 'icon-folder-open'
     	}
    	 });
      
});