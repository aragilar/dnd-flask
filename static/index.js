$.expr[':'].external = function(a){
    return a.host !== location.host || a.protocol !== location.protocol;
};

$.expr[':'].internal = function(a){
    return $(a).attr('href') !== undefined && !$.expr[':'].external(a);
};

function make_responsive(){
    $("table").each(function(){
        var elem = $(this);
        if (!elem.parent().hasClass("table-responsive")){
            elem.wrap($(document.createElement("div")).addClass("table-responsive"));
        }
    });
}

$(document).ready(function(){
    $("a:internal:not(.nochange)").each(function(){
        item = $(this);
        var link = item.attr('href');
        link += window.location.search;
        item.attr('href', link);
    });
    make_responsive();
});
