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

    const dateValue = document.getElementById("Journey_Date").value;
    if (!dateValue) {
        result.textContent = "Please select a journey date.";
        return;
    }
    const [year, month, day] = dateValue.split("-").map(Number);

    const depHour = Number(document.getElementById("Dep_Hour").value);
    const depMinute = Number(document.getElementById("Dep_Minute").value);
    const arrHour = Number(document.getElementById("Arrival_Hour").value);
    const arrMinute = Number(document.getElementById("Arrival_Minute").value);

    // Automatically calculate duration in minutes from departure and arrival times
    let durationMinutes = (arrHour * 60 + arrMinute) - (depHour * 60 + depMinute);
    if (durationMinutes <= 0) {
        durationMinutes += 24 * 60; // Next-day arrival / overnight flight
    }

    const data = {
        Airline: airlineSelect.value,
        Source: sourceSelect.value,
        Destination: destinationSelect.value,
        Route: routeSelect.value,
        Additional_Info: infoSelect.value,
        Duration: durationMinutes,
        Total_Stops: Number(stopsSelect.value),
        Journey_Day: day,
        Journey_Month: month,
        Dep_Hour: depHour,
        Dep_Minute: depMinute,
        Arrival_Hour: arrHour,
        Arrival_Minute: arrMinute
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

        let comparisonsHtml = "";
        if (output.comparisons && output.comparisons.length > 0) {
            comparisonsHtml = `
                <div style="margin-top: 15px; padding-top: 12px; border-top: 1px solid #ddd; font-size: 13px;">
                    <p style="color: #444; margin-bottom: 8px;"><strong>Other Airlines on this Route:</strong></p>
                    <div style="display: flex; gap: 8px; justify-content: center; flex-wrap: wrap;">
                        ${output.comparisons.map(c => `
                            <span style="background: #f1f5f9; padding: 4px 10px; border-radius: 6px; font-weight: 500; color: #1e293b;">
                                ${c.airline}: ${c.fare}
                            </span>
                        `).join("")}
                    </div>
                </div>
            `;
        }

        result.innerHTML = `
            <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; background: #fafafa; margin-top: 20px; text-align: center;">
                <h3 style="color: #64748b; font-size: 14px; text-transform: uppercase;">Estimated Ticket Fare</h3>
                <h1 style="color: #1d2671; font-size: 36px; margin: 8px 0;">${output.formatted_fare}</h1>
                
                <div style="font-size: 14px; color: #475569; margin: 10px 0;">
                    <span>⏱ Duration: <strong>${output.duration_text || '2h 30m'}</strong></span> &bull; 
                    <span>🏷 Category: <strong>${output.fare_category || 'Economy'}</strong></span>
                </div>

                <div style="background: #e0f2fe; color: #0369a1; padding: 8px 12px; border-radius: 6px; font-size: 13px; font-weight: 500; display: inline-block; margin-top: 5px;">
                    💡 Advice: ${output.booking_advice || 'Fair Price'}
                </div>

                ${comparisonsHtml}
            </div>
        `;

        loadRecentHistory();
    }
    catch(error) {
        result.textContent = "Error: " + error.message;
    }
    finally {
        predictButton.disabled = false;
    }
});


// ======================================
// 8. RECENT HISTORY
// ======================================

async function loadRecentHistory() {
    try {
        const response = await fetch(`${API_URL}/history`);
        if (!response.ok) return;
        const data = await response.json();
        const container = document.getElementById("recentHistory");
        const list = document.getElementById("historyList");

        if (data.history && data.history.length > 0) {
            container.style.display = "block";
            list.innerHTML = data.history.map(item => `
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; font-size: 13px;">
                    <div>
                        <strong>${item.airline}</strong>: ${item.source_city} &rarr; ${item.destination_city}
                    </div>
                    <div style="color: #2563eb; font-weight: bold; font-size: 14px;">
                        ₹${Number(item.predicted_fare).toLocaleString("en-IN")}
                    </div>
                </div>
            `).join("");
        }
    } catch (e) {
        // Silently skip if history unavailable
    }
}


// ======================================
// 9. INITIALIZE
// ======================================

loadOptions();
loadRecentHistory();
