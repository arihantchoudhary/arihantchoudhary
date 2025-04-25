#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Colors for console output
const colors = {
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
};

console.log(`${colors.bold}${colors.cyan}
╔════════════════════════════════════════════════════════╗
║                                                        ║
║            HARPER AI SALES ENGINE SETUP                ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
${colors.reset}`);

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Utility functions
const prompt = (question) => new Promise((resolve) => {
  rl.question(question, resolve);
});

const runCommand = (command, cwd = process.cwd()) => {
  try {
    console.log(`${colors.blue}Running: ${command}${colors.reset}`);
    execSync(command, { cwd, stdio: 'inherit' });
    return true;
  } catch (error) {
    console.error(`${colors.yellow}Failed to execute: ${command}${colors.reset}`);
    return false;
  }
};

const copyEnvFile = () => {
  try {
    if (!fs.existsSync('.env')) {
      fs.copyFileSync('.env.example', '.env');
      console.log(`${colors.green}Created .env file from .env.example${colors.reset}`);
    } else {
      console.log(`${colors.blue}.env file already exists${colors.reset}`);
    }
    return true;
  } catch (error) {
    console.error(`${colors.yellow}Failed to create .env file: ${error.message}${colors.reset}`);
    return false;
  }
};

const createDataDirs = () => {
  const dirs = [
    'services/document-parser/data/documents',
    'services/voice-ai/logs',
    'services/lead-scoring/data',
    'services/recommendation-engine/data'
  ];

  for (const dir of dirs) {
    const dirPath = path.join(process.cwd(), dir);
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
      console.log(`${colors.green}Created directory: ${dir}${colors.reset}`);
    }
  }
};

// Main setup function
const setup = async () => {
  try {
    // 1. Copy .env file
    copyEnvFile();
    
    // 2. Create necessary data directories
    createDataDirs();
    
    // 3. Install Node.js dependencies
    console.log(`\n${colors.magenta}Installing Node.js dependencies...${colors.reset}`);
    if (runCommand('npm install')) {
      console.log(`${colors.green}Successfully installed Node.js dependencies${colors.reset}`);
    }
    
    // 4. Ask if user wants to install Python dependencies
    const installPython = await prompt(`\n${colors.cyan}Do you want to install Python dependencies? (y/n): ${colors.reset}`);
    if (installPython.toLowerCase().startsWith('y')) {
      console.log(`\n${colors.magenta}Installing Python dependencies...${colors.reset}`);
      runCommand('pip install -r requirements.txt');
      
      // Install service-specific Python dependencies
      const pythonServices = ['document-parser', 'lead-scoring', 'recommendation-engine'];
      for (const service of pythonServices) {
        const reqPath = path.join('services', service, 'requirements.txt');
        if (fs.existsSync(reqPath)) {
          console.log(`\n${colors.magenta}Installing Python dependencies for ${service}...${colors.reset}`);
          runCommand(`pip install -r ${reqPath}`);
        }
      }
    }
    
    // 5. Ask if user wants to start Docker services
    const startDocker = await prompt(`\n${colors.cyan}Do you want to start Docker services? (y/n): ${colors.reset}`);
    if (startDocker.toLowerCase().startsWith('y')) {
      console.log(`\n${colors.magenta}Starting Docker services...${colors.reset}`);
      runCommand('docker-compose -f infra/docker-compose.yml up -d');
    }
    
    console.log(`\n${colors.green}${colors.bold}Setup completed successfully!${colors.reset}`);
    console.log(`\nYou can start the services individually:`);
    console.log(`${colors.cyan}- Customer Portal: ${colors.reset}cd services/customer-portal && npm run dev`);
    console.log(`${colors.cyan}- Voice AI Service: ${colors.reset}cd services/voice-ai && npm run dev`);
    console.log(`${colors.cyan}- Document Parser: ${colors.reset}cd services/document-parser/src && python -m uvicorn main:app --reload`);
    console.log(`${colors.cyan}- Lead Scoring: ${colors.reset}cd services/lead-scoring/src && python -m uvicorn main:app --reload`);
    
    rl.close();
  } catch (error) {
    console.error(`${colors.yellow}Setup failed: ${error.message}${colors.reset}`);
    rl.close();
    process.exit(1);
  }
};

// Run setup
setup();
