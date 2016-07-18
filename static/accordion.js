$(document).ready(function(){
    $('.accordion > dt').addClass('dt-closed');
    $('.accordion > dd').addClass('dd-closed').hide();
    
    $('.accordion > dt').click(function(){
        var elem = $(this);
        var next = elem.next();
        if (next.is('dd')){
            if (next.hasClass('dd-closed')){
                next.slideToggle(400);
                elem.removeClass('dt-closed').addClass('dt-open');
                next.removeClass('dd-closed').addClass('dd-open');
            } else {
                next.slideUp(400);
                elem.removeClass('dt-open').addClass('dt-closed');
                next.removeClass('dd-open').addClass('dd-closed');
            }
        }
    });
});

function closeAccordions(){
    $('.accordion > dd').removeClass('dd-open').addClass('dd-closed').slideUp();
    $('.accordion > dt').removeClass('dt-open').addClass('dt-closed');
    $('._preserve').removeClass('_preserve');
}
