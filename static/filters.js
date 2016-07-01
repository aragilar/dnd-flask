function getQuery(){
    var obj = {};
    if (window.location.search.length > 0){
        window.location.search.slice(1).split('&').forEach(function(item){
            var key = item.split('=', 2);
            var value = key[1].replace('%20', ' ');
            key = key[0];
            obj[key] = value
        });
    }
    return obj;
}

window.onload = function(){
    var query = getQuery();
    var elem = document.getElementById("filter");
    if (query.hasOwnProperty('filter')){
        elem.value = query['filter'];
    }
    elem.addEventListener('change', function(){
        if (this.value != '-'){
            window.location.search = 'filter=' + this.value;
        } else {
            window.location.search = '';
        }
    });
};
