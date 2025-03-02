// src/ariesUI.js
import { getWidgetIds } from '../custom/gridManager.js';

// Make Debuglvl global by adding it to window object
window.Debuglvl = 0;

window.update_app_scoll_status = function(update, style) {
  if (Debuglvl > 2){
    console.log("AriesUI: App Scroll Status Updated to: " + document.getElementById("AriesUI-app-scroll-status").textContent)
  }

  document.getElementById("AriesUI-app-scroll-status").textContent = "Status {" + update + "}";
}

function update_app_live_status_dropdown() {
  // update last updated ms in the live section
}

// Move select_app_stream outside of any module scope and add it to window
window.select_app_stream = function(UMSI) {
  //left click stream list
  //unique module.stream id
  const UMSI_raw = UMSI.split(".");
  let module_id = UMSI_raw[0];
  let stream_id = UMSI_raw[1];
  console.log("AriesUI: select stream:", UMSI);
  
  // Add null check before accessing data
  if (window.GlobalData && window.GlobalData.data && 
      window.GlobalData.data[module_id] && 
      window.GlobalData.data[module_id].streams[stream_id]) {
    console.log(window.GlobalData.data[module_id].streams[stream_id].value);
  } else {
    console.log("Stream data not yet available");
  }
  
  console.log(module_id, stream_id);
  document.getElementById("App-Configurator-select-stream-input").value = UMSI;
}

// Move preview_app_stream to window as well since it's used in oncontextmenu
window.preview_app_stream = function(UMSI) {
  //right click stream list
  console.log("AriesUI: preview stream:", UMSI);
}

function subscribe_data() {
    
}

// Mock vanilla JavaScript function to provide sensor data
window.getSensorData = (sensorId) => {
  // Simulate sensor value (can be dynamic in a real project)
  return Math.random() * 100;
};


window.update_SH_live_status = function(update, style) {
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

window.update_app_stream_list = function(data) {
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
      active_streams_innerhtml += "<li><a onclick='select_app_stream(" + '"' + module + '.' + stream + '"' + ")'" + "oncontextmenu='preview_app_stream(" + '"' + module + '.' + stream + '"' + ")'" + ">" + stream + "</a></li>";
       

    }

    active_streams_innerhtml += "</ul></details></li>";
    document.getElementById("SH-active-streams-dropdown-content").innerHTML = active_streams_innerhtml;
    document.getElementById("App-Configurator-active-streams-dropdown-content").innerHTML = active_streams_innerhtml;
  }
  

}

function update_app_grid_list(data) {
  document.getElementById("App-Configurator-active-grids-dropdown-content").innerHTML = "<div class='skeleton h-32 w-32'></div>";

  var active_grids_innerhtml = "";

  if (data.length == 0) {
    document.getElementById("App-Configurator-active-grids-dropdown-content").innerHTML = "<li><a href='#' class='text-danger'>{0 Active}</a></li>";
    return;
  }

  // For each grid in data add a heading
  for (const grid of data) {
    if (Debuglvl > 4) {
      console.log(grid);
    }
    // Add grid to list - using window.select_app_grid
    active_grids_innerhtml += `<li><a onclick="window.select_app_grid('${grid}')">${grid}</a></li>`;
  }

  document.getElementById("App-Configurator-active-grids-dropdown-content").innerHTML = active_grids_innerhtml;
}

window.update_app_widget_type_list = function update_app_widget_type_list(modsList, modName) {
  document.getElementById("App-Configurator-active-WidgetType-dropdown-content").innerHTML = "<div class='skeleton h-32 w-32'></div>";

  var active_grids_innerhtml = "";

  if (modsList.length == 0) {
    document.getElementById("App-Configurator-active-WidgetType-dropdown-content").innerHTML = "<li><a href='#' class='text-danger'>{0 Active}</a></li>";
    document.getElementById('ariesModsList').innerHTML = "<li><a href='#' class='text-danger'>{0 Active}</a></li>";
    return;
  }

  if (Debuglvl > 4) {
    console.log("widget types");
    console.log(modsList);
  }
  // For each grid in data add a heading
  
  /*
  for (const grid of data) {
    if (Debuglvl > 4) {
      console.log(grid);
    }
    // Add grid to list - using window.select_app_grid
    active_grids_innerhtml += `<li><a onclick="window.select_app_grid('${grid}')">${grid}</a></li>`;
  }
 */
  const modsListElem = document.getElementById('ariesModsList');
  const modsListElemConfig = document.getElementById("App-Configurator-active-WidgetType-dropdown-content");
  var modsListContent = '';

  for (let index = 0; index < modsList.length; index++) {
    var modName = modsList[index];
    var data = `<li><span>${modName}</span><button class="btn btn-xs btn-ghost" onclick="RemoveModToList('${modName}')">×</button><li>`;
    modsListContent += data;
  }

  modsListElem.innerHTML = modsListContent;
  modsListElemConfig.innerHTML = modsListContent;

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

document.getElementById('App-Configurator-active-grids-dropdown').addEventListener('click', () => {
  document.getElementById("App-Configurator-active-grids-dropdown-content").innerHTML = "<div class='skeleton h-10'></div>";
  const gridIds = getWidgetIds();
  update_app_grid_list(gridIds);
});


document.getElementById('App-Configurator-save-btn').addEventListener('click', () => {
  AttachStreamView(
  document.getElementById('App-Configurator-select-grid-select').value,
  document.getElementById('App-Configurator-select-stream-input').value,
  document.getElementById('App-Configurator-select-WidgetType-input').value
)
  
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

// Add select_app_grid to window object to make it globally accessible
window.select_app_grid = function(grid_id) {
  console.log("AriesUI: select grid:", grid_id);
  document.getElementById("App-Configurator-select-grid-select").value = grid_id;
}

