import React, { useState } from 'react';
import { Shield, X } from 'lucide-react';
import { Alert, AlertDescription } from './components/ui/alert';
import { Button } from './components/ui/button';

const EldenRingImageUpload = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

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

  const handleUpload = () => {
    if (selectedImage && message) {
      console.log('Offering image to the Erdtree:', selectedImage.name);
      console.log('Message:', message);
      setSelectedImage(null);
      setMessage('');
    } else {
      setError('Tarnished, both an image and a message are required for the offering.');
    }
  };

  const styles = {
    container: {
      maxWidth: '28rem',
      margin: '0 auto',
      padding: '2rem',
      background: 'linear-gradient(to bottom, #2d2411, #1a1306)',
      borderRadius: '0.5rem',
      boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
      border: '2px solid #c7a767',
      fontFamily: 'Cinzel, serif',
      color: '#e6d2a8'
    },
    title: {
      fontSize: '1.875rem',
      marginBottom: '1.5rem',
      textAlign: 'center',
      color: '#ffd700',
      fontWeight: 'bold'
    },
    uploadArea: {
      display: 'flex',
      justifyContent: 'center',
      padding: '1.5rem',
      border: '2px solid #c7a767',
      borderRadius: '0.375rem',
      backgroundColor: '#1c1609',
      marginBottom: '1.5rem'
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
    uploadButtonHover: {
      backgroundColor: '#c7a767'
    },
    offerButton: {
      width: '100%',
      backgroundColor: '#976f2d',
      color: '#1c1609',
      fontWeight: 'bold',
      padding: '0.75rem 1rem',
      borderRadius: '0.375rem',
      marginTop: '1.5rem',
      transition: 'background-color 0.3s ease',
    },
    offerButtonHover: {
      backgroundColor: '#c7a767'
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
      outline: 'none',
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Choose a Remembrance to Offer</h2>
      <div style={styles.uploadArea}>
        <div>
          <Shield color="#ffd700" size={64} />
          <div style={{marginTop: '0.75rem', fontSize: '0.875rem'}}>
            <label
              htmlFor="image-upload"
              style={styles.uploadButton}
            >
              <span>Upload a Remembrance</span>
              <input id="image-upload" name="image-upload" type="file" style={{display: 'none'}} onChange={handleImageChange} accept="image/*" />
            </label>
            <p style={{marginTop: '0.5rem'}}>or place it here</p>
          </div>
          <p style={{fontSize: '0.75rem', color: '#a89778', marginTop: '0.75rem'}}>Accepted offerings: PNG, JPG, GIF (up to 10MB)</p>
        </div>
      </div>

      <input
        type="text"
        placeholder="Enter your message for the Erdtree..."
        value={message}
        onChange={handleMessageChange}
        style={styles.messageInput}
      />

      {error && (
        <Alert variant="destructive" style={{marginBottom: '1rem', backgroundColor: '#4f1c1c', border: '1px solid #8b0000', color: '#ffa799'}}>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {selectedImage && (
        <div style={{marginTop: '1rem', position: 'relative'}}>
          <img src={URL.createObjectURL(selectedImage)} alt="Preview" style={{maxWidth: '100%', height: 'auto', borderRadius: '0.5rem', border: '2px solid #c7a767'}} />
          <button
            onClick={() => setSelectedImage(null)}
            style={{position: 'absolute', top: '0.5rem', right: '0.5rem', padding: '0.25rem', backgroundColor: '#8b0000', color: '#e6d2a8', borderRadius: '9999px'}}
          >
            <X size={16} />
          </button>
        </div>
      )}

      <Button
        onClick={handleUpload}
        disabled={!selectedImage || !message}
        style={styles.offerButton}
      >
        Offer to the Erdtree
      </Button>
    </div>
  );
};

export default EldenRingImageUpload;