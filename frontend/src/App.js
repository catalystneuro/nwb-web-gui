import React from 'react'
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";
import './App.css';
import Index from "./pages/Index"

function App() {
  return (
    <Router>
      <Switch>
        <Route exact path="/index">
          <Index />
        </Route>
      </Switch>
    </Router>
  );
}

export default App;
