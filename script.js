/**
 * SkyFare 2.0 — AI Flight Price Estimator Engine
 * Handles dynamic routing, duration calculation, city pairing, and ML API communication.
 */

// Dedicated FastAPI Prediction Backend URL
const BACKEND_PREDICT_URL = "https://airfare-prediction-1.onrender.com/predict";

function resolveApiUrl() {
    if (window.location.protocol.startsWith("http")) {
        // If served directly from the FastAPI backend (local port 8000 or the backend Render host)
        if (window.location.port === "8000" || window.location.host.includes("airfare-prediction-1")) {
            return `${window.location.origin}/predict`;
        }
    }
    // In all other cases (e.g. airfare-price-estimation-z3wm static site, Live Server port 5500, GitHub Pages)
    // always send prediction requests to the live backend service.
    return BACKEND_PREDICT_URL;
}

let API_URL = resolveApiUrl();

// DOM Elements
const form = document.getElementById("fareForm");
const predictBtn = document.getElementById("predictBtn");
const errorMessage = document.getElementById("errorMessage");
const resultCard = document.getElementById("resultCard");
const predictedFare = document.getElementById("predictedFare");
const fareRangeText = document.getElementById("fareRangeText");
const confidencePill = document.getElementById("confidencePill");
const resultChips = document.getElementById("resultChips");
const resetBtn = document.getElementById("resetBtn");

const airlineInput = document.getElementById("Airline");
const sourceInput = document.getElementById("Source");
const destInput = document.getElementById("Destination");
const routeInput = document.getElementById("Route");
const routeSuggestions = document.getElementById("routeSuggestions");
const stopsInput = document.getElementById("Total_Stops");
const infoInput = document.getElementById("Additional_Info");

const dateInput = document.getElementById("Journey_Date");
const depTimeInput = document.getElementById("Dep_Time");
const arrTimeInput = document.getElementById("Arrival_Time");
const durationInput = document.getElementById("Duration");
const durationBadge = document.getElementById("durationBadge");
const nextDayBadge = document.getElementById("nextDayBadge");

// Hero visual elements
const heroSrcCode = document.getElementById("heroSrcCode");
const heroSrcName = document.getElementById("heroSrcName");
const heroDestCode = document.getElementById("heroDestCode");
const heroDestName = document.getElementById("heroDestName");
const heroRouteText = document.getElementById("heroRouteText");

// Canonical City & Routes Knowledge
const CITY_CODES = {
    "Banglore": "BLR",
    "Chennai": "MAA",
    "Delhi": "DEL",
    "Kolkata": "CCU",
    "Mumbai": "BOM",
    "Cochin": "COK",
    "Hyderabad": "HYD",
    "New Delhi": "DEL"
};

const VALID_PAIRS = {
    "Delhi": ["Cochin"],
    "Banglore": ["New Delhi", "Delhi"],
    "Mumbai": ["Hyderabad"],
    "Kolkata": ["Banglore"],
    "Chennai": ["Kolkata"]
};

// Common dataset transit routes by pair and stop count
const KNOWN_ROUTES = {
    "DEL->COK": {
        0: ["DEL → COK"],
        1: ["DEL → BOM → COK", "DEL → BLR → COK", "DEL → HYD → COK", "DEL → AMD → COK", "DEL → MAA → COK", "DEL → JAI → BOM → COK"],
        2: ["DEL → AMD → BOM → COK", "DEL → ATQ → BOM → COK", "DEL → BDQ → BOM → COK", "DEL → BHO → BOM → COK", "DEL → CCU → BOM → COK", "DEL → GOI → BOM → COK"]
    },
    "BLR->DEL": {
        0: ["BLR → DEL"],
        1: ["BLR → BOM → DEL", "BLR → HYD → DEL", "BLR → MAA → DEL", "BLR → AMD → DEL", "BLR → GOI → DEL", "BLR → PNQ → DEL"],
        2: ["BLR → BOM → AMD → DEL", "BLR → BOM → BHO → DEL", "BLR → BOM → IDR → DEL", "BLR → CCU → BBI → DEL"]
    },
    "BOM->HYD": {
        0: ["BOM → HYD"],
        1: ["BOM → DEL → HYD", "BOM → BLR → HYD", "BOM → MAA → HYD", "BOM → GOI → HYD", "BOM → CCU → HYD", "BOM → BBI → HYD"],
        2: ["BOM → BDQ → DEL → HYD", "BOM → BHO → DEL → HYD", "BOM → GOI → PNQ → HYD", "BOM → IDR → DEL → HYD"]
    },
    "CCU->BLR": {
        0: ["CCU → BLR"],
        1: ["CCU → DEL → BLR", "CCU → BOM → BLR", "CCU → HYD → BLR", "CCU → MAA → BLR", "CCU → GAU → BLR", "CCU → BBI → BLR"],
        2: ["CCU → BBI → BOM → BLR", "CCU → BOM → AMD → BLR", "CCU → BOM → COK → BLR", "CCU → DEL → AMD → BLR"]
    },
    "MAA->CCU": {
        0: ["MAA → CCU"],
        1: ["MAA → CCU"],
        2: ["MAA → CCU"]
    }
};

