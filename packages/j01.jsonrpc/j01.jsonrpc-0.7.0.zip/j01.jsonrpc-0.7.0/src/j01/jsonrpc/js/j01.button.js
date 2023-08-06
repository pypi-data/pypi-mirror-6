/* j01.button.js, disable and enable button on submit */

(function($) {
$.fn.j01ButtonDisabler = function(o) {
    if (o !== false) {
        o = $.extend({
            duration: 5000
        }, o);
    }

    function disableButton(e) {
        var selector = '#' + e.action;
        var $btn = $(selector);
        if ($btn) {
            // get loading text
            var txt = null;
            if ($btn.is('input')) {
                txt = $btn.val();
            }else{
                txt = $btn.html();
            }
            if (txt) {
                // use loading text
                $btn.data('j01-original-text', txt);
                var loading = $btn.data('j01-loading-text');
                if (loading) {
                    $btn.val(loading);
                }
            }
            $btn.prop('disabled', true);
            setTimeout(function(){
                doEnableButtonBySelector(selector);
            },o.duration);
        }
    }

    function doEnableButton($btn){
        var txt = $btn.data('j01-original-text')
        if (txt) {
            if ($btn.is('input')) {
                txt = $btn.val(txt);
            }else{
                txt = $btn.html(txt);
            }
        }
        if ($btn.prop('disabled')) {
            $btn.prop('disabled', false);
        }
    }

    function doEnableButtonBySelector(selector){
        var $btn = $(selector);
        if ($btn) {
            doEnableButton($btn);
        }
    }

    return this.each(function(){
        if (o !== false) {
            $('body').on('j01.form.button.click', function(e){
                disableButton(e);
            });
        }else{
            $btn = $(this);
            doEnableButton($btn);
        }
    });
};
})(jQuery);
