// Version: 1.0
var container = $("#container");

//make code to make multiple boxes



var boxlist = [];

var width = 50;
var height = 50;
var rows = 16;
var cols = 34;
var snap = 50;




for (var i = 0; i < rows * cols; i++) {
  var y = Math.floor(i / cols) * height;
  var x = i * width % (cols * width);
  $("<div grid-cell></div>").css({ top: y, left: x }).prependTo(container);
}

/*
//hide grid when dragging too slow need to fix
function hidegrid() {
document.querySelectorAll("[grid-cell]").forEach(function (cell) {
    cell.style.visibility = "hidden";
});
  console.log("hidegrid");
}
Draggable.create(box2, {
  bounds: container,
  onDrag: onDrag1,
  onDragEnd: hidegrid });
*/






onDragnew = function(index) {
  return function() {
    TweenLite.to(boxlist[index], 0.5, {
      x: Math.round(this.x / snap) * snap,
      y: Math.round(this.y / snap) * snap,
      ease: Back.easeOut.config(2) });
  };
};



function createBox(content_html, x, y) {
  var box = $("<div class='block box ui-widget-content'> " + content_html + " </div>").appendTo(container);
  boxlist.push(box);
  var mainDraggable = Draggable.create(box, {
    bounds: container,
    onDrag: onDragnew(boxlist.length - 1) ,
  }); 

// use jquery alsoresizable


}






    

// make the box resizable



