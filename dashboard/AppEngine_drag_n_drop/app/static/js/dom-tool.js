define([
    'marked'
], function(
    marked
){
    "use strict";
    /*globals document*/
    function appendChildren(elem, contents, cloneChildNodes) {
        var _contents, i, l, child;

        if(contents === undefined)
            _contents = [];
        else
            _contents = contents instanceof Array ? contents : [contents];

        for(i=0,l=_contents.length;i<l;i++) {
            child = _contents[i];
            if(typeof child.nodeType !== 'number')
                child = document.createTextNode(child);
            else if(cloneChildNodes)
                child = child.cloneNode(true);//always a deep clone
            elem.appendChild(child);
        }
    }

    function createElement(tagname, attr, contents, cloneChildNodes) {
        var elem = document.createElement(tagname)
          , k
          ;

        if(attr) for(k in attr)
            elem.setAttribute(k, attr[k]);

        appendChildren(elem, contents, cloneChildNodes);
        return elem;
    }

    function createChildElement(parent, tagname, attr, contents, cloneChildNodes) {
        var elem = createElement(tagname, attr, contents, cloneChildNodes);
        parent.appendChild(elem);
        return elem;
    }

    function createElementfromHTML(tag, attr, innerHTMl) {
        var element = createElement(tag, attr);
        element.innerHTML = innerHTMl;
        return element;
    }

    function createElementfromMarkdown(tag, attr, mardownText) {
        return createElementfromHTML(tag, attr, marked(mardownText, {gfd: true}));
    }

    function appendHTML(elem, html) {
        var parsed = createElementfromHTML('div', null, html);
        while(parsed.firstChild)
            elem.appendChild(parsed.firstChild);

    }

    function appendMarkdown(elem, markdown) {
        appendHTML(elem, marked(markdown, {gfd: true}));
    }

    function createFragment(contents, cloneChildNodes) {
        var frag = document.createDocumentFragment();
        appendChildren(frag, contents, cloneChildNodes);
        return frag;
    }

    function isDOMElement(node) {
        return node && node.nodeType && node.nodeType === 1;
    }

    function replaceNode(newNode, oldNode){
        oldNode.parentNode.replaceChild(newNode, oldNode);
    }

    return {
        createElement: createElement
      , createChildElement: createChildElement
      , createElementfromHTML: createElementfromHTML
      , createElementfromMarkdown: createElementfromMarkdown
      , appendChildren: appendChildren
      , appendHTML: appendHTML
      , appendMarkdown: appendMarkdown
      , createFragment: createFragment
      , isDOMElement: isDOMElement
      , replaceNode: replaceNode
    };
});
