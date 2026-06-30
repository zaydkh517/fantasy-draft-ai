import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import { Analytics } from "@vercel/analytics/react";

root.render(
  <React.StrictMode>
    <App />
    <Analytics />
  </React.StrictMode>
);
