document.addEventListener('DOMContentLoaded', function () {
    const seatCheckboxes = document.querySelectorAll('.seat input[type="checkbox"]');
    const selectedCountEl = document.getElementById('selected-count');
    const totalPriceEl = document.getElementById('total-price');

    function updateSummary() {
        let count = 0;
        let total = 0;

        seatCheckboxes.forEach(function (cb) {
            if (cb.checked) {
                count++;
                const seatLabel = cb.closest('.seat');
                const price = parseFloat(seatLabel.dataset.price || 0);
                total += price;
            }
        });

        selectedCountEl.textContent = count;
        totalPriceEl.textContent = total.toFixed(2);
    }

    seatCheckboxes.forEach(function (cb) {
        cb.addEventListener('change', updateSummary);
    });

    updateSummary();
});
