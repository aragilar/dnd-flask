var filename = "Character.json";

var continuity = true;
var out = {};

var statList = [
    "str",
    "dex",
    "con",
    "int",
    "wis",
    "cha",
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
    "survival": "wis"
};

function toMod(i) {
    var s = i.toString();
    if (i > 0) {
        s = "+" + s;
    } else if (i == 0) {
        s = "±" + s;
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
                var tags = $(".save").each(function(){
                    var tag = $(this);
                    tag.val("");
                });
                for (var key in data) {
                    var tag = $("#" + key);
                    if (tag.length) {
                        if (tag.attr("type") == "checkbox" || tag.attr("type") == "radio") {
                            tag.prop("checked", Boolean(data[key]));
                        } else {
                            tag.val(data[key]);
                            if (statList.indexOf(key) >= 0) {
                                modifiers.call(tag);
                            }
                        }
                    }
                }

                fillAttrs();
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
    var tags = $(".save");
    var data;
    if (continuity) {
        data = out;
    } else {
        data = {};
    }

    tags.each(function(){
        var tag = $(this);
        if (tag.prop("type") === "checkbox") {
            data[tag.prop("id")] = Boolean(tag.prop("checked"));
        } else {
            data[tag.prop("id")] = tag.val();
        }
    });

    data = JSON.stringify(data, null, 4);
    var blob = new Blob([data], {type: "text/plain"});
    var href = window.URL.createObjectURL(blob);
    var element = document.createElement("a");
    element.href = href;
    element.download = filename;
    element.target = "_blank";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    window.URL.revokeObjectURL(blob);
}

function modifiers() {
    var elem = $(this);
    var value = elem.val();
    if (value === ""){
        value = elem.prop("placeholder");
    }
    value = parseNumber(value);
    value -= 10;
    value /= 2;
    value = Math.floor(value);
    var tag = $("#" + this.id + "mod");
    if (tag.length) {
        tag.val(toMod(value));
    }
}

function parseNumber(i) {
    i = parseInt(i);
    if (isNaN(i)){
        i = 0;
    }
    return i;
}

function fillAttrs() {
    $.each(statList, function(x, item){
        modifiers.call(document.getElementById(item));
    });

    var stats = {
        "str": parseNumber($("#strmod").val()),
        "dex": parseNumber($("#dexmod").val()),
        "con": parseNumber($("#conmod").val()),
        "int": parseNumber($("#intmod").val()),
        "wis": parseNumber($("#wismod").val()),
        "cha": parseNumber($("#chamod").val()),
    };

    var pElem = $("#proficiency");
    var proficiency = pElem.val();
    if (proficiency == ""){
        proficiency = pElem.prop("placeholder");
    }
    var proficiency = parseNumber(proficiency);

    var stat;
    var tag;
    var value;
    var checkbox;
    var isProficient;

    var features = $("#features", "").val().toLowerCase();
    var half = parseInt(proficiency / 2);
    var jack = features.indexOf("jack of all trades") > -1;
    if (jack) {
        jack = half;
    } else {
        jack = 0;
    }
    var athlete = features.indexOf("remarkable athlete") > -1;
    if (athlete) {
        athlete = half;
    } else {
        athlete = 0;
    }
    var athleteSkills = statList.slice(0,3);

    for (var key in skills) {
        stat = skills[key];
        tag = $("#" + key + "-value");
        value = stats[stat];

        checkbox = $("#" + key)
        if (checkbox.length) {
            isProficient = checkbox.prop("checked");
        } else {
            isProficient = false;
        }

        if (isProficient) {
            value += proficiency;
            var expertise = key.split("-").join(" ");
            expertise = "expertise: " + expertise;
            expertise = features.indexOf(expertise) > -1;
            if (expertise) {
                value += proficiency;
            }
        } else if (jack && key != stat + "save") {
            value += jack;
        } else if (athlete
            && key != stat + "save"
            && athleteSkills.indexOf(stat) > -1) {
            value += athlete;
        }
        if (tag) {
            tag.val(toMod(value));
        }
    }

    value = stats["dex"];
    if (jack) {
        value += jack;
    } else if (athlete) {
        value += athlete;
    }
    $("#initiative").val(toMod(value));

    value = parseNumber($("#perception-value").val());
    value += 10;
    $("#passive-perception").val(value);

    var magic = $("#spellcasting-ability").val();
    if (magic.length > 3){
        magic = magic.slice(0, 3);
    }
    magic = magic.toLowerCase();
    if (magic in stats) {
        value = stats[magic];
        value += proficiency;
        var value2 = value + 8;
        $("#spell-attack").val(toMod(value));
        $("#spell-save").val(value2);
    }
}

$(function(){
    var elem;
    fillAttrs();

    $.each(
        statList.concat(Object.keys(skills)),
        function(x, item){
            $("#" + item).change(fillAttrs);
        }
    );

    $("#fileselect").change(upload);
    $("#save").click(download);
    $("#calc").click(fillAttrs);
    $("#proficiency").change(fillAttrs);
    $("#features").change(fillAttrs);
    $("#spellcasting-ability").change(fillAttrs);
})
