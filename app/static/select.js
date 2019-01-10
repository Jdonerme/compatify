"use strict";

function sortSelect(selElem, sortType) {
    var tmpAry = new Array();
    for (var i=0;i<selElem.options.length;i++) {
        tmpAry[i] = new Array();
        tmpAry[i][0] = selElem.options[i].text;
        tmpAry[i][1] = selElem.options[i].value;
    }

    if (sortType == "alpha"){
    	tmpAry.sort(compareAlpha);
    }

    while (selElem.options.length > 0) {
        selElem.options[0] = null;
    }
    for (var i=0;i<tmpAry.length;i++) {
        var op = new Option(tmpAry[i][0], tmpAry[i][1]);
        selElem.options[i] = op;
    }
    return;
}

function compareAlpha(optionA, optionB) {
  
  if (optionA[0].toLowerCase() < optionB[0].toLowerCase())
    return -1;
  if (optionA[0].toLowerCase() > optionB[0].toLowerCase())
    return 1;
  return 0;
}