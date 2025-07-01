import logo from './logo.svg';
import './App.css';
import { Routes, Route } from 'react-router-dom';
import SkillsForm from './HomePage';
import MainPage from './MainPage';
// import SignupForm from './SignUpForm';

function App() {
  return (
    <div className="App">
    <Routes>
      <Route path="/" element={<MainPage />} />
      <Route path="/skills-form" element={<SkillsForm />} />
      {/* <Route path="/signup" element={<SignupForm />} /> */}
    </Routes>
    {/* <ResumeUpload /> */}
    </div>
  );
}

export default App;
