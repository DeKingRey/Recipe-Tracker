const recipes = {{ recipes|tojson }} // Gets recipes
const input = document.getElementById("location_input")
const suggestions = document.getElementById("locations")

input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase(); // Gets the users input and removes spaces and makes it lowercase
    suggestions.innerHTML = ""; 

    if (!query) return;

    const matches = locs.filter(loc =>
        loc.toLowerCase().includes(query)
    ); // Checks for locations which include the inputted search

matches.forEach(match => {
    const li = document.createElement("li");
    li.textContent = match;
    li.addEventListener("click", () => {
        input.value = match;
        suggestions.innerHTML = "";
        validateLocation(); // Revalidates location
    });
    suggestions.appendChild(li);
}); // For each match it will create a list element and allow the user to click on it to set that to the inputs value
});