let map;
let userMarker;


// Initialize map

function initializeMap() {

    map = L.map("map").setView(
        [20.5937, 78.9629],
        5
    );


    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            attribution:
                '&copy; OpenStreetMap contributors'
        }
    ).addTo(map);


    // Default marker

    L.marker([13.0827, 80.2707])
        .addTo(map)
        .bindPopup(
            "<b>Demo Activity</b><br>Chennai, India"
        )
        .openPopup();

}


// Show authorized user location

function showUserLocation(latitude, longitude) {

    if (!map) {
        return;
    }


    if (userMarker) {

        map.removeLayer(userMarker);

    }


    userMarker = L.marker(
        [latitude, longitude]
    )
        .addTo(map)
        .bindPopup(
            "<b>Your Authorized Location</b><br>" +
            latitude.toFixed(5) +
            ", " +
            longitude.toFixed(5)
        )
        .openPopup();


    map.setView(
        [latitude, longitude],
        13
    );

}