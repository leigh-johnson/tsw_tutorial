$( document ).ready(function() {
	// AJAX defaults
		$.ajaxSetup({
			contentType: 'application/json; charset=utf-8',
			dataType: 'text json',
		error: function(data) {
			$('<div class="flash-error"><span>CONNECTION ERROR - PLEASE RESAVE!</span></div>').appendTo($('#error')).fadeIn(500).delay(2600).fadeOut(500);
		    },
		success: function() {
			$('<div class="flash-success"><span>SAVED ^^V</span></div>').appendTo($('#error')).fadeIn(500).delay(2600).fadeOut(500);	

			}			
		});

	// Admin panel
	// Change language
		$('#language_submit').click(function(event) {
			lang = $('#language').val();
			var hostname = window.location.hostname

			//req to AdminController.setLang() 
			$.ajax({
				type: 'GET',
				url: '/admin/setLang?lang='+lang,
				success: function(){
					location.reload();
				}
			});
		});
	// Assign new category/parent to article
	$('#assign_parent').change(function(){
		// parent and child identities
		p_id = $(this).val();
		path = window.location.search;
		c_id = path.split('?')[1].split('=')[1];
		$.ajax({
			url: '/admin/assign',
			data: 'p_id='+p_id+'&'+'c_id='+c_id
		});
	});

	// Toggle switch
	$('.toggle input').switchButton({
		on_label: 'Edit',
  		off_label: 'Lock',
  		checked: false
	});

	$('.toggle input').change(function(){
		$('#article_options').slideToggle('slow');
	});

	// Set new layout
	$('#set_layout').change(function(){
		layout = $(this).val();
		path = window.location.search;
		_id = path.split('?')[1].split('=')[1];
		$.ajax({
			url: '/admin/setLayout',
			data: '_id='+_id+'&'+'layout='+layout,
			success: function(){
				location.reload();
			}
		});
	});

	// Delete article @todo PROMPT CASCADE WARNING
	$('#delete_article').click(function() {
	    if (confirm('Really delete this article? CANNOT BE UNDONE!')) {
			path = window.location.search;
			_id = path.split('?')[1].split('=')[1];
			$.ajax({
				url: '/admin/api/article?_id='+_id,
				type: 'DELETE',
				success: function(){
					window.location.replace('/admin');
				}
			});
		}

	});

	// Set parental hierarchy
	$('#is_category').change(function(){
		val = $(this).val();
		path = window.location.search;
		_id = path.split('?')[1].split('=')[1];
		$.ajax({
			url: '/admin/setIsCategory?_id='+_id+'&is_category='+val	
		});
	});

	// Set viewer privs
	$('#is_public').change(function(){
		val = $(this).val();
		path = window.location.search;
		_id = path.split('?')[1].split('=')[1];
		$.ajax({
			url: '/admin/setIsPublic?_id='+_id+'&is_public='+val
		});
	});

	// Hierarchy sortables
	$("#menu ol").sortable({
   	 connectWith: "#menu ol",
    	placeholder: "ui-state-highlight",
    	toleranceElement: '.sortable-handle'
	});

});