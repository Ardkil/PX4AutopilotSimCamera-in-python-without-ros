import cv2
import numpy as np
import gz.transport13 as gz 
import gz.msgs10.image_pb2 as msgs
import asyncio

class VideoUDPWriter:
    def __init__(self, udp_ip="127.0.0.1", udp_port=5621, width=640, height=480, fps=30, bitrate=500):
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.width = width
        self.height = height
        self.fps = fps
        self.bitrate = bitrate
        
        self.writer = None
        self.node = None
        self.sub = None
        
    async def start(self):
        #GStreamer encoding and sending via UDP
        out_pipeline = (
            "appsrc ! videoconvert ! x264enc tune=zerolatency bitrate={} speed-preset=superfast ! "
            "rtph264pay config-interval=1 pt=96 ! "
            "udpsink host={} port={}".format(self.bitrate, self.udp_ip, self.udp_port)
        )
        
        self.writer = cv2.VideoWriter(
            out_pipeline, 
            cv2.CAP_GSTREAMER, 
            0, 
            self.fps, 
            (self.width, self.height), 
            True
        )
        
        #Subscribe and bridge to gazebo
        self.node = gz.Node()
        self.sub = self.node.subscribe(msgs.Image, "/camera", self.image_callback)
        task = asyncio.create_task(self.process())
        print(f"Streaming Gazebo topic CAMERA to udp://{self.udp_ip}:{self.udp_port}")
        await asyncio.gather(task)

    def image_callback(self, msg):
        #Convert raw bytes to numpy array
        img = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, -1)

        if hasattr(msg, "encoding") and msg.encoding == "rgb8":
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        #Write frame to UDP stream
        if self.writer is not None:
            self.writer.write(img)

        print("Received image frame")
        #Wont work on wsl
        #cv2.imshow("Gazebo Camera", img)
        #cv2.waitKey(1)
        
    async def process(self):
        while True:
            await asyncio.sleep(0.5)

"""
if __name__ == "__main__":
    video_writer = VideoUDPWriter()
    asyncio.run(video_writer.start())
    asyncio.get_event_loop().run_forever()"""
