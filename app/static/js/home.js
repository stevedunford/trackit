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


function refreshMarkers() {

    cluster.clearLayers();

    const showPrimary =
        document.getElementById("showPrimary").checked;

    for (const marker of markers) {

        if (
            !showPrimary &&
            marker.school.school_type === "PS"
        ) {
            continue;
        }

        cluster.addLayer(marker);

    }

}


loadSchools();

document
    .getElementById("showPrimary")
    .addEventListener(
        "change",
        refreshMarkers
    );