import cv2
import numpy as np
import torch
import os
from RealESRGAN import RealESRGAN
from PIL import Image
from tqdm import tqdm

def enhance_video(video_path,output_video_path,model_path="RealESRGAN_x8.pth", scale=4):

    device= "cuda" if torch.cuda.is_available() else "cpu"

    model= RealESRGAN(path=model_path,device=device)
    model.load_weights(model_path)

    cap = cv2.VideoCapture(video_path)
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) * scale
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) * scale
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out= cv2.VideoWriter(output_video_path, fourcc, frame_rate, (frame_width,frame_height))

    frame_count= 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_image= Image.fromarray(frame)
        output_image= model.predict(input_image)
        output_frame= cv2.cvtColor(np.array(output_image), cv2.COLOR_RGB2BGR)

        out.write(output_frame)
        frame_count+=1
    cap.release()
    out.release()
    return output_video_path