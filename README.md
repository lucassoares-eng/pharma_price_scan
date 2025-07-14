# Pharma Price Scanner

A web application and API for searching medicine prices across multiple Brazilian pharmacies using Selenium-based web scraping. Features unified product results, caching, and a simple web interface.

## Features

- **Shared Selenium Driver**: The driver is initialized once and reused by all scrapers
- **Automatic ChromeDriver Management**: Automatically checks and updates ChromeDriver as needed
- **Multiple Pharmacies**: Support for multiple pharmacies with independent scrapers
- **Web Interface**: Simple interface for searching medicines
- **REST API**: Programmatic search endpoint
- **Modular Architecture**: Flask blueprints for easy integration
- **Organized Static Files**: CSS and JavaScript separated
- **Search Cache**: Results for each pharmacy are cached for 24 hours to avoid repeated searches with the same terms. Cache is only used if the search terms are exactly the same. Unified product results are always recalculated and not cached.

## Project Structure

```
pharma_price_scan/
├── app.py                 # Main Flask application with blueprints
├── requirements.txt       # Python dependencies
├── integration_example.py # Example integration
├── pharma_integration.py  # Integration module
├── setup.py               # Package setup
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py   # Base class for all scrapers
│   ├── droga_raia.py     # Scraper for Droga Raia
│   ├── sao_joao.py       # Scraper for São João
│   └── example_scraper.py # Example scraper
├── static/
│   ├── css/
│   │   └── style.css     # CSS styles
│   └── js/
│       └── app.js        # JavaScript
└── templates/
    └── index.html         # Web interface
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pharma_price_scan
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Run the Application

```bash
python app.py
```

The app will be available at `http://localhost:5000`

### Available Endpoints

- `GET /`: Web interface for searching medicines
- `POST /api/pharma/search`: API for searching medicines (returns pharmacy and unified results)
- `POST /api/pharma/search_unified`: API for searching medicines (returns only unified results)
- `GET /api/pharma/health`: Check Selenium driver status
- `GET /api/pharma/cache/stats`: Get cache statistics
- `POST /api/pharma/cache/clear`: Clear expired cache files

#### Example API Usage

```bash
curl -X POST http://localhost:5000/api/pharma/search \
  -H "Content-Type: application/json" \
  -d '{"medicine_description": "ibuprofeno 600mg 20"}'
```

### Supported Pharmacies

- **Droga Raia**: https://www.drogaraia.com.br
- **São João**: https://www.saojoaofarmacias.com.br

## Cache Functionality

- **How it works:**
  - Each search term is cached per pharmacy for 24 hours.
  - If the same term is searched again within 24 hours, cached pharmacy results are used.
  - If the term is different or the cache is expired, a new search is performed.
  - Only raw pharmacy results are cached. Unified product results are always recalculated.
- **Cache endpoints:**
  - `GET /api/pharma/cache/stats`: Returns cache file count, valid/expired files, and size.
  - `POST /api/pharma/cache/clear`: Removes expired cache files.

## Integration in Other Flask Apps

### Method 1: Simple Integration

```python
from flask import Flask
from pharma_integration import integrate_pharma_scanner

app = Flask(__name__)

# Integrate Pharma Scanner
integration = integrate_pharma_scanner(app)

# Your existing routes
@app.route('/')
def home():
    return "My app"

if __name__ == '__main__':
    app.run(debug=True)
```

### Method 2: Custom Prefix Integration

```python
from flask import Flask
from pharma_integration import integrate_pharma_scanner

app = Flask(__name__)

# Integrate with custom prefix
integration = integrate_pharma_scanner(app, url_prefix='/medicines')

# Endpoints will be at:
# - /medicines/api/pharma/search
# - /medicines/api/pharma/health
# - /medicines/ (web interface)
```

### Method 3: Manual Integration

```python
from flask import Flask
from app import get_blueprints, init_driver, cleanup_global_driver
import atexit

app = Flask(__name__)

# Initialize driver
if init_driver():
    # Register blueprints
    pharma_blueprints = get_blueprints()
    for blueprint in pharma_blueprints:
        app.register_blueprint(blueprint)
    
    # Setup cleanup
    atexit.register(cleanup_global_driver)

# Your routes
@app.route('/')
def home():
    return "My app"
```

### Method 4: Using the Integration Class

```python
from flask import Flask
from pharma_integration import PharmaScannerIntegration

app = Flask(__name__)

# Create integration
integration = PharmaScannerIntegration(app)

# Register blueprints as needed
integration.register_blueprints(url_prefix='/pharma')

# Your routes
@app.route('/')
def home():
    return "My app"
```

## Adding New Scrapers

To add a new pharmacy scraper:

1. Create a new file in `scrapers/` (e.g., `scrapers/new_pharmacy.py`)
2. Implement the scraper class following the pattern:

```python
from .base_scraper import BaseScraper

class NewPharmacyScraper(BaseScraper):
    def __init__(self, driver=None):
        super().__init__(
            base_url="https://www.new-pharmacy.com",
            search_url="https://www.new-pharmacy.com/search",
            pharmacy_name="New Pharmacy",
            driver=driver  # Important: accept the shared driver
        )
    
    def search(self, medicine_description):
        # Implement search logic
        pass
    
    def _extract_products(self, soup):
        # Implement product extraction
        pass
```

## Running Tests

To run the cache tests:

```bash
python -m unittest tests/test_cache_manager.py
```

---

**Repository short description:**

> Search and compare medicine prices from multiple Brazilian pharmacies via web scraping. Features unified results, 24h cache, and a simple web/API interface.