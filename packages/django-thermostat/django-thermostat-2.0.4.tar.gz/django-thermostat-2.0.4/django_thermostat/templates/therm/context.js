
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
    $.ajax({
        url: "{%url 'read_heat_status'%}",


        success: function(data){
            if (data.status == "ON") {
                $("#heat_on_btn").removeClass("btn-danger")
                $("#heat_on_btn").addClass("btn-success")
            }
            if (data.status == "OFF") {
                $("#heat_on_btn").removeClass("btn-success")
                $("#heat_on_btn").addClass("btn-danger")
            }
            $("#economic").html(data.economic + " º")
            $("#confort").html(data.confort + " º")
            $("#tuned_temp").html("Tunned... " + data.tuned + " º")
            $("#time").html(data.time)
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

            },

        error: function(ob){show_msg(ob.responseText)}
        });

    $.ajax({
        url: "{%url 'temperatures'%}",
        dataType: "json",
        data: "temperatures=True",
        success: function(data){
		$("#temperatures").html("")
		$.each(data, function(key, val) {
			$("#temperatures").append("<span onclick=\"set_int_ref('"+key+"')\" class='col-md-10 col-sm-10 col-lg-6 col-xs-9 label label-"+(val[1]? 'success':'default')+"'>" + key + "... " + val[0]['celsius'] +"º</span><br>")
  		});
        }})
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

function set_int_ref(id) {
    refresh_off()
    send_url("{%url 'set_internal_reference'%}" + id, function(d){refresh_on()})
}
