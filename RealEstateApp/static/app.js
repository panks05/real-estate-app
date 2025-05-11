function onEstimateClick() {
    const sqft = document.getElementById("sqft").value;
    const bhk = document.querySelector('input[name="bhk"]:checked').value;
    const bath = document.querySelector('input[name="bath"]:checked').value;
    const location = document.getElementById("location").value;

    const resultBox = document.getElementById("result");
    resultBox.innerHTML = "⏳ Calculating...";

    fetch("/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ sqft, bhk, bath, location })
    })
    .then(response => response.json())
    .then(data => {
        resultBox.innerHTML = `💰 Estimated Price: <strong>${data.estimated_price}</strong> Lakhs`;
        loadFilteredProperties();  // Load matching listings
    })
    .catch(error => {
        console.error("Error:", error);
        resultBox.innerHTML = "⚠️ Something went wrong. Try again.";
    });
}

function onSaveSearch() {
    const sqft = document.getElementById("sqft").value;
    const bhk = document.querySelector('input[name="bhk"]:checked').value;
    const bath = document.querySelector('input[name="bath"]:checked').value;
    const location = document.getElementById("location").value;

    fetch("/save-search", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ sqft, bhk, bath, location })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message || "Search saved!");
    })
    .catch(err => {
        console.error("Error saving search:", err);
        alert("Something went wrong.");
    });
}

function loadFilteredProperties() {
    const location = document.getElementById("location").value;

    fetch(`/properties?location=${location}`)
        .then(res => res.json())
        .then(data => {
            let html = "<h3>Available Properties</h3>";
            html += "<table border='1' cellpadding='6' cellspacing='0' style='width:100%'>";
            html += "<tr><th>Location</th><th>Sqft</th><th>BHK</th><th>Bath</th><th>Price</th><th>Action</th></tr>";

            data.forEach(p => {
                html += `<tr>
                    <td>${p.location}</td>
                    <td>${p.sqft}</td>
                    <td>${p.bhk}</td>
                    <td>${p.bath}</td>
                    <td>${p.price} L</td>
                    <td><button id="fav-${p.id}" onclick="addToFavorites(${p.id})">❤️ Favorite</button></td>
                </tr>`;
            });

            html += "</table>";
            document.getElementById("propertyList").innerHTML = html;
        });
}

function addToFavorites(propertyId) {
    const button = document.getElementById(`fav-${propertyId}`);
    button.disabled = true;
    button.textContent = "💾 Saving...";

    fetch('/add-favorite', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ property_id: propertyId })
    })
    .then(res => res.json())
    .then(data => {
        button.textContent = "❤️ Saved";
        alert(data.message || "Added to favorites!");
    })
    .catch(err => {
        console.error(err);
        button.disabled = false;
        button.textContent = "❤️ Favorite";
        alert("Error adding to favorites.");
    });
}
function showPropertyDetails(p) {
    const modal = new bootstrap.Modal(document.getElementById('propertyModal'));
    const body = document.getElementById('modalBody');

    body.innerHTML = `
        <p><strong>Location:</strong> ${p[1]}</p>
        <p><strong>Area:</strong> ${p[2]} sqft</p>
        <p><strong>BHK:</strong> ${p[4]}</p>
        <p><strong>Bathrooms:</strong> ${p[3]}</p>
        <p><strong>Price:</strong> ₹ ${p[5]} Lakhs</p>
    `;

    modal.show();
}
