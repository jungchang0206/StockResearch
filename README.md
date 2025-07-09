# Stock Research Tool

A modern, beautifully styled web application for researching stock financial data using SEC EDGAR filings.

## Features

- **Modern UI Design**: Clean, responsive interface with gradient backgrounds and smooth animations
- **Real-time Stock Data**: Fetch financial data from SEC EDGAR database
- **Interactive Charts**: Visualize key financial metrics over time
- **Key Metrics Display**: EPS, Revenue, and Gross Profit analysis
- **Mobile Responsive**: Works perfectly on desktop and mobile devices

## Styling Features

### Design Elements
- **Gradient Backgrounds**: Beautiful purple-blue gradient theme
- **Glass Morphism**: Semi-transparent containers with backdrop blur
- **Smooth Animations**: Hover effects and transitions throughout
- **Modern Typography**: Inter font family for clean readability
- **Card-based Layout**: Organized information in styled cards
- **Emoji Icons**: Visual indicators for different data types

### Color Scheme
- **Primary**: Purple-blue gradient (#667eea to #764ba2)
- **Secondary**: Green accents (#48bb78 to #38a169)
- **Neutral**: Gray tones (#2d3748, #4a5568, #718096)
- **Background**: Light gradients and white cards

### Interactive Elements
- **Hover Effects**: Cards lift and shadows intensify on hover
- **Focus States**: Input fields have smooth focus animations
- **Button Animations**: Buttons have press and hover effects
- **Loading States**: Spinner animations for loading feedback

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Enter a stock ticker symbol (e.g., AAPL, GOOGL, MSFT)
2. Click "Search Stock Data" to fetch financial information
3. View key metrics and interactive charts
4. Use "Search Another Stock" to analyze different companies

## File Structure

```
StockResearcher/
├── app.py                 # Flask application
├── stock_analysis.py      # Stock data analysis logic
├── static/
│   └── css/
│       └── styles.css     # Modern styling
├── templates/
│   ├── index.html         # Home page
│   └── results.html       # Results page
└── requirements.txt       # Python dependencies
```

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with modern design principles
- **Data**: SEC EDGAR API
- **Charts**: Matplotlib for data visualization
- **Fonts**: Google Fonts (Inter)

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Responsive Design

The application is fully responsive and optimized for:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (320px - 767px) 