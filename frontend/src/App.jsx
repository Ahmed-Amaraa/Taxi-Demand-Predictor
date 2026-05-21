import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import TrainPage from './pages/TrainPage';
import ResultsPage from './pages/ResultsPage';
import ComparePage from './pages/ComparePage';
import PredictionPage from './pages/PredictionPage';
import './styles/App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <h1 className="logo">🚕 Taxi Demand Forecast</h1>
          <ul className="nav-links">
            <li><Link to="/">Entraîner</Link></li>
            <li><Link to="/results">Résultats</Link></li>
            <li><Link to="/compare">Comparaison</Link></li>
            <li><Link to="/predict">Prédire</Link></li>
          </ul>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<TrainPage />} />
            <Route path="/results" element={<ResultsPage />} />
            <Route path="/compare" element={<ComparePage />} />
            <Route path="/predict" element={<PredictionPage />} />
          </Routes>
        </main>

        <footer className="footer">
          <p>© 2026 Taxi Demand Forecast - ING4 Sem2</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;