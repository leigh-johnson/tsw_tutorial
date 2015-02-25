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
	$('#set_parent_id').change(function(){
		// parent and child identities
		p_id = $(this).val();
		path = window.location.search;
		c_id = path.split('?')[1].split('=')[1];
		$.ajax({
			url: '/admin/setParentId',
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

	// Add video_src input based on layout choice
	$('#layout').change(function(){
		if($('#layout').val() == 'video'){
			$('#layout').after('<label for="video_src">Video link</label><input id="video_src" type="textarea" placeholder="Video URL">');
		}
		if($('#layout').val() != 'video'){
			$('#video_src').remove();
			$('label[for="video_src"]').remove();
		}
	});

	// Set icon
	$('#set_icon').change(function(){
		icon = $(this).val();
		path = window.location.search;
		_id = path.split('?')[1].split('=')[1];
		$.ajax({
			url: '/admin/setIcon',
			data: '_id='+_id+'&'+'icon='+icon
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
	$('#set_is_category').change(function(){
		val = $(this).val();
		path = window.location.search;
		_id = path.split('?')[1].split('=')[1];
		$.ajax({
			url: '/admin/setIsCategory?_id='+_id+'&is_category='+val	
		});
	});

	// Set viewer privs
	$('#set_is_public').change(function(){
		val = $(this).val();
		path = window.location.search;
		_id = path.split('?')[1].split('=')[1];
		$.ajax({
			url: '/admin/setIsPublic?_id='+_id+'&is_public='+val
		});
	});

	// Add Tag() relationship
	$('#set_tag').change(function(){
		val = $(this).val();
		console.log(val)
		path = window.location.search;
		_id = path.split('?')[1].split('=')[1];
		$.ajax({
			url: '/admin/setTag?_id='+_id+'&tag_id='+val
		});

	});

	// Nested Sortable ordering
	var sortable = $('#menu .sortable').nestedSortable({
		handle: 'div',
		items: 'li',
		toleranceElement: '> .sortable-wrapper',
		maxlevels: 4,
		opacity: 0.6,
		relocate: function(event, ui){
			data = $('#menu .sortable').nestedSortable('toHierarchy');
			console.log(data);
			$.ajax({
				url: '/admin/setOrder',
				headers: {'X-Admin-Menu-SetOrder': JSON.stringify(data)},
				processData: false,
				dataType: 'json'
			});
		}
	});
	
	
	// Hide admin panel on non-editable pages
	if(window.location.search == ''){
		$('#edit_article').addClass('hidden');
	}

    // Adjust article info in main panel
    if(window.location.search != '' && window.location.pathname != '/admin/search'){

    	function getArticle(){
	    	// GET request based on current window.location.search
	    	// Used to display current settings
	    	// returns a promise
	    	var query = window.location.search;
	    	return $.ajax({
	    		url: '/admin/api/article'+query,
	    	});
	    }

	    function displayData(callback){
	    	//Bakes data into html elements
	    	callback.success(function (data) {
	    		data = data[0]
	    		var options = ['icon', 'layout', 'lua_tag', 'is_public', 'is_category', 'parent_id', 'articles'];
		  		 for (var key in data){
		  		 	if(options.indexOf(key) > -1){
		  		 	$("#set_"+key).after("<p class='flash-notice'>"+key+": "+ data[key]+"</p>");
		  		 	}
	   			 }
			});
	    }

	    var promise = getArticle();
	    var data = displayData(promise);

    }

});