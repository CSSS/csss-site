function beautify() {
    try {
        raw_string = JSON.stringify(document.getElementsByName('input_json')[0].value);
        el = JSON.parse(JSON.parse(raw_string));
        $('textarea').val(JSON.stringify(el,null,'\t'));
        document.getElementById("js_formatting_error").innerHTML = "";
        document.getElementById('submit_button').removeAttribute("disabled");
    } catch(err) {
        document.getElementById('submit_button').setAttribute("disabled", "true");
        document.getElementById("js_formatting_error").innerHTML = "Unable to Beautify: " + err.message;
    }
}