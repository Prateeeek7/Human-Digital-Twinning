# Frontend Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### 3. Start Backend API

In a separate terminal:

```bash
# Make sure backend is running
uvicorn pdt.api.main:app --reload
```

## Features Implemented

### ✅ Dashboard
- Overview statistics
- Quick action cards
- System features showcase

### ✅ Medication Recommendations
- Patient information form
- Current medications management
- Real-time recommendations
- Trajectory visualizations
- Drug interaction warnings

### ✅ Document Upload
- Prescription upload & parsing
- Lab report upload & parsing
- OCR text extraction
- Automatic recommendations from documents

### ✅ Treatment Comparison
- Multiple scenario comparison
- Side-by-side benefit analysis
- Interactive charts
- Safety validation

## Color Palette

The UI uses the specified color palette:

- **Base (Slate Blue)**: #2F3E46
- **Highlight (Electric Teal)**: #00B4D8
- **Positive (Green)**: #2ECC71
- **Neutral (Gray)**: #ADB5BD
- **Negative (Red)**: #E63946

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout.tsx          # Main layout with navigation
│   │   ├── Card.tsx            # Reusable card component
│   │   ├── Button.tsx          # Button component
│   │   ├── Input.tsx           # Input component
│   │   └── RecommendationResults.tsx  # Results display
│   ├── pages/
│   │   ├── Dashboard.tsx       # Dashboard page
│   │   ├── Recommendations.tsx  # Recommendations page
│   │   ├── DocumentUpload.tsx  # Document upload page
│   │   └── TreatmentComparison.tsx  # Comparison page
│   ├── services/
│   │   └── api.ts              # API integration
│   ├── App.tsx                 # Main app component
│   └── main.tsx                # Entry point
├── package.json
└── vite.config.ts
```

## API Integration

The frontend connects to the backend API at `http://localhost:8000` by default.

All API calls are handled in `src/services/api.ts`:

- `recommendationsApi.getRecommendations()` - Get medication recommendations
- `recommendationsApi.compareScenarios()` - Compare treatment scenarios
- `documentsApi.uploadPrescription()` - Upload prescription
- `documentsApi.uploadLabReport()` - Upload lab report

## Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Environment Variables

Create a `.env` file in the `frontend/` directory:

```
VITE_API_URL=http://localhost:8000
```

## Features Coverage

✅ **All Backend Features Covered:**
- Patient information input
- Medication recommendations
- Treatment effect predictions
- Treatment scenario comparison
- Document upload (prescriptions & lab reports)
- OCR text extraction
- Drug interaction checking
- Trajectory visualizations
- Dosage optimization display

✅ **UI/UX Features:**
- Responsive design
- Modern, clean interface
- Interactive charts (Recharts)
- Loading states
- Error handling
- Form validation
- Drag & drop file upload

## Next Steps

1. Install dependencies: `npm install`
2. Start backend: `uvicorn pdt.api.main:app --reload`
3. Start frontend: `npm run dev`
4. Open browser: `http://localhost:3000`

The UI is fully functional and ready to use!



