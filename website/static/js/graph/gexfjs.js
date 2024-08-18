/* Lead developer: RaphaÃ«l Velt
 * Other developers: Jakko Salonen, Tobias Bora, Jan de Mooij
 * Twitch Analysis minor adaptations: giambaJ
 *
 * Licensed under the MIT License
 * Translations by:
 *    Vicenzo Cosenza (Italian)
 *    Eduardo Ramos IbÃ¡Ã±ez (Spanish)
 *    Jaakko Salonen (Finnish)
 *    Zeynep Akata (Turkish)
 *    Î£Ï‰Ï„Î®ÏÎ·Ï‚ Î¦ÏÎ±Î³ÎºÎ¯ÏƒÎºÎ¿Ï‚ (Greek)
 *    Martin Eckert (German)
 *    Jan de Mooij (Dutch)
 *    Bruna Delazeri (Brazilian Portuguese)
 *    Adil Aliyev (Azerbaijani)
 * */

(function($) { // Thanks to BrunoLM (https://stackoverflow.com/a/3855394)
    $.QueryString = (function(paramsArray) {
        let params = {};

        for (let i = 0; i < paramsArray.length; ++i) {
            let param = paramsArray[i]
                .split('=', 2);

            if (param.length !== 2)
                continue;

            params[param[0]] = decodeURIComponent(param[1].replace(/\+/g, " "));
        }

        return params;
    })(window.location.search.substr(1).split('&'))
})(jQuery);

