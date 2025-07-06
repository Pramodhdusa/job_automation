  import React, { useState } from 'react';
  import './index.css'

  const SkillsForm = () => {
    const [email, setEmail] = useState('');
    const [skills, setSkills] = useState({
      deepLearning: false,
      machineLearning: false,
      computerscience: false,
      generativeAi: false,
      softwareEngineering: false,
      computervision: false,
      python: false,
      BusinessAnalytics: false,
      webdeveloper: false,
      Bigdata: false
    });

    const [resume, setResume] = useState(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isSubmittingResume, setIsSubmittingResume] = useState(false);
    const [message, setMessage] = useState('');
    const [resumeMessage, setResumeMessage] = useState('');

    const handleCheckboxChange = (skillName) => {
      setSkills((prev) => ({
        ...prev,
        [skillName]: !prev[skillName],
      }));
    };

    const handleResumeChange = (e) => {
      setResume(e.target.files[0]);
    };

    const handleSkillsSubmit = async () => {
      if (!email) {
       setMessage('Please enter your email.');
         return;
       }
      setIsSubmitting(true);
      setMessage('');

      const selectedSkills = Object.keys(skills).filter((skill) => skills[skill]);
      // const token = localStorage.getItem('token'); 

      try {
        const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
         },
        body: JSON.stringify({
          email: email,
           skills: selectedSkills
         })
       });

      if (response.ok) {
         const data = await response.json();
       setMessage('Skills and email submitted successfully!');
         console.log('Response:', data);
      } else {
        throw new Error('Failed to submit');
       }

        // Reset form after successful submission
        setEmail(' ')
        setSkills({
          deepLearning: false,
          machineLearning: false,
          computerscience: false,
          generativeAi: false,
          softwareEngineering: false,
          computervision: false,
          python: false,
          BusinessAnalytics: false,
          webdeveloper: false,
          Bigdata: false
        });

      } catch (error) {
        setMessage('Error submitting skills. Please try again.');
        console.error('Error:', error);
      } finally {
        setIsSubmitting(false);
      }
    };

    const handleResumeSubmit = async () => {
      if (!resume) {
        setResumeMessage('Please select a resume file.');
        return;
      }

      setIsSubmittingResume(true);
      setResumeMessage('');

      const formData = new FormData();
      formData.append('resume', resume);

      try {
        const response = await fetch('http://localhost:5000/upload-resume', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const data = await response.json();
          setResumeMessage('Resume uploaded successfully!');
          console.log('Response:', data);
        } else {
          throw new Error('Failed to upload resume');
        }

        setResume(null);
        document.getElementById('resume-input').value = '';

      } catch (error) {
        setResumeMessage('Error uploading resume. Please try again.');
        console.error('Error:', error);
      } finally {
        setIsSubmittingResume(false);
      }
    };

  const styles = {
    container: {
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f0f9ff 0%, #e0e7ff 100%)',
      padding: '3rem 1rem',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif'
    },
    wrapper: {
      maxWidth: '1200px',
      margin: '0 auto'
    },
    titleSection: {
      textAlign: 'center',
      marginBottom: '3rem'
    },
    mainTitle: {
      fontSize: '2.5rem',
      fontWeight: 'bold',
      color: '#1f2937',
      marginBottom: '1rem'
    },
    subtitle: {
      color: '#6b7280',
      fontSize: '1.125rem'
    },
    grid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
      gap: '2rem'
    },
    card: {
      background: 'white',
      borderRadius: '1rem',
      boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
      padding: '2rem',
      border: '1px solid #e5e7eb'
    },
    cardHeader: {
      textAlign: 'center',
      marginBottom: '1.5rem'
    },
    icon: {
      width: '4rem',
      height: '4rem',
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      margin: '0 auto 1rem'
    },
    iconBlue: {
      backgroundColor: '#dbeafe'
    },
    iconGreen: {
      backgroundColor: '#dcfce7'
    },
    iconSvg: {
      width: '2rem',
      height: '2rem'
    },
    iconSvgBlue: {
      color: '#2563eb'
    },
    iconSvgGreen: {
      color: '#16a34a'
    },
    cardTitle: {
      fontSize: '1.5rem',
      fontWeight: 'bold',
      color: '#1f2937',
      marginBottom: '0.5rem'
    },
    cardDescription: {
      color: '#6b7280'
    },
    formSection: {
      display: 'flex',
      flexDirection: 'column',
      gap: '1.5rem'
    },
    formGroup: {
      display: 'flex',
      flexDirection: 'column'
    },
    label: {
      display: 'block',
      color: '#374151',
      fontWeight: '500',
      marginBottom: '0.75rem'
    },
    input: {
      width: '100%',
      padding: '0.75rem 1rem',
      border: '1px solid #d1d5db',
      borderRadius: '0.5rem',
      fontSize: '1rem',
      transition: 'all 0.2s',
      outline: 'none'
    },
    fileInput: {
      width: '100%',
      padding: '0.75rem 1rem',
      border: '2px dashed #d1d5db',
      borderRadius: '0.5rem',
      cursor: 'pointer',
      transition: 'all 0.2s'
    },
    fileName: {
      marginTop: '0.5rem',
      fontSize: '0.875rem',
      color: '#6b7280'
    },
    checkboxGroup: {
  display: 'grid',
  gridTemplateColumns: 'repeat(2, 1fr)',
  gap: '0.75rem'
},
checkboxItem: {
  display: 'flex',
  alignItems: 'center',
  gap: '0.75rem',
  padding: '0.75rem',
  borderRadius: '0.5rem',
  cursor: 'pointer',
  transition: 'background-color 0.2s'
},
checkbox: {
  width: '1.25rem',
  height: '1.25rem',
  accentColor: '#16a34a'
},
checkboxLabel: {
  color: '#374151',
  fontWeight: '500',
  textTransform: 'capitalize'
}
,
    button: {
      width: '100%',
      padding: '0.75rem 1.5rem',
      border: 'none',
      borderRadius: '0.5rem',
      fontWeight: '500',
      fontSize: '1rem',
      cursor: 'pointer',
      transition: 'all 0.2s',
      transform: 'translateY(0)'
    },
    buttonBlue: {
      backgroundColor: '#2563eb',
      color: 'white'
    },
    buttonGreen: {
      backgroundColor: '#16a34a',
      color: 'white'
    },
    buttonDisabled: {
      opacity: '0.5',
      cursor: 'not-allowed'
    },
    message: {
      padding: '1rem',
      borderRadius: '0.5rem',
      border: '1px solid'
    },
    messageSuccess: {
      backgroundColor: '#f0fdf4',
      color: '#166534',
      borderColor: '#bbf7d0'
    },
    messageError: {
      backgroundColor: '#fef2f2',
      color: '#dc2626',
      borderColor: '#fecaca'
    }
    

  };

  return (
    <div style={styles.container}>
      <div style={styles.wrapper}>
        <div style={styles.titleSection}>
          <h1 style={styles.mainTitle}>Submit Your Skills</h1>
          <p style={styles.subtitle}>Choose your preferred method to get personalized job recommendations</p>
        </div>

        <div style={styles.grid}>
          {/* Resume Upload Section */}
          <div style={styles.card}>
            <div style={styles.cardHeader}>
              <div style={{ ...styles.icon, ...styles.iconBlue }}>
                <svg style={{ ...styles.iconSvg, ...styles.iconSvgBlue }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h2 style={styles.cardTitle}>Upload Resume</h2>
              <p style={styles.cardDescription}>Let AI analyze your resume automatically</p>
            </div>

            <div style={styles.formSection}>
              <div style={styles.formGroup}>
                <label style={styles.label}>Select Resume File</label>
                <input
                  id="resume-input"
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={handleResumeChange}
                  style={styles.fileInput}
                />
                {resume && (
                  <div style={styles.fileName}>
                    Selected: {resume.name}
                  </div>
                )}
              </div>

              <button
                type="button"
                onClick={handleResumeSubmit}
                disabled={isSubmittingResume || !resume}
                style={{
                  ...styles.button,
                  ...styles.buttonBlue,
                  ...(isSubmittingResume || !resume ? styles.buttonDisabled : {}),
                }}
              >
                {isSubmittingResume ? 'Uploading...' : 'Upload Resume'}
              </button>

              {resumeMessage && (
                <div style={{
                  ...styles.message,
                  ...(resumeMessage.includes('Error') ? styles.messageError : styles.messageSuccess),
                }}>
                  {resumeMessage}
                </div>
              )}
            </div>
          </div>

          {/* Skills Selection Section */}
          <div style={styles.card}>
            <div style={styles.cardHeader}>
              <div style={{ ...styles.icon, ...styles.iconGreen }}>
                <svg style={{ ...styles.iconSvg, ...styles.iconSvgGreen }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <h2 style={styles.cardTitle}>Manual Selection</h2>
              <p style={styles.cardDescription}>Choose your skills manually</p>
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Select Your Skills</label>
              {/*  */}
              <div className="form-group">
              <label className="form-label">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="form-input"
                required
              />
              </div>


              {/*  */}
              <div style={styles.checkboxGroup}>
                {Object.keys(skills).map((skill) => (
                  <label
                    key={skill}
                    style={styles.checkboxItem}
                    onMouseEnter={(e) => e.target.style.backgroundColor = '#f9fafb'}
                    onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
                  >
                    <input
                      type="checkbox"
                      checked={skills[skill]}
                      onChange={() => handleCheckboxChange(skill)}
                      style={styles.checkbox}
                    />
                    <span style={styles.checkboxLabel}>
                      {skill.replace(/([A-Z])/g, ' $1').trim()}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <button
              type="button"
              onClick={handleSkillsSubmit}
              disabled={isSubmitting}
              style={{
                ...styles.button,
                ...styles.buttonGreen,
                ...(isSubmitting ? styles.buttonDisabled : {}),
              }}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Skills'}
            </button>

            {message && (
              <div style={{
                ...styles.message,
                ...(message.includes('Error') ? styles.messageError : styles.messageSuccess),
              }}>
                {message}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SkillsForm;




// import React, { useState } from 'react';

// const SkillsForm = () => {
//   const [email, setEmail] = useState('');
//   const [skills, setSkills] = useState({
//     softwareDevelopment: false,
//     machineLearning: false,
//     deepLearning: false,
//     generativeAI: false,
//     softwareEngineering: false
//   });
  
//   const [isSubmitting, setIsSubmitting] = useState(false);
//   const [message, setMessage] = useState('');

//   const handleCheckboxChange = (skillName) => {
//     setSkills(prev => ({
//       ...prev,
//       [skillName]: !prev[skillName]
//     }));
//   };

//   const handleSubmit = async () => {
//     if (!email) {
//       setMessage('Please enter your email.');
//       return;
//     }

//     setIsSubmitting(true);
//     setMessage('');

//     // Extract only selected skills
//     const selectedSkills = Object.keys(skills).filter(skill => skills[skill]);

//     try {
//       const response = await fetch('http://localhost:5000/predict', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({
//           email: email,
//           skills: selectedSkills
//         })
//       });

//       if (response.ok) {
//         const data = await response.json();
//         setMessage('Skills and email submitted successfully!');
//         console.log('Response:', data);
//       } else {
//         throw new Error('Failed to submit');
//       }

//       // Reset form after successful submission
//       setEmail('');
//       setSkills({
//         softwareDevelopment: false,
//         machineLearning: false,
//         deepLearning: false,
//         generativeAI: false,
//         softwareEngineering: false
//       });

//     } catch (error) {
//       setMessage('Error submitting form. Please try again.');
//       console.error('Error:', error);
//     } finally {
//       setIsSubmitting(false);
//     }
//   };

//   return (
//     <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-md">
//       <h2 className="text-2xl font-bold mb-6 text-gray-800">Subscribe for Job Alerts</h2>

//       <div onSubmit={handleSubmit} className="space-y-4">
//         {/* Email input */}
//         <div>
//           <label className="block text-gray-700 mb-2">Email Address</label>
//           <input
//             type="email"
//             value={email}
//             onChange={(e) => setEmail(e.target.value)}
//             placeholder="you@example.com"
//             className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
//             required
//           />
//         </div>

//         {/* Skills checkboxes */}
//         <div className="space-y-3">
//           {Object.keys(skills).map(skill => (
//             <label key={skill} className="flex items-center space-x-3 cursor-pointer">
//               <input
//                 type="checkbox"
//                 checked={skills[skill]}
//                 onChange={() => handleCheckboxChange(skill)}
//                 className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
//               />
//               <span className="text-gray-700 capitalize">{skill.replace(/([A-Z])/g, ' $1')}</span>
//             </label>
//           ))}
//         </div>

//         <button
//           type="button"
//           onClick={handleSubmit}
//           disabled={isSubmitting}
//           className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
//         >
//           {isSubmitting ? 'Submitting...' : 'Submit Preferences'}
//         </button>

//         {message && (
//           <div className={`mt-4 p-3 rounded-md ${
//             message.includes('Error') 
//               ? 'bg-red-100 text-red-700 border border-red-300' 
//               : 'bg-green-100 text-green-700 border border-green-300'
//           }`}>
//             {message}
//           </div>
//         )}
//       </div>
//     </div>
//   );
// };

// export default SkillsForm;
