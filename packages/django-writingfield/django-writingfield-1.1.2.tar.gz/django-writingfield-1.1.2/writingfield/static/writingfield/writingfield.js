;(function(window, document, $, undefined) {

	function Fullscreen(element, options){
		self = this;
		self.$element = $(element);
		self.init();
	}

	Fullscreen.prototype.init = function(){

		// set the icon up
		self.icon = $('<a>', {class: 'fullscreen'});
		self.icon.click(self.dispatch)
		self.$element.before(self.icon);

		// add the class names
		this.$element.parent().addClass('fullscreen-container');

		// bind keys
		Mousetrap.bind('esc', self._deactivate);
		Mousetrap.bind(['meta+s', 'ctrl+s'], self._save);

		// add the mousetrap class so that events fire
		self.$element.addClass('mousetrap');

		// handle tabs
		self.$element.keydown(function(e) {
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

		// add in the loading div
		this.loading = $('<div>')
			.addClass('loading')
			.hide()
			.text('Saving…');
		$('body').append(this.loading);
	}

	// save
	Fullscreen.prototype._save = function(e){

		// select the elements in the filter horizontals etc
		$('div.selector-chosen option').each(function(){
			$(this).attr('selected', 'selected');
		})

		// get the form
		$form = $('#content-main form');

		// Are we using grappelli
		if ($form.length == 0) {
			$form = $('#grp-content-container form');

			// if there was no form to serialize feedback
			if ($form.length == 0) {
				console.log('Sorry, could not find any FORM to serialize. '
					  + 'What Django Admin customization are you using?');
			}
		}

		// serilaize
		data = $form.serialize();

		// send ajax
		$.ajax({
			type: 'POST',
			url: window.location.href,
			data: data,
			beforeSend: function(){
				self.loading
					.text('Saving…')
					.removeClass('saved')
					.removeClass('error')
					.fadeIn(100);
			},
			success: function(){
				self.loading
					.addClass('saved')
					.text('Saved.');
				setTimeout(function(){self.loading.fadeOut(500);}, 1000);
			},
			error: function(jqXHR, textStatus, errorThrown ){
				if (jqXHR.readyState == 0 || jqXHR.status == 0) {
					self.loading
						.addClass('saved')
						.text('Saved.');
					setTimeout(function(){self.loading.fadeOut(500);}, 1000);
				}else{
					self.loading
						.addClass('error')
						.text('Error, couldn\'t save form');
					setTimeout(function(){self.loading.fadeOut(500);}, 2000);
				}  
			}
		});

		// prevent the default
		e.preventDefault();
	}

	//  Activate the fullscreen
	Fullscreen.prototype._activate = function(el){
		el.parent().addClass('active')
	}

	// Deactivate the fullscreen
	Fullscreen.prototype._deactivate = function(){
		$('div.fullscreen-container.active').removeClass('active')
	}

	// Crude controller
	Fullscreen.prototype.dispatch = function(){

		// get the next element
		var el = $(this).next();

		// toggle ALL the things
		if(el.parent().hasClass('active')){
			self._deactivate(el);
		}else{
			self._activate(el);
		}
	}

	// the plugin jiggery pokery
	$.fn.djwf = function(options){
		this.each(function(){
			return new Fullscreen(this, options)
		});
	}
})( window, document, django.jQuery );

// let's get this party started
django.jQuery(function($){
	$('textarea.fullscreen').djwf();
});
