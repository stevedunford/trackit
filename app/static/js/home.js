// Create the map
const map = L.map("map").setView([-32.5, 147.0], 6);


// Add the OpenStreetMap tiles
L.tileLayer(
    "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        attribution: "&copy; OpenStreetMap contributors"
    }
).addTo(map);


const markers = [];
const cluster = L.markerClusterGroup();

map.addLayer(cluster);


async function loadSchools() {

    const response = await fetch("/api/v1/jobs");
    const jobs = await response.json();

    for (const job of jobs) {

        const marker = L.marker([
            job.latitude,
            job.longitude
        ],

        {
            icon:
                jobIcons[job.school_type]
                ?? jobIcons.OTHER
        }
    );

        marker.school = job;

        marker.bindPopup(
            `<b>${job.name}</b>`
        );

        markers.push(marker);

    }

    refreshMarkers();

}

function createMarker(colour) {

    return new L.Icon({

        iconUrl:
            `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-${colour}.png`,

        shadowUrl:
            "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",

        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]

    });

}


const jobIcons = {
    IS: createMarker("red"),      // pink
    PS: createMarker("gold"),      // green
    HS: createMarker("orange"),      // blue
    CES: createMarker("violet"),      // purple
    SSP: createMarker("orange"),     // orange
    EEC: createMarker("green"),     // dark green
    DIST: createMarker("teal"),    // teal
    OTHER: createMarker("black")
};


function refreshMarkers() {

    cluster.clearLayers();

    const filters = {
        IS: document.getElementById("showInfant").checked,
        PS: document.getElementById("showPrimary").checked,
        HS: document.getElementById("showSecondary").checked,
        CES: document.getElementById("showCentral").checked,
        SSP: document.getElementById("showSpecific").checked,
        EEC: document.getElementById("showEnvironmental").checked,
        DIST: document.getElementById("showDistance").checked,
        OTHER: document.getElementById("showOther").checked,
    };

    for (const marker of markers) {

        const schoolType =
            marker.school.school_type;

        const visible =
            filters[schoolType] ?? filters.OTHER;

        if (!visible) {
            continue;
        }

        cluster.addLayer(marker);

    }

}


loadSchools();

document
    .querySelectorAll(".school-filter")
    .forEach(control =>
        control.addEventListener(
            "change",
            refreshMarkers
        )
    );