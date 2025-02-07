# 🔎 Sherlock WebUI

Sherlock WebUI is a powerful and intuitive web interface for **Sherlock**, the popular username enumeration tool.  
This project allows you to launch username searches from a sleek web dashboard, track logs in real-time, and manage multiple sessions effortlessly.

---

## 📂 Project Structure

```
.
├── app.py               # Main Flask application
├── setup.sh             # Linux setup script
├── setup-mac.sh         # macOS setup script
├── setup.bat            # Windows setup script
├── venv/                # Python virtual environment
├── web/
│   ├── templates/
│   │   ├── sherlock-ui/
│   │   │   ├── index.html  # Main UI
│   │   │   ├── run.html    # Log viewer
│   ├── static/            # CSS, JS, assets (if needed)
├── requirements.txt      # Python dependencies (alternative to setup.sh)
└── README.md             # Documentation
```

---

## 🚀 Installation & Setup

### **🔧 Prerequisites**

- **Linux/macOS:** Python 3, Git, Pip
- **Windows:** Python 3, Git, Pip
- **A Unix-based system (Linux, macOS, or WSL)**

---

### **📥 Installation Instructions**

#### **🐧 Linux**

```bash
chmod +x setup.sh
./setup.sh
source venv/bin/activate
python app.py  # OR flask run
```

#### **🍏 macOS**

```bash
chmod +x setup-mac.sh
./setup-mac.sh
source venv/bin/activate
python app.py  # OR flask run
```

#### **🖥️ Windows**

```bat
setup.bat
call venv\Scripts\activate
python app.py
```

---

## **⚠️ Compatibility Notes**

Currently, **only the Linux version has been fully tested**. The Windows and macOS versions **should work** but might require **adjustments**.  
We welcome **feedback and contributions** to ensure full compatibility on all platforms!

If you encounter issues, feel free to **open an issue on GitHub** or **submit a pull request**. 🚀

---

## 🎯 Usage

1. Enter a **username** in the WebUI.
2. (Optional) Enable **NSFW results**.
3. Click **Run Sherlock**.
4. View **live logs** in real-time.
5. **Download logs** when the search is complete.

---

## 🌐 Deployment

Sherlock WebUI can be deployed on **PythonAnywhere, Digital Ocean, Google Cloud, or any Linux server**.

### **PythonAnywhere**

- Upload the project files.
- Configure the web application to point to `app.py`.
- Set up a virtual environment and install dependencies.

### **Digital Ocean / Google Cloud**

- Use the **setup.sh** script to install dependencies.
- Configure your web server (e.g., Gunicorn + Nginx).

---

## 🛠️ Troubleshooting

- **Sherlock command not found?** Ensure `pipx install sherlock-project` completed successfully.
- **WebSocket not working?** Check Flask-SocketIO and use `eventlet` if necessary.
- **Permission errors?** Run `chmod +x setup.sh` and ensure your user has execution rights.

---

## 🤝 Contributing

Want to improve this project? Feel free to fork, submit issues, or create pull requests!

---

## 📝 License

This project is licensed under the MIT License - feel free to use and modify it!

Happy hacking! 🚀
