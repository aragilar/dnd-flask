if (!('open' in document.createElement('details'))){
    function toggle(){
        var details = this.parentNode;
        if (details.hasAttribute('open')){
            details.removeAttribute('open');
        } else {
            details.setAttribute('open', 'open');
        }
    }
    
    function noDetails(){
        this.onclick = toggle;
        this.click();
        this.click();
    }

    document.addEventListener('DOMContentLoaded', function(){
        var styleTag = document.createElement('style');
        var styleText = document.createTextNode('details {display: block;} details > *:not(summary) {display: none;} details[open="open"] > *:not(summary) {display: block;} details summary::before {content: "► ";} details[open] summary::before {content: "▼ ";}');
        styleTag.appendChild(styleText);
        document.head.insertBefore(styleTag, document.head.childNodes[0]);
        
        var summarys = document.querySelectorAll('details > summary');
        for (var x = 0; x < summarys.length; x++){
            var summary = summarys[x];
            noDetails.call(summary);
        }
    });
} else {
    function noDetails(){}
}
