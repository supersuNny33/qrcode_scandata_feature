import cv2
import numpy as np
from pyzbar.pyzbar import decode
import pymongo
import webbrowser  # To open a web browser for displaying product information
import time  # Import the time module

# Initialize a set to keep track of detected QR codes
detected_codes = set()
is_authorized = False  # Flag to track authorization
popup_opened = False  # Flag to track if the popup is opened
popup_start_time = None  # Variable to store the time when the popup was opened
message_duration = 2  # Set the message display duration to 5 seconds

# Connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://supersuNny33:zNV2hstjTIIPDAfn@dtg.bsx7n7j.mongodb.net/")  # Replace with your MongoDB URI
db = client["QRcode"]  # Replace with your database name
collection = db["qrcodelist"]  # Replace with your collection name

# Open the camera
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

while True:
    success, img = cap.read()

    # Detect QR codes
    for barcode in decode(img):
        myData = barcode.data.decode('utf-8')

        # Check if this QR code has not been detected before
        if myData not in detected_codes:
            detected_codes.add(myData)  # Add to the set to remember it
            print(myData)  # Print the data once

            # Check if the data exists in MongoDB
            if collection.find_one({"data": myData}):
                is_authorized = True
                myColor = (0, 255, 0)
            else:
                is_authorized = False
                myColor = (0, 0, 255)

            pts = np.array([barcode.polygon], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(img, [pts], True, myColor, 5)
            pts2 = barcode.rect

            # Show "Authorized" or "Un-Authorized" message
            cv2.putText(img, "Authorized" if is_authorized else "Un-Authorized", (pts2[0], pts2[1]), cv2.FONT_HERSHEY_SIMPLEX,
                        0.9, myColor, 2)

            # Check if the popup is not opened and authorization is true
            if is_authorized and not popup_opened:
                popup_start_time = time.time()  # Record the time when the popup was opened
                popup_opened = True

    cv2.imshow('Result', img)

    # Check if the popup is open and has been open for the specified duration
    if popup_opened and time.time() - popup_start_time >= message_duration:
        webbrowser.open_new_tab('http://127.0.0.1:5500/templates/index.html')  # Open the Flask web page
        popup_opened = False  # Reset the flag

    # Exit the loop when the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the OpenCV window
cap.release()
cv2.destroyAllWindows()
