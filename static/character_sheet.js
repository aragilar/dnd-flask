var filename = 'Character.json';

function upload() {
    var file = document.getElementById("fileselect");
    file = file.files;
    if (file.length){
        file = file[0];
        filename = file.name;
        var reader = new FileReader();
        reader.onload = function(event){
            try {
                var text = reader.result;
                data = JSON.parse(text);
                for (var key in data) {
                    var tag = document.getElementById(key);
                    if (tag) {
                        if (tag.type == "checkbox" || tag.type == "radio") {
                            tag.checked = Boolean(data[key]);
                        } else {
                            tag.value = data[key];
                            if (['str', 'dex', 'con', 'int', 'wis', 'cha'].indexOf(key) >= 0) {
                                modifiers(tag);
                            }
                        }
                    }
                }
            } catch (err) {
                alert(err);
            }
        }
        reader.readAsText(file);
    } else {
        alert("Please select a file.");
    }
}

function download() {
    var tags = document.querySelectorAll(".save");
    var data = {};
    
    for (var x = 0; x < tags.length; x++) {
        tag = tags[x];
        if (tag.type === "checkbox") {
            data[tag.id] = tag.checked;
        } else {
            data[tag.id] = tag.value;
        }
    }
    
    data = JSON.stringify(data, null, 4);
    /*alert(data);*/
    
    /*var element = document.getElementById('downloadlink');*/
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(data));
    element.setAttribute('download', filename);
    element.setAttribute('target', '_blank');
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

function modifiers(tag) {
    var value = tag.value;
    value -= 10;
    value /= 2;
    value = Math.floor(value);
    var tag = document.getElementById(tag.id + 'mod');
    if (value >= 0) {
        value = '+' + value;
    } else {
        value = value.toString();
    }
    tag.value = value;
}

function fillAttrs() {
    var skills = {
        "strsave": "str",
        "dexsave": "dex",
        "consave": "con",
        "intsave": "int",
        "wissave": "wis",
        "chasave": "cha",
        "acrobatics": "dex",
        "animal-handling": "wis",
        "arcana": "int",
        "athletics": "str",
        "deception": "cha",
        "history": "int",
        "insight": "wis",
        "intimidation": "cha",
        "investigation": "int",
        "medicine": "wis",
        "nature": "int",
        "perception": "wis",
        "performance": "cha",
        "persuasion": "cha",
        "religion": "int",
        "sleight-of-hand": "dex",
        "stealth": "dex",
        "survival": "wis"
    };
    
    var stats = {
        "str": parseInt(document.getElementById('strmod').value),
        "dex": parseInt(document.getElementById('dexmod').value),
        "con": parseInt(document.getElementById('conmod').value),
        "int": parseInt(document.getElementById('intmod').value),
        "wis": parseInt(document.getElementById('wismod').value),
        "cha": parseInt(document.getElementById('chamod').value)
    };
    
    var proficiency = parseInt(document.getElementById('proficiency').value);
    var stat;
    var tag;
    var value;
    var isProficient;
    var features = document.getElementById('features').value.toLowerCase();
    var jack = features.indexOf("jack of all trades") > -1;
    if (jack) {
        jack = parseInt(proficiency / 2);
    }
    
    for (var key in skills) {
        stat = skills[key];
        tag = document.getElementById(key + '-value');
        value = stats[stat];
        isProficient = document.getElementById(key).checked;
        if (isProficient) {
            value += proficiency;
            if (features.indexOf("expertise: " + key) > -1) {
                value += proficiency;
            }
        } else if (jack && key != stat + 'save') {
            value += jack;
        }
        if (value >= 0) {
            value = '+' + value;
        } else {
            value = value.toString();
        }
        tag.value = value;
    }
    
    value = stats['dex'];
	if (jack) {
		value += jack;
	}
    if (value >= 0) {
        value = '+' + value;
    } else {
        value = value.toString();
    }
    document.getElementById('initiative'). value = value;

    value = parseInt(document.getElementById('perception-value').value);
    value += 10;
    document.getElementById('passive-perception').value = value;

    var magic = document.getElementById('spellcasting-ability').value;
    magic = magic.slice(0, 3).toLowerCase();
    if (magic in stats) {
        value = stats[magic];
        value += proficiency;
        var value2 = value + 8;
        if (value >= 0) {
            value = '+' + value;
        } else {
            value = value.toString();
        }
        document.getElementById('spell-attack').value = value;
        document.getElementById('spell-save').value = value2;
    }
}
