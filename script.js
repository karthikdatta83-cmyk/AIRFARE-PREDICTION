const form = document.getElementById("flightForm");

form.addEventListener("submit", async function(event) {

    event.preventDefault();

    const data = {
        Airline: document.getElementById("Airline").value,
        Source: document.getElementById("Source").value,
        Destination: document.getElementById("Destination").value,
        Route: document.getElementById("Route").value,
        Additional_Info: document.getElementById("Additional_Info").value,

        Duration: Number(document.getElementById("Duration").value),
        Total_Stops: Number(document.getElementById("Total_Stops").value),
        Journey_Day: Number(document.getElementById("Journey_Day").value),
        Journey_Month: Number(document.getElementById("Journey_Month").value),
        Dep_Hour: Number(document.getElementById("Dep_Hour").value),
        Dep_Minute: Number(document.getElementById("Dep_Minute").value),
        Arrival_Hour: Number(document.getElementById("Arrival_Hour").value),
        Arrival_Minute: Number(document.getElementById("Arrival_Minute").value)
    };

    const result = document.getElementById("result");

    result.innerHTML = "Predicting airfare...";

    try {

        const response = await fetch("http://127.0.0.1:8000/predict", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(data)

        });

        const output = await response.json();

        if (!response.ok) {
            throw new Error(JSON.stringify(output.detail || output));
        }

        result.innerHTML =
            "Predicted Airfare: \u20B9" +
            Number(output.predicted_fare).toFixed(2);
    }

    catch(error) {

        result.innerHTML = "Error: " + error.message;

    }

});