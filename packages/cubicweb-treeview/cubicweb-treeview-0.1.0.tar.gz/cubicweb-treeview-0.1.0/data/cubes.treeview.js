cw.treewidget = new Namespace('cw.treewidget');

$.extend(cw.treewidget, {
    validateCheckBox: function(tree_uid, required){
        var related = [[],[]];
        $('#holder_' + tree_uid + ' input:checked').each(function(){
            related[0].push($(this).val());
            related[1].push($(this).siblings('span[class="hidden"]').text());
        });
        cw.treewidget.validateRelated(null, required, tree_uid, related );
    },

    validateRelated: function(thisnode, required, tree_uid, related){
        if (thisnode){
            related[1].push($(thisnode).text());
        }
        if(required && related[0].length == 0){
            cw.treewidget.updateTreeWidgetMessage(tree_uid, "please, select at least one value");
            return;
        }
        var $holder = $('#sel_' + tree_uid);
        var rname = tree_uid.replace('--', ':');
        for(var i=0; i<related[0].length; i++){
            var $div = $('<div />');
            $div.append($('<input/>').attr({
                id: rname, name: rname,
                type: "hidden", value: related[0][i]}));
            $div.append('<a href="javascript:$.noop()" onclick="$(this).parent().remove()">[x] </a>');
            $div.append($('<span/>').html(related[1][i]));
            $holder.append($div);
        }
        $holder.trigger('md.close');
    },

    updateTreeWidgetMessage: function(tree_uid, msg){
       $('#' + tree_uid + ' div.error').empty().html(msg);
    }
});

(function ($) {
    var defaultSettings = {
        modal: true,
        width: 600,
        height: 600,
        cancelButton: 'button_cancel',
        okButton: 'button_ok',
        buttons: []
    };

    var methods = {
        __init__: function(required, multiple, url, options) {
            var tree_uid = $(this).attr('id');
            var settings = methods.initSettings(tree_uid, required, multiple, options);
            var dialog = $(this).dialog(settings);
            if(url){
                var d = $(this).loadxhtml(url);
            };
            var $holder = $('#sel_' + tree_uid);
            $holder.bind("md.close", function() {
                dialog.dialog('close');
            });
        },

        initSettings: function(tree_uid, required, multiple, options) {
            var settings = $.extend({}, defaultSettings, options);
            if (!settings.buttons.length) {
                if (multiple) {
                    settings.buttons.push({id: "btn-validate",
                                           text: settings.okButton,
                                           click: function() {
                                               cw.treewidget.validateCheckBox(tree_uid, required);
                                           }});
                }
                settings.buttons.push({id: "btn-cancel", text: settings.cancelButton,
                                       click: function() {
                                           $(this).dialog("close");
                                       }});
            }
            return settings;
        }
    };

    $.fn.treewidget = function(required, multiple, url, options) {
        return methods.__init__.apply(this, [required, multiple, url, options]);
    };
})(jQuery);
