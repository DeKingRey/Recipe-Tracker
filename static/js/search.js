const recipes = {{ recipes|tojson }} // Gets recipes
const input = document.getElementById("search_input")
const suggestions = document.getElementById("suggestions")

input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase(); // Gets the users input and correctly formats
    suggestions.innerHTML = ""; 

    if (!query) return;

    // Checks for recipes which include the inputted search
    const matches = recipes.filter(recipe =>
        recipe.toLowerCase().includes(query)
    );

// Creates suggestions for each match for user to click
matches.forEach(match => {
    const li = document.createElement("li");
    li.textContent = match;
    li.addEventListener("click", () => {
        input.value = match;
        suggestions.innerHTML = "";
    });
    suggestions.appendChild(li);
});
});