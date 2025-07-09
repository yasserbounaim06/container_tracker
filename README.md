# Container Tracking System

A modern web application for tracking and managing shipping containers, featuring computer vision-based container detection and management capabilities.

![Dashboard Preview](frontend/containers/src/assets/images/dashboard-preview.png)

## Features

- 🚢 Real-time container tracking and management
- 📸 Image upload and processing with YOLO object detection
- 📊 Interactive dashboard with container statistics
- 🔍 Search and filter containers
- 📱 Responsive design for desktop and mobile
- 🔄 RESTful API integration with Flask backend

## Tech Stack

### Frontend
- Angular 20
- TypeScript
- Angular Material
- RxJS for state management
- SCSS for styling

### Backend
- Python Flask
- YOLO (You Only Look Once) for object detection
- RESTful API architecture

## Prerequisites

- Node.js (v18 or higher)
- npm (v9 or higher)
- Angular CLI
- Python 3.8+
- pip (Python package manager)

## Getting Started

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend/containers
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   ng serve
   ```

4. Open your browser and navigate to `http://localhost:4200`

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd Backend
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the Flask server:
   ```bash
   python app.py
   ```

## Project Structure

```
├── frontend/                  # Frontend Angular application
│   └── containers/            # Main Angular project
│       ├── src/
│       │   ├── app/          # Application components and modules
│       │   │   ├── container-create/  # Container creation component
│       │   │   ├── container-list/    # Container listing component
│       │   │   ├── container-update/  # Container update component
│       │   │   ├── models/            # Data models
│       │   │   └── services/          # API services
│       │   └── assets/       # Static assets
│       └── ...
├── Backend/                  # Flask backend
│   ├── app.py               # Main application file
│   ├── requirements.txt     # Python dependencies
│   └── ...
└── README.md                # This file
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Flask
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database
DATABASE_URI=sqlite:///containers.db

# API Configuration
API_BASE_URL=http://localhost:5000/api
```

## Deployment

### Production Build

1. Build the Angular application for production:
   ```bash
   cd frontend/containers
   ng build --configuration production
   ```

2. The production files will be available in the `dist/containers` directory.

### Deployment Options

#### Option 1: GitHub Pages

1. Install the Angular CLI GitHub Pages package:
   ```bash
   ng add angular-cli-ghpages
   ```

2. Deploy to GitHub Pages:
   ```bash
   ng deploy --base-href=/REPOSITORY_NAME/
   ```

#### Option 2: Netlify

Push your code to a Git repository and connect it to Netlify. The `netlify.toml` file is already configured.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/containers` | GET | Get all containers |
| `/api/containers` | POST | Create a new container |
| `/api/containers/:id` | GET | Get a specific container |
| `/api/containers/:id` | PUT | Update a container |
| `/api/containers/:id` | DELETE | Delete a container |
| `/api/detect` | POST | Process image for container detection |

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Angular](https://angular.io/)
- [Flask](https://flask.palletsprojects.com/)
- [YOLO](https://pjreddie.com/darknet/yolo/)
- [Angular Material](https://material.angular.io/)
