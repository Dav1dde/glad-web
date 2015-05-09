function any_contains(a, b) {
    /* any value of a is in b? */
    for (var i = 0; i < a.length; i++) {
        if ($.inArray(a[i], b) >= 0) {
            return true;
        }
    }

    return false;
}

String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
};


function show_only_specification(specification) {
    var profile_input = $('#profile-input');

    $('[data-specification]').removeAttr('hidden').removeAttr('disabled');
    $('[data-specification]:not([data-specification="' + specification + '"])').attr('hidden', 'hidden').attr('disabled', 'disabled');

    var options = profile_input.find('option:not([hidden])');
    if (options.length == 0) {
        profile_input
            .val('')
            .attr('disabled', 'disabled');
    } else {
        profile_input
            .val(options.val())
            .removeAttr('disabled');
    }
}

var bar = true;

function selection_update(event) {
    var specification = $('#specification-input').val();

    //$('[data-api]').removeAttr('hidden').removeAttr('disabled');
    show_only_specification(specification);

    var apis = [];
    $('#api').find('[data-specification="' + specification + '"]').each(function (index, value) {
        var select = $(value).find('select');

        if (!select.val().endsWith('none')) {
            apis.push(select.data('api'));
        }
    });

    /* Filter out extensions which do not exist for this API */
    $('#extensions option, #extensions li').each(function (index, option) {
        var e = $(option);
        if (!any_contains(e.data('api').split(' '), apis)) {
            e.attr('hidden', 'hidden');
            e.attr('disabled', 'disabled');
        }
    });

    /* Remove errors */
    if (event) {
        $('#error').remove();
    }
}


$(function () {
    $('#specification-input').change(selection_update);
    $('#api').find('select').change(selection_update);

    $('#extensions select').multiSelect({
        selectableHeader: "<input type='text' class='search-input u-full-width' autocomplete='off' placeholder='Search'>",
        selectionHeader: "<input type='text' class='search-input  u-full-width' autocomplete='off' placeholder='Search'>",
        afterInit: function (ms) {
            var that = this,
                $selectableSearch = that.$selectableUl.prev(),
                $selectionSearch = that.$selectionUl.prev(),
                selectableSearchString = '#' + that.$container.attr('id') + ' .ms-elem-selectable:not(.ms-selected)',
                selectionSearchString = '#' + that.$container.attr('id') + ' .ms-elem-selection.ms-selected';

            that.qs1 = $selectableSearch.quicksearch(selectableSearchString)
                .on('keydown', function (e) {
                    if (e.which === 40) {
                        that.$selectableUl.focus();
                        return false;
                    }
                });

            that.qs2 = $selectionSearch.quicksearch(selectionSearchString)
                .on('keydown', function (e) {
                    if (e.which == 40) {
                        that.$selectionUl.focus();
                        return false;
                    }
                });
        },
        afterSelect: function () {
            this.qs1.cache();
            this.qs2.cache();
        },
        afterDeselect: function () {
            this.qs1.cache();
            this.qs2.cache();
        }
    });

    selection_update();
});