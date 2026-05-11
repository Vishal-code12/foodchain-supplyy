// src/pages/Home.jsx
import React from "react";
import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div className="home-container">
      <h1>🌾 Welcome to FoodChain Supply</h1>
      <p>Track your crops securely from Farmer to Customer</p>
      <div className="buttons">
        <Link to="/farmer" className="btn">Farmer</Link>
        <Link to="/retailer" className="btn">Retailer</Link>
        <Link to="/distributor" className="btn">Distributor</Link>
        <Link to="/customer" className="btn">Customer</Link>
      </div>
    </div>
  );
};

export default Home;
