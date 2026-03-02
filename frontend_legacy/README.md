# HF-Digital Twin Platform - Frontend

Modern React-based UI for the HF-Digital Twin Platform system.

## Features

- 🎨 Modern, responsive UI with custom color palette
- 📊 Interactive charts and visualizations
- 📄 Document upload (prescriptions & lab reports)
- 💊 Medication recommendations
- 🔄 Treatment scenario comparison
- 📈 Trajectory predictions

## Tech Stack

- React 18
- TypeScript
- Vite
- React Router
- Recharts (for visualizations)
- Lucide React (icons)
- Axios (API calls)

## Setup

### Install Dependencies

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The app will run on `http://localhost:3000`

### Build

```bash
npm run build
```

## API Configuration

The frontend is configured to connect to the backend API at `http://localhost:8000` by default.

To change the API URL, create a `.env` file:

```
VITE_API_URL=http://your-api-url:8000
```

## Color Palette

- **Base**: #2F3E46 (Slate Blue)
- **Highlight**: #00B4D8 (Electric Teal)
- **Positive**: #2ECC71 (Green)
- **Neutral**: #ADB5BD (Gray)
- **Negative**: #E63946 (Red)

## Pages

1. **Dashboard** - Overview and quick actions
2. **Recommendations** - Get personalized medication recommendations
3. **Documents** - Upload and parse prescriptions/lab reports
4. **Comparison** - Compare different treatment scenarios

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Page components
│   ├── services/       # API services
│   └── App.tsx         # Main app component
├── public/             # Static assets
└── package.json        # Dependencies
```

