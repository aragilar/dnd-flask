String.prototype.format = function(){
    let s = this;
    for (let i = 0; i < arguments.length; i++){
        s = s.replace(
            new RegExp("\\{" + i + "\\}", "gm"),
            arguments[i]
        );
    }
    return s;
}

let elements = {
    list: '<div class="col-xs-12 col-sm-6 col-md-4">' +
        '<input type="text" class="name form-control" placeholder="{0}">' +
        '</div>',
    list_wide: '<div class="col-xs-12">' +
        '<input type="text" class="name form-control" placeholder="{0}">' +
        '</div>',
    dict: '<div class="col-xs-12">' +
        '<input type="text" class="name form-control" placeholder="{0}">' +
        '<textarea class="value form-control" placeholder="{0} description"></textarea>' +
        '</div>',
    dict_int: '<div class="col-xs-12 col-sm-6 col-md-4">' +
        '<input type="text" class="name form-control" placeholder="{0}">' +
        '<input type="number" class="value form-control" placeholder="0">' +
        '</div>',
}

function create_input(groupname){
    let elem = $(this);
    let parent;
    if (elem.hasClass('save-group')){
        parent = elem;
    }
    else {
        parent = elem.parent().find('.save-group');
    }
    let new_item = elements[parent.attr('type')];
    if (new_item === undefined){
        new_item = elements.list;
    }
    new_item = new_item.format(parent.attr('placeholder'));
    new_item = $(new_item);
    parent.append(new_item);
    return new_item;
}

function add_input(){
    let new_item = create_input.call(this);
    new_item.find('.name')
        .focusout(remove_empty)
        .keydown(function(event){
            let keyCode = (event.keyCode ? event.keyCode : event.which);
            if (keyCode == 13) { // 'enter' key
                remove_empty.call(this);
            }
        })
        .focus();
}

function remove_empty(){
    let elem = $(this);
    if (elem.val().trim() == ''){
        elem.parent().remove();
    }
}

function save(){
    let data = {name: ''};
    $('.save').each(function(){
        let elem = $(this);
        let value = elem.val().trim();
        if (value != ''){
            if (elem.attr('type') == 'number'){
                value = parseInt(value);
            }
            data[elem.attr('id')] = value;
        }
    });

    $('.save-group').each(function(){
        let parent = $(this);
        let temp;
        let add = false;
        if (parent.attr('type').startsWith('dict')){
            temp = {};
            parent.find('> div').each(function(){
                let elem = $(this);
                let name = elem.find('.name').val().trim();
                elem = elem.find('.value');
                let value = elem.val().trim();
                if (elem.attr('type') == 'number'){
                    if (value == ''){
                        value = '0';
                    }
                    value = parseInt(value);
                }
                temp[name] = value;
            });
            add = Boolean(Object.keys(temp).length);
        }
        else {
            temp = [];
            parent.find('.name').each(function(){
                let elem = $(this);
                let value = elem.val().trim();
                if (value != ''){
                    if (elem.attr('type') == 'number'){
                        value = parseInt(value);
                    }
                    temp.push(value);
                }
            });
            add = Boolean(temp.length);
        }
        if (add){
            data[parent.attr('id')] = temp;
        }
    });

    let filename = data.name.toLowerCase();
    filename = filename.split(' ').join('-');
    filename = filename.split('/').join('-');
    filename = filename.split("'").join('');
    filename += '.json';
    if (filename == '.json'){
        filename = 'no-name.json';
    }
    data = JSON.stringify(data, null, 4);
    let blob = new Blob([data], {type: 'text/plain'});
    let href = window.URL.createObjectURL(blob);
    let element = document.createElement('a');
    element.href = href;
    element.download = filename;
    element.target = '_blank';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    window.URL.revokeObjectURL(blob);
}

function load(){
    let file = document.getElementById("load");
    file = file.files;
    if (file.length){
        file = file[0];
        filename = file.name;
        let reader = new FileReader();
        reader.onload = function(event){
            let text = reader.result;
            let data = JSON.parse(text);

            $('.save').val('').each(function(){
                let elem = $(this);
                let key = elem.attr('id');
                let value = data[key];
                if (value !== undefined){
                    elem.val(value);
                }
            });

            $('.save-group').each(function(){
                let parent = $(this);
                parent.empty();
                let key = parent.attr('id');
                let list = data[key];
                if (list !== undefined){
                    if (parent.attr('type').startsWith('dict')){
                        Object.keys(list).forEach(function(name){
                            let value = list[name];
                            let new_item = create_input.call(parent);
                            new_item.find('.name').val(name);
                            new_item.find('.value').val(value);
                        });
                    }
                    else {
                        list.forEach(function(name){
                            let new_item = create_input.call(parent);
                            new_item.find('.name').val(name);
                        });
                    }
                }
            });
        }
        reader.readAsText(file);
    } else {
        alert("Please select a file.");
    }
}

$(function(){
    $('.add-item').click(add_input);
    $('#save').click(save);
    $('#load').change(load);
    let instr = `
<div id="help-modal" class="modal fade" tabindex="-1" role="dialog">
    <div class="modal-dialog" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                <h3>Instructions</h3>
            </div>
            <div class="modal-body">{0}</div>
        </div>
    </div>
</div>
    `.format(instructions);
    $('nav:first').after(instr);
    $('#help').click($('#help-modal').modal);
});

let instructions = marked(`
The SRC field is the source of the record. It should be the acronym of the name of the book.

Omit the leading article and operator words should be lowercase.

For example: The Lost Mine of Phandelver would be LMoP.

---

Use [markdown](https://guides.github.com/features/mastering-markdown/) for any styling.

Only use asterisks \`*\` for bold and italics.

Also use asterisks for unordered lists.

Use correct numbering for ordered lists.

---

Replace special unicode characters such as \`’\` with their ASCII equivalents when possible. \`'\` in this case.

---

Use left pipes and full-width alignment markings for tables:

\`\`\`
| Col 1 | Col 2 |
|:-----:|-------|
| Val 1 | very long answers don't need right pipes
| Val 2 | use pipes if the entire table is less than 80 characters wide and you can make the pipes line up
\`\`\`

---

Dashes should be written as 3 hyphens: \`Some words---other words.\`

Quote citations should use 2 hyphens: \`--Elminster\`.

Hyphens should use 1 hyphen: \`fifty-two\`.

---

The names of all spells, magic items, and source books should be italicized with \`*\`s

---

Only include a &lt;spell&gt; tag for spells whose effects are actually caused by an ability (not just mentioned).

Spell tags should each be their own paragraph when used:

\`\`\`
The gnome's innate spellcasting ability is Intelligence (spell save DC 11). It can innately cast the following spells, requiring no material components:

At will: *nondetection* (self only)

1/day each: *blindness/deafness*, *blur*, *disguise self*

<spell>Nondetection</spell>

<spell>Blindness/Deafness</spell>

<spell>Blur</spell>

<spell>Disguise Self</spell>
\`\`\`

---

For lists, ensure that the items are in order.

---

Test completed files [here](/test/monster)
`, {gfm: true});
