// s4 javascript utils (drive utils)
// author: Ondrej Sika, http://ondrejsika.com

function s4Upload(uri, file, callback, error, async) {
    if (async === undefined) async = true;
    var xhr = new XMLHttpRequest();
    var fd = new FormData();
    xhr.open("POST", uri, async);
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            callback(xhr.responseText);
        }
        if (xhr.readyState == 4 && xhr.status != 200) {
            error(xhr.status, xhr.responseText, xhr)
        }
    }
    fd.append('file', file);
    xhr.send(fd);
}


function s4MultiUpload(uri, files, callback, loopInterval) {
    if (loopInterval == undefined) loopInterval = 300;
    var responses = [];
    for (i = 0; i < files.length; i++) {
        console.log("a", i, files[i]);
        s4Upload(uri, files[i], function(data){
            responses.push(data);
            console.log(responses);
        }, function(a, b, c) {
            console.warn(a, b, c);
        });
    };
    loop = setInterval(function(){
        console.log(responses.length, files.length);
        if (responses.length >= files.length) {
            callback(responses);
            clearInterval(loop);
        }
    }, loopInterval);
}
