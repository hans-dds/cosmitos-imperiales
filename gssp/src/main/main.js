const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const http = require("http");

let mainWindow = null;
let loadingWindow = null;
let streamlitProcess = null;

// const pythonPath = path.join(__dirname, "python312", "pythonw.exe");
// const scriptPath = path.join(__dirname, "main_s.py");

// const pythonPath = path.join(__dirname, "..", "..", "python312", "pythonw.exe");
const pythonPath = "python3";
const scriptPath = path.join(__dirname, "presentacion", "main_s.py");
const modeloPath = path.join(__dirname, "negocio", "clasificador_sentimiento_final.pkl");



function createLoadingWindow() {
  loadingWindow = new BrowserWindow({
    width: 400,
    height: 200,
    resizable: false,
    frame: false,
    webPreferences: {
      contextIsolation: true,
      preload: path.join(__dirname, "presentacion/preload.js"),
    },
  });

  loadingWindow.loadURL(`data:text/html;charset=utf-8,
    <html>
      <body style="display:flex; flex-direction: column; align-items:center; justify-content:center; font-family:sans-serif;">
        <h2>Cargando servidor...</h2>
        <div id="message">Conectando al servidor...</div>
        <div style="margin-top:20px;">
          <button id="retry" style="display:none;">Reintentar</button>
          <button id="close" style="display:none;">Cerrar</button>
        </div>
        <script>
          const retryBtn = document.getElementById('retry');
          const closeBtn = document.getElementById('close');
          const message = document.getElementById('message');

          retryBtn.addEventListener('click', () => {
            retryBtn.style.display = 'none';
            closeBtn.style.display = 'none';
            message.textContent = 'Reintentando...';
            window.electronAPI.send('retry-server');
          });

          closeBtn.addEventListener('click', () => {
            window.electronAPI.send('close-app');
          });

          window.electronAPI.on('show-buttons', () => {
            retryBtn.style.display = 'inline-block';
            closeBtn.style.display = 'inline-block';
            message.textContent = 'No se pudo conectar con el servidor.';
          });
        </script>
      </body>
    </html>
  `);

  loadingWindow.on("closed", () => {
    loadingWindow = null;
  });
}

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 900,
    height: 700,
    webPreferences: {
      contextIsolation: true,
    },
  });
  mainWindow.setMenu(null);
  mainWindow.loadURL("http://localhost:8501");

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

function killStreamlit() {
  if (streamlitProcess) {
    if (process.platform === "win32") {
      spawn("taskkill", ["/PID", streamlitProcess.pid, "/T", "/F"]);
    } else {
      streamlitProcess.kill();
    }
  }
}

function checkServerReady(timeoutMs = 20000) {
  return new Promise((resolve) => {
    const start = Date.now();

    function tryConnect() {
      http.get("http://localhost:8501", () => {
        resolve(true);
      }).on("error", () => {
        if (Date.now() - start > timeoutMs) {
          resolve(false);
        } else {
          setTimeout(tryConnect, 1000);
        }
      });
    }
    tryConnect();
  });
}

function startStreamlitAndWait() {
  return new Promise((resolve) => {
    streamlitProcess = spawn(pythonPath, ["-m", "streamlit", "run", scriptPath], {
      // cwd: __dirname,
      cwd: path.join(__dirname, ".."),
      stdio: ["ignore", "pipe", "pipe"],
      detached: false,
    });

    streamlitProcess.stdout.on("data", (data) => {
      console.log(`Streamlit: ${data}`);
    });

    streamlitProcess.stderr.on("data", (data) => {
      console.error(`Streamlit error: ${data}`);
    });

    streamlitProcess.on("close", (code) => {
      console.log(`Streamlit proceso terminado con código ${code}`);
    });

    checkServerReady().then((ready) => {
      resolve(ready);
    });
  });
}

async function startApp() {
  createLoadingWindow();

  let ready = await startStreamlitAndWait();

  if (ready) {
    if (loadingWindow) {
      loadingWindow.close();
    }
    createMainWindow();
  } else {
    if (loadingWindow) {
      loadingWindow.webContents.send("show-buttons");
    }
  }
}

ipcMain.on("retry-server", async () => {
  if (loadingWindow) {
    loadingWindow.webContents.send("retrying");
  }

  let ready = await startStreamlitAndWait();

  if (ready) {
    if (loadingWindow) {
      loadingWindow.close();
    }
    createMainWindow();
  } else {
    if (loadingWindow) {
      loadingWindow.webContents.send("show-buttons");
    }
  }
});

ipcMain.on("close-app", () => {
  killStreamlit();
  app.quit();
});

app.whenReady().then(() => {
  startApp();
});

app.on("window-all-closed", () => {
  killStreamlit();
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("before-quit", () => {
  killStreamlit();
});
