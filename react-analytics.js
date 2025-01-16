import React from "react";
import ReactDOM from "react-dom/client";
import { Analytics } from "@vercel/analytics/react";

// React Component
const App = () => <Analytics />;

// Mount React into the target div
const root = ReactDOM.createRoot(document.getElementById("react-root"));
root.render(<App />);
