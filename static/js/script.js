function toggleLimitForm(categoryName) {
    const form = document.getElementById(`limit-form-${categoryName}`);
    form.classList.toggle("visible");
}

async function saveLimit(budgetId, categoryName) {
    const input = document.querySelector(`#limit-input-${categoryName}`);
    const limit = parseFloat(input.value);
    if (isNaN(limit)) {
        alert("Wprowadź poprawny limit.");
        return;
    }

    const response = await fetch('/set_limit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ budget_id: budgetId, category_name: categoryName, limit })
    });

    const result = await response.json();
    if (result.success) {
        const display = document.getElementById(`limit-display-${categoryName}`);
        const spent = parseFloat(display.dataset.spent);
        display.innerText = `${spent}/${limit} zł`;
        display.dataset.limit = limit;

        const form = document.getElementById(`limit-form-${categoryName}`);
        form.classList.remove("visible");
    } else {
        alert("Nie udało się zapisać limitu.");
    }
}
