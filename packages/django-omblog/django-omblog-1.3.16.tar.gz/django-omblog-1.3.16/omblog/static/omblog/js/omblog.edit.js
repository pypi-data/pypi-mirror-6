$(function(){
	ich.grabTemplates();
	// populate span.blog_url
	$('span.blog_url').text(window.omblog_url);
	// slugify the input
	$('#id_slug').slugify('#id_title');

	/*
	 * The thubmails
	 */
	hide_all = function(){
		$('div.panel').each(function(){
			$(this)
				.css('left', '-1000px')
				.addClass('hidden')
			$('div.write').removeClass('inactive')
		})
	}
	ui_toggle = function(target){
		if(target.hasClass('hidden')){
			target
				.css('left', '82px')
				.removeClass('hidden');
			$('div.write').addClass('inactive')
		}else{
			target
				.css('left', '-1000px')
				.addClass('hidden');
			$('div.write').removeClass('inactive')
		}
	}
	/*
	 * save 
	*/
	save = function(){
		// set the icons up
		$('div.feedback span.msg')
			.text('Saving');
		$('div.feedback span.icon')
			.addClass('rotate')
			.html('&#x26;');
		// make the ajax call
		$.ajax({
			type: 'POST',
			url: window.location.href,
			data: $('form').serialize(),
			ajaxSend: presend_clean(),
			success: function(data, textStatus, jqXHR){
				if (data['success'] == false){
					process_invalid(data, textStatus, jqXHR);
				}else{
					process_valid(data, textStatus, jqXHR);
				}
			},
			error: function(jqXHR, textStatus, errorThrown){
				console.log(errorThrown)
			}
		});
	}
	process_invalid = function(data, textStatus, jqXHR){
		// feedback
		$('.feedback p').addClass('error');
		$('.feedback span.msg').text('Oh noes, errors.');
		$('.feedback span.icon').removeClass('rotate').html('&#x25;');
		setTimeout(function(){
			$('.feedback').fadeOut(200);
		}, 2000)
		// process the errors for settings
		if (data['errors']['slug']){
			$('form #id_slug')
				.parent()
				.addClass('errors')
		}
		// process the errors for settings
		if (data['errors']['title']){
			$('form #id_title')
				.parent()
				.addClass('errors')
			
		}
	}
	process_valid = function(data, textStaus, jqXHR){
		$('.feedback p').addClass('success');
		$('.feedback span.msg').text('Post has been saved');
		$('.feedback span.icon').removeClass('rotate').html('&#x23;');
		update_slug(data)
		setTimeout(function(){
			$('.feedback').fadeOut(200);
		}, 1000)
	}
	/*
	 * presend methods
	 */
	presend_clean = function(){
		feedback_clean();
		forms_clean();
	}
	/*
	 * clean methods
	 */
	// forms
	forms_clean = function(){
		$('form fieldset').removeClass('errors');
	}
	// feedback
	feedback_clean = function (){
		$('.feedback p').attr('class', '');
		$('.feedback span.icon').show();
		$('.feedback').show();
	}
	/*
	 *
	 *  Handle tabs in the text area
	 */
	// handle tabs
	$('#id_source_content').keydown(function(e) {
		if(e.keyCode === 9) { // tab was pressed
			var start = this.selectionStart;
				end = this.selectionEnd;
			var $this = $(this);
			$this.val($this.val().substring(0, start)
						+ "\t"
						+ $this.val().substring(end));
			this.selectionStart = this.selectionEnd = start + 1;
			// prevent the focus lose
			return false;
		}
	});
	/* handle changes to the links  when the slug is saved*/
	function update_slug(data){
		var el = $('a.view');
		el.attr('href', el.data('base-url') + data.slug);
		el.attr('data-slug', data.slug);
	}
	/*
	 *
	 * error handling
	 * 
	 */
	/*
	 * bind to key stokes
	 */
	// add mouse trap to all inputs and text areas
	$('input, textarea, select').addClass('mousetrap');

	Mousetrap.bind(['ctrl+s', 'meta+s'], function(e){
		// prevent default
		if (e.preventDefault) {
			e.preventDefault();
		} else {
			e.returnValue = false;
		}
		save();
	});
	Mousetrap.bind(['esc', 'escape'], hide_all)

	// now the drag and drop
	
	/*
	 * handlers
	 */
	function handleDragOver(e){
		e.stopPropagation();
		e.preventDefault();
		return false;
	}
	function handleDrop(e){
		e.stopPropagation();
		e.preventDefault();
		var files = e.dataTransfer.files;
		var formData = new FormData();
		formData.append('post', $('body').attr('data-post-pk'));
		for (var i=0,f; f = files[i]; i++){
			formData.append(files[i].name, files[i]);
		}
		// make the xhr calls
		var req = new XMLHttpRequest();
		// hook up the listeners
		req.upload.addEventListener(
				'progress',
				updateProgress,
				false)
		req.addEventListener('load', load, false)
		// show the progress
		$('div.progress').show();
		// open and send
		req.open('POST', window.attach_create_url, true);
		req.send(formData);
		// hook up the progress
		return false;
	}
	function load(e,t) {
		// hide the progress bar after ones second.
			$('div.progress').fadeOut(500, function(){
				$('div.completed').width('0');
			})
		// parse the response as json
		if(this.status == 200){
			var data  = JSON.parse(this.response);
			for(var i=0; i < data.attachments.length; i++){
				var img = data.attachments[i];
				var t = ich.postimage({
						title: img.title,
						thumb: img.thumb,
						large: img.large,
						pk: img.pk,
				});
				$('#images').append(t);
				// now attach the even listenders
				t[0].addEventListener(
					'dragstart',
					deleteImageDragStart,
					false)
				t[0].addEventListener(
					'dragend',
					deleteImageDragEnd,
					false)
				//
			}
		}
	}
	function updateProgress(e){
		var position =  e.loaded;
		var total = e.total;
		completed = (position/total) * 100;
		$('div.completed').width(completed+'%');
	}
	function handleDragEnter(e){
	}
	/*
	 * delete image drag events
	 */
	var delete_pk;
	function deleteImageDrop(e){
		// now remove the Image event listeners
		document.getElementById('dropbox-target')
			.removeEventListener('drop', deleteImageDrop, false);
		// replace with the originals
		document.getElementById('dropbox-target')
			.addEventListener('drop', handleDrop, false);
		/*
		 * @TODO clean this up and check for 200's and errors
		 * */
		// make the ajax call
		var pk = e.dataTransfer.getData('pk');
		var markdown = e.dataTransfer.getData('text/plain');
		$.ajax({
			type: 'POST',
			url: window.attach_delete_url,
			data: {pk: pk},
			success: function(data, textStatus, jqXHR){
				//  remove from the dom
				$('.postimage[data-pk='+pk+']')
					.fadeOut(200, function(){
						$(this).remove();
					});
				// remove any references to the image from textarea
				var original_text = $('#id_source_content').val();
				var new_text = original_text.replace(markdown, '')
				$('#id_source_content').val(new_text)
			},
			error: function(jqXHR, textStatus, errorThrown){
				console.log(jqXHR)
				console.log(tetStatus)
				console.log(errorThrown)
			}
		});
		e.preventDefault();
	}
	function deleteImageDragStart(e){
		// set the delete pk
		
		// set the feedback
		$('#dropbox .instructions')
			.addClass('delete')
			.text('Drag images into this box to delete');
		// remove the upload event listender
		document.getElementById('dropbox-target')
			.removeEventListener('drop', handleDrop, false);
		// add the new delete image event listeners
		document.getElementById('dropbox-target')
			.addEventListener('drop', deleteImageDrop, false);
	}
	function deleteImageDragEnd(e){
		$('#dropbox .instructions')
			.removeClass('delete')
			.text('Drag images into this box to upload');
		// add the upload event listender
		document.getElementById('dropbox-target')
			.addEventListener('drop', handleDrop, false);
	}
	/*
	 * attach the listeners
	 */
	images = document.getElementsByClassName('postimage')
	for(var i=0; i < images.length; i++){
		images[i].addEventListener(
					'dragstart',
					deleteImageDragStart,
					false);
	}
	for(var i=0; i < images.length; i++){
		images[i].addEventListener(
					'dragend',
					deleteImageDragEnd,
					false);
	}
	// the upload listenders
	document.getElementById('dropbox-target')
		.addEventListener('dragenter', handleDragEnter, false);

	document.getElementById('dropbox-target')
		.addEventListener('dragenter', handleDragEnter, false);

	document.getElementById('dropbox-target')
		.addEventListener('dragover', handleDragOver, false);

	document.getElementById('dropbox-target')
		.addEventListener('drop', handleDrop, false);
});
