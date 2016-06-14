function filter(){
    var filters = [];
    var count = 0;
    var rarity = false;
    
    tags = document.querySelectorAll('.filter');
    for (var x = 0; x < tags.length; x++){
        var tag = tags[x];
        var filter = tag.id;
        filter = filter.replace('_', ' ');
        if (tag.checked){
            filters.push(filter);
            if (tag.className.indexOf('rarity') >= 0){
                rarity = true;
            }
        }
    }
    
    var name = document.getElementById('name').value;
    
    console.log(filters);
    
    tags = document.querySelectorAll('#magicitems > tbody > tr');
    for (var x = 0; x < tags.length; x++){
        var tag = tags[x];
        var val = tag.querySelector('td > details > summary');
        var text = val.innerHTML;
        text = text.trim();
        var data = items[text];
        //console.log(JSON.stringify(data['rarity']));
        var hide;
        if (rarity){
            data_rarity = data['rarity'];
            if (typeof data_rarity === 'string' ||
                data_rarity instanceof String){
                hide = filters.indexOf(data_rarity) < 0;
            }
            else{
                hide = true;
                for (var y = 0; y < data_rarity.length; y++){
                    if (filters.indexOf(data_rarity[y]) > 0){
                        hide = false;
                    }
                }
            }
        }
        else{
            hide = false;
        }
        
        if (filters.indexOf('attuned') < 0){
            if (data['attunement']){
                hide = true;
            }
        }
        if (filters.indexOf('unattuned') < 0){
            if (!data['attunement']){
                hide = true;
            }
        }
        
        if (name !== ''){
            if (data['name'].toLowerCase().indexOf(name.toLowerCase()) < 0 && data['type'].toLowerCase().indexOf(name.toLowerCase()) < 0){
                hide = true;
            }
        }
        
        tag.style.display = hide ? 'none' : 'table-row';
        if (!hide){
            count++;
        }
    }
    
    //Break Line//
    
    document.getElementById('count').innerHTML = count;
}

document.addEventListener('DOMContentLoaded', function(){
    var tags = document.querySelectorAll('.filter');
    for (var x = 0; x < tags.length; x++){
        var tag = tags[x];
        tag.setAttribute('onchange', 'filter()');
        //tag.setAttribute('onblur', 'filter()');
    }
    
    filter();
});
