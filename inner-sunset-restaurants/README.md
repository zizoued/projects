# Inner Sunset Restaurants - Hours & Days Guide

A beautiful webpage showing restaurant hours for San Francisco's Inner Sunset neighborhood, powered by the Yelp Fusion API.

## Features

- 🔍 Search restaurants by name, cuisine, or address
- 🏷️ Filter by meal time (Breakfast, Lunch, Dinner, Late Night)
- ✅ "Open Now" filter based on current time
- ⭐ Yelp ratings and reviews
- 📸 Restaurant photos from Yelp
- 📍 Address and phone links
- 🔗 Direct links to Yelp pages

## Setup

### 1. Get a Yelp API Key (Free)

1. Go to [Yelp Fusion API](https://www.yelp.com/developers/v3/manage_app)
2. Create an account or sign in
3. Create a new app to get your API key
4. The free tier includes 5,000 API calls per day

### 2. Install Dependencies

```bash
cd inner-sunset-restaurants
pip install -r requirements.txt
```

### 3. Set Your API Key

```bash
export YELP_API_KEY='your-api-key-here'
```

Or on Windows:
```cmd
set YELP_API_KEY=your-api-key-here
```

### 4. Start the Backend Server

```bash
python server.py
```

The server will run at `http://localhost:5001`

### 5. Open the Webpage

Open `index.html` in your browser, or use a local server:

```bash
# Using Python
python -m http.server 8000

# Then open http://localhost:8000
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/restaurants` | Fetch all Inner Sunset restaurants with hours |
| `GET /api/restaurant/<id>` | Get details for a specific restaurant |
| `GET /api/health` | Health check (shows if API key is set) |

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Backend**: Python Flask
- **API**: Yelp Fusion API

## Customization

To search a different neighborhood, edit `server.py` and change the location parameter:

```python
params = {
    'location': 'Your Neighborhood, City, State',
    ...
}
```

## Notes

- Restaurant hours are fetched live from Yelp and may occasionally be outdated
- The free Yelp API tier has a limit of 5,000 calls/day
- First load may take a few seconds as it fetches data for each restaurant
