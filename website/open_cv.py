import cv2

def gen_frames(video): 
    print(video) 
    camera = cv2.VideoCapture(video)
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            print('unsuccessful')
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 


def list_ports():
    is_working = True
    dev_port = 0
    working_ports = []
    while is_working:
        camera = cv2.VideoCapture(dev_port)
        if not camera.isOpened():
            is_working = False
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                working_ports.append({"port": dev_port, "width": w, "height": h})
                
        dev_port +=1
    return working_ports