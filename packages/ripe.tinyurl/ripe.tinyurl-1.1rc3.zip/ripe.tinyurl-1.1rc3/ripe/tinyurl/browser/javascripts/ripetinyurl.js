$(document).ready(function(){
    $('#tinyurl a.link-overlay').prepOverlay({
        subtype: 'ajax',
        filter: '#content>*'
    });
});
