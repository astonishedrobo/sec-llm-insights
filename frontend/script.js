// Generate year options dynamically
const currentYear = new Date().getFullYear() - 1;
const startYear = 1995;

function generateYearOptions(selectElement) {
    for (let year = startYear; year <= currentYear; year++) {
        const option = document.createElement("option");
        option.value = year;
        option.text = year;
        selectElement.appendChild(option);
    }
}

// Generate options for the "fromYear" select element
const fromYearSelect = document.getElementById("fromYear");
generateYearOptions(fromYearSelect);

// Generate options for the "toYear" select element
const toYearSelect = document.getElementById("toYear");
generateYearOptions(toYearSelect);
toYearSelect.value = currentYear; // Set the default value to the current year

// Handle form submission
document.getElementById("insightForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent form submission

    const company = document.getElementById("company").value;
    const email = document.getElementById("email").value;
    const ticker = document.getElementById("ticker").value;
    const fromYear = document.getElementById("fromYear").value;
    const toYear = document.getElementById("toYear").value;

    // Show loading message
    document.getElementById("loading").style.display = "block";

    // Make an API request to the backend
    fetch("/generate-insight", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ company, email, ticker, fromYear, toYear })
    })
    .then(response => response.json())
    .then(data => {
        // Hide loading message
        document.getElementById("loading").style.display = "none";

        if (data.error) {
            // Display error message
            alert("Error: " + data.error);
        } else {
            // Show the buttons
            document.getElementById("buttons").style.display = "block";

            // Fetch the list of plot files
            fetch(`/get-plots?ticker=${ticker}`)
                .then(response => response.json())
                .then(plots => {
                    const insightsContainer = document.getElementById("insightsContainer");
                    insightsContainer.innerHTML = ""; // Clear previous insights

                    // Create image elements for each plot
                    plots.forEach(plot => {
                        const plotElement = document.createElement("div");
                        const caption = plot.title;
                        plotElement.innerHTML = `
                            <figure>
                                <img src="${plot.path}" alt="${caption}">
                                <figcaption>${caption}</figcaption>
                            </figure>
                        `;
                        insightsContainer.appendChild(plotElement);
                    });
                })
                .catch(error => {
                    console.error("Error fetching plot files:", error);
                    alert("An error occurred while fetching the plot files. Please try again.");
                });
        }
    })
    .catch(error => {
        console.error("Error generating insight:", error);
        // Hide loading message
        document.getElementById("loading").style.display = "none";
        alert("An error occurred while generating the insight. Please try again.");
    });
});

// Add event listener for the insights button
document.getElementById("insightsBtn").addEventListener("click", function() {
    document.getElementById("insightsContainer").style.display = "block";
    document.getElementById("detailedInsightsContainer").style.display = "none";

    // Fetch the list of plot files
    fetch(`/get-plots?ticker=${ticker.value}`)
        .then(response => response.json())
        .then(plots => {
            const insightsContainer = document.getElementById("insightsContainer");
            insightsContainer.innerHTML = ""; // Clear previous insights

            // Create image elements for each plot
            plots.forEach(plot => {
                const plotElement = document.createElement("div");
                const caption = plot.title;
                plotElement.innerHTML = `
                    <figure>
                        <img src="${plot.path}" alt="${caption}">
                    </figure>
                `;
                insightsContainer.appendChild(plotElement);
            });
        })
        .catch(error => {
            console.error("Error fetching plot files:", error);
            alert("An error occurred while fetching the plot files. Please try again.");
        });
});

document.getElementById("detailedInsightsBtn").addEventListener("click", function() {
    document.getElementById("insightsContainer").style.display = "none";
    document.getElementById("detailedInsightsContainer").style.display = "block";

    // Fetch the detailed plots
    fetch(`/get-detailed-plots?ticker=${ticker.value}`)
        .then(response => response.json())
        .then(plots => {
            const detailedInsightsContainer = document.getElementById("detailedInsightsContainer");
            detailedInsightsContainer.innerHTML = ""; // Clear previous detailed insights

            // Create image elements for each detailed plot
            plots.forEach(plot => {
                const plotElement = document.createElement("div");
                plotElement.innerHTML = `
                    <figure>
                        <img src="${plot.path}" alt="${plot.title}">
                    </figure>
                `;
                detailedInsightsContainer.appendChild(plotElement);
            });
        })
        .catch(error => {
            console.error("Error fetching detailed plot files:", error);
            alert("An error occurred while fetching the detailed plot files. Please try again.");
        });
});