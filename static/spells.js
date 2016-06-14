function filterClass(){
    var filters = {};
    
    for (item in classes){
        var filter = document.getElementById(item);
        if (filter.getAttribute("type") == "checkbox"){
            if (filter.checked){
                filters[item] = true;
            }
        } else {
            var temp = filter.value;
            if (temp != '' && temp != null){
                filters[item] = temp;
            }
        }
    }
    
    tags = document.querySelectorAll('#spells > tbody > tr');
    for (var x = 0; x < tags.length; x++){
        var tag = tags[x];
        var val = tag.querySelector('td > details > summary');
        var text = val.innerHTML;
        var data = spells[text];
        //alert(JSON.stringify(data));
        var hide = false;
        for (var filter in filters){
            f = filters[filter];
            if (f){
                if (classes[filter].indexOf(text) < 0){
                    hide = true;
                }
            }
        }
        tag.style.display = hide ? 'none' : 'table-row';
    }
    
    //Break Line//
    
    var filters = {};

    var f = ["name", "level", "type", "ritual"/*, "nonverbal", "nonsomatic", "immaterial"*/];
    for (var x = 0; x < f.length; x++){
        var item = f[x];
        var filter = document.getElementById(item);
        if (filter.getAttribute("type") == "checkbox"){
            if (filter.checked){
                filters[item] = true;
            }
        } else {
            var temp = filter.value;
            if (temp != '' && temp != null){
                filters[item] = temp;
            }
        }
    }
    
    var count = 0;
    
    tags = document.querySelectorAll('#spells > tbody > tr');
    for (var x = 0; x < tags.length; x++){
        var tag = tags[x];
        var val = tag.querySelector('td > details > summary');
        var text = val.innerHTML;
        text = text.trim();
        var data = spells[text];
        //alert(JSON.stringify(data));
        var hide = tag.style.display !== 'table-row';
        for (var filter in filters){
            f = filters[filter];
            if (f){
                if (f === true){
                    if (!data[filter]){
                        hide = true;
                    }
                } else {
                    if (data[filter].toLowerCase().indexOf(f.toLowerCase()) < 0){
                        hide = true;
                    }
                }
            }
        }
        tag.style.display = hide ? 'none' : 'table-row';
        if (!hide){
            count += 1;
        }
    }
    
    document.getElementById('count').innerHTML = count;
}

document.addEventListener('DOMContentLoaded', function(){
    var tags = document.querySelectorAll('.filter');
    for (var x = 0; x < tags.length; x++){
        var tag = tags[x];
        tag.setAttribute('onchange', 'filterClass()');
        //tag.setAttribute('onblur', 'filterClass()');
    }
    
    var n;
    for (n in classes){
        var tag = document.getElementById(n);
        tag.setAttribute('onchange', 'filterClass()');
    }
    
    filterClass();
});