// Preset configurations
const PRESETS = {
    "del_cok": {
        Airline: "IndiGo",
        Source: "Delhi",
        Destination: "Cochin",
        Total_Stops: "1",
        Dep_Time: "06:15",
        Arrival_Time: "11:45",
        Route: "DEL → BOM → COK",
        Additional_Info: "No info"
    },
    "blr_del": {
        Airline: "Air India",
        Source: "Banglore",
        Destination: "New Delhi",
        Total_Stops: "0",
        Dep_Time: "07:00",
        Arrival_Time: "09:45",
        Route: "BLR → DEL",
        Additional_Info: "No info"
    },
    "bom_hyd": {
        Airline: "SpiceJet",
        Source: "Mumbai",
        Destination: "Hyderabad",
        Total_Stops: "0",
        Dep_Time: "14:20",
        Arrival_Time: "15:45",
        Route: "BOM → HYD",
        Additional_Info: "No info"
    },
    "ccu_blr": {
        Airline: "Vistara",
        Source: "Kolkata",
        Destination: "Banglore",
        Total_Stops: "1",
        Dep_Time: "10:10",
        Arrival_Time: "15:30",
        Route: "CCU → DEL → BLR",
        Additional_Info: "In-flight meal not included"
    }
};

// Set minimum date to today
const today = new Date();
const formattedToday = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
dateInput.min = formattedToday;
dateInput.value = formattedToday;

// Helper: Parse HH:MM into {hour, minute}
function getTimeParts(value) {
    if (!value || !value.includes(":")) return { hour: 0, minute: 0 };
    const [hour, minute] = value.split(":").map(Number);
    return { hour: Number.isFinite(hour) ? hour : 0, minute: Number.isFinite(minute) ? minute : 0 };
}

// Helper: Calculate duration between Dep_Time and Arrival_Time in minutes
function calculateDuration() {
    const dep = getTimeParts(depTimeInput.value);
    const arr = getTimeParts(arrTimeInput.value);

    let depMinutes = dep.hour * 60 + dep.minute;
    let arrMinutes = arr.hour * 60 + arr.minute;

    let isOvernight = false;
    if (arrMinutes < depMinutes) {
        // Flight arrives next calendar day
        arrMinutes += 24 * 60;
        isOvernight = true;
    } else if (arrMinutes === depMinutes) {
        // Assume 24h or invalid; default to 2h
        arrMinutes = depMinutes + 120;
    }

    const durationMin = arrMinutes - depMinutes;
    durationInput.value = durationMin;

    const hours = Math.floor(durationMin / 60);
    const mins = durationMin % 60;
    durationBadge.textContent = `${hours}h ${mins}m`;

    if (isOvernight) {
        nextDayBadge.style.display = "inline-block";
    } else {
        nextDayBadge.style.display = "none";
    }
}

