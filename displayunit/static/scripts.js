var moreButtonPressed = false; //global var to handle auto-refresh behaviour

function buildList(data) {
    var listupdates = [];
        $.each(data, function (n) {
            var strBuild = '<li class="listelement" onclick="displayInfo('+n+')"><a href="'+data[n].link+'">'+data[n].title+'</a>'+
            '\t/\t' + data[n].fandoms +
            '<p>'+data[n].summary+'</p><p>';
            $.each(data[n].stats, function (stat) {
                if (stat.charAt(0) !== 'B' && stat.charAt(0) !== 'H' && stat.charAt(0) !== 'L' && stat.charAt(0) !== 'K' && stat.charAt(2) !== 'm') {
                    // shonky filter to avoid displaying undesirable stats
                    strBuild = strBuild +stat+':'+data[n].stats[stat]+'\t\t';
                }
            });
            strBuild = strBuild + '</p><div class="id">'+n+'</div>';
            listupdates.push(strBuild);
        });
    return listupdates.reverse()
}

function getUpdates() {
    $.get('/refresh', function (data) {
        var updates = JSON.parse(data);
        if (moreButtonPressed === false){
            var listupdates = buildList(updates);
            $('#update_list').html(listupdates.join(''));
        }
        else {
            var breakTracker = false;
                $.each(updates, function (n) {
                    var counter = 0;
                    $('.id').each(function () {
                        if ($(this).text() != n && counter < 10) {
                            $('#newcounter').text('NEW ENTRIES FOUND');
                            breakTracker = true;
                            return false;
                        }
                        counter++
                    });
                    if (breakTracker === true) {
                        return false
                    }
                })
        }
    })
}
$(document).ready(function () {
    console.log('Script loaded.');
    getUpdates();
});

function displayInfo(id) {
    $.get('/getinfo',{'work_id': id}, function (data) {
        var info = JSON.parse(data);
        $('#dtitle').html(info.title);
        $('#dtags').html('<p>'+info.tags+'</p>');
        $('#dsummary').html('<p>'+info.summary+'</p>');
        if ($('.btnlink').length) {
            $('.btnlink').prop('href',info.link);
        }
        else {
            $('#rightdisplay').append('<a class="btnlink" href="'+info.link+'"><div class="visitbtn">VISIT WORK</div></a>');
        }
    })
}

function loadMore() {
    moreButtonPressed = true;
    var count = $('.listelement').length;
    console.log(count);
    $.get('/more', {'count': count}, function (data) {
        var info = JSON.parse(data);
        var listupdates = buildList(info);
        $('#update_list').html(listupdates.join(''))
    })
}