(function() {

    var GexfJS = {
        lensRadius: 200,
        lensGamma: 0.5,
        graphZone: {
            width: 0,
            height: 0
        },
        oldGraphZone: {},
        params: {
            centreX: 400,
            centreY: 350,
            activeNode: -1,
            currentNode: -1,
            isMoving: false
        },
        oldParams: {},
        minZoom: 0,
        maxZoom: 10,
        overviewWidth: 200,
        overviewHeight: 175,
        baseWidth: 800,
        baseHeight: 700,
        overviewScale: .25,
        totalScroll: 0,
        autoCompletePosition: 0,
        i18n: {
            "az": {
                "search": "TÉ™pÉ™lÉ™ri axtar",
                "nodeAttr": "Attributlar",
                "nodes": "TÉ™pÉ™ nÃ¶qtÉ™lÉ™ri",
                "inLinks": "Daxil olan É™laqÉ™lÉ™r:",
                "outLinks": "Ã‡Ä±xan É™laqÉ™lÉ™r:",
                "undirLinks": "Ä°stiqamÉ™tsiz É™laqÉ™lÉ™r:",
                "lensOn": "Linza rejiminÉ™ keÃ§",
                "lensOff": "Linza rejimindÉ™n Ã§Ä±x",
                "edgeOn": "TillÉ™ri gÃ¶stÉ™r",
                "edgeOff": "TillÉ™ri gizlÉ™t",
                "zoomIn": "YaxÄ±nlaÅŸdÄ±r",
                "zoomOut": "UzaqlaÅŸdÄ±r",
                "modularity_class": "ModullaÅŸma sinfi",
                "degree": "DÉ™rÉ™cÉ™"
            },
            "de": {
                "search": "Suche Knoten",
                "nodeAttr": "Attribute",
                "nodes": "Knoten",
                "inLinks": "Ankommende VerknÃ¼pfung von",
                "outLinks": "Ausgehende VerknÃ¼pfung zu",
                "undirLinks": "Ungerichtete VerknÃ¼pfung mit",
                "lensOn": "VergrÃ¶ÃŸerungsmodus an",
                "lensOff": "VergrÃ¶ÃŸerungsmodus aus",
                "edgeOn": "Kanten anzeigen",
                "edgeOff": "Kanten verstecken",
                "zoomIn": "VergrÃ¶ÃŸern",
                "zoomOut": "Verkleinern",
            },
            "el": {
                "search": "Î‘Î½Î±Î¶Î®Ï„Î·ÏƒÎ· ÎšÏŒÎ¼Î²Ï‰Î½",
                "nodeAttr": "Î§Î±ÏÎ±ÎºÏ„Î·ÏÎ¹ÏƒÏ„Î¹ÎºÎ¬",
                "nodes": "ÎšÏŒÎ¼Î²Î¿Î¹",
                "inLinks": "Î•Î¹ÏƒÎµÏÏ‡ÏŒÎ¼ÎµÎ½Î¿Î¹ Î´ÎµÏƒÎ¼Î¿Î¯ Î±Ï€ÏŒ",
                "outLinks": "Î•Î¾ÎµÏÏ‡ÏŒÎ¼ÎµÎ½Î¿Î¹ Î´ÎµÏƒÎ¼Î¿Î¯ Ï€ÏÎ¿Ï‚",
                "undirLinks": "Î‘ÎºÎ±Ï„ÎµÏÎ¸Ï…Î½Ï„Î¿Î¹ Î´ÎµÏƒÎ¼Î¿Î¯ Î¼Îµ",
                "lensOn": "Î•Î½ÎµÏÎ³Î¿Ï€Î¿Î¯Î·ÏƒÎ· Ï†Î±ÎºÎ¿Ï",
                "lensOff": "Î‘Ï€ÎµÎ½ÎµÏÎ³Î¿Ï€Î¿Î¯Î·ÏƒÎ· Ï†Î±ÎºÎ¿Ï",
                "edgeOn": "Î•Î¼Ï†Î¬Î½Î¹ÏƒÎ· Î±ÎºÎ¼ÏŽÎ½",
                "edgeOff": "Î‘Ï€ÏŒÎºÏÏ…ÏˆÎ· Î±ÎºÎ¼ÏŽÎ½",
                "zoomIn": "ÎœÎµÎ³Î­Î¸Ï…Î½ÏƒÎ·",
                "zoomOut": "Î£Î¼Î¯ÎºÏÏ…Î½ÏƒÎ·",
            },
            "en": {
                "search": "Search streamers",
                "nodeAttr": "Attributes",
                "nodes": "Nodes",
                "inLinks": "Inbound Links from:",
                "outLinks": "Outbound Links to:",
                "undirLinks": "Links with:",
                "lensOn": "Activate lens mode",
                "lensOff": "Deactivate lens mode",
                "edgeOn": "Show edges",
                "edgeOff": "Hide edges",
                "zoomIn": "Zoom In",
                "zoomOut": "Zoom Out",
            },
            "es": {
                "search": "Buscar un nodo",
                "nodeAttr": "Atributos",
                "nodes": "Nodos",
                "inLinks": "Aristas entrantes desde :",
                "outLinks": "Aristas salientes hacia :",
                "undirLinks": "Aristas no dirigidas con :",
                "lensOn": "Activar el modo lupa",
                "lensOff": "Desactivar el modo lupa",
                "edgeOn": "Mostrar aristas",
                "edgeOff": "Ocultar aristas",
                "zoomIn": "Acercar",
                "zoomOut": "Alejar",
                "modularity_class": "Clase de modularidad",
                "degree": "Grado",
                "indegree": "Grado de entrada",
                "outdegree": "Grado de salida",
                "weighted degree": "Grado ponderado",
                "weighted indegree": "Grado de entrada ponderado",
                "weighted outdegree": "Grado de salida ponderado",
                "closnesscentrality": "CercanÃ­a",
                "betweenesscentrality": "IntermediaciÃ³n",
                "authority": "PuntuaciÃ³n de autoridad (HITS)",
                "hub": "PuntuaciÃ³n de hub (HITS)",
                "pageranks": "PuntuaciÃ³n de PageRank"
            },
            "fi": {
                "search": "Etsi solmuja",
                "nodeAttr": "Attribuutit",
                "nodes": "Solmut",
                "inLinks": "LÃ¤htevÃ¤t yhteydet :",
                "outLinks": "Tulevat yhteydet :",
                "undirLinks": "Yhteydet :",
                "lensOn": "Ota linssitila kÃ¤yttÃ¶Ã¶n",
                "lensOff": "Poista linssitila kÃ¤ytÃ¶stÃ¤",
                "edgeOn": "NÃ¤ytÃ¤ kaikki yhteydet",
                "edgeOff": "NÃ¤ytÃ¤ vain valitun solmun yhteydet",
                "zoomIn": "Suurenna",
                "zoomOut": "PienennÃ¤",
            },
            "fr": {
                "search": "Rechercher un nÅ“ud",
                "nodeAttr": "Attributs",
                "nodes": "NÅ“uds",
                "inLinks": "Liens entrants depuis :",
                "outLinks": "Liens sortants vers :",
                "undirLinks": "Liens non-dirigÃ©s avec :",
                "lensOn": "Activer le mode loupe",
                "lensOff": "DÃ©sactiver le mode loupe",
                "edgeOn": "Afficher les sommets",
                "edgeOff": "Cacher les sommets",
                "zoomIn": "S'approcher",
                "zoomOut": "S'Ã©loigner",
                "modularity_class": "Classe de modularitÃ©",
                "degree": "DegrÃ©",
                "indegree": "Demi-degrÃ© intÃ©rieur",
                "outdegree": "Demi-degrÃ© extÃ©rieur",
                "weighted degree": "DegrÃ© pondÃ©rÃ©",
                "weighted indegree": "Demi-degrÃ© intÃ©rieur pondÃ©rÃ©",
                "weighted outdegree": "Demi-degrÃ© extÃ©rieur pondÃ©rÃ©",
                "closnesscentrality": "CentralitÃ© de proximitÃ©",
                "betweenesscentrality": "CentralitÃ© dâ€™intermÃ©diaritÃ©",
                "authority": "Score dâ€™autoritÃ© (HITS)",
                "hub": "Score de hub (HITS)",
                "pageranks": "Score de PageRank"
            },
            "it": {
                "search": "Cerca streamer",
                "nodeAttr": "Attributi",
                "nodes": "Streamer",
                "inLinks": "Archi in ingresso da:",
                "outLinks": "Archi in uscita verso:",
                "undirLinks": "Connessioni con:",
                "lensOn": "Attiva la lente dâ€™ingrandimento",
                "lensOff": "Disattiva la lente dâ€™ingrandimento",
                "edgeOn": "Mostra le connessioni",
                "edgeOff": "Nascondi le connessioni",
                "infoOn": "Mostra le informazioni",
                "infoOff": "Nascondi le informazioni",
                "listOn": "Mostra la lista della community",
                "listOff": "Nascondi la lista della community",
                "zoomIn": "Zoom avanti",
                "zoomOut": "Zoom indietro",
            },
            "tr": {
                "search": "DÃ¼ÄŸÃ¼m ara",
                "nodeAttr": "Ã–zellikler",
                "nodes": "DÃ¼ÄŸÃ¼mler",
                "inLinks": "Gelen baÄŸlantÄ±lar",
                "outLinks": "Giden baÄŸlantÄ±lar",
                "undirLinks": "YÃ¶nsÃ¼z baÄŸlantÄ±lar",
                "lensOn": "MerceÄŸi etkinleÅŸtir",
                "lensOff": "MerceÄŸi etkisizleÅŸtir",
                "edgeOn": "Kenar Ã§izgilerini gÃ¶ster",
                "edgeOff": "Kenar Ã§izgilerini gizle",
                "zoomIn": "YaklaÅŸtÄ±r",
                "zoomOut": "UzaklaÅŸtÄ±r",
            },
            "nl": {
                "search": "Knooppunten doorzoeken",
                "nodeAttr": "Attributen",
                "nodes": "Knooppunten",
                "inLinks": "Binnenkomende verbindingen van :",
                "outLinks": "Uitgaande verbindingen naar :",
                "undirLinks": "Ongerichtte verbindingen met:",
                "lensOn": "Loepmodus activeren",
                "lensOff": "Loepmodus deactiveren",
                "edgeOn": "Kanten tonen",
                "edgeOff": "Kanten verbergen",
                "zoomIn": "Inzoomen",
                "zoomOut": "Uitzoomen",
            },
            "pt": {
                "search": "Pesquisar nÃ³s",
                "nodeAttr": "Atributos",
                "nodes": "NÃ³s",
                "inLinks": "LigaÃ§Ãµes de entrada",
                "outLinks": "LigaÃ§Ãµes de saÃ­da",
                "undirLinks": "LigaÃ§Ãµes sem direÃ§Ã£o",
                "lensOn": "Ativar modo lente",
                "lensOff": "Ativar modo lente",
                "edgeOn": "Mostrar arestas",
                "edgeOff": "Esconder arestas",
                "zoomIn": "Aumentar zoom",
                "zoomOut": "Diminuir zoom",
            }
        },
        lang: "en"
    };

    var timedict = {}

    function measureTime(key) {
        if (timedict[key]) {
            console.log(key + " took " + (Date.now() - timedict[key]) / 1000 + "s");
            delete timedict[key]
        } else {
            timedict[key] = Date.now()
        }
    }

    var movingTO = null;

    function onStartMoving() {
        window.clearTimeout(movingTO);
        GexfJS.params.isMoving = true;
    }

    function onEndMoving() {
        movingTO = window.setTimeout(function() {
            GexfJS.params.isMoving = false;
        }, 200);
    }

    function strLang(_str) {
        var _l = GexfJS.i18n[GexfJS.lang];
        return (_l[_str] ? _l[_str] : (GexfJS.i18n["en"][_str] ? GexfJS.i18n["en"][_str] : _str.replace("_", " ")));
    }

    function replaceURLWithHyperlinks(text) {
        if (GexfJS.params.replaceUrls) {
            var _urlExp = /(\b(?:https?:\/\/)?[-A-Z0-9]+\.[-A-Z0-9.:]+(?:\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*)?)/ig,
                _protocolExp = /^https?:\/\//i,
                _res = text.split(_urlExp);
            return _res.map(function(_txt) {
                if (_txt.match(_urlExp)) {
                    return $('<a>').attr({
                        href: (_protocolExp.test(_txt) ? '' : 'http://') + _txt,
                        target: "_blank"
                    }).text(_txt.replace(_protocolExp, ''));
                } else {
                    return $('<span>').text(_txt);
                }
            });
        }
        return $("<span>").text(text);
    }

    function displayNode(_nodeIndex, _recentre) {
        GexfJS.params.currentNode = _nodeIndex;
        if (_nodeIndex != -1) {
            var _d = GexfJS.graph.nodeList[_nodeIndex],
                _html = $('<div>'),
                _ul = $('<ul>'),
                _cG = $("#leftcolumn");
            _cG.animate({
                "left": "0px"
            }, function() {
                $("#aUnfold").attr("class", "leftarrow");
                $("#zonecentre").css({
                    left: _cG.width() + "px"
                });
            });
            $('<h3>')
                .append($('<div>').addClass('largepill').css('background', _d.B))
                .append($('<span>').text(_d.l))
                .appendTo(_html);
            if (GexfJS.params.showNodeAttributes) {
                $('<h4>').text(strLang("nodeAttr")).appendTo(_html);
                _ul.appendTo(_html);
                if (GexfJS.params.showId) {
                    var _li = $("<li>");
                    $("<b>").text("id: ").appendTo(_li);
                    $("<span>").text(_d.id).appendTo(_li);
                    _li.appendTo(_ul);
                }
                for (var i = 0, l = _d.a.length; i < l; i++) {
                    var attr = _d.a[i];
                    var _li = $("<li>");
                    var attrkey = GexfJS.graph.attributes[attr[0]];
                    $("<b>").text(strLang(attrkey) + ": ").appendTo(_li);
                    if (attrkey === 'image') {
                        $('<br>').appendTo(_li);
                        $('<img>').attr("src", attr[1]).appendTo(_li).addClass("attrimg");
                    } else {
                        _li.append(replaceURLWithHyperlinks(attr[1]));
                    }
                    _li.appendTo(_ul);
                }
            }

            var _class = [];
            GexfJS.graph.sortedNodeList.forEach(function(_n) {
                if (_n.modClass == _d.modClass) {
                    var _li = $("<li>");
                    $("<div>").addClass("smallpill").css("background", _n.B).appendTo(_li);
                    $("<a>")
                        .text(_n.l)
                        .attr("href", "#")
                        .click(function() {
                            displayNode(GexfJS.graph.indexOfLabels.indexOf(_n.id.toLowerCase()), true);
                            return false;
                        })
                        .appendTo(_li);
                    $('<span>').text(" (" + _n.count + ")").appendTo(_li);
                    _class.push(_li);
                }
            });
            if (_class.length) {
                $("#communityList").html(_class);
            }

            var _str_in = [],
                _str_out = [],
                _str_undir = [];
            GexfJS.graph.edgeList.forEach(function(_e) {
                if (_e.t == _nodeIndex) {
                    var _n = GexfJS.graph.nodeList[_e.s];
                    var _li = $("<li>");
                    $("<div>").addClass("smallpill").css("background", _n.B).appendTo(_li);
                    $("<a>")
                        .text(_n.l)
                        .attr("href", "#")
                        .mouseover(function() {
                            GexfJS.params.activeNode = _e.s;
                        })
                        .click(function() {
                            displayNode(_e.s, true);
                            return false;
                        })
                        .appendTo(_li);
                    if (GexfJS.params.showEdgeLabel) {
                        $('<span>').text(" â€“ " + _e.l).appendTo(_li);
                    }
                    if (GexfJS.params.showEdgeWeight) {
                        $('<span>').text(" (" + _e.w + ")").appendTo(_li);
                    }
                    if (_e.d) {
                        _str_in.push(_li);
                    } else {
                        _str_undir.push(_li);
                    }
                }
                if (_e.s == _nodeIndex) {
                    var _n = GexfJS.graph.nodeList[_e.t];
                    var _li = $("<li>");
                    $("<div>").addClass("smallpill").css("background", _n.B).appendTo(_li);
                    $("<a>")
                        .text(_n.l)
                        .attr("href", "#")
                        .mouseover(function() {
                            GexfJS.params.activeNode = _e.t;
                        })
                        .click(function() {
                            displayNode(_e.t, true);
                            return false;
                        })
                        .appendTo(_li);
                    if (GexfJS.params.showEdgeLabel) {
                        $('<span>').text(" â€“ " + _e.l).appendTo(_li);
                    }
                    if (GexfJS.params.showEdgeWeight) {
                        $('<span>').text(" (" + _e.w + ")").appendTo(_li);
                    }
                    if (_e.d) {
                        _str_out.push(_li);
                    } else {
                        _str_undir.push(_li);
                    }
                }
            });
            if (_str_in.length) {
                $('<h4>').text(strLang("inLinks")).appendTo(_html);
                $('<ul>').html(_str_in).appendTo(_html);
            }
            if (_str_out.length) {
                $('<h4>').text(strLang("outLinks")).appendTo(_html);
                $('<ul>').html(_str_out).appendTo(_html);
            }
            if (_str_undir.length) {
                $('<h4>').text(strLang("undirLinks")).appendTo(_html);
                $('<ul>').html(_str_undir).appendTo(_html);
            }
            $("#leftcontent").html(_html);
            if (_recentre) {
                GexfJS.params.centreX = _d.x;
                GexfJS.params.centreY = _d.y;
            }
            $("#searchinput")
                .val(_d.l)
            if (GexfJS.params.showList) {
                $("#listPanel").attr("class", "");
            }
        } else {
            if (GexfJS.params.showList) {
                $("#listPanel").attr("class", "off");
            }
        }
    }

    function updateWorkspaceBounds() {

        var _elZC = $("#zonecentre");
        var _top = {
            top: $("#titlebar").height() + "px"
        };
        _elZC.css(_top);

        $("#leftcolumn").css(_top);
        GexfJS.graphZone.width = _elZC.width();
        GexfJS.graphZone.height = _elZC.height();
        GexfJS.areParamsIdentical = true;

        for (var i in GexfJS.graphZone) {
            GexfJS.areParamsIdentical = GexfJS.areParamsIdentical && (GexfJS.graphZone[i] == GexfJS.oldGraphZone[i]);
        }
        if (!GexfJS.areParamsIdentical) {

            $("#carte")
                .attr({
                    width: GexfJS.graphZone.width,
                    height: GexfJS.graphZone.height
                })
                .css({
                    width: GexfJS.graphZone.width + "px",
                    height: GexfJS.graphZone.height + "px"
                });
            for (var i in GexfJS.graphZone) {
                GexfJS.oldGraphZone[i] = GexfJS.graphZone[i];
            }
        }
    }

    function onTouchStart(evt) {

        var coords = evt.originalEvent.targetTouches[0];
        if (evt.originalEvent.targetTouches.length == 1) {
            GexfJS.lastMouse = {
                x: coords.pageX,
                y: coords.pageY
            }
            GexfJS.dragOn = true;
            GexfJS.mouseHasMoved = false;
        } else {
            GexfJS.lastPinch = getPinchDistance(evt);
            GexfJS.pinchOn = true;
        }
        onStartMoving();

    }

    function startMove(evt) {
        evt.preventDefault();
        GexfJS.dragOn = true;
        GexfJS.lastMouse = {
            x: evt.pageX,
            y: evt.pageY
        };
        GexfJS.mouseHasMoved = false;
        onStartMoving();
    }

    function onTouchEnd(evt) {
        GexfJS.dragOn = false;
        GexfJS.pinchOn = false;
        GexfJS.mouseHasMoved = false;
        onEndMoving();
    }

    function endMove(evt) {
        document.body.style.cursor = "default";
        GexfJS.dragOn = false;
        GexfJS.mouseHasMoved = false;
        onEndMoving();
    }

    function onGraphClick(evt) {
        if (!GexfJS.mouseHasMoved && !GexfJS.pinchOn) {
            displayNode(GexfJS.params.activeNode);
        }
        endMove();
    }

    function changeGraphPosition(evt, echelle) {
        document.body.style.cursor = "move";
        var _coord = {
            x: evt.pageX,
            y: evt.pageY
        };
        GexfJS.params.centreX += (GexfJS.lastMouse.x - _coord.x) / echelle;
        GexfJS.params.centreY += (GexfJS.lastMouse.y - _coord.y) / echelle;
        GexfJS.lastMouse = _coord;
    }

    function onGraphMove(evt) {
        evt.preventDefault();
        if (!GexfJS.graph) {
            return;
        }
        GexfJS.mousePosition = {
            x: evt.pageX - $(this).offset().left,
            y: evt.pageY - $(this).offset().top
        };
        if (GexfJS.dragOn) {
            changeGraphPosition(evt, GexfJS.globalScale);
            GexfJS.mouseHasMoved = true;
        } else {
            GexfJS.params.activeNode = getNodeFromPos(GexfJS.mousePosition);
            document.body.style.cursor = (GexfJS.params.activeNode != -1 ? "pointer" : "default");
        }
    }

    function onGraphDrag(evt) {
        evt.preventDefault();
        if (!GexfJS.graph) {
            return;
        }
        if (evt.originalEvent.targetTouches.length == 1) {
            var coords = evt.originalEvent.targetTouches[0];
            GexfJS.mousePosition = {
                x: coords.pageX - $(this).offset().left,
                y: coords.pageY - $(this).offset().top
            };
            if (GexfJS.dragOn) {
                evt.pageX = coords.pageX;
                evt.pageY = coords.pageY;
                changeGraphPosition(evt, GexfJS.globalScale);
                GexfJS.mouseHasMoved = true;
            } else {
                GexfJS.params.activeNode = getNodeFromPos(GexfJS.mousePosition);
            }
        } else {

            evt.pageX = evt.originalEvent.targetTouches[0].pageX +
                (
                    (
                        evt.originalEvent.targetTouches[1].pageX -
                        evt.originalEvent.targetTouches[0].pageX
                    ) / 2
                );
            evt.pageY = evt.originalEvent.targetTouches[0].pageY +
                (
                    (
                        evt.originalEvent.targetTouches[1].pageY -
                        evt.originalEvent.targetTouches[0].pageY
                    ) / 2
                );

            var currentPinch = getPinchDistance(evt);

            var delta = currentPinch - GexfJS.lastPinch;
            if (Math.abs(delta) >= 20) {
                GexfJS.lastPinch = currentPinch;
                onGraphScroll(evt, delta);
            } else {
                GexfJS.totalScroll = 0;
            }
        }
    }

    function getPinchDistance(evt) {
        return Math.sqrt(
            Math.pow(
                evt.originalEvent.targetTouches[0].pageX -
                evt.originalEvent.targetTouches[1].pageX, 2) +
            Math.pow(
                evt.originalEvent.targetTouches[0].pageY -
                evt.originalEvent.targetTouches[1].pageY, 2
            )
        );
    }

    function onOverviewMove(evt) {
        if (GexfJS.dragOn) {
            changeGraphPosition(evt, -GexfJS.overviewScale);
        }
    }

    function onOverviewDrag(evt) {
        var coords = evt.originalEvent.targetTouches[0];
        evt.pageX = coords.pageX;
        evt.pageY = coords.pageY;
        if (GexfJS.dragOn) {
            changeGraphPosition(evt, -GexfJS.overviewScale);
        }
    }

    function onGraphScroll(evt, delta) {
        GexfJS.totalScroll += delta;
        if (Math.abs(GexfJS.totalScroll) >= 1) {
            if (GexfJS.totalScroll < 0) {
                if (GexfJS.params.zoomLevel > GexfJS.minZoom) {
                    GexfJS.params.zoomLevel--;
                    var _el = (typeof($(this).offset()) == 'object') ? $(this) : $('#carte'),
                        _off = _el.offset(),
                        _deltaX = evt.pageX - _el.width() / 2 - _off.left,
                        _deltaY = evt.pageY - _el.height() / 2 - _off.top;
                    GexfJS.params.centreX -= (Math.SQRT2 - 1) * _deltaX / GexfJS.globalScale;
                    GexfJS.params.centreY -= (Math.SQRT2 - 1) * _deltaY / GexfJS.globalScale;
                    $("#zoomSlider").slider("value", GexfJS.params.zoomLevel);
                }
            } else {
                if (GexfJS.params.zoomLevel < GexfJS.maxZoom) {
                    GexfJS.params.zoomLevel++;
                    GexfJS.globalScale = Math.pow(Math.SQRT2, GexfJS.params.zoomLevel);
                    var _el = (typeof($(this).offset()) == 'object') ? $(this) : $('#carte'),
                        _off = _el.offset(),
                        _deltaX = evt.pageX - _el.width() / 2 - _off.left,
                        _deltaY = evt.pageY - _el.height() / 2 - _off.top;
                    GexfJS.params.centreX += (Math.SQRT2 - 1) * _deltaX / GexfJS.globalScale;
                    GexfJS.params.centreY += (Math.SQRT2 - 1) * _deltaY / GexfJS.globalScale;
                    $("#zoomSlider").slider("value", GexfJS.params.zoomLevel);
                }
            }
            GexfJS.totalScroll = 0;
            onStartMoving();
            onEndMoving();
        }
    }

    function initializeMap() {
        clearInterval(GexfJS.timeRefresh);
        GexfJS.oldParams = {};
        GexfJS.ctxGraphe.clearRect(0, 0, GexfJS.graphZone.width, GexfJS.graphZone.height);
        $("#zoomSlider").slider({
            orientation: "vertical",
            value: GexfJS.params.zoomLevel,
            min: GexfJS.minZoom,
            max: GexfJS.maxZoom,
            range: "min",
            step: 1,
            slide: function(event, ui) {
                GexfJS.params.zoomLevel = ui.value;
                onStartMoving();
                onEndMoving();
            }
        });
        $("#overviewzone").css({
            width: GexfJS.overviewWidth + "px",
            height: GexfJS.overviewHeight + "px"
        });
        $("#overview").attr({
            width: GexfJS.overviewWidth,
            height: GexfJS.overviewHeight
        });
        GexfJS.timeRefresh = setInterval(traceMap, 60);
        GexfJS.graph = null;
        loadGraph();
    }

    function loadGraph() {

        var url = (document.location.hash.length > 1 ? document.location.hash.substr(1) : GexfJS.params.graphFile);
        var isJson = (function(t) { return t[t.length - 1]; })(url.split('.')) === 'json';

        console.log("Loading " + url + " in " + (isJson ? "json" : "gexf") + " mode");
        measureTime("Loading graph from network");

        $.ajax({
            url: url,
            dataType: (isJson ? "json" : "xml"),
            success: function(data) {
                measureTime("Loading graph from network");
                measureTime("Pre-processing graph");
                if (isJson) {
                    GexfJS.graph = data;
                    GexfJS.graph.indexOfLabels = GexfJS.graph.nodeList.map(function(_d) {
                        return _d.l.toLowerCase();
                    });

                } else {
                    var _g = $(data).find("graph"),
                        _nodes = _g.children().filter("nodes").children(),
                        _edges = _g.children().filter("edges").children();
                    GexfJS.graph = {
                        directed: (_g.attr("defaultedgetype") == "directed"),
                        nodeList: [],
                        sortedNodeList: [],
                        indexOfLabels: [],
                        edgeList: [],
                        attributes: {},
                    };
                    var _xmin = 1e9,
                        _xmax = -1e9,
                        _ymin = 1e9,
                        _ymax = -1e9;
                    _marge = 30;
                    $(_nodes).each(function() {
                        var _n = $(this),
                            _pos = _n.find("viz\\:position,position"),
                            _x = _pos.attr("x"),
                            _y = _pos.attr("y");
                        _xmin = Math.min(_x, _xmin);
                        _xmax = Math.max(_x, _xmax);
                        _ymin = Math.min(_y, _ymin);
                        _ymax = Math.max(_y, _ymax);
                    });

                    var _scale = Math.min((GexfJS.baseWidth - _marge) / (_xmax - _xmin), (GexfJS.baseHeight - _marge) / (_ymax - _ymin));
                    var _deltax = (GexfJS.baseWidth - _scale * (_xmin + _xmax)) / 2;
                    var _deltay = (GexfJS.baseHeight - _scale * (_ymin + _ymax)) / 2;
                    var nodeIndexById = [];

                    $(_nodes).each(function() {
                        var _n = $(this),
                            _id = _n.attr("id"),
                            _label = _n.attr("label") || _id,
                            _pos = _n.find("viz\\:position,position"),
                            _d = {
                                id: _id,
                                l: _label,
                                x: _deltax + _scale * _pos.attr("x"),
                                y: _deltay - _scale * _pos.attr("y"),
                                r: _scale * _n.find("viz\\:size,size").attr("value"),
                            },
                            _col = _n.find("viz\\:color,color"),
                            _r = _col.attr("r"),
                            _g = _col.attr("g"),
                            _b = _col.attr("b"),
                            _attr = _n.find("attvalue");
                        _d.rgb = [_r, _g, _b];
                        _d.B = "rgba(" + _r + "," + _g + "," + _b + ",.7)";
                        _d.G = "rgba(" + Math.floor(84 + .33 * _r) + "," + Math.floor(84 + .33 * _g) + "," + Math.floor(84 + .33 * _b) + ",.5)";
                        _d.a = [];
                        $(_attr).each(function() {
                            var _a = $(this),
                                _for = _a.attr("for");
                            if (_for == 'count') _d.count = _a.attr("value");
                            if (_for == 'modularity_class') _d.modClass = _a.attr("value");
                            _d.a.push([
                                _for ? _for : 'attribute_' + _a.attr("id"),
                                _a.attr("value")
                            ]);
                            GexfJS.graph.attributes[_for] = _for;

                        });
                        if (GexfJS.params.sortNodeAttributes) {
                            _d.a.sort(function(a, b) {
                                return (a[0] < b[0] ? -1 : (a[0] > b[0] ? 1 : 0));
                            });
                        }
                        GexfJS.graph.nodeList.push(_d);
                        nodeIndexById.push(_d.id);
                        GexfJS.graph.indexOfLabels.push(_d.l.toLowerCase());
                    });
                    GexfJS.graph.sortedNodeList = [...GexfJS.graph.nodeList];
                    GexfJS.graph.sortedNodeList.sort((a, b) => (parseInt(a.count) < parseInt(b.count)) ? 1 : ((parseInt(b.count) < parseInt(a.count)) ? -1 : 0));

                    $(_edges).each(function() {
                        var _e = $(this),
                            _sid = _e.attr("source"),
                            _six = nodeIndexById.indexOf(_sid),
                            _tid = _e.attr("target"),
                            _tix = nodeIndexById.indexOf(_tid),
                            _w = _e.find('attvalue[for="weight"]').attr('value') || _e.attr('weight'),
                            _col = _e.find("viz\\:color,color"),
                            _directed = GexfJS.graph.directed;
                        if (_e.attr("type") == "directed") {
                            _directed = true;
                        }
                        if (_e.attr("type") == "undirected") {
                            _directed = false;
                        }
                        if (_col.length) {
                            var _r = _col.attr("r"),
                                _g = _col.attr("g"),
                                _b = _col.attr("b");
                        } else {
                            var _scol = GexfJS.graph.nodeList[_six].rgb;
                            if (_directed) {
                                var _r = _scol[0],
                                    _g = _scol[1],
                                    _b = _scol[2];
                            } else {
                                var _tcol = GexfJS.graph.nodeList[_tix].rgb,
                                    _r = Math.floor(.5 * _scol[0] + .5 * _tcol[0]),
                                    _g = Math.floor(.5 * _scol[1] + .5 * _tcol[1]),
                                    _b = Math.floor(.5 * _scol[2] + .5 * _tcol[2]);
                            }
                        }
                        GexfJS.graph.edgeList.push({
                            s: _six,
                            t: _tix,
                            W: Math.max(GexfJS.params.minEdgeWidth, Math.min(GexfJS.params.maxEdgeWidth, (_w || 1))) * _scale,
                            w: parseFloat(_w || "1"),
                            C: "rgba(" + _r + "," + _g + "," + _b + ",.6)",
                            Ct: "rgba(" + _r + "," + _g + "," + _b + ",.15)",
                            l: _e.attr("label") || "",
                            d: _directed
                        });
                    });
                }
                GexfJS.graph.edgeList.sort((a, b) => (a.w < b.w) ? 1 : ((b.w < a.w) ? -1 : 0));
                measureTime("Pre-processing graph");

                /*GexfJS.ctxMini.clearRect(0, 0, GexfJS.overviewWidth, GexfJS.overviewHeight);

                GexfJS.graph.nodeList.forEach(function(_d) {
                    GexfJS.ctxMini.fillStyle = _d.B;
                    GexfJS.ctxMini.beginPath();
                    GexfJS.ctxMini.arc(_d.x * GexfJS.overviewScale, _d.y * GexfJS.overviewScale, _d.r * GexfJS.overviewScale + 1, 0, Math.PI * 2, true);
                    GexfJS.ctxMini.closePath();
                    GexfJS.ctxMini.fill();
                });

                GexfJS.imageMini = GexfJS.ctxMini.getImageData(0, 0, GexfJS.overviewWidth, GexfJS.overviewHeight);*/

            }
        });
    }

    function getNodeFromPos(_coords) {
        for (var i = GexfJS.graph.nodeList.length - 1; i >= 0; i--) {
            var _d = GexfJS.graph.nodeList[i];
            if (_d.visible && _d.withinFrame) {
                var _c = _d.actual_coords;
                _r = Math.sqrt(Math.pow(_c.x - _coords.x, 2) + Math.pow(_c.y - _coords.y, 2));
                if (_r < _c.r) {
                    return i;
                }
            }
        }
        return -1;
    }

    function calcCoord(x, y, coord) {
        var _r = Math.sqrt(Math.pow(coord.x - x, 2) + Math.pow(coord.y - y, 2));
        if (_r < GexfJS.lensRadius) {
            var _cos = (coord.x - x) / _r;
            var _sin = (coord.y - y) / _r;
            var _newr = GexfJS.lensRadius * Math.pow(_r / GexfJS.lensRadius, GexfJS.lensGamma);
            var _coeff = (GexfJS.lensGamma * Math.pow((_r + 1) / GexfJS.lensRadius, GexfJS.lensGamma - 1));
            return {
                "x": x + _newr * _cos,
                "y": y + _newr * _sin,
                "r": _coeff * coord.r
            };
        } else {
            return coord;
        }
    }

    function findAngle(sx, sy, ex, ey) {
        var tmp = Math.atan((ey - sy) / (ex - sx));
        if (ex - sx >= 0) {
            return tmp
        } else {
            return tmp + Math.PI
        }
    }

    function drawArrowhead(ctx, locx, locy, angle, sizex, sizey) {
        var tmp = ctx.lineWidth;
        var hx = sizex / 2;
        var hy = sizey / 2;
        ctx.translate((locx), (locy));
        ctx.rotate(angle);
        ctx.translate(-hx, -hy);
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(0, 1 * sizey);
        ctx.lineTo(1 * sizex, 1 * hy);
        ctx.closePath();
        ctx.fillStyle = "#424242";
        ctx.fill();
        ctx.stroke();
        ctx.translate(hx, hy);
        ctx.rotate(-angle);
        ctx.translate(-locx, -locy);
        ctx.lineWidth = tmp;
    }

    function traceArc(ctx, source, target, arrow_size, draw_arrow) {
        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        if (GexfJS.params.curvedEdges) {
            var x2, y2, x3, y3, x4, y4, x5, y5;
            x2 = source.x;
            y2 = source.y;
            if ((source.x == target.x) && (source.y == target.y)) {
                x3 = source.x + 2.8 * source.r;
                y3 = source.y - source.r;
                x4 = source.x;
                y4 = source.y + 2.8 * source.r;
                x5 = source.x + 1;
                y5 = source.y;
            } else {
                x3 = .3 * target.y - .3 * source.y + .8 * source.x + .2 * target.x;
                y3 = .8 * source.y + .2 * target.y - .3 * target.x + .3 * source.x;
                x4 = .3 * target.y - .3 * source.y + .2 * source.x + .8 * target.x;
                y4 = .2 * source.y + .8 * target.y - .3 * target.x + .3 * source.x;
                x5 = target.x;
                y5 = target.y;
            }
            ctx.bezierCurveTo(x3, y3, x4, y4, x5, y5);
            ctx.stroke();
            if (draw_arrow) {
                // Find the middle of the bezierCurve
                var tmp = Math.pow(0.5, 3)
                var x_middle = tmp * (x2 + 3 * x3 + 3 * x4 + x5)
                var y_middle = tmp * (y2 + 3 * y3 + 3 * y4 + y5)
                    // Find the angle of the bezierCurve at the middle point
                var tmp = Math.pow(0.5, 2)
                var x_prime_middle = 3 * tmp * (-x2 - x3 + x4 + x5)
                var y_prime_middle = 3 * tmp * (-y2 - y3 + y4 + y5)
                drawArrowhead(ctx, x_middle, y_middle, findAngle(0, 0, x_prime_middle, y_prime_middle), arrow_size, arrow_size);
            }
        } else {
            ctx.lineTo(target.x, target.y);
            ctx.stroke();
            if (draw_arrow) {
                drawArrowhead(ctx, (source.x + target.x) / 2, (source.y + target.y) / 2, findAngle(source.x, source.y, target.x, target.y), GexfJS.overviewScale * arrow_size, GexfJS.overviewScale * arrow_size);
                ctx.stroke();
            }
        }
    }

    function traceMap() {
        updateWorkspaceBounds();
        if (!GexfJS.graph) {
            return;
        }
        var _identical = GexfJS.areParamsIdentical;
        GexfJS.params.mousePosition = (GexfJS.params.useLens ? (GexfJS.mousePosition ? (GexfJS.mousePosition.x + "," + GexfJS.mousePosition.y) : "out") : null);
        for (var i in GexfJS.params) {
            _identical = _identical && (GexfJS.params[i] == GexfJS.oldParams[i]);
        }
        if (_identical) {
            return;
        }
        for (var i in GexfJS.params) {
            GexfJS.oldParams[i] = GexfJS.params[i];
        }

        GexfJS.globalScale = Math.pow(Math.SQRT2, GexfJS.params.zoomLevel);
        GexfJS.decalageX = (GexfJS.graphZone.width / 2) - (GexfJS.params.centreX * GexfJS.globalScale);
        GexfJS.decalageY = (GexfJS.graphZone.height / 2) - (GexfJS.params.centreY * GexfJS.globalScale);

        var _sizeFactor = GexfJS.globalScale * Math.pow(GexfJS.globalScale, -.15),
            _edgeSizeFactor = _sizeFactor * GexfJS.params.edgeWidthFactor,
            _nodeSizeFactor = _sizeFactor * GexfJS.params.nodeSizeFactor,
            _textSizeFactor = GexfJS.params.fontSizeFactor || 1;

        GexfJS.ctxGraphe.clearRect(0, 0, GexfJS.graphZone.width, GexfJS.graphZone.height);

        if (GexfJS.params.useLens && GexfJS.mousePosition) {
            GexfJS.ctxGraphe.fillStyle = "rgba(220,220,250,0.1)";
            GexfJS.ctxGraphe.beginPath();
            GexfJS.ctxGraphe.arc(GexfJS.mousePosition.x, GexfJS.mousePosition.y, GexfJS.lensRadius, 0, Math.PI * 2, true);
            GexfJS.ctxGraphe.closePath();
            GexfJS.ctxGraphe.fill();
        }

        var _centralNode = ((GexfJS.params.activeNode != -1) ? GexfJS.params.activeNode : GexfJS.params.currentNode);

        for (var i in GexfJS.graph.nodeList) {
            var _d = GexfJS.graph.nodeList[i];
            _d.actual_coords = {
                x: GexfJS.globalScale * _d.x + GexfJS.decalageX,
                y: GexfJS.globalScale * _d.y + GexfJS.decalageY,
                r: _nodeSizeFactor * _d.r
            };
            _d.withinFrame = ((_d.actual_coords.x + _d.actual_coords.r > 0) && (_d.actual_coords.x - _d.actual_coords.r < GexfJS.graphZone.width) && (_d.actual_coords.y + _d.actual_coords.r > 0) && (_d.actual_coords.y - _d.actual_coords.r < GexfJS.graphZone.height));
            _d.visible = (GexfJS.params.currentNode == -1 || i == _centralNode); //  || GexfJS.params.showEdges  --  focus?
        }

        var _tagsMisEnValeur = [];

        if (_centralNode != -1) {
            _tagsMisEnValeur = [_centralNode];
        }

        if (!GexfJS.params.isMoving && (GexfJS.params.showEdges || _centralNode != -1)) {

            var _showAllEdges = (GexfJS.params.showEdges && GexfJS.params.currentNode == -1);

            for (var i in GexfJS.graph.edgeList) {
                var _d = GexfJS.graph.edgeList[i],
                    _six = _d.s,
                    _tix = _d.t,
                    _ds = GexfJS.graph.nodeList[_six],
                    _dt = GexfJS.graph.nodeList[_tix];
                var _isLinked = false;
                if (_centralNode != -1) {
                    if (_six == _centralNode) {
                        _tagsMisEnValeur.push(_tix);
                        _coulTag = _dt.B;
                        _isLinked = true;
                        _dt.visible = true;
                    }
                    if (_tix == _centralNode) {
                        _tagsMisEnValeur.push(_six);
                        _coulTag = _ds.B;
                        _isLinked = true;
                        _ds.visible = true;
                    }
                }

                if ((_isLinked || _showAllEdges) && (_ds.withinFrame || _dt.withinFrame) && _ds.visible && _dt.visible) {
                    GexfJS.ctxGraphe.lineWidth = _edgeSizeFactor * _d.W;
                    var _coords = ((GexfJS.params.useLens && GexfJS.mousePosition) ? calcCoord(GexfJS.mousePosition.x, GexfJS.mousePosition.y, _ds.actual_coords) : _ds.actual_coords);
                    _coordt = ((GexfJS.params.useLens && GexfJS.mousePosition) ? calcCoord(GexfJS.mousePosition.x, GexfJS.mousePosition.y, _dt.actual_coords) : _dt.actual_coords);
                    //GexfJS.ctxGraphe.strokeStyle = (_isLinked ? _d.C : "rgba(100,100,100,0.2)");
                    GexfJS.ctxGraphe.strokeStyle = (_isLinked ? _d.C : _d.Ct);
                    traceArc(GexfJS.ctxGraphe, _coords, _coordt, _sizeFactor * 3.5, GexfJS.params.showEdgeArrow && _d.d);
                }
            }

        }

        GexfJS.ctxGraphe.lineWidth = 4;
        GexfJS.ctxGraphe.strokeStyle = "rgba(0,100,0,0.8)";

        if (_centralNode != -1) {
            var _dnc = GexfJS.graph.nodeList[_centralNode];
            _dnc.real_coords = ((GexfJS.params.useLens && GexfJS.mousePosition) ? calcCoord(GexfJS.mousePosition.x, GexfJS.mousePosition.y, _dnc.actual_coords) : _dnc.actual_coords);
        }

        for (var i in GexfJS.graph.nodeList) {
            var _d = GexfJS.graph.nodeList[i];
            if (_d.visible && _d.withinFrame) {
                if (i != _centralNode) {
                    _d.real_coords = ((GexfJS.params.useLens && GexfJS.mousePosition) ? calcCoord(GexfJS.mousePosition.x, GexfJS.mousePosition.y, _d.actual_coords) : _d.actual_coords);
                    _d.isTag = (_tagsMisEnValeur.indexOf(parseInt(i)) != -1);
                    GexfJS.ctxGraphe.beginPath();
                    GexfJS.ctxGraphe.fillStyle = ((_tagsMisEnValeur.length && !_d.isTag) ? _d.G : _d.B);
                    GexfJS.ctxGraphe.arc(_d.real_coords.x, _d.real_coords.y, _d.real_coords.r, 0, Math.PI * 2, true);
                    GexfJS.ctxGraphe.closePath();
                    GexfJS.ctxGraphe.fill();
                }
            }
        }

        for (var i in GexfJS.graph.nodeList) {
            var _d = GexfJS.graph.nodeList[i];
            if (_d.visible && _d.withinFrame) {
                if (i != _centralNode) {
                    var _fs = _d.real_coords.r * _textSizeFactor + 3;
                    if (_d.isTag) {
                        if (_centralNode != -1) {
                            var _dist = Math.sqrt(Math.pow(_d.real_coords.x - _dnc.real_coords.x, 2) + Math.pow(_d.real_coords.y - _dnc.real_coords.y, 2));
                            if (_dist > 80) {
                                _fs = Math.max(GexfJS.params.textDisplayThreshold + 2, _fs);
                            }
                        } else {
                            _fs = Math.max(GexfJS.params.textDisplayThreshold + 2, _fs);
                        }
                    }
                    if (_fs > GexfJS.params.textDisplayThreshold) {
                        GexfJS.ctxGraphe.fillStyle = ((i != GexfJS.params.activeNode) && _tagsMisEnValeur.length && ((!_d.isTag) || (_centralNode != -1)) ? "rgba(171,171,171,0.6)" : "rgba(255,255,255,0.6)");
                        GexfJS.ctxGraphe.font = "bold " + Math.floor(_fs) + "px Segoe UI";
                        GexfJS.ctxGraphe.textAlign = "center";
                        GexfJS.ctxGraphe.textBaseline = "middle";
                        GexfJS.ctxGraphe.lineWidth = Math.floor(_fs * 0.1);
                        GexfJS.ctxGraphe.strokeStyle = ((i != GexfJS.params.activeNode) && _tagsMisEnValeur.length && ((!_d.isTag) || (_centralNode != -1)) ? "rgba(0,0,0,0.2)" : "rgb(0,0,0)");
                        GexfJS.ctxGraphe.strokeText(_d.l, _d.real_coords.x, _d.real_coords.y);
                        GexfJS.ctxGraphe.fillText(_d.l, _d.real_coords.x, _d.real_coords.y);
                    }
                }
            }
        }

        if (_centralNode != -1) {
            GexfJS.ctxGraphe.fillStyle = _dnc.B;
            GexfJS.ctxGraphe.beginPath();
            GexfJS.ctxGraphe.arc(_dnc.real_coords.x, _dnc.real_coords.y, _dnc.real_coords.r, 0, Math.PI * 2, true);
            GexfJS.ctxGraphe.closePath();
            GexfJS.ctxGraphe.fill();
            GexfJS.ctxGraphe.stroke();
            var _fs = Math.max(GexfJS.params.textDisplayThreshold + 2, _dnc.real_coords.r * _textSizeFactor) + 2;
            GexfJS.ctxGraphe.font = "800 " + Math.floor(_fs) + "px Segoe UI";
            GexfJS.ctxGraphe.textAlign = "center";
            GexfJS.ctxGraphe.textBaseline = "middle";
            GexfJS.ctxGraphe.strokeStyle = "rgb(0,0,0)";
            GexfJS.ctxGraphe.lineWidth = Math.floor(_fs * 0.15);
            GexfJS.ctxGraphe.strokeText(_dnc.l, _dnc.real_coords.x, _dnc.real_coords.y);
            GexfJS.ctxGraphe.fillStyle = "rgb(255,255,255)";
            GexfJS.ctxGraphe.fillText(_dnc.l, _dnc.real_coords.x, _dnc.real_coords.y);
        }

        //GexfJS.ctxMini.putImageData(GexfJS.imageMini, 0, 0);
        var _r = GexfJS.overviewScale / GexfJS.globalScale,
            _x = -_r * GexfJS.decalageX,
            _y = -_r * GexfJS.decalageY,
            _w = _r * GexfJS.graphZone.width,
            _h = _r * GexfJS.graphZone.height;

        /*GexfJS.ctxMini.strokeStyle = "rgb(220,0,0)";
        GexfJS.ctxMini.lineWidth = 3;
        GexfJS.ctxMini.fillStyle = "rgba(120,120,120,0.2)";
        GexfJS.ctxMini.beginPath();
        GexfJS.ctxMini.fillRect(_x, _y, _w, _h);
        GexfJS.ctxMini.strokeRect(_x, _y, _w, _h);*/
    }

    function hoverAC() {
        $("#autocomplete li").removeClass("hover");
        $("#liac_" + GexfJS.autoCompletePosition).addClass("hover");
        GexfJS.params.activeNode = GexfJS.graph.indexOfLabels.indexOf($("#liac_" + GexfJS.autoCompletePosition).text().toLowerCase());
    }

    function changePosAC(_n) {
        GexfJS.autoCompletePosition = _n;
        hoverAC();
    }

    function updateAutoComplete(_sender) {
        var _val = $(_sender).val().toLowerCase();
        var _ac = $("#autocomplete");
        var _acContent = $('<ul>');
        if (_val != GexfJS.lastAC || _ac.html() == "") {
            GexfJS.lastAC = _val;
            var _n = 0;
            GexfJS.graph.indexOfLabels.forEach(function(_l, i) {
                if (_n < 30 && _l.search(_val) != -1) {
                    var closure_n = _n;
                    /*$('<li>')
                        .attr("id", "liac_" + _n)
                        .append($('<a>')
                            .mouseover(function() {
                                changePosAC(closure_n);
                            })
                            .click(function() {
                                displayNode(i, true);
                                return false;
                            })
                            .text(GexfJS.graph.nodeList[i].l)
                        )
                        .appendTo(_acContent);*/

                    $('<li>')
                        .attr("id", "liac_" + _n)
                        .mouseover(function() {
                            changePosAC(closure_n);
                        })
                        .click(function() {
                            displayNode(i, true);
                            return false;
                        })
                        .append($('<a>')
                            .text(GexfJS.graph.nodeList[i].l)
                        )
                        .appendTo(_acContent);
                    _n++;
                }
            });
            GexfJS.autoCompletePosition = 0;
            /*_ac.html(
                $('<div>').append(
                    $('<h4>').text(strLang("nodes"))
                ).append(_acContent)
            );*/

            _ac.html($('<div>').append(_acContent));
        }
        hoverAC();
        _ac.show();
    }

    function updateButtonStates() {
        $("#lensButton").attr("class", GexfJS.params.useLens ? "" : "off")
            .attr("title", strLang(GexfJS.params.useLens ? "lensOff" : "lensOn"));

        $("#edgesButton").attr("class", GexfJS.params.showEdges ? "" : "off")
            .attr("title", strLang(GexfJS.params.showEdges ? "edgeOff" : "edgeOn"));

        $("#infoButton").attr("class", GexfJS.params.showInfo ? "off" : "")
            .attr("title", strLang(GexfJS.params.showInfo ? "infoOff" : "infoOn"));

        $("#listButton").attr("class", GexfJS.params.showList ? "off" : "")
            .attr("title", strLang(GexfJS.params.showList ? "listOff" : "listOn"));
    }

    function updateInfoPanel() {
        $("#infoPanel").attr("class", GexfJS.params.showInfo ? "" : "off");
        $("#listPanel").attr("class", (GexfJS.params.showList && GexfJS.params.currentNode != -1) ? "" : "off");
    }

    GexfJS.setParams = function setParams(paramlist) {
        for (var i in paramlist) {
            GexfJS.params[i] = paramlist[i];
        }
    }

    $(document).ready(function() {
        var lang = (
            typeof GexfJS.params.language != "undefined" && GexfJS.params.language ?
            GexfJS.params.language :
            (
                navigator.language ?
                navigator.language.substr(0, 2).toLowerCase() :
                (
                    navigator.userLanguage ?
                    navigator.userLanguage.substr(0, 2).toLowerCase() :
                    "en"
                )
            )
        );
        GexfJS.lang = (GexfJS.i18n[lang] ? lang : "en");

        let version;
        switch ($.QueryString.v ?? '202312-202403') {
            default:
                // version = '202312-202403';
                // GexfJS.setParams({
                //     centreY: 560,
                //     maxEdgeWidth: 90,
                //     ref: "from DEC 01 2023 to MAR 31 2024"
                // });
                break;

            case '202312-202403':
                version = '202312-202403';
                GexfJS.setParams({
                    centreY: 560,
                    maxEdgeWidth: 90,
                    ref: "from DEC 01 2023 to MAR 31 2024"
                });
                break;

            case '202404-202406':
                version = '202404-202406';
                GexfJS.setParams({
                    centreY: 400,
                    maxEdgeWidth: 130,
                    ref: "from Apr 01 2024 to Jun 31 2024"
                });
                break;

            case '202407':
                version = '202407';
                GexfJS.setParams({
                    centreY: 400,
                    maxEdgeWidth: 250,
                    ref: "from Jul 1 2024 to Jul 31 2024"
                });
                break;

            case '202403':
                version = '202403';
                GexfJS.setParams({
                    centreY: 400,
                    maxEdgeWidth: 200,
                    ref: "from FEB 1 2024 to FEB 29 2024"
                });
                break;

            case '202402':
                version = '202402';
                GexfJS.setParams({
                    centreY: 150,
                    maxEdgeWidth: 200,
                    ref: "from FEB 1 2024 to FEB 29 2024"
                });
                break;

            case '202401':
                version = '202401';
                GexfJS.setParams({
                    centreY: 200,
                    maxEdgeWidth: 150,
                    ref: "from GEN 01 2024 to GEN 31 2024"
                });
                break;

            case '202312':
                version = '202312';
                GexfJS.setParams({
                    centreY: 300,
                    maxEdgeWidth: 200,
                    ref: "from DEC 01 2023 to DEC 31 2023"
                });
                break;

            case '2022':
                version = '2022';
                GexfJS.setParams({
                    // centreY: 400,
                    // maxEdgeWidth: 600,
                    ref: "dal 03/DIC/2021 al 31/DIC/2021"
                });
                break;
        }
        GexfJS.setParams({
            graphFile: "get_graph_file/" + version + ".gexf",
            version
        });

        updateButtonStates();

        GexfJS.ctxGraphe = document.getElementById('carte').getContext('2d');
        updateWorkspaceBounds();

        initializeMap();

        window.onhashchange = initializeMap;

        $(".expand-button").click(() => {
            $(".expand-button").toggleClass('active');
            $("#timeline--container").toggleClass('hidden');
        });
        $(`.step[data-ref=${GexfJS.params.version}]`).addClass('active');
        $("#searchinput")
            .keyup(function(evt) {
                updateAutoComplete(this);
            }).keydown(function(evt) {
                var _l = $("#autocomplete li").length;
                switch (evt.keyCode) {
                    case 40:
                        if (GexfJS.autoCompletePosition < _l - 1) {
                            GexfJS.autoCompletePosition++;
                        } else {
                            GexfJS.autoCompletePosition = 0;
                        }
                        break;
                    case 38:
                        if (GexfJS.autoCompletePosition > 0) {
                            GexfJS.autoCompletePosition--;
                        } else {
                            GexfJS.autoCompletePosition = _l - 1;
                        }
                        break;
                    case 27:
                        $("#autocomplete").slideUp();
                        break;
                    case 13:
                        if ($("#autocomplete").is(":visible")) {
                            var _liac = $("#liac_" + GexfJS.autoCompletePosition);
                            if (_liac.length) {
                                $(this).val(_liac.text());
                            }
                        }
                        break;
                    default:
                        GexfJS.autoCompletePosition = 0;
                        break;
                }
                updateAutoComplete(this);
                if (evt.keyCode == 38 || evt.keyCode == 40) {
                    return false;
                }
            });
        $("#recherche").submit(function() {
            if (GexfJS.graph) {
                displayNode(GexfJS.graph.indexOfLabels.indexOf($("#searchinput").val().toLowerCase()), true);
            }
            return false;
        });
        $("#carte")
            .mousemove(onGraphMove)
            .bind('touchmove', onGraphDrag)
            .click(onGraphClick)
            .bind('touchend', onGraphClick)
            .mousedown(startMove)
            .bind('touchstart', onTouchStart)
            .mouseout(function() {
                GexfJS.mousePosition = null;
                endMove();
            })
            .bind('touchend', function() {
                GexfJS.mousePosition = null;
                onTouchEnd();
            })
            .mousewheel(onGraphScroll);
        $("#overview")
            .mousemove(onOverviewMove)
            .bind('touchmove', onOverviewDrag)
            .mousedown(startMove)
            .bind('touchstart', onTouchStart)
            .mouseup(endMove)
            .bind('touchend', onTouchEnd)
            .mouseout(endMove)
            .mousewheel(onGraphScroll);
        $("#zoomMinusButton").click(function() {
                GexfJS.params.zoomLevel = Math.max(GexfJS.minZoom, GexfJS.params.zoomLevel - 1);
                $("#zoomSlider").slider("value", GexfJS.params.zoomLevel);
                return false;
            })
            .attr("title", strLang("zoomOut"));
        $("#zoomPlusButton").click(function() {
                GexfJS.params.zoomLevel = Math.min(GexfJS.maxZoom, GexfJS.params.zoomLevel + 1);
                $("#zoomSlider").slider("value", GexfJS.params.zoomLevel);
                return false;
            })
            .attr("title", strLang("zoomIn"));
        $(document).click(function(evt) {
            $("#autocomplete").slideUp();
        });
        $("#autocomplete").css({
            top: ($("#searchinput").offset().top) + "px",
            left: ($("#searchinput").offset().left + $("#searchinput").outerWidth() + 22) + "px"
        });
        if (GexfJS.params.useLens === null) {
            $("#lensButton").hide();
        }
        if (GexfJS.params.showEdges === null) {
            $("#edgesButton").hide();
        }
        if (GexfJS.params.showInfo === null) {
            $("#infoButton").hide();
        }
        if (GexfJS.params.showList === null) {
            $("#listButton").hide();
        }
        $("#lensButton").click(function() {
            GexfJS.params.useLens = !GexfJS.params.useLens;
            updateButtonStates();
            return false;
        });
        $("#edgesButton").click(function() {
            GexfJS.params.showEdges = !GexfJS.params.showEdges;
            updateButtonStates();
            return false;
        });
        $("#infoButton").click(function() {
            GexfJS.params.showInfo = !GexfJS.params.showInfo;
            if (GexfJS.params.showList) GexfJS.params.showList = false;
            updateButtonStates();
            updateInfoPanel();
            return false;
        });
        $("#listButton").click(function() {
            GexfJS.params.showList = !GexfJS.params.showList;
            if (GexfJS.params.showInfo) GexfJS.params.showInfo = false;
            updateButtonStates();
            updateInfoPanel();
            return false;
        });
        $("#aUnfold").click(function() {
            var _cG = $("#leftcolumn");
            if (_cG.offset().left < 0) {
                _cG.animate({
                    "left": "0px"
                }, function() {
                    $("#aUnfold").attr("class", "leftarrow");
                    $("#zonecentre").css({
                        left: _cG.width() + "px"
                    });
                });
            } else {
                _cG.animate({
                    "left": "-" + _cG.width() + "px"
                }, function() {
                    $("#aUnfold").attr("class", "rightarrow");
                    $("#zonecentre").css({
                        left: "0"
                    });
                });
            }
            return false;
        });
        $("#comm").append(
            $("<p>").text(GexfJS.params.community)
        );
        $("#ref").append(
            $("<p>").text(GexfJS.params.ref)
        );
    });

    GexfJS.benchmark = function(iteration_count) {
        iteration_count = iteration_count || 10;
        measureTime(iteration_count + " iterations of traceMap()");
        for (var i = 0; i < iteration_count; i++) {
            GexfJS.params.benchmark_iteration = i;
            traceMap();
        }
        measureTime(iteration_count + " iterations of traceMap()");
    }

    window.GexfJS = GexfJS;
})();