// Helper: Update route suggestions & auto-populate default route
function syncRouteAndDestinations() {
    const src = sourceInput.value;
    const dest = destInput.value;
    const stops = Number(stopsInput.value) || 0;

    // Check valid destination pairing
    if (src && VALID_PAIRS[src]) {
        const allowed = VALID_PAIRS[src];
        if (!allowed.includes(dest)) {
            destInput.value = allowed[0];
        }
    }

    const currentDest = destInput.value;
    const sCode = CITY_CODES[src] || "DEL";
    const dCode = CITY_CODES[currentDest] || "COK";
    const pairKey = `${sCode}->${dCode}`;

    // Update Datalist suggestions
    routeSuggestions.innerHTML = "";
    const pairRoutes = KNOWN_ROUTES[pairKey] || {};
    const candidateRoutes = pairRoutes[stops] || pairRoutes[0] || [`${sCode} → ${dCode}`];

    candidateRoutes.forEach((r) => {
        const opt = document.createElement("option");
        opt.value = r;
        routeSuggestions.appendChild(opt);
    });

    // Auto-populate route input with the best match
    routeInput.value = candidateRoutes[0] || `${sCode} → ${dCode}`;

    // Sync Hero Card
    if (heroSrcCode) heroSrcCode.textContent = sCode;
    if (heroSrcName) heroSrcName.textContent = src || "Source";
    if (heroDestCode) heroDestCode.textContent = dCode;
    if (heroDestName) heroDestName.textContent = currentDest || "Destination";
    if (heroRouteText) heroRouteText.textContent = stops === 0 ? "NON-STOP FLIGHT" : `${stops} STOP TRANSIT`;
}

// Auto-convert standard typed arrows '->' or '--' to unicode arrow ' → '
routeInput.addEventListener("input", (e) => {
    let val = e.target.value;
    if (val.includes("->") || val.includes("-->") || val.includes(" - ")) {
        e.target.value = val.replace(/\s*(?:-->|->|–>|—>|\sto\s|-)\s*/gi, " → ").toUpperCase();
    }
});

// Event Listeners for dynamic synchronization
depTimeInput.addEventListener("input", calculateDuration);
arrTimeInput.addEventListener("input", calculateDuration);

sourceInput.addEventListener("change", syncRouteAndDestinations);
destInput.addEventListener("change", syncRouteAndDestinations);
stopsInput.addEventListener("change", syncRouteAndDestinations);

// Quick Preset Click Handlers
document.querySelectorAll(".preset-pill").forEach((btn) => {
    btn.addEventListener("click", () => {
        const presetKey = btn.dataset.preset;
        const config = PRESETS[presetKey];
        if (!config) return;

        airlineInput.value = config.Airline;
        sourceInput.value = config.Source;
        destInput.value = config.Destination;
        stopsInput.value = config.Total_Stops;
        depTimeInput.value = config.Dep_Time;
        arrTimeInput.value = config.Arrival_Time;
        infoInput.value = config.Additional_Info;

        calculateDuration();
        syncRouteAndDestinations();
        if (config.Route) {
            routeInput.value = config.Route;
        }

        // Smooth scroll to form
        document.getElementById("predictor").scrollIntoView({ behavior: "smooth" });
    });
});

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = "block";
}

function clearMessages() {
    errorMessage.textContent = "";
    errorMessage.style.display = "none";
}

