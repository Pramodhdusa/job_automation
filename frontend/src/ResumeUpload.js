import React, { useState } from 'react';

const ResumeUpload = () => {
  const [file, setFile] = useState(null);
  const [detectedSkills, setDetectedSkills] = useState([]);
  const [message, setMessage] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setMessage("");
    setDetectedSkills([]);
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage("Please select a PDF file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:5000/upload-resume/", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setDetectedSkills(result.detected_skills);
        setMessage(`Uploaded: ${result.filename}`);
      } else {
        setMessage(result.error || "An error occurred while uploading.");
      }

    } catch (error) {
      setMessage("Failed to connect to the server.");
      console.error(error);
    }
  };

  return (
    <div style={{ maxWidth: "500px", margin: "2rem auto", textAlign: "center" }}>
      <h2>Upload Your Resume (PDF)</h2>
      <input 
        type="file" 
        accept="application/pdf" 
        onChange={handleFileChange}
        style={{ margin: "1rem 0" }}
      />
      <button 
        onClick={handleUpload} 
        style={{ padding: "0.5rem 1.5rem", backgroundColor: "#16a34a", color: "#fff", border: "none", borderRadius: "0.5rem", cursor: "pointer" }}
      >
        Upload & Analyze
      </button>

      {message && <p style={{ marginTop: "1rem", color: "#333" }}>{message}</p>}

      {detectedSkills.length > 0 && (
        <div style={{ marginTop: "1.5rem", textAlign: "left" }}>
          <h3>Detected Skills:</h3>
          <ul>
            {detectedSkills.map((skill, index) => (
              <li key={index}>{skill}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ResumeUpload;
