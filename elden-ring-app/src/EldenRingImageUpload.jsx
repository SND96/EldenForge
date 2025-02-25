import React, { useState } from 'react';
import { Shield, X } from 'lucide-react';
import { Alert, AlertDescription } from './components/ui/alert';
import { Button } from './components/ui/button';
import { marked } from 'marked';

const EldenRingImageUpload = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [responseData, setResponseData] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type.substr(0, 5) === "image") {
      setSelectedImage(file);
      setError('');
    } else {
      setSelectedImage(null);
      setError('Tarnished, only image files are accepted in the Lands Between.');
    }
  };

  const handleMessageChange = (e) => {
    setMessage(e.target.value);
  };

  const handleUpload = async () => {
    if (selectedImage && message) {
      setIsUploading(true);
      setError('');
      setSuccess('');
      setResponseData(null);

      try {
        const formData = new FormData();
        formData.append('image', selectedImage);
        formData.append('message', message);

        const response = await fetch('http://localhost:3001/upload', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Failed to upload to the Erdtree');
        }

        const result = await response.json();
        console.log('Offering accepted by the Erdtree:', result);
        
        setResponseData(result);
        const renderedPythonResponse = marked.parse(result.pythonResponse);
        setSuccess(<div>
          <p>Your offering has been accepted by the Erdtree, Tarnished.</p>
          <div 
            className="markdown-content"
            dangerouslySetInnerHTML={{ __html: renderedPythonResponse }}
          />
        </div>);

        setSelectedImage(null);
        setMessage('');
      } catch (err) {
        console.error('Error offering to the Erdtree:', err);
        setError('The Erdtree rejected your offering. Please try again, Tarnished.');
      } finally {
        setIsUploading(false);
      }
    } else {
      setError('Tarnished, both an image and a message are required for the offering.');
    }
  };

  
  const styles = {
    container: {
      width: '100vw',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'flex-start',
      alignItems: 'center',
      background: 'linear-gradient(to bottom, #2d2411, #1a1306)',
      fontFamily: 'Cinzel, serif',
      color: '#e6d2a8',
      padding: '2rem',
      boxSizing: 'border-box',
      overflowY: 'auto',
    },
    content: {
      width: '100%',
      maxWidth: '80rem',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
    },
    title: {
      fontSize: '2.5rem',
      marginBottom: '2rem',
      textAlign: 'center',
      color: '#ffd700',
      fontWeight: 'bold'
    },
    twoColumnLayout: {
      display: 'flex',
      width: '100%',
      gap: '2rem',
      flexWrap: 'wrap',
    },
    column: {
      flex: '1 1 300px',
      display: 'flex',
      flexDirection: 'column',
    },
    uploadArea: {
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '2rem',
      border: '2px solid #c7a767',
      borderRadius: '0.5rem',
      backgroundColor: '#1c1609',
      marginBottom: '2rem',
      width: '100%',
    },
    uploadButton: {
      cursor: 'pointer',
      backgroundColor: '#976f2d',
      color: '#1c1609',
      padding: '0.5rem 1rem',
      borderRadius: '0.375rem',
      fontWeight: 'bold',
      transition: 'background-color 0.3s ease',
    },
    messageInput: {
      width: '100%',
      marginTop: '1rem',
      padding: '0.75rem',
      backgroundColor: '#1c1609',
      color: '#e6d2a8',
      border: '2px solid #c7a767',
      borderRadius: '0.375rem',
      fontFamily: 'Cinzel, serif',
      fontSize: '1rem',
    },

    offerButton: {
      width: '100%',
      backgroundColor: '#976f2d',
      color: '#1c1609',
      fontWeight: 'bold',
      padding: '1rem',
      borderRadius: '0.5rem',
      marginTop: '2rem',
      transition: 'background-color 0.3s ease',
      fontSize: '1.1rem',
    },
    successMessage: {
      marginTop: '1.5rem',
      padding: '1rem',
      backgroundColor: '#1c1609',
      border: '1px solid #c7a767',
      color: '#e6d2a8',
      borderRadius: '0.5rem',
      width: '100%',
      overflowWrap: 'break-word',
      wordWrap: 'break-word',
      hyphens: 'auto',
      textAlign: 'left',  
    },
    imagePreview: {
      marginTop: '1.5rem',
      position: 'relative',
      width: '100%',
    },
    previewImage: {
      maxWidth: '100%',
      height: 'auto',
      borderRadius: '0.5rem',
      border: '2px solid #c7a767',
    },
    removeButton: {
      position: 'absolute',
      top: '0.5rem',
      right: '0.5rem',
      padding: '0.25rem',
      backgroundColor: '#8b0000',
      color: '#e6d2a8',
      borderRadius: '9999px',
      cursor: 'pointer',
    },
  };

  return (
    <div className="elden-ring-theme" style={styles.container}>
      <div style={styles.content}>
        <h2 style={styles.title}>Choose a Remembrance to Offer</h2>
        <div style={styles.twoColumnLayout}>
          <div style={styles.column}>
            <div style={styles.uploadArea}>
              <div style={{textAlign: 'center'}}>
                <Shield color="#ffd700" size={80} />
                <div style={{marginTop: '1rem', fontSize: '1rem'}}>
                  <label htmlFor="image-upload" style={styles.uploadButton}>
                    <span>Upload a Remembrance</span>
                    <input id="image-upload" name="image-upload" type="file" style={{display: 'none'}} onChange={handleImageChange} accept="image/*" />
                  </label>
                  <p style={{marginTop: '0.75rem'}}>or place it here</p>
                </div>
                <p style={{fontSize: '0.875rem', color: '#a89778', marginTop: '1rem'}}>Accepted offerings: PNG, JPG (up to 10MB)</p>
              </div>
            </div>

            <input
              type="text"
              placeholder="Enter your message for the Erdtree..."
              value={message}
              onChange={handleMessageChange}
              style={styles.messageInput}
            />

            <Button
              onClick={handleUpload}
              disabled={!selectedImage || !message || isUploading}
              style={styles.offerButton}
            >
              {isUploading ? 'Offering to the Erdtree...' : 'Offer to the Erdtree'}
            </Button>

            {selectedImage && (
              <div style={styles.imagePreview}>
                <img src={URL.createObjectURL(selectedImage)} alt="Preview" style={styles.previewImage} />
                <button onClick={() => setSelectedImage(null)} style={styles.removeButton}>
                  <X size={16} />
                </button>
              </div>
            )}

            {error && (
              <Alert variant="destructive" style={{marginTop: '1.5rem', backgroundColor: '#4f1c1c', border: '1px solid #8b0000', color: '#ffa799', width: '100%'}}>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
          </div>

          <div style={styles.column}>
            {success && (
              <div className="success-message" style={styles.successMessage}>
                <h3>Offering Accepted</h3>
                <div className="markdown-content">{success}</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EldenRingImageUpload;