// Create the map
const map = L.map("map").setView([-32.5, 147.0], 6);


// Add the OpenStreetMap tiles
L.tileLayer(
    "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        attribution: "&copy; OpenStreetMap contributors"
    }
).addTo(map);


// Load a school from the API
async function loadSchool(code) {

    const response = await fetch(`/api/v1/school/${code}`);

    const school = await response.json();

    L.marker([school.latitude, school.longitude])
        .addTo(map)
        .bindPopup(
            `<b>${school.name}</b><br>${school.town}`
        )
        .openPopup();

    map.setView(
        [school.latitude, school.longitude],
        15
    );
}

loadSchool(8347);