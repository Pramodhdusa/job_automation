import React, { useState } from 'react';
import { UserPlus, X } from 'lucide-react';

function SignupForm({ onClose }) {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });
  // const [token, setToken] = useState(null);


  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log(formData);
    try {
      const response = await fetch('http://localhost:5000/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      console.log('Server Response:', data);
      if (response.ok) {
        alert('Account created successfully!');
        // localStorage.setItem('token', data.access_token);
        // setToken(data.access_token);
        // Close the form after successful signup
        onClose();
      } else {
        alert(data.error || 'Signup failed');
      }
      // Reset form data
      setFormData({
        username: '',
        email: '',
        password: ''
      });
    } catch (error) {
      console.error('Error:', error);
      alert('An error occurred. Please try again.');
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="container1">
      <div className="form-container1">
        <button className="close-button1" onClick={onClose}>
          <X className="close-icon1" />
        </button>
        <div className="header1">
          <h2>
            <UserPlus className="icon1" /> Create Account
          </h2>
        </div>
        <form onSubmit={handleSubmit} className="form1">
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            placeholder="Username"
            required
          />
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Email Address"
            required
          />
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Password"
            required
          />
          <button type="submit">Sign Up</button>
        </form>
        <p className="footer-text1">
          Already have an account? Sign in
        </p>
      </div>

    </div>
  );
}

export default SignupForm;