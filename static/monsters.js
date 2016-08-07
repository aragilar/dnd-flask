function getCR(val){
    val = val.trim();
    try {
        if (val.startsWith('1/')){
            val = 1.0 / parseFloat(val.slice(2).trim());
        } else if (val.includes('/')){
            val = val.split('/');
            val = parseFloat(val[0].trim()) / parseFloat(val[1].trim());
        } else {
            val = parseFloat(val);
        }
    } catch (err){
        val = undefined;
    }
    return val;
}

function Filter(){
    var filters = [];
    var count = 0;
    var size = false;
    
    $(".filter").each(function(){
        var tag = $(this);
        var filter = tag.attr('id').replace('_', ' ');
        if (tag.is(':checked')){
            filters.push(filter);
            if (tag.hasClass('size')){
                size = true;
            }
        }
    });
    
    var name = $('#name').val();
    var type = $('#type').val();
    var mincr = getCR($('#crge').val());
    var maxcr = getCR($('#crle').val());
    
    $('#monsters > li').each(function(){
        var tag = $(this);
        var val = tag.children('a');
        var text = val.html();
        var data = monsters[text];
        var hide = false;
        
        if (size){
            var data_size = data['size'];
            if (typeof data_size === 'string'
            || data_size instanceof String){
                hide = filters.indexOf(data_size) < 0;
            } else {
                hide = true;
                $.each(data_size, function(x, item){
                    if (filters.indexOf(item) >= 0){
                        hide = false;
                    }
                });
            }
        }
        
        if (filters.indexOf('legendary') >= 0 && !data['legendary']){
            hide = true;
        }
        
        if (name != ''){
            if (data['name'].toLowerCase().indexOf(name.toLowerCase()) < 0){
                hide = true;
            }
        }
        if (type != ''){
            if (data['type'].toLowerCase().indexOf(type.toLowerCase()) < 0){
                hide = true;
            }
        }
        
        if (mincr !== undefined && data['challenge rating'] < mincr){
            hide = true;
        }
        
        if (maxcr !== undefined && data['challenge rating'] > maxcr){
            hide = true;
        }
        
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
