// Arizmendi Pizza Tracker

const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 
                'July', 'August', 'September', 'October', 'November', 'December'];

function formatDate(date) {
    return `${DAYS[date.getDay()]}, ${MONTHS[date.getMonth()]} ${date.getDate()}`;
}

function formatDateKey(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function isMonday(date) {
    return date.getDay() === 1;
}

function isSpecialClosure(dateKey) {
    return SPECIAL_CLOSURES && SPECIAL_CLOSURES[dateKey];
}

function getPizzaForDate(date) {
    const dateKey = formatDateKey(date);
    
    // Check for special closures
    if (isSpecialClosure(dateKey)) {
        return { closed: true, reason: SPECIAL_CLOSURES[dateKey] };
    }
    
    // Closed on Mondays
    if (isMonday(date)) {
        return { closed: true, reason: 'Closed on Mondays' };
    }
    
    // Get pizza from data
    const pizza = PIZZA_DATA[dateKey];
    if (pizza) {
        if (pizza.startsWith('CLOSED')) {
            return { closed: true, reason: pizza.replace('CLOSED - ', '') };
        }
        return { closed: false, pizza: pizza };
    }
    
    return { closed: false, pizza: 'Menu not yet available' };
}

function parseIngredients(pizzaDescription) {
    // Extract main ingredients (before oils and p&p)
    const parts = pizzaDescription.split(',').map(p => p.trim());
    const ingredients = [];
    
    for (const part of parts) {
        // Skip oils and p&p
        if (part.includes('oil') || part === 'p&p' || part.includes('parsley') || part.includes('parmesan')) {
            continue;
        }
        // Clean up and add
        const cleaned = part.replace(/with /g, '').trim();
        if (cleaned.length > 0 && cleaned.length < 40) {
            ingredients.push(cleaned);
        }
    }
    
    return ingredients.slice(0, 4); // Max 4 ingredient tags
}

function renderTodayCard() {
    const container = document.getElementById('today-card');
    const today = new Date();
    const pizzaInfo = getPizzaForDate(today);
    
    if (pizzaInfo.closed) {
        container.innerHTML = `
            <div class="label">Today</div>
            <div class="date">${formatDate(today)}</div>
            <div class="closed-text">😴 ${pizzaInfo.reason}</div>
        `;
        container.classList.add('closed');
    } else {
        const ingredients = parseIngredients(pizzaInfo.pizza);
        container.innerHTML = `
            <div class="label">Today's Pizza</div>
            <div class="date">${formatDate(today)}</div>
            <div class="pizza-name">${pizzaInfo.pizza}</div>
            ${ingredients.length > 0 ? `
                <div class="ingredients">
                    ${ingredients.map(i => `<span class="ingredient-tag">${i}</span>`).join('')}
                </div>
            ` : ''}
        `;
        container.classList.remove('closed');
    }
}

function renderUpcomingPizzas() {
    const container = document.getElementById('pizza-list');
    const today = new Date();
    const cards = [];
    
    // Show next 14 days
    for (let i = 1; i <= 14; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() + i);
        
        const pizzaInfo = getPizzaForDate(date);
        const dayName = DAYS[date.getDay()];
        const dateStr = `${MONTHS[date.getMonth()]} ${date.getDate()}`;
        
        if (pizzaInfo.closed) {
            cards.push(`
                <div class="pizza-card closed ${isSpecialClosure(formatDateKey(date)) ? 'special-closed' : ''}">
                    <div class="day-date">
                        <span class="day">${dayName}</span>
                        <span class="date">${dateStr}</span>
                    </div>
                    <div class="pizza-name">😴 ${pizzaInfo.reason}</div>
                </div>
            `);
        } else {
            cards.push(`
                <div class="pizza-card">
                    <div class="day-date">
                        <span class="day">${dayName}</span>
                        <span class="date">${dateStr}</span>
                    </div>
                    <div class="pizza-name">${pizzaInfo.pizza}</div>
                </div>
            `);
        }
    }
    
    container.innerHTML = cards.join('');
}

function init() {
    renderTodayCard();
    renderUpcomingPizzas();
}

// Initialize on load
document.addEventListener('DOMContentLoaded', init);

// Refresh at midnight
function scheduleRefresh() {
    const now = new Date();
    const midnight = new Date(now);
    midnight.setDate(midnight.getDate() + 1);
    midnight.setHours(0, 0, 0, 0);
    
    const msUntilMidnight = midnight - now;
    setTimeout(() => {
        init();
        scheduleRefresh();
    }, msUntilMidnight);
}

scheduleRefresh();
