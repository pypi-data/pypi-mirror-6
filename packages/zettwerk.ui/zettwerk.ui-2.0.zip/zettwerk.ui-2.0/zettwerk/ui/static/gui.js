$(document).ready(function() {
    enablePersonalTool();
    enableForms();
    enableDialogs();
    enableTabs();
    enableGlobalTabs();
    enableEditBar();
});

var enablePersonalTool = function() {
    // enable overlay, cause the id is changed
    // taken from Products.CMFPlone.skins.plone_ecmascript/popupforms.js
    $('#portal-personaltools-ui a[href$="/login"], #portal-personaltools-ui a[href$="/login_form"]').prepOverlay(
        {
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: 'form#login_form',
            noform: function () {
                if (location.href.search(/pwreset_finish$/) >= 0) {
                    return 'redirect';
                } else {
                    return 'reload';
                }
            },
            redirect: function () {
                var href = location.href;
                if (href.search(/pwreset_finish$/) >= 0) {
                    return href.slice(0, href.length-14) + 'logged_in';
                } else {
                    return href;
                }
            }
        }
    );

    // custom stuff
    $('#portal-personaltools-ui').hover(function() {
        $(this).addClass('ui-state-hover');
    }, function() {
        $(this).removeClass('ui-state-hover');
    });
    $('#portal-personaltools-ui dd a').hover(function() {
        $(this).addClass('ui-state-hover');
    }, function() {
        $(this).removeClass('ui-state-hover');
    });
};

var enableForms = function($content) {
    if (!$content) {
	var $content = $('body');
    }
    $content.find('.optionsToggle').removeClass('optionsToggle');
    $content.find('select, textarea, input:text, input:password').bind({
	focusin: function() {
            $(this).addClass('ui-state-focus');
        },
        focusout: function() {
            $(this).removeClass('ui-state-focus');
        }
    });

    $content.find(".hover").hover(function(){
        $(this).addClass("ui-state-hover");
    },function(){
        $(this).removeClass("ui-state-hover");
    });
}

var enableDialogs = function() {
    $("a.link-overlay").unbind('click').click(function() {
        // remove old dialogs
        $('#dialogContainer').remove();

        // use the links content as default title of the dialog
        var title = $(this).html();
        $.get($(this).attr('href'),
              {},
	      function(data) {
		  showDialogContent(data,title)
	      }
	     );
        return false; // avoid the execution of the regular link
    });

    $("form.link-overlay input[type='submit']").unbind('click').click(function() {
        // remove old dialogs
        $('#dialogContainer').remove();

        // use the links content as default title of the dialog
        var title = '';
        $.get($(this).parents('form').attr('action'),
              {},
	      function(data) {
		  showDialogContent(data,title)
	      }
	     );
        return false; // avoid the execution of the regular link
    });
};

var showDialogContent = function(data, title) {
    var $content = $(data).find('#content');

    // take the first heading as dialog title, if available
    $content.find('h1.documentFirstHeading').each(function() {
        title = $(this).html();
        $(this).hide();
    });
    $('<div id="dialogContainer" title="'+title+'"></div>').appendTo('body');

    // search for submit buttons and use them as dialog buttons
    var buttons = {};
    $content.find('input[type=submit]').each(function() {
        var buttonValue = $(this).val();
        buttons[buttonValue] = function() {
            $('input[type=submit][value='+buttonValue+']').click();
        };
        $(this).hide();
    });

    // bring up the dialog
    $content.appendTo('#dialogContainer');
    enableForms($content);

    var $dialog = $('#dialogContainer').dialog({width: '60%', buttons: buttons});
    console.log($dialog);
    $dialog.parent().css('z-index', '1000000');
};

var enableTabs = function() {
    $('div.ui-tabs > ul > li').hover(function() {
        $(this).addClass('ui-state-hover');
        $(this).find('span').addClass('ui-state-hover');
    }, function() {
        $(this).removeClass('ui-state-hover');
        $(this).find('span').removeClass('ui-state-hover');
    });
    $('div.ui-tabs > ul > li a').click(function() {
	// handle the tabs
        $(this).parent().parent().find('.ui-state-active').removeClass('ui-state-active');
        $(this).parent().addClass('ui-state-active');
        $(this).find('span').addClass('ui-state-active');

	// hide all fieldsets
	$('div.ui-tabs>fieldset,div.ui-tabs>dd').hide();

	var active_id = $(this).attr('href');  // thats the hidden legend in the fieldset
	var $active = $(active_id);

	if ($active[0].tagName.toLowerCase() == 'dd') {
	    $active.show();
	} else {
	    $active.parent().show();
	}
	return false;
    });
    $('ul.ui-tabs-nav').find('.selected').parent().addClass('ui-state-active');
};

var enableGlobalTabs = function() {
    $('#portal-globalnav-ui > li').hover(function() {
        $(this).addClass('ui-state-hover');
    }, function() {
        $(this).removeClass('ui-state-hover');
    });
};

var edit_bar_interval = null;
var enableEditBar = function() {
    edit_bar_interval = window.setInterval('enableEditBar2()', 100);
}

var enableEditBar2 = function() {
    if ($('#edit-bar-ui').length) {
	window.clearInterval(edit_bar_interval);

	$('#content-views-ui li a').hover(function() {
	    $(this).addClass('ui-state-hover');
	}, function() {
	    $(this).removeClass('ui-state-hover');
	});
	$('#content-views-ui li a').css('border', '0').css('line-height', '2em');

	$('#contentActionMenus-ui dl.actionMenu').hover(function() {
	    $(this).addClass('ui-state-hover ui-corner-bottom').css('border', '0px');
	}, function() {
	    $(this).removeClass('ui-state-hover ui-corner-bttom');
	});

	$('#contentActionMenus-ui a.actionMenuSelected').addClass('ui-state-default ui-corner-all');
	$('#contentActionMenus-ui a').addClass('ui-corner-all');
	$('#contentActionMenus-ui a').hover(function() {
	    $(this).addClass('ui-state-hover');
	}, function() {
	    $(this).removeClass('ui-state-hover');
	});

	$('dd.actionMenuContent').addClass('ui-state-active');
    }
}
