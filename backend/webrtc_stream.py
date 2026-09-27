import asyncio
import cv2
from aiortc import VideoStreamTrack
from av import VideoFrame
import fractions
import time

class OpenCVStreamTrack(VideoStreamTrack):
    """
    A video stream track that returns frames from an OpenCV camera.
    """
    def __init__(self, stream_url):
        super().__init__()
        self.stream_url = stream_url
        try:
            url = int(stream_url) if str(stream_url).isdigit() else stream_url
        except:
            url = stream_url
            
        self.cap = cv2.VideoCapture(url)
        self.start_time = time.time()
        self.frames_count = 0

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        
        # Read frame in a separate thread so we don't block the event loop
        success, frame = await asyncio.to_thread(self.cap.read)
        if not success:
            raise Exception("Failed to read frame")
            
        # Optional: resize for better streaming performance
        frame = cv2.resize(frame, (640, 360))
        
        # Convert BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create an av.VideoFrame
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        
        return video_frame

    def stop(self):
        super().stop()
        if self.cap:
            self.cap.release()
