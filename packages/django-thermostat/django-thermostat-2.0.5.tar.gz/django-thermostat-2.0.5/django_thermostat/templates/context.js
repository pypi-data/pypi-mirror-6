
function toggle_heat_status() {

    send_url("{%url 'toggle_heat_status'%}", function(data){
        $("#heat_on_btn").toggleClass("btn-success btn-danger")

        })
}

function toggle_manual() {
    send_url("{%url 'toggle_heat_manual'%}", function(data){
        if(data.manual){
            $("#heat_manual_btn").html("Manual")
        }else{
            $("#heat_manual_btn").html("Program")
        }})
}

function read_heat_status() {
    send_url("{%url 'read_heat_status'%}", function(data){
        if (data.status == "ON") {
            $("#heat_on_btn").removeClass("btn-danger")
            $("#heat_on_btn").addClass("btn-success")
        }
        if (data.status == "OFF") {
            $("#heat_on_btn").removeClass("btn-success")
            $("#heat_on_btn").addClass("btn-danger")
        }
        $("#economic").val(data.economic)
        $("#confort").val(data.confort)
        if (data.flame == true) {
            $("#flame").removeClass("label-default")
            $("#flame").addClass("label-danger")
        }else{
            $("#flame").removeClass("label-danger")
            $("#flame").addClass("label-default")
        }
        if(data.manual){
            $("#heat_manual_btn").html("Manual")
            $("#heat_manual_btn").addClass("btn-warning")
        }else{
            $("#heat_manual_btn").html("Program")
            $("#heat_manual_btn").removeClass("btn-warning")
            }
        })
    //load_url("#temperature", "{{temp_url}}")
}

function dim(temp) {
    send_url("{%url 'dim_temp'%}" + temp, function(data){
        if (temp == "confort") {
            $("#confort").val(data.confort)
        }
        if (temp == "economic"){
            $("#economic").val(data.economic)
        }
        })
}

function bri(temp) {
    send_url("{%url 'bri_temp'%}" + temp, function(data){
        if (temp == "confort") {
            $("#confort").val(data.confort)
        }
        if (temp == "economic"){
            $("#economic").val(data.economic)
        }
        })
}
