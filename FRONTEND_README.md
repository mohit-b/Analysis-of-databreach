# 🛡️ CyberGuard - Beautiful Data Breach Activity Classifier

A stunning, girly web interface for the Data-Breach Activity Classifier with a beautiful pink theme and modern design.

## ✨ Features

### 🎨 Beautiful Design
- **Girly Pink Theme**: Soft pink gradients with lavender and mint accents
- **Modern UI**: Clean, responsive design with smooth animations
- **Interactive Elements**: Hover effects, loading spinners, and smooth transitions
- **Mobile Responsive**: Works perfectly on all devices

### 🔍 Single Activity Analysis
- **Real-time Classification**: Analyze individual activity records instantly
- **Multiple Input Formats**: Supports both CSV rows and JSON objects
- **Sample Data**: One-click loading of sample data for testing
- **Clear Results**: Beautiful result cards with status indicators

### 📊 Batch Processing
- **Drag & Drop Upload**: Intuitive file upload with drag and drop support
- **Multiple File Types**: Supports CSV and JSON Lines files
- **Header Detection**: Automatic header detection for CSV files
- **Statistics Dashboard**: Real-time statistics showing total, malicious, and error counts
- **Detailed Results**: Individual result cards for each processed activity

### 🎯 Smart Classification
- **Threat Detection**: Identifies various attack types including:
  - Unauthorized backup access
  - Path traversal attempts
  - Privilege escalation attempts
  - Suspicious login attempts
  - Malware upload attempts
  - SQL injection attempts
  - Network reconnaissance

## 🚀 Quick Start

### Option 1: Using Makefile
```bash
# Install dependencies
make install

# Start the beautiful web interface
make run-frontend
```

### Option 2: Direct Python
```bash
# Install Flask dependencies
pip install Flask Flask-CORS

# Start the interface
python start_cyberguard.py
```

### Option 3: Using the startup script
```bash
python start_cyberguard.py
```

## 🌐 Access the Interface

Once started, open your browser and go to:
**http://localhost:5001**

The interface will automatically open in your default browser!

## 💖 Interface Features

### 🎨 Visual Design
- **Color Scheme**: Pink gradients (#ff6b9d, #ff8fab) with lavender and mint accents
- **Typography**: Modern Poppins font family
- **Icons**: Font Awesome icons throughout the interface
- **Animations**: Smooth hover effects and loading animations

### 📱 Responsive Layout
- **Desktop**: Full-width layout with side-by-side cards
- **Tablet**: Optimized spacing and button layouts
- **Mobile**: Stacked layout with full-width buttons

### 🔔 User Experience
- **Notifications**: Beautiful toast notifications for all actions
- **Loading States**: Elegant loading spinners and overlays
- **Error Handling**: Clear error messages with helpful suggestions
- **Success Feedback**: Positive reinforcement for successful operations

## 🛠️ Technical Details

### Backend API
- **Flask Server**: RESTful API with CORS support
- **Endpoints**:
  - `GET /` - Main interface
  - `POST /api/classify` - Single activity classification
  - `POST /api/classify/batch` - Batch processing
  - `GET /api/sample-data` - Sample data for testing

### Frontend Technology
- **HTML5**: Semantic markup with accessibility features
- **CSS3**: Modern styling with gradients, animations, and responsive design
- **JavaScript**: Vanilla JS with ES6+ features
- **Font Awesome**: Beautiful icons throughout the interface

### File Structure
```
templates/
├── index.html          # Main interface template
static/
├── css/
│   └── style.css       # Beautiful girly styling
├── js/
│   └── app.js          # Frontend functionality
└── images/             # Future image assets
```

## 🎯 Usage Examples

### Single Activity Classification
1. Enter CSV data: `2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,"Mozilla/5.0",/login?backup.sql`
2. Click "Classify Activity"
3. View the beautiful result card with threat analysis

### Batch Processing
1. Drag and drop a CSV or JSON file
2. Check "First row is header" if applicable
3. Click "Process Batch"
4. View statistics and detailed results

### Sample Data
1. Click "Load Sample" to populate with test data
2. Click "Classify Activity" to see the classification in action

## 🎨 Customization

The interface is highly customizable through CSS variables:

```css
:root {
    --primary-pink: #ff6b9d;
    --secondary-pink: #ff8fab;
    --light-pink: #ffb3d1;
    --lavender: #c8a2c8;
    --mint: #a8e6cf;
    --peach: #ffd3a5;
}
```

## 🔧 Development

### Adding New Features
1. **Backend**: Add new endpoints in `app.py`
2. **Frontend**: Add new functionality in `static/js/app.js`
3. **Styling**: Update `static/css/style.css` for new elements

### Testing
```bash
# Run the integration test
python test_frontend_backend.py

# Run unit tests
make test
```

## 💖 Why This Interface is Special

- **Beautiful Design**: Carefully crafted with attention to detail
- **User-Friendly**: Intuitive interface that anyone can use
- **Professional**: Suitable for cybersecurity professionals
- **Fun**: Makes threat analysis enjoyable with its girly aesthetic
- **Functional**: All backend features are accessible through the interface

## 🎉 Conclusion

CyberGuard provides a beautiful, functional, and user-friendly interface for the Data-Breach Activity Classifier. The girly pink theme makes cybersecurity work more enjoyable while maintaining professional functionality.

**Made with 💖 for cybersecurity professionals who appreciate beautiful interfaces!**
