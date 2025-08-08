# Carrigar by Tubematic

A modern manufacturing services website offering tube laser cutting, sheet laser cutting, CNC machining, VMC machining, and 3D printing services.

## Features

### Core Services
- **Tube Laser Cutting** - Precision cutting for tubular materials
- **Sheet Laser Cutting** - High-accuracy sheet metal cutting
- **CNC Machining** - Computer numerical control machining
- **VMC Machining** - Vertical machining center operations
- **3D Printing** - Additive manufacturing solutions

### Order Management
- **Small Orders** - Quick quotes with project numbers
- **Bulk Orders** - Enterprise manufacturing with engineer consultation
- **File Upload** - Secure file handling with customer-specific naming
- **Order Tracking** - Real-time order status updates

### User System
- **Authentication** - Email/password and Google OAuth login
- **Profile Management** - Individual and company profiles
- **GST Integration** - Business tax compliance
- **Address Management** - Personal and business addresses

### Content Pages
- **Services** - Detailed service descriptions with media
- **How It Works** - Process explanation and quality assurance
- **Become a Vendor** - Partnership opportunities and training

## Tech Stack

### Frontend
- **HTML5/CSS3/JavaScript** - Core web technologies
- **Bootstrap 5.3.0** - Responsive UI framework
- **Font Awesome 6.4.0** - Icon library
- **Google Fonts (Poppins)** - Typography

### Backend
- **Python 3.13** - Programming language
- **Django 5.2.4** - Web framework
- **SQLite** - Database (development)
- **Django ORM** - Database abstraction
- **Google OAuth 2.0** - Third-party authentication

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/h1t1er0/Carrigar.git
   cd Carrigar
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the website**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Environment Setup

### Google OAuth (Optional)
For Google login functionality, set up OAuth credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs
6. Update settings in `mywebsite/settings.py`

See `GOOGLE_OAUTH_SETUP.md` for detailed instructions.

## Project Structure

```
Carrigar/
├── accounts/                 # User authentication and profiles
│   ├── models.py            # UserProfile model
│   ├── views.py             # Auth views and profile management
│   ├── urls.py              # Auth URL patterns
│   └── templates/           # Auth templates
├── core/                    # Main application
│   ├── models.py            # Order and business models
│   ├── views.py             # Main views and API endpoints
│   ├── urls.py              # Main URL patterns
│   ├── templates/           # Main templates
│   └── static/              # Static files (CSS, JS, images)
├── mywebsite/               # Project settings
│   ├── settings.py          # Django configuration
│   └── urls.py              # Main URL configuration
├── media/                   # User uploaded files (gitignored)
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Key Features

### Modern UI/UX
- Clean, compartmentalized design
- Responsive layout for all devices
- Guided multi-step order forms
- Interactive service selection

### File Management
- Secure file uploads
- Customer-specific file naming
- Organized storage structure
- File type validation

### Business Logic
- Individual and company profiles
- GST number handling
- Order status tracking
- Project number generation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is proprietary software for Carrigar by Tubematic.

## Support

For technical support or business inquiries, contact the development team.
