import React, { useState, useEffect } from 'react';
import './App.css';

//This code displays: 
//-A heading "Notebook Conversion Tool"
//-A dev with a "Choose File" button (opens the directory dialogue for notebook selection)
//-A dropdown menu asking to select the template (Currently only offering Cookiecutter as dummy)
//-Three buttons (Convert, Back and Cancel)
//- Convert button is disabled till a notebook file is selected (needs checks for ipynb file type) 
//and is only enabled when file selected
//- Back and cancel buttons will stop displaying the conversion progress bar
//-A conversion bar which displays tool's conversion progress
//- Message "Conversion completed" is displayed (need check, in case conversion fails, should display that)
//- TODO: Add how many scripts generated text while conversion progress bar continues
function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [conversionProgress, setConversionProgress] = useState(0);
  const [conversionCompleted, setConversionCompleted] = useState(false);
  const [conversionCancelled, setConversionCancelled] = useState(false);
  const [notebookNotSelected, setNotebookNotSelected] = useState(false);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setNotebookNotSelected(false);
  };

  const handleTemplateChange = (event) => {
    const template = event.target.value;
    setSelectedTemplate(template);
  };

  const handleConvertClick = () => {
    if (!selectedFile) {
      setNotebookNotSelected(true);
      return;
    }

    setConversionCompleted(false);
    setConversionCancelled(false);

    let progress = 0;
    const interval = setInterval(() => {
      if (!conversionCancelled) {
        progress += 10;
        setConversionProgress(progress);
        if (progress >= 100) {
          clearInterval(interval);
          if (!conversionCancelled) {
            setConversionCompleted(true);
          }
        }
      }
    }, 1000);
  };

  const handleBackClick = () => {
    setConversionProgress(0);
    setConversionCancelled(true);
  };

  const handleCancelClick = () => {
    setConversionProgress(0);
    setConversionCancelled(true);
  };

  useEffect(() => {
    setConversionCancelled(false);
  }, [selectedFile, selectedTemplate]);

  return (
    <div className="App">
      <h1>Notebook Conversion Tool</h1>
      <div className="form">
        <input type="file" accept=".ipynb" onChange={handleFileChange} />
        {notebookNotSelected && (
          <p className="notebook-not-selected">Please select a notebook first.</p>
        )}
        <select value={selectedTemplate} onChange={handleTemplateChange}>
          <option value="cookiecutter">Cookiecutter</option>
          {/* Add other template options here */}
        </select>
        <button
          onClick={handleConvertClick}
          disabled={!selectedFile} // Disable the button when no notebook is selected
          className={!selectedFile ? 'disabled' : ''}
        >
          Convert
        </button>
        <button className="back" onClick={handleBackClick}>Back</button>
        <button className="cancel" onClick={handleCancelClick}>Cancel</button>
      </div>
      {conversionProgress < 100 && !conversionCancelled && (
        <progress value={conversionProgress} max="100" />
      )}
      {conversionProgress >= 100 && conversionCompleted && !conversionCancelled && (
        <div className="conversion-status">Conversion Completed!</div>
      )}
    </div>
  );
}

export default App;
