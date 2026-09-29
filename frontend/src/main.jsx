import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import { ThemeProvider } from "./context/ThemeContext.jsx";
import { AnalysisProvider } from "./context/AnalysisContext.jsx";
import { ToastProvider } from "./context/ToastContext.jsx";
import "./styles/index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ThemeProvider>
      <ToastProvider>
        <AnalysisProvider>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </AnalysisProvider>
      </ToastProvider>
    </ThemeProvider>
  </React.StrictMode>
);
