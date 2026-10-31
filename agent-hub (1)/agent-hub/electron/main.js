const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const python = path.join(process.env.LOCALAPPDATA, 'Programs', 'Python', 'Python311', 'python.exe');
let py;
app.whenReady().then(() => {
  py = spawn(python, [path.join(__dirname, '..', 'backend', 'server.py')], {
    stdio: 'inherit',
    env: { ...process.env, PORT: '8766' }
  });
  const win = new BrowserWindow({
    width: 1200, height: 800, backgroundColor: '#0b0e14',
    webPreferences: { backgroundThrottling: false }
  });
  win.setMenuBarVisibility(false);
  setTimeout(() => win.loadFile('index.html'), 1500);
  win.webContents.on('did-finish-load', () => {
    win.show();
    win.focus();
    win.webContents.focus();
    win.webContents.executeJavaScript("document.getElementById('t').focus()");
  });
});
app.on('window-all-closed', () => { if (py) py.kill(); app.quit(); });