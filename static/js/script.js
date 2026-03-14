// ── WHEN BUTTON IS CLICKED ──
document.getElementById("check-btn").addEventListener("click", async () => {

    const start = document.getElementById("start-input").value.trim();
    const destination = document.getElementById("destination-input").value.trim();

    // Make sure both fields are filled
    if (!start || !destination) {
        alert("Please enter both your location and destination!");
        return;
    }

    // Show results section
    const resultsSection = document.getElementById("results");
    resultsSection.style.display = "block";

    // Show loading state
    document.getElementById("ai-summary").innerHTML = "<p class='loading'>Generating your safety briefing...</p>";
    document.getElementById("incident-list").innerHTML = "";
    document.getElementById("neighbourhood-name").textContent = destination;

    // Update Google Maps button
    const mapsBtn = document.getElementById("maps-btn");
    const mapsUrl = `https://www.google.com/maps/dir/${encodeURIComponent(start)}/${encodeURIComponent(destination)}`;
    mapsBtn.href = mapsUrl;

    try {
        // ── STEP 1: Get crime data from Flask ──
        const safetyRes = await fetch(`/safety?neighbourhood=${encodeURIComponent(destination)}`);
        const safetyData = await safetyRes.json();

        // Show incident count
        document.getElementById("neighbourhood-name").textContent = safetyData.neighbourhood;
        document.getElementById("peak-times").textContent = `${safetyData.incident_count} incidents recorded in this area`;

        // Show incident breakdown
        const incidentList = document.getElementById("incident-list");
        incidentList.innerHTML = "";
        for (const [type, count] of Object.entries(safetyData.incident_types)) {
            const li = document.createElement("li");
            li.innerHTML = `${type} <span>${count}</span>`;
            incidentList.appendChild(li);
        }

        // Set safety score colour
        const scoreCircle = document.getElementById("score-circle");
        const scoreNumber = document.getElementById("score-number");
        const count = safetyData.incident_count;

        let score, colorClass;
        if (count < 100) {
            score = 80; colorClass = "green";
        } else if (count < 300) {
            score = 55; colorClass = "yellow";
        } else {
            score = 30; colorClass = "red";
        }

        scoreNumber.textContent = score;
        scoreCircle.className = `score-circle ${colorClass}`;

        // ── STEP 2: Get Gemini AI summary ──
        const typesString = Object.entries(safetyData.incident_types)
            .map(([type, count]) => `${type}: ${count}`)
            .join(", ");

        const geminiRes = await fetch(`/gemini?neighbourhood=${encodeURIComponent(destination)}&incident_count=${safetyData.incident_count}&incident_types=${encodeURIComponent(typesString)}`);
        const geminiData = await geminiRes.json();

        document.getElementById("ai-summary").innerHTML = `<p>${geminiData.summary}</p>`;

    } catch (error) {
        document.getElementById("ai-summary").innerHTML = "<p>Sorry, something went wrong. Please try again!</p>";
        console.error(error);
    }
});