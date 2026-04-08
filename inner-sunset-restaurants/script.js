// API Configuration - Use static JSON file for GitHub Pages
const USE_STATIC_DATA = true;
const API_BASE_URL = 'http://localhost:5001/api';
const STATIC_DATA_URL = 'restaurants.json';

// Restaurant data - will be populated from Yelp API
let restaurants = [];

// Tried restaurants - stored in localStorage
const TRIED_STORAGE_KEY = 'innerSunsetTriedRestaurants';

function getTriedRestaurants() {
    const stored = localStorage.getItem(TRIED_STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
}

function saveTriedRestaurants(tried) {
    localStorage.setItem(TRIED_STORAGE_KEY, JSON.stringify(tried));
}

function isRestaurantTried(restaurantId) {
    return getTriedRestaurants().includes(restaurantId);
}

// Removed restaurants - fetched from Google Sheet
let removedRestaurants = [];

// Google Sheet URL (CSV export) - replace SHEET_ID with your actual sheet ID
// Format: https://docs.google.com/spreadsheets/d/SHEET_ID/gviz/tq?tqx=out:csv
const GOOGLE_SHEET_CSV_URL = localStorage.getItem('removedSheetUrl') || '';

async function fetchRemovedRestaurants() {
    // First check the local JS file
    if (typeof REMOVED_RESTAURANTS !== 'undefined' && REMOVED_RESTAURANTS.length > 0) {
        removedRestaurants = [...REMOVED_RESTAURANTS];
    }
    
    // Then try to fetch from Google Sheet if URL is set
    if (GOOGLE_SHEET_CSV_URL) {
        try {
            const response = await fetch(GOOGLE_SHEET_CSV_URL);
            if (response.ok) {
                const csv = await response.text();
                const ids = csv.split('\n')
                    .map(line => line.trim().replace(/"/g, ''))
                    .filter(id => id && id !== 'restaurant_id'); // Skip header
                removedRestaurants = [...new Set([...removedRestaurants, ...ids])];
            }
        } catch (e) {
            console.log('Could not fetch Google Sheet:', e);
        }
    }
}

function isRestaurantRemoved(restaurantId) {
    return removedRestaurants.includes(restaurantId);
}

function removeRestaurant(restaurantId, restaurantName, event) {
    event.stopPropagation();
    
    const sheetUrl = GOOGLE_SHEET_CSV_URL || localStorage.getItem('removedSheetUrl');
    
    if (!sheetUrl) {
        // First time - prompt for setup
        const msg = `To enable shared removal, set up a Google Sheet:\n\n` +
            `1. Create a new Google Sheet\n` +
            `2. Add "restaurant_id" in cell A1\n` +
            `3. File → Share → "Anyone with link can edit"\n` +
            `4. Copy the Sheet ID from the URL\n\n` +
            `Sheet URL format:\nhttps://docs.google.com/spreadsheets/d/SHEET_ID/edit\n\n` +
            `Enter your SHEET_ID:`;
        
        const sheetId = prompt(msg);
        if (sheetId) {
            const csvUrl = `https://docs.google.com/spreadsheets/d/${sheetId}/gviz/tq?tqx=out:csv`;
            localStorage.setItem('removedSheetUrl', csvUrl);
            localStorage.setItem('removedSheetEditUrl', `https://docs.google.com/spreadsheets/d/${sheetId}/edit`);
            alert('Sheet connected! Click the remove button again to add restaurants.');
            return;
        }
        return;
    }
    
    const editUrl = localStorage.getItem('removedSheetEditUrl') || sheetUrl.replace('/gviz/tq?tqx=out:csv', '/edit');
    
    // Copy the ID and open the sheet
    navigator.clipboard.writeText(restaurantId).then(() => {
        const open = confirm(
            `"${restaurantName}" ID copied!\n\n` +
            `ID: ${restaurantId}\n\n` +
            `Click OK to open the Google Sheet and paste the ID in a new row.`
        );
        if (open) {
            window.open(editUrl, '_blank');
        }
    }).catch(() => {
        prompt(`Copy this ID and add it to your Google Sheet:`, restaurantId);
        window.open(editUrl, '_blank');
    });
}

function toggleTriedStatus(restaurantId) {
    const tried = getTriedRestaurants();
    const index = tried.indexOf(restaurantId);
    
    if (index === -1) {
        tried.push(restaurantId);
    } else {
        tried.splice(index, 1);
    }
    
    saveTriedRestaurants(tried);
    renderRestaurants();
    filterRestaurants();
}

// Fetch restaurants from static JSON or backend API
async function fetchRestaurants() {
    const grid = document.getElementById('restaurant-grid');
    grid.innerHTML = `
        <div class="loading">
            <div class="loading-spinner"></div>
            <p>Loading restaurants...</p>
        </div>
    `;
    
    try {
        const url = USE_STATIC_DATA ? STATIC_DATA_URL : `${API_BASE_URL}/restaurants`;
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Transform data to our format and filter out removed restaurants
        restaurants = data.restaurants
            .map(transformYelpData)
            .filter(r => !isRestaurantRemoved(r.id));
        
        // Update cuisine filter options based on actual data
        updateCuisineOptions();
        
        renderRestaurants();
        
    } catch (error) {
        console.error('Error fetching restaurants:', error);
        grid.innerHTML = `
            <div class="error-message">
                <h3>⚠️ Could not load restaurants</h3>
                <p>${error.message}</p>
                <button onclick="fetchRestaurants()" class="retry-btn">Retry</button>
            </div>
        `;
    }
}

// Transform Yelp API data to our format
function transformYelpData(yelpBusiness) {
    // Handle both live API format and static JSON format
    const hoursData = Array.isArray(yelpBusiness.hours) ? yelpBusiness.hours : [];
    const hours = parseYelpHours(hoursData);
    const tags = generateTags(hours);
    
    // Categories can be array of strings or array of objects
    const categories = yelpBusiness.categories || [];
    const categoryNames = categories.map(c => typeof c === 'string' ? c : c.title || c);
    const cuisine = (categoryNames[0] || 'restaurant').toLowerCase().replace(/\s+/g, '-');
    
    return {
        id: yelpBusiness.id,
        name: yelpBusiness.name,
        cuisine: cuisine,
        cuisineDisplay: categoryNames.join(', '),
        address: yelpBusiness.address,
        phone: yelpBusiness.phone,
        hours: hours,
        tags: tags,
        rating: yelpBusiness.rating,
        reviewCount: yelpBusiness.review_count,
        price: yelpBusiness.price,
        imageUrl: yelpBusiness.image_url,
        yelpUrl: yelpBusiness.url,
        isClosed: yelpBusiness.is_closed
    };
}

// Parse Yelp hours format to our format
function parseYelpHours(yelpHours) {
    const daysMap = {
        0: 'monday',
        1: 'tuesday', 
        2: 'wednesday',
        3: 'thursday',
        4: 'friday',
        5: 'saturday',
        6: 'sunday'
    };
    
    const hours = {
        monday: 'Closed',
        tuesday: 'Closed',
        wednesday: 'Closed',
        thursday: 'Closed',
        friday: 'Closed',
        saturday: 'Closed',
        sunday: 'Closed'
    };
    
    if (!yelpHours || !yelpHours[0] || !yelpHours[0].open) {
        return hours;
    }
    
    yelpHours[0].open.forEach(slot => {
        const day = daysMap[slot.day];
        const start = formatYelpTime(slot.start);
        const end = formatYelpTime(slot.end);
        
        if (hours[day] === 'Closed') {
            hours[day] = `${start} - ${end}`;
        } else {
            // Multiple time slots (e.g., lunch and dinner)
            hours[day] += `, ${start} - ${end}`;
        }
    });
    
    return hours;
}

// Format Yelp time (HHMM) to readable format
function formatYelpTime(time) {
    const hours = parseInt(time.substring(0, 2));
    const minutes = time.substring(2);
    const period = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours > 12 ? hours - 12 : (hours === 0 ? 12 : hours);
    return `${displayHours}:${minutes} ${period}`;
}

// Generate tags based on hours
function generateTags(hours) {
    const tags = [];
    
    for (const [day, timeStr] of Object.entries(hours)) {
        if (timeStr === 'Closed') continue;
        
        const times = timeStr.split(', ');
        times.forEach(time => {
            const parts = time.split(' - ');
            if (parts.length !== 2) return;
            
            const openTime = parseTime(parts[0]);
            const closeTime = parseTime(parts[1]);
            
            if (openTime !== null) {
                if (openTime <= 10 * 60) tags.push('breakfast');
                if (openTime <= 14 * 60 && closeTime >= 12 * 60) tags.push('lunch');
                if (closeTime >= 17 * 60 || closeTime < 6 * 60) tags.push('dinner');
                if (closeTime >= 22 * 60 || closeTime < 6 * 60) tags.push('late-night');
            }
        });
    }
    
    return [...new Set(tags)]; // Remove duplicates
}

// Update cuisine dropdown based on actual data
function updateCuisineOptions() {
    const cuisines = [...new Set(restaurants.map(r => r.cuisine))].sort();
    const select = document.getElementById('cuisine-select');
    
    // Keep "All Cuisines" option
    select.innerHTML = '<option value="all">All Cuisines</option>';
    
    cuisines.forEach(cuisine => {
        const option = document.createElement('option');
        option.value = cuisine;
        option.textContent = cuisine.split('-').map(w => 
            w.charAt(0).toUpperCase() + w.slice(1)
        ).join(' ');
        select.appendChild(option);
    });
}

// Days of the week
const daysOfWeek = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
const daysDisplay = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

// Get current day and time
function getCurrentDay() {
    return daysOfWeek[new Date().getDay()];
}

function getCurrentTime() {
    return new Date();
}

// Parse time string to comparable format
function parseTime(timeStr) {
    if (!timeStr || timeStr === 'Closed') return null;
    
    const match = timeStr.match(/(\d{1,2}):(\d{2})\s*(AM|PM)/i);
    if (!match) return null;
    
    let hours = parseInt(match[1]);
    const minutes = parseInt(match[2]);
    const period = match[3].toUpperCase();
    
    if (period === 'PM' && hours !== 12) hours += 12;
    if (period === 'AM' && hours === 12) hours = 0;
    
    return hours * 60 + minutes;
}

// Check if restaurant is currently open
function isOpen(restaurant) {
    const currentDay = getCurrentDay();
    const hoursStr = restaurant.hours[currentDay];
    
    if (!hoursStr || hoursStr === 'Closed') return false;
    
    const parts = hoursStr.split(' - ');
    if (parts.length !== 2) return false;
    
    const openTime = parseTime(parts[0]);
    let closeTime = parseTime(parts[1]);
    
    if (openTime === null || closeTime === null) return false;
    
    // Handle times past midnight
    if (closeTime < openTime) {
        closeTime += 24 * 60;
    }
    
    const now = new Date();
    let currentMinutes = now.getHours() * 60 + now.getMinutes();
    
    // Check if we're past midnight but before close
    if (closeTime > 24 * 60 && currentMinutes < openTime) {
        currentMinutes += 24 * 60;
    }
    
    return currentMinutes >= openTime && currentMinutes < closeTime;
}

// Create restaurant card HTML
function createRestaurantCard(restaurant) {
    const currentDay = getCurrentDay();
    const openStatus = isOpen(restaurant);
    
    const hoursListHTML = daysOfWeek.map((day, index) => {
        const isToday = day === currentDay;
        return `
            <li class="${isToday ? 'today' : ''}">
                <span class="day">${daysDisplay[index]}</span>
                <span class="time">${restaurant.hours[day]}</span>
            </li>
        `;
    }).join('');

    // Rating stars
    const ratingStars = restaurant.rating ? 
        `<div class="rating">
            <span class="stars">${'★'.repeat(Math.round(restaurant.rating))}${'☆'.repeat(5 - Math.round(restaurant.rating))}</span>
            <span class="rating-text">${restaurant.rating} (${restaurant.reviewCount || 0})</span>
        </div>` : '';

    // Price display
    const priceDisplay = restaurant.price ? `<span class="price-tag">${restaurant.price}</span>` : '';
    
    // Tried status
    const isTried = isRestaurantTried(restaurant.id);
    
    return `
        <div class="restaurant-card ${isTried ? 'tried' : ''}" data-cuisine="${restaurant.cuisine}" data-tags="${restaurant.tags.join(',')}" data-open="${openStatus}" data-tried="${isTried}" data-id="${restaurant.id}">
            ${restaurant.imageUrl ? `<div class="card-image" style="background-image: url('${restaurant.imageUrl}')"></div>` : ''}
            <div class="card-header">
                <h2>${restaurant.name}</h2>
                <div class="card-meta">
                    <span class="cuisine-tag">${restaurant.cuisineDisplay || restaurant.cuisine}</span>
                    ${priceDisplay}
                </div>
                ${ratingStars}
            </div>
            <div class="card-body">
                <div class="status-badge ${openStatus ? 'open' : 'closed'}">
                    ${openStatus ? 'Open Now' : 'Closed'}
                </div>
                <ul class="hours-list">
                    ${hoursListHTML}
                </ul>
            </div>
            <div class="card-footer">
                <div class="address">📍 ${restaurant.address}</div>
                ${restaurant.phone ? `<a href="tel:${restaurant.phone}" class="phone">📞 ${restaurant.phone}</a>` : ''}
                ${restaurant.yelpUrl ? `<a href="${restaurant.yelpUrl}" target="_blank" class="yelp-link">View on Yelp →</a>` : ''}
                <div class="card-actions">
                    <button class="tried-toggle ${isTried ? 'is-tried' : ''}" onclick="toggleTriedStatus('${restaurant.id}')">
                        ${isTried ? '✓ Tried' : 'Mark as Tried'}
                    </button>
                    <button class="remove-btn" onclick="removeRestaurant('${restaurant.id}', '${restaurant.name.replace(/'/g, "\\'").replace(/"/g, '')}', event)" title="Remove from list">
                        ✕
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Render all restaurants
function renderRestaurants(filteredRestaurants = restaurants) {
    const grid = document.getElementById('restaurant-grid');
    
    if (filteredRestaurants.length === 0) {
        grid.innerHTML = `
            <div class="no-results">
                <h3>No restaurants found</h3>
                <p>Try adjusting your filters or search term.</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = filteredRestaurants.map(createRestaurantCard).join('');
}

// Filter restaurants
function filterRestaurants() {
    const searchTerm = document.getElementById('search').value.toLowerCase();
    const cuisineFilter = document.getElementById('cuisine-select').value;
    const activeFilter = document.querySelector('.filter-btn.active').dataset.filter;
    const triedFilter = document.querySelector('.tried-btn.active')?.dataset.tried || 'all';
    
    let filtered = restaurants.filter(restaurant => {
        // Search filter
        const matchesSearch = restaurant.name.toLowerCase().includes(searchTerm) ||
                             restaurant.cuisine.toLowerCase().includes(searchTerm) ||
                             restaurant.address.toLowerCase().includes(searchTerm);
        
        // Cuisine filter
        const matchesCuisine = cuisineFilter === 'all' || restaurant.cuisine === cuisineFilter;
        
        // Time/tag filter
        let matchesTag = true;
        if (activeFilter === 'open-now') {
            matchesTag = isOpen(restaurant);
        } else if (activeFilter !== 'all') {
            matchesTag = restaurant.tags.includes(activeFilter);
        }
        
        // Tried filter
        let matchesTried = true;
        if (triedFilter === 'tried') {
            matchesTried = isRestaurantTried(restaurant.id);
        } else if (triedFilter === 'not-tried') {
            matchesTried = !isRestaurantTried(restaurant.id);
        }
        
        return matchesSearch && matchesCuisine && matchesTag && matchesTried;
    });
    
    renderRestaurants(filtered);
}

// Update current time display
function updateTimeDisplay() {
    const now = new Date();
    const dayDisplay = document.getElementById('current-day');
    const timeDisplay = document.getElementById('current-time');
    
    dayDisplay.textContent = now.toLocaleDateString('en-US', { weekday: 'long' });
    timeDisplay.textContent = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
}

// Event listeners
document.addEventListener('DOMContentLoaded', async () => {
    // Fetch removed restaurants first (from Google Sheet)
    await fetchRemovedRestaurants();
    
    // Fetch restaurants from Yelp API via backend
    fetchRestaurants();
    updateTimeDisplay();
    
    // Update time every minute
    setInterval(updateTimeDisplay, 60000);
    
    // Refresh open/closed status every minute
    setInterval(() => {
        if (restaurants.length > 0) {
            renderRestaurants();
        }
    }, 60000);
    
    // Search input
    document.getElementById('search').addEventListener('input', filterRestaurants);
    
    // Cuisine select
    document.getElementById('cuisine-select').addEventListener('change', filterRestaurants);
    
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterRestaurants();
        });
    });
    
    // Tried filter buttons
    document.querySelectorAll('.tried-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tried-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterRestaurants();
        });
    });
});
