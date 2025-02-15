# DIY Raspberry Pi Thermal Camera

<img src="https://raw.githubusercontent.com/Ballistyxx/eliferrara/master/assets/Digital-Camera/full_computer_render.png" alt="Project Thumbnail: Onshape screenshot of my Raspberry Pi Zero 2W interfacing with my custom circuit board, with all components attached" width="600" ALIGN="left" HSPACE="20" VSPACE="20"/>

## Overview
This project is a **DIY Thermal Camera** built using a **Raspberry Pi Zero 2W**, the **MLX90640 thermal sensor**, and a **custom PCB**. It blends visible-light imaging with thermal data to create a functional, cost-effective alternative to expensive commercial FLIR cameras.

📜 **Read the full blog post here:** [How I Built a Thermal Camera from Scratch](https://eliferrara.com/2025/02/11/Thermal_Camera.html)

## Features
✔ **32x24 MLX90640 Thermal Sensor**  
✔ **Real-time image blending** of thermal and visible-light data  
✔ **Threaded image processing** for better performance  
✔ **Custom PCB for modular design**  
✔ **3D-printed enclosure** for portability  
✔ **Physical buttons for controls (save image, pause stream, shutdown)**  
✔ **USB-C charging with LiPo battery support**  

## Project Images

### Final Build
<img src="https://raw.githubusercontent.com/Ballistyxx/eliferrara/master/assets/Digital-Camera/full_model_render.png" alt="Screenshot of Onshape 3D model" width="500" ALIGN="left" HSPACE="20" VSPACE="20"/>

## Hardware Components
- **Raspberry Pi Zero 2W**
- **MLX90640 Thermal Sensor**
- **Standard Raspberry Pi Camera Module (v1.3)**
- **2.4-inch LCD Display (SPI)**
- **Custom PCB (See Files Below)**
- **3D-printed enclosure**
- **LiPo Battery + USB-C Charging Module**
- **Push Buttons & Slide Switch**

## Software & Code
The project uses **Python** for image processing and multi-threading to improve performance. The software includes:

- **Multi-threaded image capture** for smooth performance
- **Blending of thermal & visible-light images**
- **Real-time display on LCD screen (~30FPS)**
- **Custom button functions (pause, save, shutdown)**

### Thermal Output
![Thermal Output](https://raw.githubusercontent.com/Ballistyxx/eliferrara/master/assets/Digital-Camera/thermal_output.png)

## 3D Printing Files & PCB Design
All **.STEP**, **PCB Gerber**, and **STL files** for the 3D-printed case are provided in the repository.

📂 **Download Here:** [GitHub Repository](https://github.com/Ballistyxx/thermal-camera)

🖥️ **Onshape Project:** [Onshape Project](https://cad.onshape.com/documents/573f1e1d02ff5d0fed5dbfdf/w/9f337434dbe970ed80adfd86/e/1005719233a43e1e58861aa3?renderMode=0&uiState=67b0c546afc06c170b5bcf1e)

🛠️ **Installation:** An installation script may be coming in the future, but for now simply clone this repository into your Pi's home directory and run `main_multithreaded.py`.

## Known Limitations & Future Improvements
⚠ **Low Thermal Sensor Resolution** – Future upgrades could use the **FLIR Lepton 3.5** for higher quality imaging.  
⚠ **Thermal Framerate Limitations** – MLX90640 maxes out at **4-16 FPS** due to I2C bandwidth.  
⚠ **Better Image Alignment Needed** – Offset calculations could be improved for better accuracy.  

## License
This project is open-source under the **MIT License**. Feel free to modify and improve!

## Author
Developed by **Ballistyxx**  
📧 **Contact:** [GitHub Issues](https://github.com/Ballistyxx/thermal-camera/issues)

---
✨ **If you like this project, consider giving it a ⭐ on GitHub!**

