;(function ( $, window, document, undefined ) {
    var pluginName = "djangoBootstrapTags",
    defaults = {};

    function Plugin ( element, options ) {
        this.element = element;
        this.settings = $.extend( {}, defaults, options );
        this._defaults = defaults;
        this._name = pluginName;
        this.init();
    }

    Plugin.prototype = {
        init: function () {
            // Hide django multi-select and create tags widget
            $(this.element).hide();
            $(this.element).after('\
                <div class="form-control tag-input-widget">\
                    <span class="labels"></span>\
                    <input type="text" class="typeahead" autocomplete="off">\
                    <div style="clear: both;"></div>\
                </div>\
            ');

            // Populate widget with selected options and initialize typeahead
            $(this.element).each(function() {
                var currentElement = this;
                var options = [];
                $(this).find('option').each(function() {
                    options.push($(this).text());

                    if($(this).is('[selected]')) {
                        $(currentElement).siblings('.tag-input-widget').children('.labels').append('\
                            <span class="label label-default">\
                                ' + $(this).text() + '\
                                <a class="remove" href="#"><span class="glyphicon glyphicon-remove"></span></a>\
                            </span>\
                        ');
                    }
                });

                // Initialize typeahead
                $(this).siblings('.tag-input-widget').children('.typeahead').typeahead({
                    source: options,
                    updater: function(item) {
                        $(this)[0].$element.siblings('.labels').append('\
                            <span class="label label-default">\
                                ' + item + '\
                                <a class="remove" href="#"><span class="glyphicon glyphicon-remove"></span></a>\
                            </span>\
                        ');
                        return '';
                    },
                });
            });

            // Remove labels on remove button click
            $('.tag-input-widget .labels').on('click', '.remove', function(e) {
                e.preventDefault();
                $(this).parent().remove();
            });

            // Set up key events for typeahead
            $('.tag-input-widget .typeahead').keyup(function( event ) {
                if( event.which == 13 && $(this).val() != '' && $(this).siblings('ul.typeahead:visible').length < 1 ) {
                    $(this).siblings('.labels').append('\
                        <span class="label label-default">\
                            ' + $(this).val() + '\
                            <a class="remove" href="#"><span class="glyphicon glyphicon-remove"></span></a>\
                        </span>\
                    ');
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

            // Process tags before form submission
            $('form').on('submit', function(e) {
                $(this).find('.tag-input').each(function() {
                    var selectElement = this;
                    $(selectElement).children().removeAttr('selected');

                    $(this).siblings('.tag-input-widget').children('.labels').children().each(function() {
                        var value = $(this).text().trim();
                        var found = false;

                        $(selectElement).children('option').each(function() {
                            if($(this).text().trim() == value) {
                                $(this).attr('selected', 'selected');
                                found = true;
                            }
                        });
                        if(!found) {
                            $(selectElement).append('<option value="' + value + '" selected="selected">' + value + '</option>');
                        }
                    });
                });
            });
        }
    };

    $.fn[ pluginName ] = function ( options ) {
        this.each(function() {
            if ( !$.data( this, "plugin_" + pluginName ) ) {
                $.data( this, "plugin_" + pluginName, new Plugin( this, options ) );
            }
        });
        return this;
    };
})( jQuery, window, document );

$(document).ready(function() {
    $('.tag-input').djangoBootstrapTags();
})