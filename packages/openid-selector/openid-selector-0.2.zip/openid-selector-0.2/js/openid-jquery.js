/*
	Simple OpenID Plugin
	http://code.google.com/p/openid-selector/
	
	This code is licensed under the New BSD License.
*/

var providers;
var openid;
(function ($) {
openid = {
	version : '1.3', // version constant
	demo : false,
	demo_text : null,
	cookie_expires : 6 * 30, // 6 months.
	cookie_name : 'openid_provider',
	cookie_path : '/',

	img_path : 'images/',
	locale : null, // is set in openid-<locale>.js
	sprite : null, // usually equals to locale, is set in
	// openid-<locale>.js
	signin_text : null, // text on submit button on the form
	all_small : false, // output large providers w/ small icons
	no_sprite : false, // don't use sprite image
	image_title : '{provider}', // for image title

	input_id : null,
	method : null,
	provider_url : null,
	provider_id : null,
	openid_label : null,
	openid_username : null,
	openid_submit : null,

	/**
	 * Class constructor
	 * 
	 * @return {Void}
	 */
	init : function(input_id) {
		providers = $.extend({}, providers_large, providers_small);
		var openid_btns = $('#openid_btns');
		this.input_id = input_id;
		this.openid_label = $('#openid_label');
		this.openid_username = $('#openid_username');
		this.openid_submit = $('#openid_submit');
		$('#openid_choice').show();
		$('#openid_input_area').empty();
		var i = 0;
		// add box for each provider
		var id, box;
		for (id in providers_large) {
			box = this.getBoxHTML(id, providers_large[id], (this.all_small ? 'small' : 'large'), i++);
			openid_btns.append(box);
		}
		if (providers_small) {
			openid_btns.append('<br/>');
			for (id in providers_small) {
				box = this.getBoxHTML(id, providers_small[id], 'small', i++);
				openid_btns.append(box);
			}
		}
		$('#openid_form').submit(this.submit);
		var box_id = this.readCookie();
		if (box_id) {
			this.signin(box_id, true);
		}
	},

	/**
	 * @return {String}
	 */
	getBoxHTML : function(box_id, provider, box_size, index) {
		if (this.no_sprite) {
			var image_ext = box_size == 'small' ? '.ico.gif' : '.gif';
			return '<a title="' + this.image_title.replace('{provider}', provider.name) + '" href="javascript:openid.signin(\'' + box_id + '\');"'
					+ ' style="background: #FFF url(' + this.img_path + '../images.' + box_size + '/' + box_id + image_ext + ') no-repeat center center" '
					+ 'class="' + box_id + ' openid_' + box_size + '_btn"></a>';
		}
		var x = box_size == 'small' ? -index * 24 : -index * 100;
		var y = box_size == 'small' ? -60 : 0;
		return '<a title="' + this.image_title.replace('{provider}', provider.name) + '" href="javascript:openid.signin(\'' + box_id + '\');"'
				+ ' style="background: #FFF url(' + this.img_path + 'openid-providers-' + this.sprite + '.png); background-position: ' + x + 'px ' + y + 'px" '
				+ 'class="' + box_id + ' openid_' + box_size + '_btn"></a>';
	},

	/**
	 * Provider image click
	 * 
	 * @return {Void}
	 */
	signin : function(box_id, onload) {
		var provider = providers[box_id];
		if (!provider) {
			return;
		}
		this.highlight(box_id);
		this.setCookie(box_id);
		this.provider_id = box_id;
		this.provider_url = provider.url;
		// obtain method
		if (provider.method) {
			this.method = provider.method;
		} else {
			this.method = 'openid';
		}
		// prompt user for input?
		if (provider.label) {
			this.useInputBox(provider);
		} else {
			$('#openid_input_area').empty();
			if (!onload) {
				$('#openid_form').submit();
			}
		}
	},

	/**
	 * Sign-in button click
	 * 
	 * @return {Boolean}
	 */
	submit : function() {
		var url = openid.provider_url;
		var provider = openid.provider_id;
		var method = openid.method;
		if (url) {
			url = url.replace('{username}', $('#openid_username').val());
			openid.setOpenIdUrl(url);
		}
		if (openid.demo) {
			alert(openid.demo_text + "\r\n" + document.getElementById(openid.input_id).value);
			return false;
		}
		openid.setProvider(provider);
		openid.setMethod(method);
		if (url && url.indexOf("javascript:") == 0) {
			url = url.substr("javascript:".length);
			eval(url);
			return false;
		}
		return true;
	},

	/**
	 * @return {Void}
	 */
	setOpenIdUrl : function(url) {
		var hidden = document.getElementById(this.input_id);
		if (hidden != null) {
			hidden.value = url;
		} else {
			$('#openid_form').append('<input type="hidden" id="' + this.input_id + '" name="' + this.input_id + '" value="' + url + '"/>');
		}
	},

	/**
	 * @return {Void}
	 */
	setProvider : function(provider) {
		var hidden = document.getElementById("provider");
		if (hidden != null) {
			hidden.value = provider;
		} else {
			$('#openid_form').append('<input type="hidden" id="provider" name="provider" value="' + provider + '"/>');
		}
	},

	/**
	 * @return {Void}
	 */
	setMethod : function(method) {
		var hidden = document.getElementById("method");
		if (hidden != null) {
			hidden.value = method;
		} else {
			$('#openid_form').append('<input type="hidden" id="method" name="method" value="' + method + '"/>');
		}
	},

	/**
	 * @return {Void}
	 */
	highlight : function(box_id) {
		// remove previous highlight.
		var highlight = $('#openid_highlight');
		if (highlight) {
			highlight.replaceWith($('#openid_highlight a')[0]);
		}
		// add new highlight.
		$('.' + box_id).wrap('<div id="openid_highlight"></div>');
	},

	setCookie : function(value) {
		var date = new Date();
		date.setTime(date.getTime() + (this.cookie_expires * 24 * 60 * 60 * 1000));
		var expires = "; expires=" + date.toGMTString();
		document.cookie = this.cookie_name + "=" + value + expires + "; path=" + this.cookie_path;
	},

	readCookie : function() {
		var nameEQ = this.cookie_name + "=";
		var ca = document.cookie.split(';');
		for ( var i = 0; i < ca.length; i++) {
			var c = ca[i];
			while (c.charAt(0) == ' ')
				c = c.substring(1, c.length);
			if (c.indexOf(nameEQ) == 0)
				return c.substring(nameEQ.length, c.length);
		}
		return null;
	},

	/**
	 * @return {Void}
	 */
	useInputBox : function(provider) {
		var input_area = $('#openid_input_area');
		var label = provider.label;
		var id = 'openid_username';

		input_area.empty();
		this.openid_label.text(label);
		input_area.append(this.openid_label);

		if (provider.name == 'OpenID') {
			id   = this.input_id;
			this.openid_username.val('http://');
			this.openid_username.css('background', '#FFF url(' + this.img_path + 'openid-inputicon.gif) no-repeat scroll 0 50%')
					    .css('padding-left', '18px');
		} else {
			this.openid_username.val('');
			this.openid_username.css('background', 'white').css('padding-left', '18px');
		}
		input_area.append(this.openid_username);
		this.openid_username.trigger('change');

		this.openid_submit.val(this.signin_text);
		input_area.append(this.openid_submit);

		$('#' + id).focus();
	},

	setDemoMode : function(demoMode) {
		this.demo = demoMode;
	}
};
})(jQuery);
