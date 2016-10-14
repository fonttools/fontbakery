define([
    'dom-tool'
  , 'Controller'
], function(
    dom
  , Controller
) {
    "use strict";
    /*global document, FileReader*/

    function makeFileInput(fileOnLoad, element) {
        var hiddenFileInput = dom.createChildElement(element, 'input'
                                , {type: 'file', 'multiple': 'multiple'});
        hiddenFileInput.style.display = 'none'; // can be hidden!

        function handleFiles(files) {
            var i, l, reader, file;
            for(i=0,l=files.length;i<l;i++) {
                file = files[i];
                reader = new FileReader();
                reader.onload = fileOnLoad.bind(null, file);
                reader.readAsArrayBuffer(file);
            }
        }

        // for the file dialogue
        function fileInputChange(e) {
            /*jshint validthis:true, unused:vars*/
            handleFiles(this.files);
        }
        function forwardClick(e) {
            /*jshint unused:vars*/
            // forward the click => opens the file dialogue
            hiddenFileInput.click();
        }

        // for drag and drop
        function noAction(e) {
            e.stopPropagation();
            e.preventDefault();
        }
        function drop(e) {
            e.stopPropagation();
            e.preventDefault();
            handleFiles(e.dataTransfer.files);
        }

        hiddenFileInput.addEventListener('change', fileInputChange);
        element.addEventListener('click', forwardClick);
        element.addEventListener("dragenter", noAction);
        element.addEventListener("dragover", noAction);
        element.addEventListener("drop", drop);
    }

    function initFileInputs(fileOnLoad, doc, klass) {
        var _makefileInput =  makeFileInput.bind(null, fileOnLoad);
        Array.from(doc.getElementsByClassName(klass)).forEach(_makefileInput);
    }

    return function main(){
        var ctrl = new Controller(
                    document.getElementsByClassName('files-controls')[0]
                  , document.getElementsByClassName('general-controls')[0]
        );
        initFileInputs(ctrl.fileOnLoad, document, 'drop-fonts');
    };
});
