xhost local:root
XAUTH=/tmp/.docker.xauth
DIR=$(pwd)
echo $DIR

docker run -it --rm \
    --gpus all \
    --name=rl_learn_gpu_container \
    --env="DISPLAY=$DISPLAY" \
    --env="QT_X11_NO_NITSHM=1" \
    --volume="/tmp/.X11-unix/:/tmp/.X11-unix:rw" \
    --env="XAUTHORITY=$XAUTH"\
    --volume="$XAUTH:$XAUTH" \
    --volume="$DIR:/home/docker/ws" \
    --net=host \
    --privileged \
    rl_learn_gpu:latest