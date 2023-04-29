# Adapted from "Hello World Example"

import sensor, image, time, network, socket, argparse
from google.cloud import pubsub
from sys.path.append(os.path.join(os.path.dirname(__file__), "cloudiot_mqtt_image_publish")) import send_image


# connect/ show IP config a specific network interface
# adapted from https://docs.openmv.io/library/network.html
nic = network.Driver(...)
if not nic.isconnected():
    nic.connect()
    print("Waiting for connection...")
    while not nic.isconnected():
        time.sleep(1)
print(nic.ifconfig())

# now use socket as usual
addr = socket.getaddrinfo('micropython.org', 80)[0][-1]
s = socket.socket()
s.connect(addr)
s.send(b'GET / HTTP/1.1\r\nHost: micropython.org\r\n\r\n')
data = s.recv(1000)
s.close()


#  grant access to the Cloud IoT Core service account on a given PubSub topic
# adapted from https://github.com/GoogleCloudPlatform/python-docs-samples/blob/main/iot/api-client/scripts/iam.py

def set_topic_policy(topic_name):
    """Sets the IAM policy for a topic for Cloud IoT Core."""
    pubsub_client = pubsub.Client()
    topic = pubsub_client.topic(topic_name)
    policy = topic.get_iam_policy()

    # Add a group as publishers.
    publishers = policy.get('roles/pubsub.publisher', [])
    publishers.append(policy.service_account(
            'cloud-iot@system.gserviceaccount.com'))
    policy['roles/pubsub.publisher'] = publishers

    # Set the policy
    topic.set_iam_policy(policy)

    print('IAM policy for topic {} set.'.format(topic.name))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_argument(
            dest='topic_name',
            help='The PubSub topic to grant Cloud IoT Core access to')

    args = parser.parse_args()

    set_topic_policy(args.topic_name)


# initialize variables
period = input("Enter period: ") * 60   # Period in seconds
n_samples = input("Enter number of samples: ") # number of images desired

# initialize pubsub
set_topic_policy("plasticam")

# initialize camera
sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
clock = time.clock()                # Create a clock object to track the FPS.

#get input from user

while(True):
    starttime = time.time()
    i = n_samples

    while (i>0):
        img = sensor.snapshot()         # Take a picture and return the image.
        send_image(plasticam, plasticam_reg, test_device_id, capsys, img) # send the image to the cloud
        time.sleep(period - ((time.time() - starttime) % 60.0)) # Wait for "period" of time before taking next image
        i = i-1                         # countdown number of pictures that need to be taken
        clock.tick()                    # Update the FPS clock.
