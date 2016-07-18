$(document).ready(function(){
    $('.accordion > dt').addClass('dt-closed');
    $('.accordion > dd').addClass('dd-closed').hide();
    
    $('.accordion > dt').click(function(){
        var elem = $(this);
        var next = elem.next();
        if (next.is('dd')){
            next.slideToggle(400);
            elem.toggleClass('dt-closed dt-open');
            next.toggleClass('dd-closed dd-open');
        }
    });
});