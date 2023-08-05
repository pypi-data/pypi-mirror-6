$(document).ready(function(){
$('input[type="submit"]').click(function(){
        if (typeof window.tinyMCE !== 'undefined') {
            for (var id in tinyMCE.editors) {
                var ed = tinyMCE.editors[id];
                if (ed.plugins && ed.plugins.spellchecker && ed.plugins.spellchecker.active) {
                    ed.plugins.spellchecker._done();
                }
            }
        }
});
});
