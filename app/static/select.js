"use strict";

/** fuction to replace the elements in a multiselect (selectList) with a different
   set of options (originalList) */

function replaceSelect(originalList, selectList) {
    while (selectList.options.length > 0) {
        selectList.options[0] = null;
    }
    for (var i=0;i<originalList.length;i++) {
        var op = new Option(originalList[i][0], originalList[i][1]);
        selectList.options[i] = op;
    }
    return;
}

/** fuction to sort the elements in a multiselect (selectList) in alphabetical
    order */
function sortSelect(selectList) {
    var tmpAry = new Array();
    for (var i=0;i<selectList.options.length;i++) {
        tmpAry[i] = new Array();
        tmpAry[i][0] = selectList.options[i].text;
        tmpAry[i][1] = selectList.options[i].value;
    }

    tmpAry.sort(compareAlpha);

    while (selectList.options.length > 0) {
        selectList.options[0] = null;
    }
    for (var i=0;i<tmpAry.length;i++) {
        var op = new Option(tmpAry[i][0], tmpAry[i][1]);
        selectList.options[i] = op;
    }
    return;
}
/** Compare Strings in case insensitve Alphabetical Order */


function compareAlpha(optionA, optionB) {
  
  if (optionA[0].toLowerCase() < optionB[0].toLowerCase())
    return -1;
  if (optionA[0].toLowerCase() > optionB[0].toLowerCase())
    return 1;
  return 0;
}