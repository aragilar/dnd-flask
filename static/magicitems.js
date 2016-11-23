function Filter(){
    var filters = [];
    var count = 0;
    var rarity = false;
    
    $(".filter").each(function(){
        var tag = $(this);
        var filter = tag.attr('id').replace('_', ' ');
        if (tag.is(':checked')){
            filters.push(filter);
            if (tag.hasClass('rarity')){
                rarity = true;
            }
        }
    });
    
    var name = $('#name').val();
    
    $('#magicitems > li').each(function(){
        var tag = $(this);
        var val = tag.children('a');
        var text = val.html();
        var data = items[text];
        var hide = false;
        
        if (rarity){
            var data_rarity = data['rarity'];
            if (typeof data_rarity === 'string'
            || data_rarity instanceof String){
                hide = filters.indexOf(data_rarity) < 0;
            } else {
                hide = true;
                $.each(data_rarity, function(x, item){
                    if (filters.indexOf(item) >= 0){
                        hide = false;
                    }
                });
            }
        }
        /*if (data === undefined){
            alert(text)
        }*/
        if (data['attunement']){
            if (filters.indexOf('attuned') < 0){
                hide = true;
            }
        } else {
            if (filters.indexOf('unattuned') < 0){
                hide = true;
            }
        }
        
        if (name != ''){
            if (data['name'].toLowerCase().indexOf(name.toLowerCase()) < 0
            && data['type'].toLowerCase().indexOf(name.toLowerCase()) < 0){
                hide = true;
            }
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
