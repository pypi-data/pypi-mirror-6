upload_file = function(t){
    var t = $(t);
    var drive_static_url = t.attr("data-drivestaticurl");
    var url  = t.attr("data-url");
    var name = t.attr("id").replace("upload-", "");
    var file = $("#file_"+name)[0].files[0];
    if (file) {
        s4Upload(url, file, function(data){
            $("#input_"+name).val(data);
            $("#path_"+name).html(data);
            $("#path_"+name).attr("href", drive_static_url+data);
        })
    }
}

remove_file = function(t){
    var name = $(t).attr("id").replace("remove-", "");
    $("#input_"+name).val("");
    $("#path_"+name).html("");
    $("#path_"+name).removeAttr("href");
}