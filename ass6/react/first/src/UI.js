import React, { Component } from "react";
import { Link } from "react-router-dom";
import "./ui.css";

class UI extends Component {
  render() {
    return (
      <div className="about-page">
        <div className="info-card">
          <h1>Facebook</h1>
          <p>
            Facebook is a social media platform that connects people around the world. 
            Users can share photos, videos, messages, and stay in touch with friends and family.
          </p>
          <h3>Key Features</h3>
          <ul>
            <li>Connect with friends</li>
            <li>Share photos and videos</li>
            <li>Chat and video calls</li>
            <li>Join groups and communities</li>
          </ul>
          <p className="footer-text">Founded by Mark Zuckerberg in 2004.</p>
          <Link to="/" className="nav-link">
            Back to Home
          </Link>
        </div>
      </div>
    );
  }
}

export default UI;
