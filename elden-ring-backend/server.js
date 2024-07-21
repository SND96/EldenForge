const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs').promises;

const app = express();
const port = 3001;

app.use(cors({
  origin: 'http://localhost:3000',
  credentials: true
}));

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'uploads/')
  },
  filename: function (req, file, cb) {
    cb(null, Date.now() + path.extname(file.originalname))
  }
});

const upload = multer({ storage: storage });

app.post('/upload', upload.single('image'), async (req, res) => {
  try {
    if (!req.file) {
      throw new Error('No file uploaded');
    }

    const message = req.body.message;
    
    console.log('Received file:', req.file.filename);
    console.log('Received message:', message);

    // Write the message to a text file
    const textFileName = `${path.parse(req.file.filename).name}.txt`;
    const textFilePath = path.join(__dirname, 'uploads', textFileName);
    
    console.log('Attempting to write text file:', textFilePath);

    try {
      await fs.writeFile(textFilePath, message);
      console.log('Text file written successfully');
    } catch (writeError) {
      console.error('Error writing text file:', writeError);
      throw new Error('Failed to save message');
    }

    // Check if the file was actually created
    try {
      await fs.access(textFilePath);
      console.log('Text file exists after writing');
    } catch (accessError) {
      console.error('Text file does not exist after attempted write:', accessError);
      throw new Error('Failed to verify message was saved');
    }
    
    res.json({
      message: 'Offering accepted by the Erdtree',
      imageName: req.file.filename,
      textName: textFileName,
      userMessage: message,
      customMessage: 'The Erdtree glows with appreciation for your offering.'
    });
  } catch (error) {
    console.error('Error in /upload:', error);
    res.status(400).json({ error: error.message });
  }
});

app.listen(port, () => {
  console.log(`Elden Ring backend listening at http://localhost:${port}`);
});