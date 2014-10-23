myApp.controller('reviewGlyphInspectorController', ['$scope', '$rootScope', '$window', '$route', 'appConfig', function($scope, $rootScope, $window, $route, appConfig) {
    $scope.dataLoaded = false;
    // Glyph inspector tab
    var cellCount = 100,
        cellWidth = 44,
        cellHeight = 40,
        cellMarginTop = 1,
        cellMarginBottom = 8,
        cellMarginLeftRight = 1,
        glyphMargin = 5;

    var pageSelected, font, fontScale, fontSize, fontBaseline, glyphScale, glyphSize, glyphBaseline;

    function showErrorMessage(message) {
        var el = document.getElementById('message');
        if (!message || message.trim().length === 0) {
            el.style.display = 'none';
        } else {
            el.style.display = 'block';
        }
        el.innerHTML = message;
    }

    function pathCommandToString(cmd) {
        var str = '<strong>' + cmd.type + '</strong> ' +
            ((cmd.x !== undefined) ? 'x='+cmd.x+' y='+cmd.y+' ' : '') +
            ((cmd.x1 !== undefined) ? 'x1='+cmd.x1+' y1='+cmd.y1+' ' : '') +
            ((cmd.x2 !== undefined) ? 'x2='+cmd.x2+' y2='+cmd.y2 : '');
        return str;
    }

    function contourToString(contour) {
        return '<pre class="contour">' + contour.map(function(point) {
            return '<span class="' + (point.onCurve ? 'on' : 'off') + 'curve">x=' + point.x + ' y=' + point.y + '</span>';
        }).join('\n') + '</pre>';
    }

    function displayGlyphData(glyphIndex) {
        var container = document.getElementById('glyph-data');
        if (glyphIndex < 0) {
            container.innerHTML = '';
            return;
        }
        var glyph = $window.font.glyphs[glyphIndex],
            html = '<dl><dt>index</dt><dd>'+glyph.index+'</dd>';
        if ($window.font.glyphIndexToName) {
            html += '<dt>name</dt><dd>'+$window.font.glyphIndexToName(glyph.index)+'</dd>';
        }
        if (glyph.xMin !== 0 || glyph.xMax !== 0 || glyph.yMin !== 0 || glyph.yMax !== 0) {
            html += '<dt>xMin</dt><dd>'+glyph.xMin+'</dd>' +
                '<dt>xMax</dt><dd>'+glyph.xMax+'</dd>' +
                '<dt>yMin</dt><dd>'+glyph.yMin+'</dd>' +
                '<dt>yMax</dt><dd>'+glyph.yMax+'</dd>';
        }
        html += '<dt>advanceWidth</dt><dd>'+glyph.advanceWidth+'</dd>';
        if(glyph.leftSideBearing !== undefined) {
            html += '<dt>leftSideBearing</dt><dd>'+glyph.leftSideBearing+'</dd>';
        }
        html += '</dl>';
        if (glyph.path) {
            html += 'path:<br><pre>  ' + glyph.path.commands.map(pathCommandToString).join('\n  ') + '\n</pre>';
        }
        else if (glyph.numberOfContours > 0) {
            var contours = glyph.getContours();
            html += 'contours:<br>' + contours.map(contourToString).join('\n');
        }
        else if(glyph.isComposite) {
            html += '<br>This composite glyph is a combination of :<ul><li>' +
                glyph.components.map(function(component) {
                    return 'glyph '+component.glyphIndex+' at dx='+component.dx+', dy='+component.dy;
                }).join('</li><li>') + '</li></ul>';
        }
        container.innerHTML = html;
    }

    var arrowLength = 10,
        arrowAperture = 4;

    function drawArrow(ctx, x1, y1, x2, y2) {
        var dx = x2 - x1,
            dy = y2 - y1,
            segmentLength = Math.sqrt(dx*dx + dy*dy),
            unitx = dx / segmentLength,
            unity = dy / segmentLength,
            basex = x2 - arrowLength * unitx,
            basey = y2 - arrowLength * unity,
            normalx = arrowAperture * unity,
            normaly = -arrowAperture * unitx;
        ctx.beginPath();
        ctx.moveTo(x2, y2);
        ctx.lineTo(basex + normalx, basey + normaly);
        ctx.lineTo(basex - normalx, basey - normaly);
        ctx.lineTo(x2, y2);
        ctx.closePath();
        ctx.fill();
    }

    /**
     * This function is Path.prototype.draw with an arrow
     * at the end of each contour.
     */
    function drawPathWithArrows(ctx, path) {
        var i, cmd, x1, y1, x2, y2;
        var arrows = [];
        ctx.beginPath();
        for (i = 0; i < path.commands.length; i += 1) {
            cmd = path.commands[i];
            if (cmd.type === 'M') {
                if(x1 !== undefined) {
                    arrows.push([ctx, x1, y1, x2, y2]);
                }
                ctx.moveTo(cmd.x, cmd.y);
            } else if (cmd.type === 'L') {
                ctx.lineTo(cmd.x, cmd.y);
                x1 = x2;
                y1 = y2;
            } else if (cmd.type === 'C') {
                ctx.bezierCurveTo(cmd.x1, cmd.y1, cmd.x2, cmd.y2, cmd.x, cmd.y);
                x1 = cmd.x2;
                y1 = cmd.y2;
            } else if (cmd.type === 'Q') {
                ctx.quadraticCurveTo(cmd.x1, cmd.y1, cmd.x, cmd.y);
                x1 = cmd.x1;
                y1 = cmd.y1;
            } else if (cmd.type === 'Z') {
                arrows.push([ctx, x1, y1, x2, y2]);
                ctx.closePath();
            }
            x2 = cmd.x;
            y2 = cmd.y;
        }
        if (path.fill) {
            ctx.fillStyle = path.fill;
            ctx.fill();
        }
        if (path.stroke) {
            ctx.strokeStyle = path.stroke;
            ctx.lineWidth = path.strokeWidth;
            ctx.stroke();
        }
        ctx.fillStyle = '#000000';
        arrows.forEach(function(arrow) {
            drawArrow.apply(null, arrow);
        });
    }

    function displayGlyph(glyphIndex) {
        var canvas = document.getElementById('glyph'),
            ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if(glyphIndex < 0) return;
        var glyph = $window.font.glyphs[glyphIndex],
            glyphWidth = glyph.advanceWidth * glyphScale,
            xmin = (canvas.width - glyphWidth)/2,
            xmax = (canvas.width + glyphWidth)/2,
            x0 = xmin,
            markSize = 10;

        ctx.fillStyle = '#606060';
        ctx.fillRect(xmin-markSize+1, glyphBaseline, markSize, 1);
        ctx.fillRect(xmin, glyphBaseline, 1, markSize);
        ctx.fillRect(xmax, glyphBaseline, markSize, 1);
        ctx.fillRect(xmax, glyphBaseline, 1, markSize);
        ctx.textAlign = 'center';
        ctx.fillText('0', xmin, glyphBaseline+markSize+10);
        ctx.fillText(glyph.advanceWidth, xmax, glyphBaseline+markSize+10);

        ctx.fillStyle = '#000000';
        var path = glyph.getPath(x0, glyphBaseline, glyphSize);
        path.fill = '#808080';
        path.stroke = '#000000';
        path.strokeWidth = 1.5;
        drawPathWithArrows(ctx, path);
        glyph.drawPoints(ctx, x0, glyphBaseline, glyphSize);
    }

    function renderGlyphItem(canvas, glyphIndex) {
        var cellMarkSize = 4;
        var ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, cellWidth, cellHeight);
        if (glyphIndex >= $window.font.numGlyphs) return;

        ctx.fillStyle = '#606060';
        ctx.font = '9px sans-serif';
        ctx.fillText(glyphIndex, 1, cellHeight-1);
        var glyph = $window.font.glyphs[glyphIndex],
            glyphWidth = glyph.advanceWidth * fontScale,
            xmin = (cellWidth - glyphWidth)/2,
            xmax = (cellWidth + glyphWidth)/2,
            x0 = xmin;

        ctx.fillStyle = '#a0a0a0';
        ctx.fillRect(xmin-cellMarkSize+1, fontBaseline, cellMarkSize, 1);
        ctx.fillRect(xmin, fontBaseline, 1, cellMarkSize);
        ctx.fillRect(xmax, fontBaseline, cellMarkSize, 1);
        ctx.fillRect(xmax, fontBaseline, 1, cellMarkSize);

        ctx.fillStyle = '#000000';
        glyph.draw(ctx, x0, fontBaseline, fontSize);
    }

    function displayGlyphPage(pageNum) {
        pageSelected = pageNum;
        document.getElementById('p'+pageNum).className = 'page-selected';
        var firstGlyph = pageNum * cellCount;
        for(var i = 0; i < cellCount; i++) {
            renderGlyphItem(document.getElementById('g'+i), firstGlyph+i);
        }
    }

    function pageSelect(event) {
        document.getElementsByClassName('page-selected')[0].className = '';
        displayGlyphPage(+event.target.id.substr(1));
    }

    function initGlyphDisplay() {
        var glyphBgCanvas = document.getElementById('glyph-bg'),
            w = glyphBgCanvas.width,
            h = glyphBgCanvas.height,
            glyphW = w - glyphMargin*2,
            glyphH = h - glyphMargin*2,
            head = $window.font.tables.head,
            maxHeight = head.yMax - head.yMin,
            ctx = glyphBgCanvas.getContext('2d');

        glyphScale = Math.min(glyphW/(head.xMax - head.xMin), glyphH/maxHeight);
        glyphSize = glyphScale * $window.font.unitsPerEm;
        glyphBaseline = glyphMargin + glyphH * head.yMax / maxHeight;

        function hline(text, yunits) {
            ypx = glyphBaseline - yunits * glyphScale;
            ctx.fillText(text, 2, ypx+3);
            ctx.fillRect(80, ypx, w, 1);
        }

        ctx.clearRect(0, 0, w, h);
        ctx.fillStyle = '#a0a0a0'
        hline('Baseline', 0);
        hline('yMax', $window.font.tables.head.yMax);
        hline('yMin', $window.font.tables.head.yMin);
        hline('Ascender', $window.font.tables.hhea.ascender);
        hline('Descender', $window.font.tables.hhea.descender);
        hline('Typo Ascender', $window.font.tables.os2.sTypoAscender);
        hline('Typo Descender', $window.font.tables.os2.sTypoDescender);
    }

    function onFontLoaded(font) {
        window.font = font;
        $window.font = font;

        var w = cellWidth - cellMarginLeftRight * 2,
            h = cellHeight - cellMarginTop - cellMarginBottom,
            head = $window.font.tables.head,
            maxHeight = head.yMax - head.yMin;
        fontScale = Math.min(w/(head.xMax - head.xMin), h/maxHeight);
        fontSize = fontScale * $window.font.unitsPerEm;
        fontBaseline = cellMarginTop + h * head.yMax / maxHeight;

        var pagination = document.getElementById("pagination");
        pagination.innerHTML = '';
        var fragment = document.createDocumentFragment();
        var numPages = Math.ceil($window.font.numGlyphs / cellCount);
        for(var i = 0; i < numPages; i++) {
            var link = document.createElement('span');
            var lastIndex = Math.min($window.font.numGlyphs-1, (i+1)*cellCount-1);
            link.textContent = i*cellCount + '-' + lastIndex;
            link.id = 'p' + i;
            link.addEventListener('click', pageSelect, false);
            fragment.appendChild(link);
            // A white space allows to break very long lines into multiple lines.
            // This is needed for fonts with thousands of glyphs.
            fragment.appendChild(document.createTextNode(' '));
        }
        pagination.appendChild(fragment);

        initGlyphDisplay();
        displayGlyphPage(0);
        displayGlyph(-1);
        displayGlyphData(-1);
    }

    function onReadFile(e) {
        document.getElementById('font-name').innerHTML = '';
        var file = e.target.files[0];
        var reader = new FileReader();
        reader.onload = function (e) {
            try {
                $window.font = opentype.parse(e.target.result);
                showErrorMessage('');
                onFontLoaded($window.font);
            } catch (err) {
                showErrorMessage(err.toString());
                throw(err);
            }
        };
        reader.onerror = function (err) {
            showErrorMessage(err.toString());
        };

        reader.readAsArrayBuffer(file);
    }

    function cellSelect(event) {
        if (!$window.font) return;
        var firstGlyphIndex = pageSelected*cellCount,
            cellIndex = +event.target.id.substr(1),
            glyphIndex = firstGlyphIndex + cellIndex;
        if (glyphIndex < $window.font.numGlyphs) {
            displayGlyph(glyphIndex);
            displayGlyphData(glyphIndex);
        }
    }

    function prepareGlyphList() {
        var marker = document.getElementById('glyph-list-end'),
            parent = marker.parentElement;
        for(var i = 0; i < cellCount; i++) {
            var canvas = document.createElement('canvas');
            canvas.width = cellWidth;
            canvas.height = cellHeight;
            canvas.className = 'item';
            canvas.id = 'g'+i;
            canvas.addEventListener('click', cellSelect, false);
            parent.insertBefore(canvas, marker);
        }
    }

    angular.element(document).ready(function() {
        $scope.dataLoaded = true;
        if ($rootScope.metadata.fonts.length > 0) {
            var fontFileName = [
                appConfig.base_url,
                $route.current.params.repo_owner,
                $route.current.params.repo_name,
                'gh-pages/build_info/static/css/fonts',
                $rootScope.metadata.fonts[0].filename
            ].join('/');
            var parser = document.createElement('a');
            parser.href = fontFileName;
            document.getElementById('font-name').innerHTML = parser.href.substr(parser.href.lastIndexOf('/') + 1);

            var fileButton = document.getElementById('file');
            fileButton.addEventListener('change', onReadFile, false);

            prepareGlyphList();
            opentype.load(fontFileName, function (err, font) {
                var amount, glyph, ctx, x, y, fontSize;
                if (err) {
                    showErrorMessage(err.toString());
                    return;
                }
                onFontLoaded(font);
            });
        }
    });

}]);