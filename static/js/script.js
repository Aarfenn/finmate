document.addEventListener("DOMContentLoaded", () => {
    // Obsługa kliknięcia ⚙️
    document.querySelectorAll(".gear-link").forEach(link => {
        link.addEventListener("click", event => {
            event.preventDefault();
            const categoryName = link.dataset.category;
            const form = document.getElementById(`limit-form-${categoryName}`);
            if (form) {
                form.classList.toggle("visible");
            }
        });
    });

    // Obsługa kliknięcia ➕
document.querySelectorAll(".plus-link").forEach(link => {
  link.addEventListener("click", event => {
    event.preventDefault();
    const categoryName = link.dataset.category;
    const form = document.getElementById(`expense-form-${categoryName}`);
    if (form) {
      form.classList.toggle("visible");
    }
  });
});

// Obsługa kliknięcia Dodaj wydatek
document.querySelectorAll(".add-expense-btn").forEach(button => {
  button.addEventListener("click", async () => {
    const categoryName = button.dataset.category;
    const budgetId = button.dataset.budget;
    const input = document.getElementById(`expense-input-${categoryName}`);
    const amount = parseFloat(input.value);

    if (isNaN(amount) || amount <= 0) {
      alert("Wprowadź poprawną kwotę.");
      return;
    }

    const formData = new FormData();
    formData.append("category", categoryName);
    formData.append("budget_id", budgetId);
    formData.append("amount", amount);

    const response = await fetch("/add_expense", {
      method: "POST",
      body: formData
    });

    if (response.redirected) {
      window.location.href = response.url; // fallback
      return;
    }

    // Na sukces: zaktualizuj wartości lokalnie
    const display = document.getElementById(`limit-display-${categoryName}`);
    const progress = document.getElementById(`progress-bar-${categoryName}`);

    let currentSpent = parseFloat(display.dataset.spent);
    const limit = parseFloat(display.dataset.limit);

    currentSpent += amount;
    display.dataset.spent = currentSpent;
    display.innerText = `${currentSpent}/${limit} zł`;

    let percent = 0;
    if (limit > 0) {
    percent = Math.min((currentSpent / limit) * 100, 100);
    }
    progress.style.width = `${percent}%`;
    progress.style.zIndex = "1";

    // Jeśli przekroczono limit, pokazujemy nadmiarowy czerwony pasek
    const overLimit = currentSpent - limit;
    let overBar = document.getElementById(`over-bar-${categoryName}`);

    if (overLimit > 0 && limit > 0) {
    if (!overBar) {
        overBar = document.createElement("div");
        overBar.id = `over-bar-${categoryName}`;
        overBar.className = "progress-bar bg-danger position-absolute";
        overBar.style.height = "100%";
        overBar.style.left = "0";
        overBar.style.zIndex = "2";
        const parent = progress.parentElement;
        parent.appendChild(overBar);
    }

    const overPercent = Math.min((overLimit / limit) * 100, 100);
    overBar.style.width = `${overPercent}%`;
    } else if (overBar) {
    overBar.remove();
    }

    input.value = "";
    const form = document.getElementById(`expense-form-${categoryName}`);
    form.classList.remove("visible");
  });
});


    // Obsługa kliknięcia przycisku "Zapisz"
    document.querySelectorAll(".save-limit-btn").forEach(button => {
        button.addEventListener("click", async () => {
            const categoryName = button.dataset.category;
            const budgetId = button.dataset.budget;
            const input = document.getElementById(`limit-input-${categoryName}`);
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
        });
    });
});
