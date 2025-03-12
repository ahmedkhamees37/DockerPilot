 # 🚀 DockerPilot

## 📝 Overview
Docker-On-Hand is a graphical user interface (GUI) tool designed to simplify the process of managing Docker containers, networks, and volumes. This project provides an interactive environment where users can visually create, configure, and deploy containerized applications using Docker Compose.

## 🎯 Features
- 🖥️ **Graphical User Interface**: Intuitive GUI for managing Docker components.
- 🎯 **Drag and Drop Support**: Easily add and configure containers, networks, and volumes.
- 🔄 **Automatic Docker Compose Generation**: Convert user-defined configurations into a valid `docker-compose.yml` file.
- 🌐 **Dynamic Network & Volume Management**: Create and configure networks and volumes with ease.
- 🚢 **Live Container Deployment**: Deploy and manage containers directly from the interface.

## 📂 Project Structure
```
Docker-On-Hand/
├── left_bar.py        # Sidebar UI for draggable components (Containers, Volumes, Networks)
├── MyApp.py           # Main application logic and Docker Compose generation
├── network.py         # Network management and interaction
├── images/            # Icons for GUI elements
├── tmp/               # Temporary storage for generated JSON configurations
└── README.md          # Documentation
```

## 🛠️ Installation & Setup
### ✅ Prerequisites
Ensure you have the following installed on your system:
- 🐍 Python 3.8+
- 🐳 Docker & Docker Compose
- 🎨 Tkinter (for GUI support)
- 📦 Required Python packages (Pillow, PyYAML)

### 📥 Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Mohamed2107/Docker-On--Hand.git
   cd Docker-On--Hand
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage
1. Run the application:
   ```bash
   python MyApp.py
   ```
2. Use the graphical interface to add and configure Docker components.
3. Click **Start** to generate `docker-compose.yml` and deploy the containers.

## 🔧 How It Works
- 🖱️ **Drag components** from the sidebar to create new containers, networks, or volumes.
- ⚙️ **Configure settings** via popups and specify attributes such as network subnets, container images, and volume mappings.
- 📜 **Generate and deploy** the configuration using Docker Compose.

## 🤝 Contributing
Contributions are welcome! Feel free to submit issues and pull requests to enhance functionality and usability.

## 📜 License
This project is licensed under the MIT License. See `LICENSE` for details.

## 👨‍💻 Author
Developed by https://github.com/ahmedkhamees37 .

