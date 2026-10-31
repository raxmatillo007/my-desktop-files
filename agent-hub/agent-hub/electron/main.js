const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
let py;
app.whenReady().then(() => {
  py = spawn('python', [path.join(__dirname, '..', 'backend', 'server.py')], { stdio: 'inherit' });
  const win = new BrowserWindow({ width: 1200, height: 800, backgroundColor: '#0b0e14' });
  win.setMenuBarVisibility(false);
  setTimeout(() => win.loadFile('index.html'), 1500);
});
app.on('window-all-closed', () => { if (py) py.kill(); app.quit(); });
