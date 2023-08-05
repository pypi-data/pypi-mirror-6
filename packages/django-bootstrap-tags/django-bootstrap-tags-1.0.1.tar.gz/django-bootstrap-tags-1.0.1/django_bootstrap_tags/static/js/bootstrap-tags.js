$(document).ready(function() {
	$('.bootstrap-tags .remove').click(function(e) {
		e.preventDefault();
		$(this).parent().remove();
	});

	$('.bootstrap-tags .twitter-typeahead').keyup(function( event ) {
		if( event.which == 13 && $(this).val() != '' && $(this).siblings('ul.typeahead:visible').length < 1 ) {
			$(this).siblings('.labels').append('<span class="label label-default">'+$(this).val()+' <a class="remove" href="#"><span class="glyphicon glyphicon-remove"></span></a></span> ');
			$(this).val('');
		}
	}).keydown(function( event ) {
		if ( event.which == 13 && $(this).siblings('ul.typeahead:visible').length < 1 ) {
			event.preventDefault();
		}
		if( event.which == 8 ) {
			if( $(this).val() == '' ) {
				$(this).siblings('.labels').children().last().remove();
			}
		}
	});

	$('.bootstrap-tags').parents('form').submit(function(e) {
		$(this).find('.bootstrap-tags').each(function() {
			var vals = [];
			$(this).find('.labels').children().each(function() {
				vals.push( $(this).text().trim() );
			});
			console.log(vals);
			$(this).find('input[type=hidden]').val( vals.join(',') );
		});
	})
})

function typeahead_updater(item) {
	var element = $(this)[0].$element;
	element.siblings('.labels').append('<span class="label label-default">'+item+' <a class="remove" href="#"><span class="glyphicon glyphicon-remove"></span></a></span> ');
	return '';
}