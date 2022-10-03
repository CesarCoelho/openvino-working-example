import cv2
import time
from openvino.inference_engine import IECore
from datetime import datetime

# Model IR files
model_xml = "model_img_adjustments.xml"
model_bin = "model_img_adjustments.bin"

# Input image file. 
# Copy the path to one of images from the dataset imported in DL Workbench
# or use the default image "./car.bmp".
input_image_path = "car.png"

# Device to use
device = "MYRIAD"

print(
    "\nConfiguration parameters settings:"
    f"\n\t >> model_xml = {model_xml}",
    f"\n\t >> model_bin = {model_bin}",
    f"\n\t >> input_image_path = {input_image_path}",
    f"\n\t >> device = {device}", 
)

# Create an Inference Engine instance
print("\nCreating Inference Engine...")
ie = IECore()

# List the available devices
devices = ie.available_devices
print("Available devices: ", devices)

# Read the network from IR files
print("\nReading the network...")
net = ie.read_network(model=model_xml, weights=model_bin) 

print("Loading the network to the device...")
exec_net = ie.load_network(network=net, num_requests=2, device_name=device)

# Store names of input and output blobs
input_blob = next(iter(net.inputs))
output_blob = next(iter(net.outputs))

# Read the input dimensions: n=batch size, c=number of channels, h=height, w=width
n, c, h, w = net.inputs[input_blob].shape

print(f"Loaded the model into the Inference Engine for the {device} device.", 
      f"\nModel input dimensions: n={n}, c={c}, h={h}, w={w}")

# Define the function to load the input image
def load_input_image(input_path):
    print("Loading input image...")
    # Globals to store input width and height
    global input_w, input_h
    
    # Use OpenCV to load the input image
    img = cv2.imread(input_path)
    
    input_h, input_w, *_ = img.shape
    print("Loaded the input image %s. \nInput image resolution: %s x %s" % (input_path,input_w,input_h))
    return img

# Define the function to resize the input image
def resize_input_image(image):
    print("Resizing input image...")
    # Resize the image dimensions from image to model input w x h
    in_frame = cv2.resize(image, (w, h))
    # Change data layout from HWC to CHW
    in_frame = in_frame.transpose((2, 0, 1))  
    # Reshape to input dimensions
    in_frame = in_frame.reshape((n, c, h, w))
    #print(f"Resized the input image to {w}x{h}.")
    print("Resized the input image to %s x %s." % (w,h))
    return in_frame

# Load the image
image = load_input_image(input_image_path)

# Resize the input image
in_frame = resize_input_image(image)

# Save the starting time
inf_start = time.time()

# Run the inference
print("\nRunning the inference...")
res = exec_net.infer(inputs={input_blob: in_frame})   

# Calculate time from start until now
inf_time = time.time() - inf_start
print(f"Inference is complete. Run time: {inf_time * 1000:.3f} ms.")
print('Model output_blob has the following shape: %s'  % ({res[output_blob].shape}))

image_outputed = list(res.values())[0]
print(image_outputed.shape)

last = cv2.resize(image, (image_outputed.shape[2], image_outputed.shape[3]))
print(last.shape)

print("\nStoring image...")
from PIL import Image
img = Image.fromarray(last, 'RGB')
filename = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
img.save('output_' + filename + '.png')
print("Stored!")
