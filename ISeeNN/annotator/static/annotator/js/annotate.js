/**
 * Created by sunshy on 2017/2/23.
 */
var scores = []
var label_id = 0
var time_used = 0

function set_visible(id) {
    $('.targets').hide()
    $('.targets:eq('+id+')').show()
    $('#target_status').text('the '+(label_id+1)+'/'+$('.targets').length+' target.')
    $('#score_display').text('')
    if (id <= scores.length - 1 && id >= 0) {
        score_text = ''
        switch(scores[id]) {
            case 5:
            case 4:
            case 3:
            case 2:
            case 1:
                score_text = scores[id]
                break
            default:
                score_text = 'Undefined'
                break
        }

        $('#score_display').html('Your score on this pair is <span style="color:green">' + score_text + "</span>")
    }
}

function postcall(url,params){
    var tempform = $('#submit_form')[0]
    for (var x in params) {
        var opt = document.createElement("input");
        opt.name = x;
        opt.setAttribute("value",params[x]);
        tempform.appendChild(opt);
    }
    tempform.submit();
}

function submit() {
    var parms = {
        'query_id': $('#annotation_id').text(),
        'scores': JSON.stringify(scores)
    }
    postcall('annotator/annotate_submit', parms)
}

function score(s) {
    scores[label_id] = s
    if (label_id < $('.targets').length - 1) {
        label_id += 1
        set_visible(label_id)
    } else {
        $('#score_display').html(
            'You have completed this query. <a href="#" onclick="submit(); return false;">Click</a> to submit and label the next query.'
        )
    }
}


function previous() {
    if (label_id <= 0) {
        alert("This is the first one!")
        return false
    }
    --label_id
    set_visible(label_id)
}

function next() {
    if (label_id >= scores.length) {
        alert("Please score this image pair below!")
        return false
    }
    ++label_id
    set_visible(label_id)
}

function tick() {
    time_used += 1
    $('#ticker').text(" Ticker " + time_used + " s.")
}


function set_key_events() {
    $(window).keypress(function (event) {
        e = event || window.event
	    currKey = e.keyCode || e.which || e.charCode
        switch (currKey) {
            case 37: // left
            case 57: // 9
                previous()
                break
            case 39: // right
            case 48: // 0
                next()
                break
            case 49: // 1
                score(1)
                break
            case 50: // 2
                score(2)
                break
            case 51: // 3
                score(3)
                break
            case 52: // 4
                score(4)
                break
            case 53: // 5
                score(5)
                break
            default:
                break
        }
    })
}


$(function() {
    set_visible(label_id)
    setInterval(tick, 1000)
    set_key_events()
});