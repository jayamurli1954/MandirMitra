import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);


if (process.env.NODE_ENV === 'production' && 'serviceWorker' in navigator) {
  const swUrl = `${process.env.PUBLIC_URL}/service-worker.js`;
  window.addEventListener('load', () => {
    navigator.serviceWorker.register(swUrl).catch((err) => {
      // Keep runtime stable if SW registration fails.
      // eslint-disable-next-line no-console
      console.error('Service worker registration failed:', err);
    });
  });
}

