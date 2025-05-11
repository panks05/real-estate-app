document.addEventListener("DOMContentLoaded", function () {
    fetch("/properties")
        .then(response => response.json())
        .then(data => {
            // Group prices by location
            const locationPriceMap = {};
            const locationCountMap = {};

            data.forEach(property => {
                const loc = property.location;
                const price = parseFloat(property.price);
                if (!locationPriceMap[loc]) {
                    locationPriceMap[loc] = 0;
                    locationCountMap[loc] = 0;
                }
                locationPriceMap[loc] += price;
                locationCountMap[loc] += 1;
            });

            // Calculate average price per location
            const averages = Object.keys(locationPriceMap).map(loc => ({
                location: loc,
                avgPrice: locationPriceMap[loc] / locationCountMap[loc]
            }));

            // Sort by highest average price
            averages.sort((a, b) => b.avgPrice - a.avgPrice);
            const topLocations = averages.slice(0, 5);

            // Plot chart
            const ctx = document.getElementById("edaChart").getContext("2d");
            new Chart(ctx, {
                type: "bar",
                data: {
                    labels: topLocations.map(l => l.location),
                    datasets: [{
                        label: "Avg Price (Lakhs)",
                        data: topLocations.map(l => l.avgPrice.toFixed(2)),
                        backgroundColor: "rgba(75, 192, 192, 0.7)"
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false },
                        title: {
                            display: true,
                            text: "Top 5 Locations by Average Price"
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        });
});
x