function beautify() {
    try {
        raw_string = JSON.stringify(document.getElementsByName('input_json')[0].value);
        el = JSON.parse(JSON.parse(raw_string));
        $('textarea').val(JSON.stringify(el,null,'\t'));
        document.getElementById("js_formatting_error").innerHTML = "";
    } catch(err) {
        document.getElementById("js_formatting_error").innerHTML = "Unable to Beautify: " + err.message;
    }

}