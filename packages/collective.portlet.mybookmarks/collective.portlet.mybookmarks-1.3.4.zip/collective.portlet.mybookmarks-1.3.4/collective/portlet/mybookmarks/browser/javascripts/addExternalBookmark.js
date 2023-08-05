$(document).ready(function() {
	var dd=$('#addExternalBlock');
	if (dd.length === 1) {
		var translated_label=dd.children('span#hiddenJsLabel').html();
		var translated_alt=dd.children('span#hiddenAltLabel').html();
		var href_title=$('#externalBookmarkFieldset legend').html();
		var form=dd.children('#externalBookmarkForm');
		html='<a id="addExternalLink"';
		html+='title="'+href_title+'"';
		html+='href="#">';
		html+='<img class="bookmarkIcon" src="'+portal_url+'/++resource++collective.portlet.mybookmarks.images/add.png" alt="' + translated_alt + '"/>';
		html+=translated_label;
		html+='</a>';
		form.before(html);
		$('a#addExternalLink').bind('click', function(event){
			event.preventDefault();
			form.toggle();
		});
	}
});

