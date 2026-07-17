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

    const response = await fetch("/api/v1/schools");
    const schools = await response.json();

    for (const school of schools) {

        const marker = L.marker([
            school.latitude,
            school.longitude
        ]);

        marker.school = school;

        marker.bindPopup(
            `<b>${school.name}</b>`
        );

        markers.push(marker);

    }

    refreshMarkers();

}


/**CES,Central/Community School
EEC,Environmental Education Centre
IS,Infants School
OTHER,Other School
PS,Primary School
SSP,School for Specific Purposes
HS,Secondary School
**/


function refreshMarkers() {

    cluster.clearLayers();

    const filters = {
        IS: document.getElementById("showInfant").checked,
        PS: document.getElementById("showPrimary").checked,
        HS: document.getElementById("showSecondary").checked,
        CES: document.getElementById("showCentral").checked,
        SSP: document.getElementById("showSpecific").checked,
        EEC: document.getElementById("showEnvironmental").checked,
        OTHER: document.getElementById("showOther").checked,
    };

    for (const marker of markers) {

        if (!filters[marker.school.school_type]) {
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