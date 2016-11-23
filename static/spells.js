function Filter(){
    var cfilters = {};
    
    $.each(classes, function(item){
        var filter = $(document.getElementById(item));
        if (filter.is(":checked")){
            cfilters[item] = true;
        }
    });

    var filters = {};

    $.each(["name", "level", "type", "ritual"], function(x, item){
        var filter = $(document.getElementById(item));
        if (filter.attr("type") == "checkbox"){
            if (filter.is(":checked")){
                filters[item] = true;
            }
        } else {
            var temp = filter.val();
            if (temp != "" && temp !== undefined){
                filters[item] = temp;
            }
        }
    });

    var count = 0;
    
    $('#spells > li').each(function(){
        var tag = $(this);
        var val = tag.children('a');
        var text = val.html();
        var data = spells[text];
        var hide = false;
        
        $.each(cfilters, function(filter, value){
            if (value && classes[filter].indexOf(text) < 0){
                hide = true;
            }
        });

        $.each(filters, function(filter, value){
            if (value){
                if (value === true){
                    if (!data[filter]){
                        hide = true;
                    }
                } else {
                    if (data[filter].toString().toLowerCase().indexOf(value.toString().toLowerCase()) < 0){
                        hide = true;
                    }
                }
            }
        });

        if (hide){
            tag.hide();
        } else {
            tag.show();
            count += 1;
        }
    });

    $('#count').html(count);
}

$(document).ready(function(){
    $('.filter').each(function(){
        $(this).change(Filter);
    });

    Filter();
});
