openArrow = '▼ ';
closedArrow = '► ';

if (!('open' in document.createElement('details'))){
    function noDetails(){
        if (!this.querySelector('.d-arrow')){
            var arrow = document.createElement('span');
            arrow.className = 'd-arrow';
            var detailArrow = document.createTextNode(closedArrow);
            arrow.appendChild(detailArrow);
            this.insertBefore(arrow, this.childNodes[0]);
            this.onclick = function(){
                var arrow = this.querySelector('.d-arrow');
                var details = this.parentNode;
                if (details.hasAttribute('open')){
                    details.removeAttribute('open');
                    var arrowText = closedArrow;
                } else {
                    details.setAttribute('open', 'open')
                    var arrowText = openArrow;
                }
                arrow.childNodes[0].nodeValue = arrowText;
            };
            this.click();
            this.click();
        }
    }

    document.addEventListener('DOMContentLoaded', function(){
        var styleTag = document.createElement('style');
        var styleText = document.createTextNode('details {display: block;} details > *:not(summary) {display: none;} details[open="open"] > *:not(summary) {display: block;}');
        styleTag.appendChild(styleText);
        document.head.appendChild(styleTag);
        
        var summarys = document.querySelectorAll('details > summary');
        for (var x = 0; x < summarys.length; x++){
            var summary = summarys[x];
            noDetails.call(summary);
        }
    });
} else {
    function noDetails(){}
}
