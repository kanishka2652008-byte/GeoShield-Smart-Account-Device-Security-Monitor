// ---------------- LOAD EVENTS ----------------

async function loadEvents() {

    try {

        const response =
            await fetch("/api/events");

        const events =
            await response.json();


        const container =
            document.getElementById(
                "events-container"
            );


        if (!events.length) {

            container.innerHTML =
                '<div class="loading">No security events found.</div>';

            return;
        }


        container.innerHTML = "";


        let highRisk = 0;

        let devices = new Set();


        events.forEach(event => {

            if (event.risk === "High") {

                highRisk++;

            }


            devices.add(event.device);


            let riskClass =
                "risk-low";


            if (event.risk === "Medium") {

                riskClass =
                    "risk-medium";

            }


            if (event.risk === "High") {

                riskClass =
                    "risk-high";

            }


            const eventHTML = `

                <div class="event">

                    <div class="event-type">
                        ${event.event_type}
                    </div>

                    <div class="event-info">
                        📍 ${event.location}
                    </div>

                    <div class="event-info">
                        📱 ${event.device}
                    </div>

                    <div class="risk ${riskClass}">
                        ${event.risk}
                    </div>

                    <div class="event-info">
                        ${event.timestamp}
                    </div>

                </div>

            `;


            container.innerHTML += eventHTML;

        });


        // Update statistics

        document.getElementById(
            "eventCount"
        ).textContent = events.length;


        document.getElementById(
            "highRisk"
        ).textContent = highRisk;


        document.getElementById(
            "deviceCount"
        ).textContent = devices.size;


        // Simple security score

        let score =
            100 - (highRisk * 8);


        if (score < 0) {

            score = 0;

        }


        document.getElementById(
            "securityScore"
        ).textContent = score + "%";


    } catch (error) {

        console.error(
            "Error loading events:",
            error
        );

    }

}


// ---------------- DEMO ACTIVITY ----------------

async function generateDemoEvents() {

    try {

        const response =
            await fetch(
                "/api/demo-events",
                {
                    method: "POST"
                }
            );


        const result =
            await response.json();


        if (result.success) {

            alert(
                "3 demo security events generated!"
            );


            loadEvents();

        }

    } catch (error) {

        console.error(error);

        alert(
            "Unable to generate demo activity."
        );

    }

}


// ---------------- LOCATION ----------------

function shareLocation() {

    if (!navigator.geolocation) {

        alert(
            "Geolocation is not supported by this browser."
        );

        return;

    }


    navigator.geolocation.getCurrentPosition(

        async function(position) {

            const latitude =
                position.coords.latitude;

            const longitude =
                position.coords.longitude;


            try {

                const response =
                    await fetch(
                        "/api/location",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                latitude: latitude,
                                longitude: longitude
                            })
                        }
                    );


                const result =
                    await response.json();


                if (result.success) {

                    showUserLocation(
                        latitude,
                        longitude
                    );


                    alert(
                        "Your location was shared successfully."
                    );


                    loadEvents();

                }

            } catch (error) {

                console.error(error);

                alert(
                    "Unable to save location."
                );

            }

        },

        function(error) {

            alert(
                "Location permission was not granted."
            );

        }

    );

}


// ---------------- START ----------------

document.addEventListener(
    "DOMContentLoaded",
    function() {

        initializeMap();

        loadEvents();

    }
);