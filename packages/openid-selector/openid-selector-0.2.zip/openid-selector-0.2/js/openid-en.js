/*
	Simple OpenID Plugin
	http://code.google.com/p/openid-selector/
	
	This code is licensed under the New BSD License.
*/

var providers_large = {
	google : {
		name : 'Google',
		method : 'google_oauth2',
		url : null
	},
	yahoo : {
		name : 'Yahoo',
		method : 'yahoo',
		url : 'http://me.yahoo.com/'
	},
	linkedin : {
		name : 'LinkedIn',
		method : 'linkedin',
		url : null
	},
	twitter : {
		name : 'Twitter',
		method : 'twitter',
		url : null
	},
	facebook : {
		name : 'Facebook',
		method : 'facebook',
		url : null
	}
};

var providers_small = {
	aol : {
		name : 'AOL',
		label : 'Enter your AOL screenname.',
		url : 'http://openid.aol.com/{username}'
	},
	winliveid : {
		name : 'Live',
		method : 'live',
		url : null
	},
	verisign : {
		name : 'Verisign',
		label : 'Enter your Verisign username',
		url : 'http://{username}.pip.verisignlabs.com/'
	},
	myopenid : {
		name : 'MyOpenID',
		label : 'Enter your MyOpenID username.',
		url : 'http://{username}.myopenid.com/'
	},
	livejournal : {
		name : 'LiveJournal',
		label : 'Enter your Livejournal username.',
		url : 'http://{username}.livejournal.com/'
	},
	flickr : {
		name : 'Flickr',        
		label : 'Enter your Flickr username.',
		url : 'http://flickr.com/{username}/'
	},
	technorati : {
		name : 'Technorati',
		label : 'Enter your Technorati username.',
		url : 'http://technorati.com/people/technorati/{username}/'
	},
	wordpress : {
		name : 'Wordpress',
		label : 'Enter your Wordpress username.',
		url : 'http://{username}.wordpress.com/'
	},
	blogger : {
		name : 'Blogger',
		label : 'Enter your Blogger account',
		url : 'http://{username}.blogspot.com/'
	},
	launchpad : {
		name : 'Launchpad',
		label : 'Enter your Launchpad username',
		url : 'https://launchpad.net/~{username}'
	},
	github : {
		name : 'Github',
		method : 'github',
		url : null,
	},
	bitbucket : {
		name : 'Bitbucket',
		method : 'bitbucket',
		url : null,
	},
	vidoop : {
		name : 'Vidoop',
		label : 'Enter your Vidoop username',
		url : 'http://{username}.myvidoop.com/'
	},
	claimid : {
		name : 'ClaimID',
		label : 'Enter your ClaimID username',
		url : 'http://claimid.com/{username}'
	},
	clickpass : {
		name : 'ClickPass',
		label : 'Enter your ClickPass username',
		url : 'http://clickpass.com/public/{username}'
	},
	google_profile : {
		name : 'Google Profile',
		method : 'google',
		label : 'Enter your Google Profile username',
		url : 'http://www.google.com/profiles/{username}'
	},
	openid : {
		name : 'OpenID',
		label : 'Enter your OpenID to any provider',
		url : null
	},
	mailru : {
		name : 'mail.ru',
		method : 'mailru',
		url : 'http://openid.mail.ru/'
	},
	yandex : {
		name : 'Яндекс',
		url : 'http://openid.yandex.ru'
	},
	rambler : {
		name : 'Рамблер',
		url : 'http://www.rambler.ru'
	},
	vkontakte : {
		name : 'ВКонтакте',
		url : 'http://vkontakteid.ru'
	}
};





openid.locale = 'en';
openid.sprite = 'en'; // reused in german& japan localization
openid.demo_text = 'In client demo mode. Normally would have submitted OpenID:';
openid.signin_text = 'Sign-In';
openid.image_title = 'log in with {provider}';
