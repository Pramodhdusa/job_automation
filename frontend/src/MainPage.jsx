import React, { useState } from 'react';
import './index.css';
import { useNavigate } from 'react-router-dom';
import SkillsForm from './HomePage';
import SignupForm from './SignUpForm';  // make sure this is imported

const MainPage = () => {
  const navigate = useNavigate();
  const [showSignup, setShowSignup] = useState(false); // modal visibility

  const openSignup = () => setShowSignup(true);
  const closeSignup = () => setShowSignup(false);

  return (
    <div className="index-container">
      <nav className="navbar">
        <div className="logo-container">
          <h1 className="logo">
            Smart<span className="logo-highlight">Jobs</span>
          </h1>
        </div>
        <div className="nav-buttons">
          <button className="nav-link">
            About
          </button>
          <button className="nav-link">
            Track Applications
          </button>
          <button
            className="nav-btn signup-btn"
            onClick={openSignup}   // show signup modal
          >
            Sign Up
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-text">
          <h1 className="hero-title">
            Track Your Job Applications
            <span className="highlight"> With AI Intelligence</span>
          </h1>
          <p className="hero-description">
            Never lose track of your job search again. Get AI-powered insights, automated follow-ups, and smart recommendations for your career journey.
          </p>
          <button className="hero-button" onClick={() => navigate("/skills-form")}>
            Start Tracking Now →
          </button>
        </div>

        <div className="hero-image">
          <img
            src="https://images.unsplash.com/photo-1586717791821-3f44a563fa4c?auto=format&fit=crop&q=80&w=800&h=600"
            alt="AI Job Application Tracking"
            className="rounded-lg shadow-lg"
          />
        </div>
      </div>

      {/* Modal signup form */}
      {showSignup && (
        <div className="modal-overlay">
          <div className="modal-content">
            <SignupForm onClose={closeSignup} />
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="footer">
        <p className="footer-text">© 2024 SmartJobs. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default MainPage;












// import React, { useState } from 'react';
// import './index.css';
// import { useNavigate } from 'react-router-dom';
// import SkillsForm from './HomePage';

// const MainPage = () => {
//     const navigate = useNavigate();
//   return (
//     <div className="index-container">
//       <nav className="navbar">
//         <div className="logo-container">
//           <h1 className="logo">
//             Smart<span className="logo-highlight">Jobs</span>
//           </h1>
//         </div>
//         <div className="nav-buttons">
//           <button className="nav-link" >
//             About
//           </button>
//           <button className="nav-link">
//             Track Applications
//           </button>
//           <button
//             className="nav-btn signup-btn"
//           >
//             Sign Up
//           </button>
//         </div>
//       </nav>

//       {/* Hero Section */}
//       <div className="hero-section">
//         <div className="hero-text">
//           <h1 className="hero-title">
//             Track Your Job Applications
//             <span className="highlight"> With AI Intelligence</span>
//           </h1>
//           <p className="hero-description">
//             Never lose track of your job search again. Get AI-powered insights, automated follow-ups, and smart recommendations for your career journey.
//           </p>
//           <button className="hero-button" onClick={() => navigate("/skills-form")} >
//             Start Tracking Now →
//           </button>
//         </div>

//         <div className="hero-image">
//           <img
//             src="https://images.unsplash.com/photo-1586717791821-3f44a563fa4c?auto=format&fit=crop&q=80&w=800&h=600"
//             alt="AI Job Application Tracking"
//             className="rounded-lg shadow-lg"
//           />
//         </div>
//       </div>

//       {/* Footer */}
//       <footer className="footer">
//         <p className="footer-text">© 2024 SmartJobs. All rights reserved.</p>
//       </footer>
//     </div>
//   );
// };

// export default MainPage;