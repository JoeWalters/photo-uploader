# Pee-Yew Photo Uploader
<img src="static/logo.png" alt="Pee-Yew Logo" style="float: left; margin-right: 10px; max-width: 100px;">

**Pee-Yew Photo Uploader** is a web application designed to upload images to a select directory. It features a user-friendly interface for uploading images, sorting them by name or date, and displaying them in a gallery format. Users can also delete images directly from the interface.

This is a good option for uploading files to a photo-slideshow. 

## Gallery Section

|                                       |                                       |
|:-------------------------------------:|:-------------------------------------:|
| <img src="src/image1.png" width="500"> |<img src="src/image2.png" width="500">|
| <img src="src/image3.png" width="500"> ||

<style>
.gallery {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
}

.gallery-item {
  margin: 10px;
  text-align: center;
}

.gallery-item img {
  max-width: 200px;
  height: auto;
  display: block;
}

.caption {
    font-size: small;
}
</style>

## Features

- **Image Upload**: Supports multiple file uploads at once.
- **Sorting Options**: Sort images by:
  - Name (A-Z)
  - Name (Z-A)
  - Date (Oldest First)
  - Date (Newest First)
- **Responsive Gallery**: Displays images in a grid layout with preview and details.
- **Image Management**: Allows users to delete uploaded images, and to resize imgages to a max height and width.

## Technologies Used

- **Frontend**: HTML5, CSS3, Bootstrap
- **Backend**: Flask (Python)
- **Template Engine**: Jinja2
- **Additional Libraries**: Bootstrap 5 for responsive design and modern UI components.

## Setup and Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/JoeWalters/photo-uploader.git
   cd photo-uploader
   ```
2. **Install Flask**:
   ```bash
   pip install flask
   ```
3.	**Settings**:
    Here are some settings in the Python script which you might wish to change.
    Descriptions which start with an asterisk `*` denote a setting which is also available in the WebGUI. 
    | Variable | Description |
    | -------- | -------- |
    | `port=` | The port on which this site will run on |
    | `UPLOAD_FOLDER` | * Where to upload images |
    | `ALLOWED_EXTENSIONS` | * Which extensions to allow |
    | `MAX_HEIGHT` | * Max height of uploaded images. Taller images will be shrunk to fit. |
    | `MAX_WIDTH` | * Max width of uploaded images. Wider images will be shrunk to fit. |
4. **Run the Application**:
   ```bash
   python3 photo_uploader.py
   ```
   The application will be accessible at `http://<your-ip>:5000`.

## How to Use
1.	**Settings**:
    Press the Settings button in the top right of the page
    | Option | Description |
    | -------- | -------- |
    | `Upload Folder` | Where to upload images |
    | `Allowed Extensions` | Which extensions to allow |
    | `Max Image Height` | Max height of uploaded images. Taller images will be shrunk to fit. |
    | `Max Image Width` | Max width of uploaded images. Wider images will be shrunk to fit. |
2.	**Upload Images**
	* Select images using the “Choose File” button.
	* Click “Upload” to add the images to the gallery.
3.	Sort Images:
    * Use the Sort Options dropdown to organize images by name or date.
4.	Delete Images:
    * Click the “Delete” button below an image to remove it.

## License

This project is licensed under the [LGPL v3.0](https://www.gnu.org/licenses/lgpl-3.0.html).

You are free to use, modify, and distribute this software under the terms of the Lesser General Public License version 3.0. If you make modifications to this software, you must make those modifications available under the same license. However, you may link this software with proprietary programs under certain conditions. 

For more details, refer to the full [LGPL v3.0 license text](https://www.gnu.org/licenses/lgpl-3.0.html).