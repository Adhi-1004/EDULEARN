import os
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_bytes

def _get_tessdata_directory_path():
    import sys
    from pathlib import Path
    env_root = Path(sys.executable).parent.parent
    share_dir = os.path.join(env_root, "share", "tessdata")
    assert share_dir, "tessdata directory does not exist in <envroot>/share/tessdata"
    return str(share_dir)

def extract_text_from_image(image):
    return pytesseract.image_to_string(image)

def deskew(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    coords = np.column_stack(np.where(gray > 0))
    angle = cv2.minAreaRect(coords)[-1]
    angle = -(90 + angle) if angle < -45 else -angle
    center = (image.shape[1] // 2, image.shape[0] // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, M, (image.shape[1], image.shape[0]), flags=cv2.INTER_CUBIC)


def parse_PDF(file):
    file_bytes = file.read()

    pages = convert_from_bytes(file_bytes)

    extracted_text = []

    for i,page in enumerate(pages[:3]):

        page_arr = np.array(page)
        deskewed_page = deskew(page_arr)

        text = extract_text_from_image(deskewed_page)
        extracted_text.append(text)

    extracted_text = "\n".join(extracted_text)

    return extracted_text
