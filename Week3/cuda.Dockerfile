FROM nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04

ENV TZ=Asia/Singapore

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata
RUN apt install -y software-properties-common curl build-essential

ENV USER=docker

RUN useradd -ms /bin/bash ${USER}

RUN groupadd mygroup && usermod -a -G mygroup ${USER}

##################################
# install conda
##################################
ENV PYTHON_VERSION=py312_25.1.1-2
RUN curl -OL https://repo.anaconda.com/miniconda/Miniconda3-${PYTHON_VERSION}-Linux-x86_64.sh

RUN bash Miniconda3-${PYTHON_VERSION}-Linux-x86_64.sh  -b -f -p /home/${USER}/miniconda3/ 
RUN ln -s /home/${USER}/miniconda3/etc/profile.d/conda.sh /etc/profile.d/conda.sh
RUN echo ". /home/${USER}/miniconda3/etc/profile.d/conda.sh" >> /home/${USER}/.bashrc

ENV PATH /home/${USER}/miniconda3/bin/:$PATH

RUN mkdir -p /home/${USER}/ws
COPY ./environment.yml /home/${USER}/ws/environment.yml

WORKDIR /home/${USER}/ws

RUN apt-get update && apt-get install -y \
    swig

# for display
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx libgl1-mesa-dri

ENV LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6

USER ${USER}

RUN conda env create --file environment.yml -y
RUN echo "source activate rl_coverage" > ~/.bashrc

ENV PATH /home/${USER}/.conda/envs/rl_coverage/bin:$PATH
