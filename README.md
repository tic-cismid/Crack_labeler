
# Crack Labeler

**Crack Labeler** is a graphical application for manual image annotation, developed in Python using Tkinter and OpenCV. It is designed to facilitate the labeling and cataloging of cracks on wall images, allowing users to draw rectangles and scale lines directly on the images.

![Alt text](images/blank.png?raw=true "Title")

---

## Features

- Open folders containing images (`.png`, `.jpg`, `.jpeg`, `.bmp`).
- Image display with zoom and pan functionality.
- Draw rectangles ("Wall") to mark crack areas.
- Draw scale lines ("SF") for calibration.
- Save annotations as JSON files linked to each image.
- Simple and user-friendly interface built with Tkinter.
- Visual indication in the image list when an image has saved annotations.

---

## Requirements

- Python 3.6 or higher
- Python libraries:

```bash
pip install opencv-python pillow
```

Tkinter is usually included with Python installations.

---

## Usage

1. Run the script:

```bash
python Crack_labeler.py
```

2. Click **Open Folder** to select the folder containing the images you want to annotate.

3. Select an image from the list to load it into the workspace.

4. Click **Wall** to enable rectangle drawing mode to mark cracks.

5. Click **SF** to enable line drawing mode for scale lines.

6. Use the mouse wheel to zoom in and out, and the middle mouse button (wheel click) to pan the image.

7. Save your annotations using the **Save** button. The data will be saved as a JSON file next to the image.

---

## JSON File Structure

The JSON file contains two lists:

- `"wall"`: list of rectangles with coordinates (x1, y1, x2, y2).
- `"line"`: list of lines with start and end coordinates.

Example:

```json
{
  "wall": [
    [[x1, y1], [x2, y2]],
    ...
  ],
  "line": [
    [[x1, y1], [x2, y2]],
    ...
  ]
}
```

---

## Additional Notes

- Image scaling and panning adjust automatically to facilitate drawing.
- Drawn shapes scale and move accordingly when zooming or panning.
- Images with saved annotations are highlighted in green in the image list.

---

## Creating an Executable

To create a Windows `.exe` executable file, it is recommended to use PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed Crack_labeler.py
```

The executable will be generated in the `dist` folder.

---

## Author

Developed by [Your Name]  
Internal project for labeling cracks in wall images.

---

## License

This project is for internal use only and is not published or hosted in any public repository.
