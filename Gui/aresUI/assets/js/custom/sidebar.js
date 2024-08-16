
var lockedpage = false;

if ((lockedpage) == false) {
    
function openNav() {
    document.getElementById("mySidenav").style.width = "350px";
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "0px";
}

function openDeviceNav() {
    document.getElementById("myDevicenav").style.width = "350px";
    document.getElementById("myDevicenav").style.visibility = "all";
}

function closeDeviceNav() {
    document.getElementById("myDevicenav").style.width = "0px";
    document.getElementById("myDevicenav").style.visibility = "hidden";
}

}

window.addEventListener('click', function(e){   
  if (!document.getElementById('mySidenav').contains(e.target) && !document.getElementById('title-main').contains(e.target)){
    // Clicked in box
   document.getElementById("mySidenav").style.width = "0px";  
  } else{
   
 // document.getElementById("mySidenav").style.width = "0px";
  }
});



window.addEventListener('click', function(e){   
  if (!document.getElementById('myDevicenav').contains(e.target) && !document.getElementById('myDeviceMenu').contains(e.target)){
    // Clicked in box
   document.getElementById("myDevicenav").style.width = "0px";  
   document.getElementById("myDevicenav").style.visibility = "hidden";
  } else{
   
 // document.getElementById("mySidenav").style.width = "0px";
 document.getElementById("myDevicenav").style.visibility = "visible";
  }
});

//mouseover
document.getElementById("title-main").addEventListener("mouseover", function() {
    // Do something when the element is hovered over
    openNav();
});

