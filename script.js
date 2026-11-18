
const API_URL = "https://airfare-price-estimation-z3wm.onrender.com/#predictor";

const form = document.getElementById("fareForm");
const predictBtn = document.getElementById("predictBtn");
const errorMessage = document.getElementById("errorMessage");
const resultCard = document.getElementById("resultCard");
const predictedFare = document.getElementById("predictedFare");
const resetBtn = document.getElementById("resetBtn");

const dateInput = document.getElementById("Journey_Date");
const today = new Date();

dateInput.min = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;

function getTimeParts(value) {
    const [hour, minute] = value.split(":").map(Number);
    return { hour, minute };
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = "block";
}

function clearMessages() {
    errorMessage.textContent = "";
    errorMessage.style.display = "none";
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    clearMessages();
    resultCard.classList.remove("show");

    const journeyDate = new Date(`${dateInput.value}T00:00:00`);
    const departure = getTimeParts(document.getElementById("Dep_Time").value);
    const arrival = getTimeParts(document.getElementById("Arrival_Time").value);

    const source = document.getElementById("Source").value;
    const destination = document.getElementById("Destination").value;

    if (source === destination) {
        showError("Source and destination must be different cities.");
        return;
    }

    const payload = {
        Airline: document.getElementById("Airline").value,
        Source: source,
        Destination: destination,
        Route: document.getElementById("Route").value.trim(),
        Additional_Info: document.getElementById("Additional_Info").value,
        Duration: Number(document.getElementById("Duration").value),
        Total_Stops: Number(document.getElementById("Total_Stops").value),
        Journey_Day: journeyDate.getDate(),
        Journey_Month: journeyDate.getMonth() + 1,
        Dep_Hour: departure.hour,
        Dep_Minute: departure.minute,
        Arrival_Hour: arrival.hour,
        Arrival_Minute: arrival.minute
    };

    if (!payload.Route) {
        showError("Please enter the flight route.");
        return;
    }

    predictBtn.disabled = true;
    predictBtn.innerHTML = "Predicting...";
    predictBtn.style.opacity = "0.75";

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Prediction failed.");
        }

        if (typeof data.predicted_fare !== "number") {
            throw new Error("Invalid prediction response from backend.");
        }

        predictedFare.textContent = new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 2
        }).format(data.predicted_fare);

        resultCard.classList.add("show");

        resultCard.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });

    } catch (error) {
        if (error.message.includes("Failed to fetch")) {
            showError("Unable to connect to backend. Check your internet connection, backend status and CORS settings.");
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

    document.getElementById("predictor").scrollIntoView({
        behavior: "smooth"
    });
});
