"use strict";

var myLang = new String("en");

function getOppositLng()
{
  return myLang == "ru" ? "en" : "ru";
}

function switchLng()
{
  myLang = getOppositLng();
  document.getElementById("lngSwitcher").innerHTML=myLang;

  var allImgs = document.getElementsByClassName("dv_show_card");
  var from = "/" + getOppositLng().toString() + "/";
  var to = "/" + myLang.toString() + "/";
  for (var i = 0; i < allImgs.length; ++i)
    allImgs[i].src = allImgs[i].src.replace(from, to);
  var tags = [ "dv_card", "dv_card_back" ];
  for (var i = 0; i < tags.length; ++i) {
    var bigImg = document.getElementById(tags[i]);
    bigImg.src = bigImg.src.replace(from, to);
  }
}


window.onload = function() {
  // Set default values
  document.getElementById("dv_pick_n").value = 1;
  document.getElementById("dv_show_checkbox").checked = true;

  (function() {
    var tags = ["dv_image_player1", "dv_image_pack1", "dv_image_pick1"];
    for (var i = 0; i < tags.length; ++i) {
      var tmp = document.getElementsByClassName(tags[i]);
      for (var j = 0; j < tmp.length; ++j)
        tmp[j].style.display = "block"
    }
  })();

  (function() {
    var tags = ["dv_player", "dv_pick", "dv_pack"];
    for (var i = 0; i < tags.length; ++i)
      document.getElementById(tags[i]).options["0"].setAttribute("selected", "selected");
  })();

  // Register event handlers
  var allImgs = document.getElementsByClassName("dv_show_card");
  for (var i = 0; i < allImgs.length; ++i)
    allImgs[i].addEventListener(
      "mouseover",
      function() {
        var face = document.getElementById("dv_card");
        face.src = this.src;
        var back = document.getElementById("dv_card_back");
        back.style.display = "none";
        if (face.src.substr(-5) == "a.jpg") {
          back.src = face.src.substr(0, face.src.length - 5) + "b.jpg";
          back.style.display = "block";
        }
      }
    );

  var playerVgt = document.getElementById("dv_player");
  playerVgt.addEventListener(
    "change",
    function() {
      for (var i = 1; i <= playerVgt.options.length; ++i)
        document.getElementsByClassName("dv_image_player" + i.toString())[0].style.display = "none";
      var cur = playerVgt.options.selectedIndex + 1;
      document.getElementsByClassName("dv_image_player" + cur.toString())[0].style.display = "block";
    }
  );

  var packVgt = document.getElementById("dv_pack");
  packVgt.addEventListener(
    "change",
    function() {
      for (var i = 1; i <= packVgt.options.length; ++i)
      {
        var packs = document.getElementsByClassName("dv_image_pack" + i.toString());
        for (var j = 0; j < packs.length; ++j)
          packs[j].style.display = "none";
      }
      var cur = packVgt.options.selectedIndex + 1;
      var packs = document.getElementsByClassName("dv_image_pack" + cur.toString());
      for (var j = 0; j < packs.length; ++j)
        packs[j].style.display = "block";
    }
  );

  var pickVgt = document.getElementById("dv_pick");
  pickVgt.addEventListener(
    "change",
    function() {
      for (var i = 1; i <= pickVgt.options.length; ++i)
      {
        var picks = document.getElementsByClassName("dv_image_pick" + i.toString());
        for (var j = 0; j < picks.length; ++j)
          picks[j].style.display = "none";
      }
      var cur = pickVgt.options.selectedIndex + 1;
      var picks = document.getElementsByClassName("dv_image_pick" + cur.toString());
      for (var j = 0; j < picks.length; ++j)
        picks[j].style.display = "block";

      document.getElementById("dv_pick_n").value = cur;
      document.getElementById("dv_next_pick_link").style.display = "inline";
      document.getElementById("dv_prev_pick_link").style.display = "inline";
      if (cur == pickVgt.options.length) document.getElementById("dv_next_pick_link").style.display = "none";
      if (cur == 1) document.getElementById("dv_prev_pick_link").style.display = "none";

      }
  );

  var prev = document.getElementById("dv_prev_pick_link");
  prev.addEventListener(
    "click",
    function() {
      var dvOldPick = parseInt(document.getElementById("dv_pick_n").value);
      var dvPick = dvOldPick - 1;
      var picks = document.getElementsByClassName("dv_image_pick" + dvOldPick);
      for (var i = 0; i < picks.length; ++i)
        picks[i].style.display = "none";

      picks = document.getElementsByClassName("dv_image_pick" + dvPick);
      for (var i = 0; i < picks.length; ++i)
        picks[i].style.display = "block";

      document.getElementById("dv_pick_n").value = dvPick;
      document.getElementById("dv_next_pick_link").style.display = "inline";
      document.getElementById("dv_prev_pick_link").style.display = "inline";
      if (dvPick == pickVgt.options.length) document.getElementById("dv_next_pick_link").style.display = "none";
      if (dvPick == 1) document.getElementById("dv_prev_pick_link").style.display = "none";
      /*
      for (var i = 0; i < pickVgt.options.length; ++i)
        pickVgt.options["" + i].removeAttribute("selected");
      pickVgt.options["" + (dvPick - 1)].setAttribute("selected", "selected");
      */
      pickVgt.options.selectedIndex = dvPick - 1;
    }
  );

  var next = document.getElementById("dv_next_pick_link");
  next.addEventListener(
    "click",
    function() {
      var dvOldPick = parseInt(document.getElementById("dv_pick_n").value);
      var dvPick = dvOldPick + 1;
      var picks = document.getElementsByClassName("dv_image_pick" + dvOldPick);
      for (var i = 0; i < picks.length; ++i)
        picks[i].style.display = "none";

      picks = document.getElementsByClassName("dv_image_pick" + dvPick);
      for (var i = 0; i < picks.length; ++i)
        picks[i].style.display = "block";

      document.getElementById("dv_pick_n").value = dvPick;
      document.getElementById("dv_next_pick_link").style.display = "inline";
      document.getElementById("dv_prev_pick_link").style.display = "inline";
      if (dvPick == pickVgt.options.length) document.getElementById("dv_next_pick_link").style.display = "none";
      if (dvPick == 1) document.getElementById("dv_prev_pick_link").style.display = "none";
      /*
      for (var i = 0; i < pickVgt.options.length; ++i)
        pickVgt.options["" + i].removeAttribute("selected");
      pickVgt.options["" + (dvPick - 1)].setAttribute("selected", "selected");
      */
      pickVgt.options.selectedIndex = dvPick - 1;
    }
  );

  (function() {
    var element = document.getElementById("dv_show_checkbox");
    element.addEventListener(
      "change",
      function() {
        var border_style = element.checked ? "2px solid red" : "2px solid black";
        var divs = document.getElementsByClassName("crdbx-act");
        for (var i = 0; i < divs.length; ++i)
          divs[i].style.border = border_style;
      }
    )
  })();

  document.getElementById("dv_image_draft").style.display = "block";

}

/*
*/



/*
onReady( function() {
  alert("BOOOOOOOOOOOOOOO");
  var allImgs = document.getElementByClassName("dv_show_card");
  for (var i=0; i < allImgs.length; ++i)
    allImgs[i].attachEvent("onmouseover", doShowBigImage);
});
*/

/*
document.addEventListener("DOMContentLoaded", function() {
  var allImgs = document.getElementsByClassName("dv_show_card");
  for (var i=0; i < allImgs.length; ++i)
    allImgs[i].addEventListener(
      "mouseover",
      function() { document.getElementById("dv_card").src = this.src; }
      );
}, false);
*/

/*
$( document ).ready(function() {
  alert("ILYA");
  var allImgs = document.getElementsByClassName("dv_show_card");
  for (i=0; i < allImgs.length; ++i)
    allImgs[i].addEventListener(
      "mouseover",
      function() { document.getElementById("dv_card").src = this.src; }
      );
});
*/
