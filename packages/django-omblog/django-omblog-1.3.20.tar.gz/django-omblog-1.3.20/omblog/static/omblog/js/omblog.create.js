$(function(){

	$('#id_title').autosize();
	$('#id_description').autosize();

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
		// title
		if(data.errors.title){
			$('#id_title')
				.parent()
				.addClass('errors')
		}
		if(data.errors.description){
			$('#id_description')
				.parent()
				.addClass('errors')
		}
		//console.log(data)
	}
	process_valid = function(data, textStaus, jqXHR){
		window.location = data.url
	}
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
	 * Set up the keyboard shortcuts
	 */
	// add mouse trap to all inputs and text areas
	$('input, textarea').addClass('mousetrap');

	Mousetrap.bind(['ctrl+s', 'meta+s'], function(e){
		// prevent default
		if (e.preventDefault) {
			e.preventDefault();
		} else {
			e.returnValue = false;
		}
		save();
	});
});
