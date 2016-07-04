var filename = 'Character.json';

var continuity = true;
var out = {};

var statList = [
    'str',
    'dex',
    'con',
    'int',
    'wis',
    'cha',
];

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
    "survival": "wis",
    "initiative": "dex",
};

function getValue(id, fail) {
    if (fail === undefined) {
        fail = 0;
    }

    var value;
    var elem = document.getElementById(id);
    if (elem) {
        value = elem.value;
    } else {
        value = fail;
    }
    return value;
}

function setValue(id, value) {
    var elem = document.getElementById(id);
    if (elem) {
        elem.value = value;
    }
}

function toMod(i) {
    var s = i.toString();
    if (i > 0) {
        s = '+' + s;
    } else if (i == 0) {
        s = '±' + s;
    }
    return s;
}

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
                if (continuity) {
                    out = data;
                }
                var tags = document.getElementsByClassName('save');
                for (var x = 0; x < tags.length; x++){
                    var tag = tags[x];
                    tag.value = "";
                }
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
    var tags = document.getElementsByClassName('save');
    //var tags = document.querySelectorAll(".save");
    var data;
    if (continuity) {
        data = out;
    } else {
        data = {};
    }
    
    for (var x = 0; x < tags.length; x++) {
        var tag = tags[x];
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
    //document.body.appendChild(element);
    element.click();
    //document.body.removeChild(element);
}

function modifiers(tag) {
    /*if (tag === undefined) {
        tag = this;
    }*/
    var value = tag.value;
    value -= 10;
    value /= 2;
    value = Math.floor(value);
    var tag = document.getElementById(tag.id + 'mod');
    tag.value = toMod(value);
}

function parseNumber(i) {
    i = parseInt(i);
    if (isNaN(i)){
        i = 0;
    }
    return i;
}

function fillAttrs() {
    var stats = {
        "str": parseNumber(getValue('strmod')),
        "dex": parseNumber(getValue('dexmod')),
        "con": parseNumber(getValue('conmod')),
        "int": parseNumber(getValue('intmod')),
        "wis": parseNumber(getValue('wismod')),
        "cha": parseNumber(getValue('chamod'))
    };
    
    var proficiency = parseNumber(getValue('proficiency'));

    var stat;
    var tag;
    var value;
    var checkbox;
    var isProficient;

    var features = getValue('features', '').toLowerCase();
    var jack = features.indexOf("jack of all trades") > -1;
    var half = parseInt(proficiency / 2);
    if (jack) {
        jack = half;
    }
    var athlete = features.indexOf("remarkable athlete") > -1;
    if (athlete) {
        athlete = half;
    }
    var athleteSkills = statList.slice(0,3);
    
    for (var key in skills) {
        stat = skills[key];
        tag = document.getElementById(key + '-value');
        if (!tag){
            tag = document.getElementById(key);
        }
        value = stats[stat];

        checkbox = document.getElementById(key)
        if (checkbox) {
            isProficient = checkbox.checked;
        } else {
            isProficient = false;
        }

        if (isProficient) {
            value += proficiency;
            if (features.indexOf("expertise: " + key) > -1) {
                value += proficiency;
            }
        } else if (jack && key != stat + 'save') {
            value += jack;
        } else if (athlete
            && key != stat + 'save'
            && athleteSkills.indexOf(stat) > -1) {
            value += athlete;
        }
        if (tag) {
            tag.value = toMod(value);
        }
    }

    value = parseNumber(getValue('perception-value'));
    value += 10;
    setValue('passive-perception', value);

    var magic = getValue('spellcasting-ability', 'aaa');
    magic = magic.slice(0, 3).toLowerCase();
    if (magic in stats) {
        value = stats[magic];
        value += proficiency;
        var value2 = value + 8;
        setValue('spell-attack', toMod(value));
        setValue('spell-save', value2);
    }
}

window.onload = function(){
    var elem;
    for (var item in statList) {
        item = statList[item];
        elem = document.getElementById(item);
        if (elem) {
            elem.addEventListener('change', modifiers);
            elem.value = '10';
            modifiers(elem);
        }
    }
    
    setValue('proficiency', 2);
    fillAttrs();
    
    var fs = {
        'load': upload,
        'calc': fillAttrs,
        'save': download,
    };
    for (var key in fs) {
        elem = document.getElementById(key);
        if (elem) {
            elem.addEventListener('click', fs[key]);
        }
    }
}
