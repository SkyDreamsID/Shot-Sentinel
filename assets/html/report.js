document.addEventListener('DOMContentLoaded', () => {
    const table = document.querySelector('table');
    if (!table) return;
    
    const headers = table.querySelectorAll('th');
    const tbody = table.querySelector('tbody');
    let currentSortColumn = -1;
    let isAscending = true;

    headers.forEach((header, index) => {
        header.addEventListener('click', () => {
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            if (currentSortColumn === index) {
                isAscending = !isAscending;
            } else {
                isAscending = true;
                currentSortColumn = index;
            }

            rows.sort((rowA, rowB) => {
                let cellA = rowA.children[index].textContent.trim();
                let cellB = rowB.children[index].textContent.trim();
                
                // Try to sort numerically if applicable
                const numA = parseFloat(cellA.replace(/[^0-9.-]+/g,""));
                const numB = parseFloat(cellB.replace(/[^0-9.-]+/g,""));
                
                if (!isNaN(numA) && !isNaN(numB) && cellA.match(/^[0-9.,$-]+$/)) {
                    return isAscending ? numA - numB : numB - numA;
                }

                return isAscending ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
            });

            // Reorder headers visualization (optional arrows)
            headers.forEach(h => h.textContent = h.textContent.replace(/ [▼▲]$/, ''));
            header.textContent += isAscending ? ' ▲' : ' ▼';

            // Append sorted rows back to tbody
            rows.forEach(row => tbody.appendChild(row));
        });
    });
});
