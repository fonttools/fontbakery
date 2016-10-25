define([
    'dom-tool'
  , 'opentype'
  , 'jquery'
  , 'jquery-ui'
], function(
    dom
  , opentype
  , JQ
) {
    "use strict";
    /*global window, console, XMLHttpRequest, URL, TextDecoder, Blob, Uint8Array, TextEncoder, Uint32Array*/

    function mergeArrays(arrays) {
        var jobSize = arrays.reduce(function(prev, cur){
                                    return prev + cur.byteLength; }, 0)
          , result, i, l, offset
          ;
        result = new Uint8Array(jobSize);
        for(i=0,l=arrays.length,offset=0; i<l;offset+=arrays[i].byteLength, i++)
            result.set(new Uint8Array(arrays[i]), offset);
        return result.buffer;
    }

    var Font = (function(){

    var weighClass2WeightName = {
        250: 'Thin'
      , 275: 'ExtraLight'
      , 300: 'Light'
      , 400: 'Regular'
      , 500: 'Medium'
      , 600: 'SemiBold'
      , 700: 'Bold'
      , 800: 'ExtraBold'
      , 900: 'Black'
    };

    function Font(parentElement, filename, font, arrBuff, amendmentValue){
        this._filename = filename;
        this._parentElement = parentElement;
        this._font = font;
        this._arrBuff = arrBuff;
        this._amendmentValue = amendmentValue;

        var names =  font.names
         , os2 = font.tables.os2
         ;

        this._familyName = names.postScriptName.en
                        || Object.values(names.postScriptName)[0]
                        || filename.split('.')[0]
                        ;
        this._familyName = this._familyName.split('-')[0];

        this._weightName = weighClass2WeightName[os2.usWeightClass] || 'Regular';

        this._isItalic = !!(os2.fsSelection & font.fsSelectionValues.ITALIC);
        this._version = names.version.en
                        || Object.values(names.version)[0]
                        || '1.0000';
        this._version = this._version.split(';')[0]
                    .toLowerCase()
                    .replace('version ', '')
                    ;
        this._vendorID = os2.achVendID || '';

        this._controlsElement = this._makeControlsElement();
        this._parentElement.appendChild(this._controlsElement);
    }

    var _p = Font.prototype;


    _p.setAmendment = function(amendmentValue) {
        this._amendmentValue = amendmentValue;
        var old = this._controlsElement;
        this._controlsElement = this._makeControlsElement();
        old.parentElement.replaceChild(this._controlsElement, old);
    };

    _p.makeFileName = function() {
        var suffix
          , suffixIndex = this._filename.lastIndexOf('.')
          ;
        if(suffixIndex !== -1)
            suffix = this._filename.slice(suffixIndex);
        else
            // what about woff/woff2 etc?
            suffix = this._font.outlinesFormat === 'truetype' ? '.ttf' : '.otf';


        return [ this._familyName
               , '-'
               , this._weightName
               , this._isItalic ? 'Italic' : ''
               , suffix
        ].join('');
    };

    _p._getDate = function(unix_timestamp) {
        var date = new Date(unix_timestamp * 1000)
          , year = date.getFullYear()
          , month = '' + (date.getMonth() + 1)
          , day = '' + date.getDate()
          ;
        if (month.length === 1)
            month = '0' + month;
        if (day.length === 1)
            day = '0' + day;
        return [year, month, day].join('');
    };

    _p._makeControlsElement = function() {
        return dom.createElement('p', null, [
                        [
                                 this._familyName
                                , this._weightName
                                , this._isItalic && 'italic'
                                , this._version
                        ]
                        .filter(function(item){return !!item;})
                        .join(', ')
                        , dom.createElement('span', {'class': 'filename'}, ' => ' + this.makeFileName())
                        ]);
    };

    _p.getJobData = function() {
        var bytesJson = new TextEncoder('utf-8').encode(JSON.stringify({
                 filename: this.makeFileName()
               , familyName: this._familyName
               , weightName: this._weightName
               , isItalic: this._isItalic
               , version: this._version
               , vendorID: this._vendorID
            })).buffer
            // header, json, font
          , job = [null, bytesJson, this._arrBuff]
          , header, i, l
          ;
        header = new Uint32Array(job.length-1);
        job[0] = header.buffer;
        // store at the beginning the length of each element
        for(i=1,l=job.length;i<l;i++)
            header[i-1] = job[i].byteLength;
        return job;
    };
    return Font;
    })();

    function Controller(filesControlsContainer, generalControlsContainer) {
        this._files = [];
        this.fileOnLoad = this._fileOnLoad.bind(this);
        this._filesControlsContainer = filesControlsContainer;
        this.generalControls = generalControlsContainer;
        this._amendmentValue = this._defaultAmendmentValue = '{created}';
        this._initControls();

    }
    var _p = Controller.prototype;

    _p._fileOnLoad = function(filename, e) {
        var reader = e.target;
        this._addFile(filename, reader.result);
    };

    _p._addFile = function(file, arrBuff) {
        var itemContainer = this._filesControlsContainer.ownerDocument.createElement('li')
          , font, item
          ;
        try {
            font = opentype.parse(arrBuff);
            // console.log(font);
        }
        catch(error) {
            // can't parse file.
            console.warn('Can\'t parse', file.name, 'as font');
            return;
        }
        item = new Font(itemContainer, file.name, font, arrBuff, this._amendmentValue);
        this._filesControlsContainer.appendChild(itemContainer);
        this._files.push(item);
    };

    _p.unpack = function(data) {
        var offset = 0, head, json, font;
        while(offset < data.byteLength) {
            head = new Uint32Array(data, offset, 2);
            offset += head.byteLength;
            json = new Uint8Array(data, offset, head[0]);
            offset += json.byteLength;
            font = new Uint8Array(data, offset, head[1]);
            offset += font.byteLength;
            json = new TextDecoder('utf-8').decode(json);
            data = data.slice(offset);
            offset = 0;
        }
    };

    _p._send = function() {
        var i,l, job = [], data, xhr, blob;

        for(i=0,l=this._files.length;i<l;i++)
            Array.prototype.push.apply(job, this._files[i].getJobData());
        data = mergeArrays(job);

        // unpack(data);

        console.info('Sending', data.byteLength ,'Bytes');

        xhr = new XMLHttpRequest();
        xhr.open('POST', 'runchecks');
//        xhr.setRequestHeader('Content-Type', 'application/octet-stream');
        xhr.send(data);
//        xhr.responseType = 'arraybuffer';
        xhr.responseType = 'html';

        xhr.onreadystatechange = function () {
            if(xhr.readyState !== XMLHttpRequest.DONE)
                return;
            if(xhr.status !== 200)
                console.warn(xhr.status, xhr.statusText );
            else {
                //alert(xhr.response);
                document.getElementById("results").innerHTML = xhr.response;
                JQ("#tabs").tabs();

                console.info('Received:', xhr.responseType, xhr.response.byteLength, 'Bytes');
                //blob = new Blob([xhr.response], {type: "application/zip"});
                //window.open(URL.createObjectURL(blob));
            }
        };

    };

    _p._updateAmendment = function(e) {
        var i,l;
        this._amendmentValue = e.target.value || this._defaultAmendmentValue;
        for(i=0,l=this._files.length;i<l;i++)
            this._files[i].setAmendment(this._amendmentValue);
    };

    _p._initControls = function() {
        //TODO: tweak this in order to create a checkbox for hotfixing.
        /*
        var amendment = dom.createChildElement(this.generalControls, 'input'
                                , {
                                    type: 'text'
                                  , placeholder: this._defaultAmendmentValue
                                  , title: 'Use alpha numeric characters, space and the special strings "{created}", "{modified}" and "{version}".'
                                });*/

        var send = dom.createChildElement(this.generalControls, 'button', null,
                                          [dom.createElement('em', null,'3.'),
                                           ' Run the Checks!']);

//        amendment.addEventListener('input', this._updateAmendment.bind(this));
        send.addEventListener('click', this._send.bind(this));
    };

    return Controller;
});
