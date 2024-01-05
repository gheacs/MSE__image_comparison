import cv2
import numpy as np
from datetime import datetime
import tkinter as tk
from PIL import Image, ImageTk
from picamera import PiCamera
import time

def capture_new_image(filename, delay=1, iso=100, shutter_speed=0, awb_mode='auto'):
    with PiCamera() as camera:
        camera.resolution = (1024, 768)
        camera.iso = iso  # Adjust this based on lighting conditions. Higher for darker conditions.
        if shutter_speed > 0:
            camera.shutter_speed = shutter_speed  # In microseconds.
        camera.awb_mode = awb_mode  # 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon'

        # Give the camera some time to adjust to conditions
        time.sleep(2)
        camera.exposure_mode = 'auto'
        while camera.awb_gains == (0, 0):
            time.sleep(0.1)
        
        camera.start_preview()
        time.sleep(delay)  # Wait for the delay before capturing
        camera.capture(filename)
        camera.stop_preview()

def mse(imageA, imageB):
    # Compute the mean squared error between the two images
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    return err

def compare_images(imageA_path, imageB_path):
    try:
        # Load the images
        imageA = cv2.imread(imageA_path)
        imageB = cv2.imread(imageB_path)
        
        # Ensure the images have the same size
        if imageA.shape != imageB.shape:
            # Resize imageB to the shape of imageA
            imageB = cv2.resize(imageB, (imageA.shape[1], imageA.shape[0]))
        
        # Convert the images to grayscale
        imageA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        imageB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
        
        # Compute the mean squared error between the images
        m = mse(imageA, imageB)
        return m
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def display_image_on_screen(image_path, root=None):
    # Function to display an image on the screen
    if not root:
        root = tk.Tk()
        root.attributes('-fullscreen', True)
        root.bind("<Escape>", lambda e: root.quit())
    
    img = Image.open(image_path)
    img = ImageTk.PhotoImage(img)
    panel = tk.Label(root, image=img)
    panel.pack(side="bottom", fill="both", expand="yes")

    root.mainloop()

# Define the paths to the images
benchmark_image_path = "/home/gheacs/benchmark.jpg"
current_image_path = "/home/gheacs/current.jpg"

# Display the happy face by default
root = tk.Tk()
display_image_on_screen("/home/gheacs/happy face.jpg", root)

# Capture a new image and compare it
capture_new_image(current_image_path, delay=1, iso=200, shutter_speed=60000, awb_mode='sunlight')
mse_value = compare_images(benchmark_image_path, current_image_path)

# Show the angry face if the MSE exceeds the threshold
if mse_value is not None and mse_value > 4000:
    display_image_on_screen("/home/gheacs/angry face.jpg", root)
