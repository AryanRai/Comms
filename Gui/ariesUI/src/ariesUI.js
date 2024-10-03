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

function update_app_stream_list() {
  
}

function update_SH_live_status(update, style) {
  // update last updated ms in the live section
  if (Debuglvl > 2){
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

//websocket close
document.getElementById('Itf-close-btn').addEventListener('click', () => {
  closeWebSocket();
});

document.getElementById('Itf-connect-btn').addEventListener('click', () => {
  startWebSocket();
});

document.getElementById('SH-active-streams-dropdown').addEventListener('click', () => {
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

