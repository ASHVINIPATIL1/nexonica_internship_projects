import React, { useState } from "react";
import { Link } from "react-router-dom";
import "./Home.css";


class Home extends React.Component {
  state = {
    name: "",
    email: "",
    address: ""
  };

  handleChange = (e) => {
    this.setState({ [e.target.name]: e.target.value });
  };

  handleSubmit = (e) => {
    e.preventDefault();
    alert(
      `Name: ${this.state.name}\nEmail: ${this.state.email}\nAddress: ${this.state.address}`
    );
    this.setState({ name: "", email: "", address: "" });
  };

  render() {
    return (
      <div className="home-page">
        <div className="form-card">
          <h1>Contact Form</h1>
          <form onSubmit={this.handleSubmit}>
            <input
              type="text"
              name="name"
              placeholder="Name"
              value={this.state.name}
              onChange={this.handleChange}
              required
            />
            <input
              type="email"
              name="email"
              placeholder="Email"
              value={this.state.email}
              onChange={this.handleChange}
              required
            />
            <textarea
              name="address"
              placeholder="Address"
              value={this.state.address}
              onChange={this.handleChange}
              required
            />
            <button type="submit">Submit</button>
          </form>
          <Link to="/about" className="nav-link">
            Go to About Page
          </Link>
        </div>
      </div>
    );
  }
}

export default Home;
