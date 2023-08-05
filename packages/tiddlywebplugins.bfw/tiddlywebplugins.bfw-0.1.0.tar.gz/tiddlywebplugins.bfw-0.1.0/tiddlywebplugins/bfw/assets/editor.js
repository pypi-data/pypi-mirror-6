/*jslint white: true, vars: true */
/*global jQuery, wideArea */

(function($) {

"use strict";

wideArea();

$("input.list").selectize({
	delimiter: ",",
	create: true,
	preload: "focus",
	load: function(query, callback) {
		var filter = query || this.items; // default to related tags
		getTags(filter, callback); // TODO: throttle
	}
});

function getTags(filter, callback) {
	// XXX: client-side URI generation is evil
	var uri = "/tags";
	if(filter.pop) { // list of related tags
		uri += "/" + $.map(filter, function(tag) { return tag.trim(); }).
				join(",");
	}
	$("<div />").load(uri, function(data, status, xhr) {
		var tags = parseTags(this);
		tags = $.map(tags, function(tag) { return { value: tag, text: tag }; });
		callback(tags);
	});
}

function parseTags(container) {
	var tags = $("#tags", container).nextUntil("h2");
	return $.map(tags, function(node) { return $(node).text(); });
}

}(jQuery));
