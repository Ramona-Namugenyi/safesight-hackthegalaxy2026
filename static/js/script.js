
// ── AUTOCOMPLETE ──
const neighbourhoods = [
    "Arbutus Ridge", "Central Business District", "Dunbar-Southlands",
    "Fairview", "Grandview-Woodland", "Hastings-Sunrise",
    "Kensington-Cedar Cottage", "Kerrisdale", "Killarney",
    "Kitsilano", "Marpole", "Mount Pleasant", "Musqueam",
    "Oakridge", "Renfrew-Collingwood", "Riley Park", "Shaughnessy",
    "South Cambie", "Stanley Park", "Strathcona", "Sunset",
    "Victoria-Fraserview", "West End", "West Point Grey"
];

function setupAutocomplete(inputId, listId) {
    const input = document.getElementById(inputId);
    const list = document.getElementById(listId);

    input.addEventListener("input", () => {
        const val = input.value.toLowerCase();
        list.innerHTML = "";

        if (!val) {
            list.style.display = "none";
            return;
        }

        const matches = neighbourhoods.filter(n => 
            n.toLowerCase().startsWith(val)
        );

        if (matches.length === 0) {
            list.style.display = "none";
            return;
        }

        matches.forEach(match => {
            const li = document.createElement("li");
            li.textContent = match;
            li.addEventListener("click", () => {
                input.value = match;
                list.style.display = "none";
            });
            list.appendChild(li);
        });

        list.style.display = "block";
    });

    // Hide list when clicking outside
    document.addEventListener("click", (e) => {
        if (!input.contains(e.target) && !list.contains(e.target)) {
            list.style.display = "none";
        }
    });
}

setupAutocomplete("start-input", "start-list");
setupAutocomplete("destination-input", "dest-list");document.getElementById("check-btn").addEventListener("click", async () => {

    const start = document.getElementById("start-input").value.trim();
    const destination = document.getElementById("destination-input").value.trim();

    if (!start || !destination) {
        alert("Please enter both your location and destination!");
        return;
    }

    // Show results section
    const resultsSection = document.getElementById("results");
    resultsSection.style.display = "block";

    // Reset loading state
    document.getElementById("ai-summary").innerHTML = "<p class='loading'>Generating your safety briefing...</p>";
    document.getElementById("start-incident-list").innerHTML = "";
    document.getElementById("dest-incident-list").innerHTML = "";
    document.getElementById("start-name").textContent = start;
    document.getElementById("dest-name").textContent = destination;

    // Update Google Maps button
    const mapsBtn = document.getElementById("maps-btn");
    mapsBtn.href = `https://www.google.com/maps/dir/${encodeURIComponent(start)}/${encodeURIComponent(destination)}`;

    function getScore(count) {
        if (count < 500) return { score: 85, colorClass: "green" };
        if (count < 1000) return { score: 70, colorClass: "green" };
        if (count < 1500) return { score: 55, colorClass: "yellow" };
        if (count < 2000) return { score: 35, colorClass: "yellow" };
        return { score: 20, colorClass: "red" };
    }

    function populateIncidentList(listId, incidentTypes) {
        const list = document.getElementById(listId);
        list.innerHTML = "";
        for (const [type, count] of Object.entries(incidentTypes)) {
            const li = document.createElement("li");
            li.innerHTML = `<span class="incident-type">${type}</span><span class="incident-count">${count}</span>`;
            list.appendChild(li);
        }
    }

    try {
        // Fetch safety data for BOTH locations
        const [startRes, destRes] = await Promise.all([
            fetch(`/safety?neighbourhood=${encodeURIComponent(start)}`),
            fetch(`/safety?neighbourhood=${encodeURIComponent(destination)}`)
        ]);

        const startData = await startRes.json();
        const destData = await destRes.json();

        // Populate start card
        const startScore = getScore(startData.incident_count);
        document.getElementById("start-score-number").textContent = startScore.score;
        document.getElementById("start-score-circle").className = `score-circle ${startScore.colorClass}`;
        document.getElementById("start-incident-count").textContent = `${startData.incident_count} incidents recorded`;
        populateIncidentList("start-incident-list", startData.incident_types);

        // Populate destination card
        const destScore = getScore(destData.incident_count);
        document.getElementById("dest-score-number").textContent = destScore.score;
        document.getElementById("dest-score-circle").className = `score-circle ${destScore.colorClass}`;
        document.getElementById("dest-incident-count").textContent = `${destData.incident_count} incidents recorded`;
        populateIncidentList("dest-incident-list", destData.incident_types);

        // Build types strings for Gemini
        const startTypes = Object.entries(startData.incident_types)
            .map(([type, count]) => `${type}: ${count}`).join(", ");
        const destTypes = Object.entries(destData.incident_types)
            .map(([type, count]) => `${type}: ${count}`).join(", ");

        // Call Gemini
        const geminiRes = await fetch(`/gemini?start=${encodeURIComponent(start)}&destination=${encodeURIComponent(destination)}&start_count=${startData.incident_count}&dest_count=${destData.incident_count}&start_types=${encodeURIComponent(startTypes)}&dest_types=${encodeURIComponent(destTypes)}`);
        const geminiData = await geminiRes.json();

        document.getElementById("ai-summary").innerHTML = `<p>${geminiData.summary}</p>`;

    } catch (error) {
        document.getElementById("ai-summary").innerHTML = "<p>Sorry, something went wrong. Please try again!</p>";
        console.error(error);
    }
});