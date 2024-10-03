// src/ariesUI.js

let Debuglvl = 1;

function update_app_scoll_status(update, style) {
  if (Debuglvl > 2){
    console.log("AriesUI: App Scroll Status Updated to: " + document.getElementById("AriesUI-app-scroll-status").textContent)
  }

  document.getElementById("AriesUI-app-scroll-status").textContent = "Status {" + update + "}";
}

function update_app_live_status_dropdown() {
  // update last updated ms in the live section
}

function select_app_stream(UMSI) {
  //left click stream list
  console.log("AriesUI: select stream:", UMSI);
}
  
function preview_app_stream(stream) {
  //right click stream list
}
  
function subscribe_data() {
    
}

function update_SH_live_status(update, style) {
  // update last updated ms in the live section
  if (Debuglvl > 3){
    console.log("AriesUI: SH_live_status Updated to: " + document.getElementById("SH-live-status").textContent)
  }

  document.getElementById("SH-live-status").textContent = "SH: [" + update + "]";

  if (style == "success") {
    document.getElementById("SH-live-status").classList.remove("text-danger");
    document.getElementById("SH-live-status").classList.remove("text-warning");
    document.getElementById("SH-live-status").classList.add("text-success");
  }

  if (style == "danger") {
    document.getElementById("SH-live-status").classList.remove("text-warning");
    document.getElementById("SH-live-status").classList.remove("text-success");
    document.getElementById("SH-live-status").classList.add("text-danger");
  }
  
  if (style == "warning") {
    document.getElementById("SH-live-status").classList.remove("text-danger");
    document.getElementById("SH-live-status").classList.remove("text-success");
    document.getElementById("SH-live-status").classList.add("text-warning");
  }

}

function update_app_stream_list(data) {
  //document.getElementById("SH-active-streams-dropdown-content")
  document.getElementById("SH-active-streams-dropdown-content").innerHTML = "<div class='skeleton h-32 w-32'></div>";
  document.getElementById("App-Configurator-active-streams-dropdown-content").innerHTML = "<div class='skeleton h-32 w-32'></div>";


  var active_streams_innerhtml = "";

  if (data.length == 0) {
    document.getElementById("SH-active-streams-dropdown-content").innerHTML = "<li><a href='https://www.youtube.com/watch?v=dQw4w9WgXcQ' class='text-danger'>{0 Active}</a></li>";
    document.getElementById("App-Configurator-active-streams-dropdown-content").innerHTML = "<li><a href='https://www.youtube.com/watch?v=dQw4w9WgXcQ' class='text-danger'>{0 Active}</a></li>";
  }
  //for each module in data add a heading 
  for (const module in data) {
    if (Debuglvl > 4) {
      console.log(module);
    }
    //add module to list
    active_streams_innerhtml += "<li><details open><summary>" + module + "</summary><ul>";
    if (Debuglvl > 4) {
      console.log(data[module]["streams"]);
    }
    for (const stream in data[module]["streams"]) {
      if (Debuglvl > 4) {
        console.log(stream);
      }
      //add stream to list
      active_streams_innerhtml += "<li><a onclick='select_app_stream(" + '"' + module + '.' + stream + '"' + ")'>" + stream + "</a></li>";
       

    }

    active_streams_innerhtml += "</ul></details></li>";
    document.getElementById("SH-active-streams-dropdown-content").innerHTML = active_streams_innerhtml;
    document.getElementById("App-Configurator-active-streams-dropdown-content").innerHTML = active_streams_innerhtml;
  }
  

}

//websocket close
document.getElementById('Itf-close-btn').addEventListener('click', () => {
  closeWebSocket();
});

document.getElementById('Itf-connect-btn').addEventListener('click', () => {
  startWebSocket();
});

document.getElementById('SH-active-streams-dropdown').addEventListener('click', () => {
  document.getElementById("SH-active-streams-dropdown-content").innerHTML = "<div class='skeleton h-10 w-32'></div>";
  queryActiveStreams();
});

document.getElementById('App-Configurator-active-streams-dropdown').addEventListener('click', () => {
  document.getElementById("App-Configurator-active-streams-dropdown-content").innerHTML = "<div class='skeleton h-10'></div>";
  queryActiveStreams();
});

document.getElementById('App-live-status-dropdown').addEventListener('click', () => {
  pingServer();
});



document.getElementById('Itf-reconnect-btn').addEventListener('click', () => {
  //console.log("clicked");
  if (document.getElementById('Itf-reconnect-btn').checked == true){
    //autoconn on
    ReconnBool = true;
    console.log('ariesUI: Itf reconnect on');
    //startWebSocket();
  } else {
    //autoconn off
    ReconnBool = false;
    console.log('ariesUI: Itf reconnect off');
  }

});



update_app_scoll_status("AriesUI: GUI initialized", NaN);

