const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs').promises;
const { spawn } = require('child_process');

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

function runPythonScript(message, imagePath) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', [
      'query_index.py',
      '--query', message,
      '--image', imagePath
    ]);
    
    let scriptOutput = '';
    let scriptError = '';

    pythonProcess.stdout.on('data', (data) => {
      scriptOutput += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      scriptError += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python script exited with code ${code}. Error: ${scriptError}`));
      } else {
        resolve(scriptOutput.trim());
      }
    });
  });
}

app.post('/upload', upload.single('image'), async (req, res) => {
  try {
    if (!req.file) {
      throw new Error('No file uploaded');
    }

    const message = req.body.message;
    const imagePath = path.join(__dirname, req.file.path);
    
    console.log('Received file:', req.file.filename);
    console.log('Image path:', imagePath);
    console.log('Received message:', message);

    // Write the message to a text file
    const textFileName = `${path.parse(req.file.filename).name}.txt`;
    const textFilePath = path.join(__dirname, 'uploads', textFileName);
    
    await fs.writeFile(textFilePath, message);
    
    console.log('Running Python script...');
    // Run Python script with the message and image path, and await its completion
    const pythonResponse = await runPythonScript(message, imagePath);
    console.log('Python script response:', pythonResponse);

    res.json({
      message: 'Offering accepted by the Erdtree',
      imageName: req.file.filename,
      textName: textFileName,
      userMessage: message,
      pythonResponse: pythonResponse,
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