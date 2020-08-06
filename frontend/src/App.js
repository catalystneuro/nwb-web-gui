import React from 'react'
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";
import './App.css';
import Index from "./pages/Index"
import NavigationBar from "./components/Navbar"

function App() {
  return (
    <Router>
      <NavigationBar />
      <Switch>

        <Route exact path="/index">
          <Index />
        </Route>
      </Switch>
    </Router>
  );
}

export default App;
