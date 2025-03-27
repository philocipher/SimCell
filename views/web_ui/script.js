on("ready", function(){
    var PORT = "8010";

    /**
     * @class
     * @param display: the display string
     * @param internal: the internal string, like the VClass string in SUMO
     * @param fringeFactor: initial fringe factor value
     * @param count: initial count value
     */
    function Settings(){
        this.init.apply(this, arguments);
    }

    Settings.prototype = {
        init: function(display, internal, fringeFactor, count, enabled){
            this.internal = internal;

            var node = elem("<div>", {className: "container"});
            var header = elem("<h4>", {textContent: display});
            header.append("<img>", {src: "images/" + internal + ".png"});
            node.append(header);
            this.enable = elem("<input>", {type: "checkbox", checked: enabled});
            node.append(this.enable);

            var options = elem("<div>", {className: "options"});
            var label = elem("<label>", {textContent: "Through Traffic Factor"});
            this.fringeFactor = elem("<input>", {type: "number", min: .5, max: 100, step: .1, value: fringeFactor});
            label.append(this.fringeFactor);
            options.append(label);

            label = elem("<label>", {textContent: "Count", title: "Count per hour per kilometer"});
            this.count = elem("<input>", {type: "number", min: .2, max: 100, step: .1, value: count});
            label.append(this.count);
            options.append(label);

            node.append(options);
            elem("#vehicle-controls").append(node);
        },

        toJSON: function(){
            if(this.enable.checked){
                return {
                    fringeFactor: parseFloat(this.fringeFactor.value),
                    count: parseFloat(this.count.value)
                };
            }
            return null;
        }
    };

    var vehicleClasses = [
        new Settings("Cars", "passenger", 5, 12, true),
        new Settings("Trucks", "truck", 5, 8),
        new Settings("Bus", "bus", 5, 4),
        new Settings("Motorcycles", "motorcycle", 2, 4),
        new Settings("Bicycles", "bicycle", 2, 6),
        new Settings("Pedestrians", "pedestrian", 1, 10),
        new Settings("Trams", "tram", 20, 2),
        new Settings("Urban trains", "rail_urban", 40, 2),
        new Settings("Trains", "rail", 40, 2),
        new Settings("Ships", "ship", 40, 2)
    ];

    function RoadTypes(){
        this.init.apply(this, arguments);
    }

    RoadTypes.prototype = {
        init: function (category, typeList) {
            this.category = category;
            this.typeList = typeList;

            var node = elem("<div>", {className: "container"});
            var header = elem("<h4>", {textContent: category});
            var checkbox = elem("<input>",{type: "checkbox", checked:true, className: "checkAll", id: category.toLowerCase()});
            node.append(header);
            node.append(checkbox);

            var types = elem("<div>", {className: "roadTypes " + category.toLowerCase()});
            var label = elem("<label>");

            for (var i = 0; i < typeList.length; i++) {
                label = elem("<label>", {textContent: typeList[i]});
                let roadTypeId = this.category + "_" + typeList[i]
                this.roadTypeCheck = elem("<input>",{type: "checkbox", checked:true, id: roadTypeId});

                label.append(this.roadTypeCheck);
                types.append(label);
            }

            node.append(types);
            elem("#road-types").append(node);
        },

        getEnabledTypeList: function () {
            var retEnabledTypeList = [];
            for (var j = 0; j < this.typeList.length; j++) {
                var roadTypeId = this.category + "_" + this.typeList[j];
                if (document.getElementById(roadTypeId).checked) {
                    retEnabledTypeList.push(this.typeList[j]);
                    if (this.typeList[j].match(/^(motorway|trunk|primary|secondary|tertiary)$/)) {
                        retEnabledTypeList.push(this.typeList[j] + "_link");
                    }
                }
            }
            return retEnabledTypeList;
        }
    };

    const categories = {};
    categories["Highway"] = ["motorway", "trunk", "primary","secondary", "tertiary", "unclassified", "residential",
        "living_street", "unsurfaced", "service", "raceway", "bus_guideway"];
    categories["Pedestrians"] = ["track", "footway", "pedestrian", "path", "bridleway", "cycleway", "step", "steps",
        "stairs"];              //"Pedestrians" has also the "highway" key in OSM, this will be transformed in startBuild()
    categories["Railway"] = ["preserved", "tram", "subway", "light_rail", "rail", "highspeed", "monorail"];
    categories["Aeroway"] = ["stopway", "parking_position", "taxiway", "taxilane", "runway", "highway_strip"]
    categories["Waterway"] = ["river", "canal"];
    categories["Aerialway"] = ["cable_car", "gondola"];
    categories["Route"] = ["ferry"];

    var roadClasses = [];

    for (const [key, value] of Object.entries(categories)) {
        roadClasses.push(new RoadTypes(key, value));
    }

    var activeTab = null;

    /**
     * @function
     * @param id: the id of the tab to open
     */
    function openTab(id){
        var tab = elems(".tab")[id];
        var side = elem("#side");
        var control = elems(".controls")[id];

        // clicked on the open tab, close everything
        if(activeTab === id){
            side.classList.remove("open");
            control.classList.remove("open");
            tab.classList.remove("open");
            activeTab = null;
        } else {
            // open the side and control
            side.classList.add("open");
            control.classList.add("open");
            tab.classList.add("open");

            // close the other tab, if there is one
            if(activeTab !== null){
                elems(".controls")[activeTab].classList.remove("open");
                elems(".tab")[activeTab].classList.remove("open");
            }

            activeTab = id;
        }
    }

    elems(".tab").forEach(function(tab, index){
        tab.dataset.symbol = tab.textContent;
        tab.on("click", function(){
            openTab(index);
        });
    });

    openTab(0);

    var canvas = elem("canvas");
    var canvasActive = false;
    var canvasRect = [.1, .1, .75, .9];
    var ctx = canvas.getContext("2d");

    /**
     * @function
     * sets the canvas to full page size
     */
    function setCanvasSize(){
        canvas.width = innerWidth;
        canvas.height = innerHeight;
        draw();
    }

    setCanvasSize();
    on("resize", setCanvasSize);

    /**
     * @function
     * draws the rect on the canvas, to select an area
     **/
    function draw(){
        var x0 = canvas.width * canvasRect[0],
            y0 = canvas.height * canvasRect[1],
            x1 = canvas.width * canvasRect[2],
            y1 = canvas.height * canvasRect[3];

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = "#808080";
        ctx.globalAlpha = .5;

        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.clearRect(x0, y0, x1 - x0, y1 - y0);
        
    }

    var mouse = {
        x: 0, // last x coordinate
        y: 0, // last y coordinates
        area: null // if mouse button is down, and in which function; move or resize
    }

    canvas.on("mousedown", function(evt){
        mouse.area = changeMousePointer(evt.clientX, evt.clientY, true);
    });
    canvas.on("mouseup", function(evt){
        mouse.area = null;
        changeMousePointer(evt.clientX, evt.clientY);
    });

    function changeMousePointer(x, y, down){
        var x0 = canvas.width * canvasRect[0],
            y0 = canvas.height * canvasRect[1],
            x1 = canvas.width * canvasRect[2],
            y1 = canvas.height * canvasRect[3];

        var cursor = "", t = 20; //tolerance

        if(lequal(x0 - t, x, x1 + t) && lequal(y0 - t, y, y1 + t)){
            if(lequal(y0 - t, y, y0 + t))
                cursor += "n";
            else if(lequal(y1 - t, y, y1 + t))
                cursor += "s";

            if(lequal(x0 - t, x, x0 + t))
                cursor += "w";
            else if(lequal(x1 - t, x, x1 + t))
                cursor += "e";

            if(cursor) cursor += "-resize";
            else if(mouse.area || down) cursor = "move";
            else cursor = "pointer";
        } else
            cursor = "auto"

        canvas.style.cursor = cursor;
        return cursor.match(/^([nsm])?([we])?/);
    }

    canvas.on("mousemove", function(evt){
        changeMousePointer(evt.clientX, evt.clientY);
        var dx = (evt.clientX - mouse.x) / canvas.width, dy = (evt.clientY - mouse.y) / canvas.height;
        mouse.x = evt.clientX;
        mouse.y = evt.clientY;
        if(mouse.area !== null){
            if(mouse.area[1] == "n"){
                if((canvasRect[1] + dy)<=canvasRect[3]){
                    canvasRect[1] += dy;
                } else if ((canvasRect[1] + dy)>canvasRect[3]){
                    [canvasRect[1], canvasRect[3]] = [canvasRect[3], canvasRect[1]];
                    canvasRect[3] += dy;
                    mouse.area[1] = "s";
                }
            }
            else if(mouse.area[1] == "s"){
                if((canvasRect[3] + dy)>=canvasRect[1]){
                    canvasRect[3] += dy;
                } else if ((canvasRect[3] + dy)<canvasRect[1]){
                    [canvasRect[1], canvasRect[3]] = [canvasRect[3], canvasRect[1]];
                    canvasRect[1] += dy;
                    mouse.area[1] = "n";
                }
            }

            if(mouse.area[2] == "w"){
                if((canvasRect[0] + dx)<=canvasRect[2]){
                    canvasRect[0] += dx;
                } else if ((canvasRect[0] + dx)>canvasRect[2]){
                    [canvasRect[0], canvasRect[2]] = [canvasRect[2], canvasRect[0]];
                    canvasRect[2] += dx;
                    mouse.area[2] = "e";
                }
            }
            else if(mouse.area[2] == "e"){
                if((canvasRect[2] + dx)>=canvasRect[0]){
                    canvasRect[2] += dx;
                } else if ((canvasRect[2] + dx)<canvasRect[0]){
                    [canvasRect[0], canvasRect[2]] = [canvasRect[2], canvasRect[0]];
                    canvasRect[0] += dx;
                    mouse.area[2] = "w";
                }
            }

            if(mouse.area[1] == "m"){
                canvasRect[0] += dx;
                canvasRect[1] += dy;
                canvasRect[2] += dx;
                canvasRect[3] += dy;
            }

            draw();
        }
    });

    /**
     * @function
     * checks if the checkbox is checked and displays the canvas in this case, else not
     **/
    function toggleCanvas(){
        if(canvasToggle.checked){
            canvasActive = true;
            canvas.style.removeProperty("display");
        } else {
            canvasActive = false;
            canvas.style.display = "none";
        }
    }

    var canvasToggle = elem("#canvas-toggle");

    canvasToggle.on("click", toggleCanvas);
    toggleCanvas();

    // function to check or uncheck all checkboxes for a certain roadType
    var checkOrUncheckAll = function() {
        Array.from(document.querySelectorAll(".roadTypes." + this.getAttribute("id") + " input[type=checkbox]")).forEach(el => el.checked = this.checked);
    };

    // listen if a roadType checkbox is selected/unselected
    var roadTypeCheckboxes = document.getElementsByClassName("checkAll");

    Array.from(roadTypeCheckboxes).forEach(function(element) {
        element.addEventListener("click", checkOrUncheckAll);
    });

    // OSM map
    // avoid cross domain resource sharing issues (#3991)
    // (https://gis.stackexchange.com/questions/83953/openlayers-maps-issue-with-ssl)
    var map = new OpenLayers.Map("map");
    var maplayer = new OpenLayers.Layer.OSM("OpenStreetMap",
    // Official OSM tileset as protocol-independent URLs
    [
        'https://tile.openstreetmap.org/${z}/${x}/${y}.png'
    ], null);
    map.addLayer(maplayer);

    function setPosition(lon, lat){
        if(!lon || !lat){
            latLon = elem("#lat_lon").value.split(" ")
            lon = parseFloat(latLon[1]);
            lat = parseFloat(latLon[0]);
        } else {
            elem("#lat_lon").value = lat.toFixed(6) + " " + lon.toFixed(6);
        }

        var leftHandBounds = [new OpenLayers.Bounds(-11,50,1,60), // British Isles
                              new OpenLayers.Bounds(0.774536,50.986099,1.779785,53.146770), // British Isles (part2)
                              new OpenLayers.Bounds(66, 3, 90, 30), // India, Pakistan
                              new OpenLayers.Bounds(95, -45, 179, 2), // Australia, Indonesia
                              new OpenLayers.Bounds(-20, -35, 40, -15), // Southern Africa
                              new OpenLayers.Bounds(135, 30, 150, 42), // Japan
                             ];
        elem("#leftHand").checked = false;
        for (var i = 0; i < leftHandBounds.length; i++) {
            if (leftHandBounds[i].contains(lon, lat)) {
                elem("#leftHand").checked = true;
                break;
            }
        }

        var lonLat = new OpenLayers.LonLat(lon, lat);
        lonLat.transform(
            new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
            map.getProjectionObject() // to Spherical Mercator Projection
        );

        map.setCenter(lonLat, 16);
    }

    function setPositionByString() {
        query = elem("#address").value
        $.ajax({
        url: "https://nominatim.openstreetmap.org/search?q=" + query + "&format=json&polygon=0&addressdetails=0&limit=1&callback",
        cache: false,
        dataType: "json",
            success: function(data) {
                var result = data[0];
                lon = parseFloat(result.lon);
                lat = parseFloat(result.lat);
                setPosition(lon, lat);
            },
            error: function (request, status, err) {
                window.alert('Could not locate address: ' + err);
            }
        });
    }

    elem("#address").on("keyup", function(e){
        if (e.keyCode == 13) {
            setPositionByString();
        }
    });

    var getJSON = function(url, callback) {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);
        xhr.responseType = 'json';
        xhr.onload = function() {
          var status = xhr.status;
          if (status == 200) {
            callback(null, xhr.response);
          } else {
            callback(status);
          }
        };
        xhr.send();
    };


    // set default position to center Irvine, California
    setPosition(-117.84, 33.646);

    
    /**
     * @listener
     * set the coordinates of the map to current coordinates (got from browser)
     */
    elem("#buttonCurrent").on("click", function(){
        if(!navigator.geolocation) return;

        navigator.geolocation.getCurrentPosition(function(position){
            setPosition(position.coords.longitude, position.coords.latitude);
        });
    });

    /**
     * @listener
     * whenever the input boxes changes, update the map coordinates
     */
    elem("#buttonSearch").on("click", setPositionByString);
    elem("#buttonLatLon").on("click", setPosition);

    /**
     * @listener
     * whenever the map coordinates changes, update the input boxes
     */
    map.events.register("move", map, function(){
        var cor = map.getExtent();
        cor.transform(
            map.getProjectionObject(), // from Spherical Mercator Projection
            new OpenLayers.Projection("EPSG:4326")
        );
        lat = (cor.top + (cor.bottom - cor.top) / 2);
        lon = (cor.left + (cor.right - cor.left) / 2);

        elem("#lat_lon").value = lat.toFixed(6) + " " + lon.toFixed(6);
    });


    
    let peerConnection;
    let dataChannel;

    async function setupWebRTC() {
        peerConnection = new RTCPeerConnection();

        dataChannel = peerConnection.createDataChannel("udp_channel");

        dataChannel.onopen = () => {
            console.log("📡 WebRTC data channel open");
        };

        dataChannel.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            switch (msg.type) {
                case "draw_circle":
                    drawIconMarker(msg.lon, msg.lat);
                    break;
                case "place_gnb":
                    console.log(`🚚 Placing gNB ${msg.id} at the position`);
                    placeGnbMarker(msg.id, msg.lon, msg.lat);
                    break;
                case "move_ue":
                    console.log(`🚚 Placing UE ${msg.id} at the position`);
                    placeUeMarker(msg.id, msg.lon, msg.lat);
                    break;
                case "draw_line":
                    drawLine(msg.a_lat, msg.a_lon, msg.b_lat, msg.b_lon, msg.ue_id);
                    break;
                case "add_ue":
                    console.log("🚚 Adding UE", msg);
                    addUEToList({
                        id: msg.id,
                        supi: msg.supi,
                        max_dl: msg.ambr_downlink,
                        max_ul: msg.ambr_uplink
                    });
                    break;
                default:
                    console.warn("⚠️ Unknown JSON message type:", msg.type);
            }
        };

        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);

        // WebSocket for signaling
        const signalingSocket = new WebSocket("ws://localhost:8765");

        signalingSocket.onmessage = async (event) => {
            const message = JSON.parse(event.data);
            if (message.type === "answer") {
                const desc = new RTCSessionDescription(message);
                await peerConnection.setRemoteDescription(desc);
            }
        };

        signalingSocket.onopen = () => {
            signalingSocket.send(JSON.stringify({
                type: "offer",
                sdp: peerConnection.localDescription.sdp
            }));
        };
    }

    setupWebRTC();



    var socket;
    var totalSteps;
    var currentStep;
    var presentedErrorLog = false;

    /**
     * @function
     * connects to the socket, when it fails it tries it again after five seconds
     */
    function connectSocket(){
        var address = location.hostname;
        // when accessing via file, location.hostname is an empty string, so guess that the server is on localhost
        if(!address)
            address = "localhost";
        try {
            socket = new WebSocket("ws://" + address + ":" + PORT);
        } catch(e){
            // connection failed, wait five seconds, then try again
	    setTimeout(connectSocket, 5000);
            return;
        }

	socket.onerror = function(error) {
	    if (presentedErrorLog == false) {
		window.alert("Socket connection failed. Please open the OSM WebWizard by using osmWebWizard.py or the link in your start menu.");
		presentedErrorLog = true;
	    }
	};

        // whenever the socket closes (e.g. restart) try to reconnect
        socket.addEventListener("close", connectSocket);
        socket.onmessage = function(event) {
            console.log("🛰️ Message received from server:", event.data);
            let msg;
    
            // Try to parse the message as JSON
            try {
                msg = JSON.parse(event.data);
    
                // Handle JSON-based protocol
                switch (msg.type) {
                    case "draw_circle":
                        drawIconMarker(msg.lon, msg.lat);
                        break;
                    default:
                        console.warn("⚠️ Unknown JSON message type:", msg.type);
                }
            } catch (e) {
                // Not a JSON message, fall back to plain text protocol
                const message = event.data;
                const index = message.indexOf(" ");
                if (index === -1) return;
    
                const type = message.substr(0, index);
                const content = message.substr(index + 1);
    
                if (type === "zip") {
                    showZip(content);
                } else if (type === "report") {
                    currentStep++;
                    elem("#status > span").textContent = content;
                    elem("#status > div").style.width = (100 * currentStep / totalSteps) + "%";
    
                    if (currentStep === totalSteps) {
                        setTimeout(() => {
                            elem("#status").style.display = "none";
                            elem("#export-button").style.display = "block";
                        }, 2000);
                    }
                } else if (type === "steps") {
                    totalSteps = parseInt(content);
                    currentStep = 0;
                } else {
                    console.warn("⚠️ Unknown plain-text message type:", type);
                }
            }
        };
    }

    connectSocket();


    /**
     * @function
     * generate and send the data to the websocket
     */
    function startBuild(){
        var cor = map.getExtent();
        cor.transform(
            map.getProjectionObject(), // from Spherical Mercator Projection
            new OpenLayers.Projection("EPSG:4326")
        );

        
        console.log("Bounding Box (WGS84):");
        console.log("left (lon):", cor.left.toFixed(6));
        console.log("bottom (lat):", cor.bottom.toFixed(6));
        console.log("right (lon):", cor.right.toFixed(6));
        console.log("top (lat):", cor.top.toFixed(6));


        var data = {
            poly: elem("#polygons").checked,
            duration: parseInt(elem("#duration").value),
            publicTransport: elem("#publicTransport").checked,
            leftHand: elem("#leftHand").checked,
            decal: elem("#decal").checked,
            carOnlyNetwork: elem("#carOnlyNetwork").checked,
            vehicles: {},
            roadTypes:{}                                                            // sab-inf
        };

        // calculates the coordinates of the rectangle if area-picking is active
        if(canvasActive){
            var width = cor.right - cor.left;
            var height = cor.bottom - cor.top;
            data.coords = [
                cor.left + width * canvasRect[0],
                cor.top + height * canvasRect[3],
                cor.left + width * canvasRect[2],
                cor.top + height * canvasRect[1]
            ];
        } else
            data.coords = [cor.left, cor.bottom, cor.right, cor.top];

        vehicleClasses.forEach(function(vehicleClass){
            var result = vehicleClass.toJSON();
            if(result)
                data.vehicles[vehicleClass.internal] = result;
        });

        roadClasses.forEach(function(roadType){
            var result = roadType.getEnabledTypeList();
            if(result){
                // in OSM "pedestrians" have also the key "highway", therefore we prepare the data accordingly
                if(roadType.category == "Pedestrians" || roadType.category == "Highway"){
                    try{
                        data.roadTypes["Highway"] = data.roadTypes["Highway"].concat(result);
                    }catch (e){
                        if (e instanceof TypeError) {
                            data.roadTypes["Highway"] = result;
                        }
                    }
                }else
                    data.roadTypes[roadType.category] = result;
            }
        });

        try {
            socket.send(JSON.stringify(data));
        } catch(e){
            return;
        }

        elem("#status").style.display = "block";
        elem("#export-button").style.display = "none";
    }

    elem("#export-button").on("click", startBuild);

    /**
     * @function
     * @param uri: a base64-encoded string for a zip file
     * shows a download dialog to save the zip file
     */
    function showZip(uri){
        var url = "data:application/zip;base64," + uri;

        // using a temporarily link to trigger the download dialog
        var link = elem("<a>", {
            download: "osm.zip",
            href: url,
            target: "_blank"
        });

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }



    let userEquipments = [];
    let gNBs = [];
    let selectedElement = null;
    
    function renderNetworkList() {
        const ueList = elem("#ue-list");
        const gnbList = elem("#gnb-list");
    
        ueList.innerHTML = "";
        gnbList.innerHTML = "";
    
        userEquipments.forEach((ue, index) => {
            const item = elem("<li>", {
                textContent: `UE ${index + 1}`
            });
    
            if (selectedElement === ue) {
                item.classList.add("selected");
            }
    
            item.on("click", () => {
                selectNetworkElement(ue);
            });
    
            ueList.append(item);
        });
    
        gNBs.forEach((gnb, index) => {
            const item = elem("<li>", {
                textContent: `gNB ${index + 1}`
            });
    
            if (selectedElement === gnb) {
                item.classList.add("selected");
            }
    
            item.on("click", () => {
                selectNetworkElement(gnb);
            });
    
            gnbList.append(item);
        });
    }
    
    function selectNetworkElement(element) {
        selectedElement = element;
        renderNetworkList();
    }
    
    elem("#add-ue").on("click", () => {
        const ue = {
            type: "UE",
            trajectory: [],
            color: "blue"
        };
        userEquipments.push(ue);
        renderNetworkList();
    });
    
    elem("#add-gnb").on("click", () => {
        const gnb = {
            type: "gNB",
            position: [13.4, 52.52], // Replace with real map center later
            color: "red"
        };
        gNBs.push(gnb);
        renderNetworkList();
    });
    


    
    function drawRedCircle(lon, lat) {
        console.log("🔴 drawRedCircle called with lon:", lon, "lat:", lat);

        const centerLonLat = new OpenLayers.LonLat(lon, lat).transform(
            new OpenLayers.Projection("EPSG:4326"),
            map.getProjectionObject()
        );
    
        const circleLayer = new OpenLayers.Layer.Vector("Red Circle Layer");
    
        const circleFeature = new OpenLayers.Feature.Vector(
            new OpenLayers.Geometry.Point(centerLonLat.lon, centerLonLat.lat),
            {},
            {
                pointRadius: 20,
                fillColor: "red",
                fillOpacity: 0.6,
                strokeColor: "darkred",
                strokeWidth: 2
            }
        );
    
        circleLayer.addFeatures([circleFeature]);
        map.addLayer(circleLayer);
    }

    function drawIconMarker(lon, lat) {
        console.log("📍 drawIconMarker with fixed gnb");
    
        const iconUrl = document.getElementById("gnb-icon").src;
    
        const lonLat = new OpenLayers.LonLat(lon, lat).transform(
            new OpenLayers.Projection("EPSG:4326"),
            map.getProjectionObject()
        );
    
        const iconSize = new OpenLayers.Size(32, 32); // adjust if needed
        const iconOffset = new OpenLayers.Pixel(-(iconSize.w / 2), -(iconSize.h / 2));
        const icon = new OpenLayers.Icon(iconUrl, iconSize, iconOffset);
    
        const markerLayer = new OpenLayers.Layer.Markers("gnb Icon Layer");
        const marker = new OpenLayers.Marker(lonLat, icon);
    
        markerLayer.addMarker(marker);
        map.addLayer(markerLayer);
    }


    

    const gnbMarkers = {};
    let gnbLayer = null;
    

    function placeGnbMarker(id, lon, lat) {
        const lonLat = new OpenLayers.LonLat(lon, lat).transform(
            new OpenLayers.Projection("EPSG:4326"),
            map.getProjectionObject()
        );
    
        if (!gnbLayer) {
            gnbLayer = new OpenLayers.Layer.Markers("gNBs");
            map.addLayer(gnbLayer);
        }
    
        if (gnbMarkers[id]) {
            gnbMarkers[id].moveTo(map.getLayerPxFromLonLat(lonLat));
        } else {
            const iconUrl = document.getElementById("gnb-icon").src;
            const iconSize = new OpenLayers.Size(32, 32);
            const iconOffset = new OpenLayers.Pixel(-(iconSize.w / 2), -(iconSize.h / 2));
            const icon = new OpenLayers.Icon(iconUrl, iconSize, iconOffset);
    
            const marker = new OpenLayers.Marker(lonLat, icon);
            gnbLayer.addMarker(marker);
            gnbMarkers[id] = marker;
        }
        gnbLayer.redraw();
    }
    
    let selectedUeId = null;

    const ueIcons = {
        default: new OpenLayers.Icon(document.getElementById("ue-icon").src, new OpenLayers.Size(32, 32), new OpenLayers.Pixel(-16, -16)),
        selected: new OpenLayers.Icon("images/ue_selected.png", new OpenLayers.Size(32, 32), new OpenLayers.Pixel(-16, -16)) // You need this image
    };

    


    const ueMarkers = {};
    let ueLayer = null;
    const ueTrace = {};


    
    function highlightUeOnMap(ueId) {
        if (!ueMarkers[ueId]) return;
    
        // Reset previous selection
        if (selectedUeId && ueMarkers[selectedUeId]) {
            ueMarkers[selectedUeId].setUrl(ueIcons.default.url);
        }
    
        // Highlight current
        ueMarkers[ueId].setUrl(ueIcons.selected.url);
        selectedUeId = ueId;
    }


    function placeUeMarker(id, lon, lat) {
        const lonLat = new OpenLayers.LonLat(lon, lat).transform(
            new OpenLayers.Projection("EPSG:4326"),
            map.getProjectionObject()
        );
    
        if (!ueLayer) {
            ueLayer = new OpenLayers.Layer.Markers("UEs");
            map.addLayer(ueLayer);
        }

        if (!ueTrace[id]) {
            ueTrace[id] = [];
        }
        if (ueMarkers[id]) {
            const prevLonLat = ueMarkers[id].lonlat;
            ueTrace[id].push(prevLonLat); // Save old position
    
            // Add trace marker (dimmed or smaller icon)
            // const traceIcon = new OpenLayers.Icon(
            //     document.getElementById("ue-icon").src,
            //     new OpenLayers.Size(12, 12), // Smaller size
            //     new OpenLayers.Pixel(-6, -6) // Adjust offset
            // );
            // const traceMarker = new OpenLayers.Marker(prevLonLat.clone(), traceIcon);
            // ueLayer.addMarker(traceMarker);
        }

    
        if (ueMarkers[id]) {
            ueMarkers[id].moveTo(map.getLayerPxFromLonLat(lonLat));
            ueMarkers[id].lonlat = lonLat.clone(); // Update for next trace
        } else {
            const iconUrl = document.getElementById("ue-icon").src;
            const iconSize = new OpenLayers.Size(32, 32);
            const iconOffset = new OpenLayers.Pixel(-(iconSize.w / 2), -(iconSize.h / 2));
            const icon = new OpenLayers.Icon(iconUrl, iconSize, iconOffset);
    
            const marker = new OpenLayers.Marker(lonLat, ueIcons.default.clone());
            marker.lonlat = lonLat.clone(); // Store position
            ueLayer.addMarker(marker);
            ueMarkers[id] = marker;
            console.log("🔴 ue called with lon:", lon, "lat:", lat);
        }
        ueLayer.redraw();

    }


    

    const ueLines = {};

    let lineLayer = new OpenLayers.Layer.Vector("UE Lines");
    map.addLayer(lineLayer);
    
    /**
     * Draw a line between a UE and its gNB, replacing the previous one for the same UE.
     * @param {string} ueId - The ID of the UE
     * @param {number} aLat - UE latitude
     * @param {number} aLon - UE longitude
     * @param {number} bLat - gNB latitude
     * @param {number} bLon - gNB longitude
     */
    function drawLine(aLat, aLon, bLat, bLon, ueId) {
        if (ueLines[ueId]) {
            lineLayer.removeFeatures([ueLines[ueId]]);
        }
    
        const aPoint = new OpenLayers.Geometry.Point(aLon, aLat)
            .transform("EPSG:4326", map.getProjectionObject());
        const bPoint = new OpenLayers.Geometry.Point(bLon, bLat)
            .transform("EPSG:4326", map.getProjectionObject());
    
        const line = new OpenLayers.Geometry.LineString([aPoint, bPoint]);
        const feature = new OpenLayers.Feature.Vector(line, null, {
            strokeColor: "#00FF00",  // 💚 GREEN line
            strokeWidth: 2
        });
    
        ueLines[ueId] = feature;
        lineLayer.addFeatures([feature]);
    }
    
    
    let virtualTime = 0;
    const slider = document.getElementById("time-slider");
    const timeLabel = document.getElementById("current-time");
    const playBtn = document.getElementById("play-button");
    const pauseBtn = document.getElementById("pause-button");
    const advanceBtn = document.getElementById("advance-button");
    
    let playing = false;
    let intervalId = null;
    
    function sendTimeUpdate(time) {
        const msg = JSON.stringify({ type: "set_time", value: time });
        console.log("⏰ Sending time update:", msg);
        if (dataChannel && dataChannel.readyState === "open") {
            dataChannel.send(msg);
        }
    }
    
    slider.addEventListener("input", () => {
        virtualTime = parseInt(slider.value);
        timeLabel.textContent = `${virtualTime}s`;
        sendTimeUpdate(virtualTime);
    });
    
    playBtn.addEventListener("click", () => {
        if (playing) return;
        playing = true;
        intervalId = setInterval(() => {
            if (virtualTime < 180) {
                virtualTime++;
                slider.value = virtualTime;
                timeLabel.textContent = `${virtualTime}s`;
                sendTimeUpdate(virtualTime);
            }
        }, 1000);
    });
    
    pauseBtn.addEventListener("click", () => {
        playing = false;
        clearInterval(intervalId);
    });
    
    advanceBtn.addEventListener("click", () => {
        if (virtualTime < 180) {
            virtualTime++;
            slider.value = virtualTime;
            timeLabel.textContent = `${virtualTime}s`;
            sendTimeUpdate(virtualTime);
        }
    });


    function addUEToList({ id, supi, max_dl, max_ul }) {
        const ueList = document.querySelector("#ue-list");
    
        const li = document.createElement("li");
        li.className = "ue-item";
        li.dataset.ueId = id; // important
    
        // Highlight UE when clicked
        li.addEventListener("click", () => {
            highlightUeOnMap(id);
        });
    
        const summary = document.createElement("div");
        summary.className = "ue-summary";
        summary.style.display = "flex";
        summary.style.justifyContent = "space-between";
        summary.style.alignItems = "center";
    
        const label = document.createElement("span");
        label.textContent = `UE ID: ${id}`;
        label.style.flex = "1";
        label.style.whiteSpace = "nowrap";
        label.style.overflow = "hidden";
        label.style.textOverflow = "ellipsis";
    
        const toggleBtn = document.createElement("button");
        toggleBtn.textContent = "▼";
        toggleBtn.style.background = "transparent";
        toggleBtn.style.border = "none";
        toggleBtn.style.color = "#fff";
        toggleBtn.style.cursor = "pointer";
        toggleBtn.style.fontSize = "16px";
        toggleBtn.style.padding = "0";
        toggleBtn.style.marginLeft = "8px";
    
        summary.appendChild(label);
        summary.appendChild(toggleBtn);
        li.appendChild(summary);
    
        const details = document.createElement("div");
        details.className = "ue-details hidden";
        details.style.padding = "6px 10px";
        details.style.fontSize = "0.85em";
        details.style.lineHeight = "1.4";
        details.style.backgroundColor = "#29297a";
        details.style.borderTop = "1px solid #444";
    
        details.innerHTML = `
            <div><strong>SUPI:</strong> ${supi}</div>
            <div><strong>Max DL:</strong> ${max_dl}</div>
            <div><strong>Max UL:</strong> ${max_ul}</div>
        `;
    
        toggleBtn.addEventListener("click", () => {
            details.classList.toggle("hidden");
            toggleBtn.textContent = details.classList.contains("hidden") ? "▼" : "▲";
        });
    
        li.appendChild(details);
        ueList.appendChild(li);
    }
    
    
    
    
    

});

