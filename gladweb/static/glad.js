/* UTILITY */

function any_contains(a, b) {
    /* any value of a is in b? */
    for (var i = 0; i < a.length; i++) {
        if ($.inArray(a[i], b) >= 0) {
            return true;
        }
    }

    return false;
}

String.prototype.endsWith = function (suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

$.fn.deserialize = function (serializedString) {
    // modified version of:
    // http://stackoverflow.com/questions/9856587/is-there-an-inverse-function-to-jquery-serialize
    // modified in a way it will only work for this site
    var $form = $(this);
    $form[0].reset();    // (A) optional
    serializedString = serializedString.replace(/\+/g, '%20'); // (B)
    var formFieldArray = serializedString.split("&");

    var data = {};

    // Loop over all name-value pairs
    $.each(formFieldArray, function (i, pair) {
        var nameValue = pair.split("=");
        var name = decodeURIComponent(nameValue[0]).toLowerCase(); // (C)
        var value = decodeURIComponent(nameValue[1]).split(',');

        if (data.hasOwnProperty(name)) {
            data[name] = [].concat(data[name], value);
        } else {
            data[name] = value;
        }
    });

    reset_form();

    /* set api */
    if (!$.isArray(data['api'])) {
        data['api'] = [data['api']];
    }
    $.each(data['api'], function (i, apistr) {
        var tmp = apistr.split('=', 2);
        var tmp2 = tmp[0].split(':');
        var version = tmp[1];
        var api = tmp2[0];
        var profile = tmp2[1];

        $form.find('select[name=api][data-api=' + api + ']').val(api + '=' + version);

        if (profile) {
            $form.find('select[name=profile][data-api=' + api + ']').val(api + '=' + profile);
        }
    });
    selection_update();

    /* set language */
    $form.find('select[name=generator]').val(data['generator'][0]);

    $.each((data['profile'] || []), function (i, profilestr) {
        var tmp = profilestr.split('=', 2);
        var api = tmp[0];
        var profile = tmp[1];

        $form.find('select[name=profile][data-api=' + api + ']').val(profilestr);
    });

    /* set extensions */
    $.each([].concat((data['extensions'] || [])), function (i, ext) {
        $form.find('select[name=extensions]').multiSelect('select', ext);
    });

    /* set options */
    $.each((data['options'] || []), function (i, option) {
        $form.find('input[name=options][value=' + option + ']').attr('checked', true);
    });

    return this;
};


/* Actual logic */

function reset_form() {
    $('#main-form')[0].reset();
    $('#extensions').find('select').multiSelect('deselect_all');
    selection_update();
}

function selection_update(event) {
    //$('[data-api]').removeAttr('hidden').removeAttr('disabled');
    $('#extensions').find('select').multiSelect('deselect_all');

    // Find selected APIs
    var apis = [];
    $('#api').find('.row').each(function (index, value) {
        var select = $(value).find('select');

        if (select.val() && !select.val().endsWith('none')) {
            apis.push(select.data('api'));
        }
    });

    /* Filter out extensions which do not exist for this API */
    $('#extensions option, #extensions li').each(function (index, option) {
        var e = $(option);
        if (any_contains(e.data('api').split(' '), apis)) {
            // Extension is part of at least one of the selected APIs
            e.removeAttr('hidden');
            e.removeAttr('disabled');
        } else {
            // Extension is not part of at least one selected API
            e.attr('hidden', 'hidden');
            e.attr('disabled', 'disabled');
        }
    });

    // Show only relevant options
    var generator = $('#generator').find('select').val();
    $('#options').find('.option[data-generator]').attr('hidden', 'hidden');
    $('#options').find('.option[data-generator=' + generator + ']').removeAttr('hidden');
    if ($('#options').find('.option:not([hidden])').length == 0) {
        // Hide the options section if there are no available options
        $('#options').attr('hidden', 'hidden');
    } else {
        $('#options').removeAttr('hidden');
    }

    // Remove errors
    if (event) {
        $('#error').remove();
    }
}

function add_extensions(extensions) {
    if (!$.isArray(extensions)) {
        extensions = extensions.replace(/,/g, ' ').replace(/\s+/g, ' ').trim().split(' ');
    }

    $('#main-form').find('select[name=extensions]').multiSelect('select', extensions);
}


$(function () {
    $('#generator').find('select').change(selection_update);
    $('#api').find('select[name=api]').change(selection_update);
    $('.extension-add-list').click(function () {
        $('#addListModal').css('visibility', 'visible');
    });
    $('.extension-addlist-add').click(function () {
        add_extensions($('#addListModal textarea').val());
        $('#addListModal textarea').val('');
        $('#addListModal').css('visibility', 'hidden');
    });
    $('.extension-addlist-close').click(function () {
        $('#addListModal').css('visibility', 'hidden');
    });
    $('.extensions-add-all').click(function () {
        $('#extensions').find('select').multiSelect('select', $('#extensions .ms-selectable li:visible').toArray().map($.text));
    });
    $('.extensions-remove-all').click(function () {
        $('#extensions').find('select').multiSelect('deselect', $('#extensions .ms-selection li:visible').toArray().map($.text));
    });

    var qs_options = {
        'prepareQuery': function (val) {
            return new RegExp(val, "i");
        },
        'testQuery': function (query, txt, _row) {
            return query.test(txt);
        }
    };

    $('#extensions').find('select').multiSelect({
        selectableHeader: "<input type='text' class='search-input u-full-width' autocomplete='off' placeholder='Search'>",
        selectionHeader: "<input type='text' class='search-input  u-full-width' autocomplete='off' placeholder='Search'>",
        afterInit: function (ms) {
            var that = this,
                $selectableSearch = that.$selectableUl.prev(),
                $selectionSearch = that.$selectionUl.prev(),
                selectableSearchString = '#' + that.$container.attr('id') + ' .ms-elem-selectable:not(.ms-selected)',
                selectionSearchString = '#' + that.$container.attr('id') + ' .ms-elem-selection.ms-selected';

            that.qs1 = $selectableSearch
                .quicksearch(selectableSearchString, qs_options)
                .on('keydown', function (e) {
                    if (e.which === 40) {
                        that.$selectableUl.focus();
                        return false;
                    }
                });

            that.qs2 = $selectionSearch
                .quicksearch(selectionSearchString, qs_options)
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

    if (window.location.hash) {
        $('#main-form').deserialize(window.location.hash.replace(/^#/, ''));
    }

    $('#generator-input').focus();
});