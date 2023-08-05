function edit_title(doc_id, elt) {
    //noinspection JSLint
    $('#loading_title').css('display', 'inline')
    $.ajax({url: '/updoc/edit/' + doc_id + '/', type: 'POST', data: {'name': elt.textContent},
        'success': function () {$('#loading_title').css('display', 'none'); }});
}

function edit_keywords(doc_id, elt) {
    //noinspection JSLint
    $('#loading_keywords').css('display', 'inline')
    $.ajax({url: '/updoc/edit/' + doc_id + '/', type: 'POST', data: {'keywords': elt.textContent},
        'success': function () {$('#loading_keywords').css('display', 'none'); }});
}
