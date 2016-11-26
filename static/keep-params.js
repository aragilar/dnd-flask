$.expr[':'].external = function(a){
    return a.host !== location.host || a.protocol !== location.protocol;
};

$.expr[':'].internal = function(a){
    return $(a).attr('href') !== undefined && !$.expr[':'].external(a);
};

$(document).ready(function(){
    $("a:not(.dropdown-item):internal").each(function(){
        item = $(this);
        var link = item.attr('href');
        link += window.location.search;
        item.attr('href', link);
    });
});
