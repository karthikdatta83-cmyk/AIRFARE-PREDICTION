const API_URL = "https://airfare-prediction-1.onrender.com";

const form = document.getElementById("flightForm");
const result = document.getElementById("result");
const predictButton = document.getElementById("predictButton");

const airlineSelect = document.getElementById("Airline");
const sourceSelect = document.getElementById("Source");
const destinationSelect = document.getElementById("Destination");
const routeSelect = document.getElementById("Route");
const infoSelect = document.getElementById("Additional_Info");
const stopsSelect = document.getElementById("Total_Stops");

let routeData = [];


// ======================================
// 1. POPULATE DROPDOWN
// ======================================

function populateDropdown(element, values, placeholder) {

    element.innerHTML = "";

    const firstOption = document.createElement("option");

    firstOption.value = "";
    firstOption.textContent = placeholder;

    element.appendChild(firstOption);

    values.forEach(value => {

        const option = document.createElement("option");

        option.value = value;
        option.textContent = value;

        element.appendChild(option);

    });

}


// ======================================
// 2. LOAD OPTIONS FROM BACKEND
// ======================================

async function loadOptions() {

    try {

        result.textContent = "Loading flight options...";

        predictButton.disabled = true;

        const response = await fetch(`${API_URL}/options`);

        if (!response.ok) {

            throw new Error("Unable to load flight options.");

        }

        const options = await response.json();

        routeData = options.routes;

        // Airline dropdown

        populateDropdown(
            airlineSelect,
            options.airlines,
            "Select Airline"
        );

        // Source dropdown

        populateDropdown(
            sourceSelect,
            options.sources,
            "Select Source"
        );

        // Additional information dropdown

        populateDropdown(
            infoSelect,
            options.additional_info,
            "Select Additional Information"
        );

        // Default additional info
        if (options.additional_info.includes("No info")) {
            infoSelect.value = "No info";
        }

        // Default airline
        if (options.airlines.includes("IndiGo")) {
            airlineSelect.value = "IndiGo";
        }

        // Default source
        if (options.sources.includes("Delhi")) {
            sourceSelect.value = "Delhi";
        }

        updateDestinations();
        result.textContent = "";
    }
    catch (error) {
        result.textContent = "Error loading dropdowns: " + error.message;
    }
    finally {
        predictButton.disabled = false;
    }
}


// ======================================
// 3. UPDATE DESTINATION DROPDOWN
// ======================================

function updateDestinations() {
    const source = sourceSelect.value;
    const availableRoutes = routeData.filter(item => item.source === source);

    const destinations = [
        ...new Set(availableRoutes.map(item => item.destination))
    ];

    populateDropdown(
        destinationSelect,
        destinations,
        "Select Destination"
    );

    routeSelect.innerHTML = '<option value="">Select Route</option>';
    stopsSelect.innerHTML = '<option value="">Select Route First</option>';

    // Select first destination by default
    if (destinations.length > 0) {
        destinationSelect.value = destinations[0];
    }

    updateRoutes();
}


// ======================================
// 4. UPDATE ROUTE DROPDOWN
// ======================================

function updateRoutes() {

    const source = sourceSelect.value;

    const destination = destinationSelect.value;

    const matchingRoutes = routeData.filter(item =>

        item.source === source &&
        item.destination === destination

    );

    routeSelect.innerHTML =
        '<option value="">Select Route</option>';

    matchingRoutes.forEach(item => {

        const option = document.createElement("option");

        option.value = item.route;

        option.textContent = item.route;

        routeSelect.appendChild(option);

    });

    stopsSelect.innerHTML =
        '<option value="">Select Route First</option>';

    // Automatically select first available route

    if (matchingRoutes.length > 0) {

        routeSelect.value = matchingRoutes[0].route;

        updateStops();

    }

}


// ======================================
// 5. UPDATE TOTAL STOPS
// ======================================

function updateStops() {

    const selectedRoute = routeSelect.value;

    const selected = routeData.find(item =>

        item.source === sourceSelect.value &&
        item.destination === destinationSelect.value &&
        item.route === selectedRoute

    );

    stopsSelect.innerHTML = "";

    if (!selected) {

        stopsSelect.innerHTML =
            '<option value="">Select Route First</option>';

        return;

    }

    const option = document.createElement("option");

    option.value = selected.stops;

    option.textContent = selected.stops === 0
        ? "Non-stop"
        : selected.stops + (
            selected.stops === 1 ? " Stop" : " Stops"
        );

    stopsSelect.appendChild(option);

    stopsSelect.value = String(selected.stops);

}


// ======================================
// 6. DROPDOWN EVENT LISTENERS
// ======================================

sourceSelect.addEventListener("change", function() {

    updateDestinations();

});

destinationSelect.addEventListener("change", function() {

    updateRoutes();

});

routeSelect.addEventListener("change", function() {

    updateStops();

});


// ======================================
// 7. PREDICT FARE
// ======================================

form.addEventListener("submit", async function(event) {

    event.preventDefault();

    if (!routeSelect.value || stopsSelect.value === "") {
        result.textContent = "Please select a valid route first.";
        return;
    }

    const data = {

        Airline: airlineSelect.value,

        Source: sourceSelect.value,

        Destination: destinationSelect.value,

        Route: routeSelect.value,

        Additional_Info: infoSelect.value,

        Duration: Number(
            document.getElementById("Duration").value
        ),

        Total_Stops: Number(stopsSelect.value),

        Journey_Day: Number(
            document.getElementById("Journey_Day").value
        ),

        Journey_Month: Number(
            document.getElementById("Journey_Month").value
        ),

        Dep_Hour: Number(
            document.getElementById("Dep_Hour").value
        ),

        Dep_Minute: Number(
            document.getElementById("Dep_Minute").value
        ),

        Arrival_Hour: Number(
            document.getElementById("Arrival_Hour").value
        ),

        Arrival_Minute: Number(
            document.getElementById("Arrival_Minute").value
        )

    };

    result.textContent = "Predicting airfare...";

    predictButton.disabled = true;

    try {

        const response = await fetch(`${API_URL}/predict`, {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify(data)

        });

        const output = await response.json();

        if (!response.ok) {

            const message = Array.isArray(output.detail)

                ? output.detail.map(error => error.msg).join(", ")

                : output.detail || "Prediction failed.";

            throw new Error(message);

        }

        result.innerHTML =

            "<h2>Predicted Airfare</h2>" +

            "<h1>" + output.formatted_fare + "</h1>";

    }

    catch(error) {

        result.textContent = "Error: " + error.message;

    }

    finally {

        predictButton.disabled = false;

    }

});


// ======================================
// 8. INITIALIZE
// ======================================

loadOptions();
