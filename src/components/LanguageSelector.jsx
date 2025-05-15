import React from 'react';

const LanguageSelector = ({ selectedLanguage, onLanguageChange }) => {
  // List of supported Indian languages with their codes
  const languages = [
    { code: 'hi', name: 'Hindi' },
    { code: 'bn', name: 'Bengali' },
    { code: 'ta', name: 'Tamil' },
    { code: 'te', name: 'Telugu' },
    { code: 'mr', name: 'Marathi' },
    { code: 'gu', name: 'Gujarati' },
    { code: 'kn', name: 'Kannada' },
    { code: 'ml', name: 'Malayalam' },
    { code: 'pa', name: 'Punjabi' },
    { code: 'en', name: 'English' }
  ];

  const handleChange = (e) => {
    onLanguageChange(e.target.value);
  };

  return (
    <div className="language-selector">
      <label htmlFor="language-select">Select your language:</label>
      <select 
        id="language-select" 
        value={selectedLanguage} 
        onChange={handleChange}
        className="form-select"
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default LanguageSelector;
