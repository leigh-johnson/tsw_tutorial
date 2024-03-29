// admin.js

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


/*
*************
ADMIN PANEL
*************
*/	
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
	$('#set-parent_id').change(function(){
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
	$('#set-layout-icon').change(function(){
		layout = $(this).find(':selected').data('layout');
		icon = $(this).find(':selected').data('icon');
		path = window.location.search;
		_id = path.split('?')[1].split('=')[1];
		console.log(layout, icon);
		$.ajax({
			type: 'PUT',
			url: '/admin/api/article?_id='+_id+'&'+'layout='+layout+'&icon='+icon,
			success: function(){
				window.location.reload();
			}
		});

	});

	// Delete article @todo PROMPT CASCADE WARNING
	$('#delete-article').click(function() {
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
	$('#set-is_category').change(function(){
		val = $(this).val();
		path = window.location.search;
		_id = path.split('?')[1].split('=')[1];
		$.ajax({
			type: 'PUT',
			url: '/admin/api/article?_id='+_id+'&is_category='+val,
			success: function(){
				window.location.reload();
			}
		});
	});

	// Set viewer privs
	$('#set-is_public').change(function(){
		val = $(this).val();
		path = window.location.search;
		_id = path.split('?')[1].split('=')[1];
		$.ajax({
			type: 'PUT',
			url: '/admin/api/article?_id='+_id+'&is_public='+val,
		});
	});

	// Set video_src
	$('#set-video-src-submit').click(function(){
		val = $('#set-video_src').val();
		query = window.location.search;
		_id = query.split('?')[1].split('=')[1];
		$.ajax({
			type: 'PUT',
			url: '/admin/api/article?_id='+_id+'&video_src='+val,
			success: function(){
				window.location.reload();
			}
		});
	});

	// Set banner_src
	$('#set-banner-src-submit').click(function(){
		val = $('#set-banner_src').val();
		query = window.location.search;
		_id = query.split('?')[1].split('=')[1];
		$.ajax({
			type: 'PUT',
			url: '/admin/api/article?_id='+_id+'&banner_src='+val,
			success: function(){
				window.location.reload();
			}
		});
	});

	// Set lua_tag
	$('#set-lua-tag-submit').click(function(){
		val = $('#set-lua_tag').val();
		query = window.location.search;
		_id = query.split('?')[1].split('=')[1];
		$.ajax({
			type: 'PUT',
			url: '/admin/api/article?_id='+_id+'&lua_tag='+val,
			success: function(){
				window.location.reload();
			}
		});
	});

	// Add Tag() relationship
	$('#set-search-tag-submit').click(function(){
		val = $('#set-search-tag').val();
		console.log(val)
		query = window.location.search;
		_id = query.split('?')[1].split('=')[1];
		$.ajax({
			url: '/admin/setTag?_id='+_id+'&tag_id='+val
		});

	});

	// Remove Tag() relationship
	$('.remove-tag').click(function(){
		val = $(this).attr('data-attr');
		query = window.location.search;
		_id = query.split('?')[1].split('=')[1];
		$.ajax({
			url: '/admin/setTag?_id='+_id+'&tag_id='+val+'&remove=True',
			success: function(){
				window.location.reload();
			}
		})
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

	    // Displays current column values in .flash-notice boxes
	    function displayData(callback){
	    	//Bakes data into html elements
	    	callback.success(function (data) {
	    		data = data[0];
	    		var options = ['layout', 'lua_tag', 'is_public', 'is_category', 'parent_id', 'articles'];
		  		 for (var key in data){
		  		 	if(options.indexOf(key) > -1){
		  		 		if (key == 'layout'){
		  		 			$("#set-layout-icon").after("<p class='flash-notice'>"+key+": "+ data[key]+"</p>");
		  		 		}
		  		 		else{
		  		 			$("#set-"+key).after("<p class='flash-notice'>"+key+": "+ data[key]+"</p>");
		  				}
		  			}
	   			 }
			});
	    }

	    var promise = getArticle();
	    var data = displayData(promise);

    }



/*
*************
API REQUESTS
*************
*/
    // admin/tags POST
	$('#new-tag-submit').click(function(e){
		e.preventDefault();
		data = {}
		$('#new-tag input').each(function(column){
			column_name = $(this).attr('id');
			data[column_name] = $(this).val();
			console.log(data);
		});
		$.ajax({
			type: 'POST',
			url: '/admin/api/tag',
            //processData: false,
			dataType: 'json',
			contentType: "application/x-www-form-urlencoded; charset=utf-8",
			data: data,
			success: function(){
				location.reload();
			}
		});

	});

	// admin/tags PUT
	$(".tables [contenteditable='true']").each(function(index){
		var column_id = $(this).attr('data-attr');
		var tag_id = $(this).parent().attr('id');
		$(this).blur(function(){
			data = {}
			data[column_id] = $(this).html();
			$.ajax({
				type: 'PUT',
				url: '/admin/api/tag?_id='+tag_id,
				dataType: 'json',
  				contentType: "application/x-www-form-urlencoded; charset=utf-8",
  				data: data
			});
		});
	});

	// admin/tags DELETE
	$(".tag-delete").click(function(){
		console.log($(this).attr('data-attr'));
		var tag_id = $(this).attr('data-attr');
		$.ajax({
			type: 'DELETE',
			url: '/admin/api/tag?_id='+tag_id,
			dataType: 'json',
			success: function(){
				location.reload();
			}
		});
	});

	// POST
	$('#new-article-submit').click(function(e){
		e.preventDefault();
		data = {}
		$('#new-article input, #new-article select, #new-article textarea').each(function(column){
			column_name = $(this).attr('id');
			data[column_name] = $(this).val();
		});
		$.ajax({
			type: 'POST',
			url: '/admin/api/article',
			contentType: "application/x-www-form-urlencoded; charset=utf-8",
			data: data,
			dataType: 'json',
			success: function(response){
				_id = response['_id']
				window.location.replace('/admin/article?_id='+_id)
			}
		});

	});

/*
*************
ADD BODY ("WIDGET" OR "SECTION")
*************
*/
	$('#add-body').click(function(){
		var _id = window.location.search
		$.ajax({
			type: 'PUT',
			url: '/admin/api/article'+_id+'&new_body=True',
			success: function(){
				window.location.reload();
			}
		});

	});

	// Remove widget & delete all Body_$lang() instances (requires confrim)
});