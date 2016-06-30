if (!('open' in document.createElement('details'))){
    var details_style_text = ''
        + 'details {display: block;} '
        + 'details > *:not(summary) {display: none;} '
        + 'details[open="open"] > *:not(summary) {display: block;} ';
    
    var b = false;
    for (var x in document.styleSheets){
        var sheet = document.styleSheets[x];
        for (var y in sheet.cssRules){
            var rule = sheet.cssRules[y];
            if (rule instanceof CSSRule){
                console.log(rule.cssText);
            }
            if (rule instanceof CSSRule && rule.cssText.indexOf('summary::-webkit-details-marker') > -1){
                b = true;
                break;
            }
        }
        if (b){
            break;
        }
    }
    if (!b){
        details_style_text += ''
            + 'details summary::before {content: "► ";} '
            + 'details[open] summary::before {content: "▼ ";}';
    }

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
        var styleText = document.createTextNode(details_style_text);
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