// Form Submission
form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessages();
    resultCard.classList.remove("show");

    if (!dateInput.value) {
        showError("Please select a journey date.");
        return;
    }

    const journeyDate = new Date(`${dateInput.value}T00:00:00`);
    const departure = getTimeParts(depTimeInput.value);
    const arrival = getTimeParts(arrTimeInput.value);
    const source = sourceInput.value;
    const destination = destInput.value;

    if (source === destination) {
        showError("Source and destination must be different cities.");
        return;
    }

    const duration = Number(durationInput.value);
    const stops = Number(stopsInput.value);

    if (!Number.isFinite(duration) || duration <= 0) {
        showError("Please provide a valid flight duration in minutes.");
        return;
    }

    let routeText = routeInput.value.trim();
    if (!routeText) {
        routeText = `${CITY_CODES[source] || "DEL"} → ${CITY_CODES[destination] || "COK"}`;
    }

    const payload = {
        Airline: airlineInput.value,
        Source: source,
        Destination: destination,
        Route: routeText,
        Additional_Info: infoInput.value,
        Duration: duration,
        Total_Stops: stops,
        Journey_Day: journeyDate.getDate(),
        Journey_Month: journeyDate.getMonth() + 1,
        Dep_Hour: departure.hour,
        Dep_Minute: departure.minute,
        Arrival_Hour: arrival.hour,
        Arrival_Minute: arrival.minute
    };

    predictBtn.disabled = true;
    predictBtn.innerHTML = '<span class="spinner"></span> Analyzing flight...';
    predictBtn.style.opacity = "0.75";

    try {
        let response;
        let responseText;

        try {
            response = await fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            responseText = await response.text();
        } catch (fetchErr) {
            if (API_URL !== BACKEND_PREDICT_URL) {
                console.warn("Primary API URL unreachable. Retrying with production backend...", fetchErr);
                API_URL = BACKEND_PREDICT_URL;
                response = await fetch(API_URL, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                responseText = await response.text();
            } else {
                throw fetchErr;
            }
        }

        // If a static server returned an empty 200 response (content-length: 0), fallback to backend
        if ((!responseText || !responseText.trim()) && API_URL !== BACKEND_PREDICT_URL) {
            console.warn("Empty response from origin, retrying with backend:", BACKEND_PREDICT_URL);
            API_URL = BACKEND_PREDICT_URL;
            response = await fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            responseText = await response.text();
        }

        let data;
        try {
            data = JSON.parse(responseText);
        } catch {
            throw new Error(`The prediction server returned an invalid response (HTTP ${response.status}). Please check https://airfare-prediction-1.onrender.com/health`);
        }

        if (!response.ok) {
            const detail = data.detail;
            throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail || data));
        }

        if (typeof data.predicted_fare !== "number") {
            throw new Error("Invalid prediction response received from the backend.");
        }

        // Format and render results
        const formattedPrice = data.formatted_fare || new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0
        }).format(data.predicted_fare);

        predictedFare.textContent = formattedPrice;

        if (data.fare_range && data.fare_range.formatted_range) {
            fareRangeText.textContent = data.fare_range.formatted_range;
        } else {
            const low = Math.round(data.predicted_fare * 0.92);
            const high = Math.round(data.predicted_fare * 1.12);
            fareRangeText.textContent = `₹${low.toLocaleString("en-IN")} – ₹${high.toLocaleString("en-IN")}`;
        }

        if (confidencePill && data.confidence) {
            confidencePill.textContent = `${data.confidence} confidence`;
        }

        // Render flight summary tags
        resultChips.innerHTML = "";
        const summary = data.flight_summary || {};
        const chips = [
            payload.Airline,
            summary.route || payload.Route,
            `${stops === 0 ? "Non-stop" : stops + (stops === 1 ? " stop" : " stops")}`,
            durationBadge.textContent
        ];

        chips.forEach((c) => {
            if (c) {
                const chip = document.createElement("span");
                chip.className = "result-chip";
                chip.textContent = c;
                resultChips.appendChild(chip);
            }
        });

        resultCard.classList.add("show");
        resultCard.scrollIntoView({ behavior: "smooth", block: "center" });

    } catch (error) {
        console.error("Prediction Error:", error);
        if (error.message.includes("Failed to fetch") || error instanceof TypeError) {
            showError("Unable to connect to the prediction backend. If running locally, start uvicorn (uvicorn main:app --reload). If on Render, the free instance may take 30s to wake up.");
        } else {
            showError(error.message);
        }
    } finally {
        predictBtn.disabled = false;
        predictBtn.innerHTML = 'Predict airfare <span>→</span>';
        predictBtn.style.opacity = "1";
    }
});

resetBtn.addEventListener("click", () => {
    form.reset();
    clearMessages();
    resultCard.classList.remove("show");
    calculateDuration();
    syncRouteAndDestinations();
    document.getElementById("predictor").scrollIntoView({ behavior: "smooth" });
});

// Initialize on page load
calculateDuration();
syncRouteAndDestinations();
