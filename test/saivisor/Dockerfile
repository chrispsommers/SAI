FROM amd64/ubuntu:18.04
ARG PARALLEL_MAKE=on 
ENV GRPC_RELEASE_TAG v1.28.1 

RUN apt-get update && apt-get install -y \
  autoconf \
  automake \
  build-essential \
  libtool \
  curl \
  g++ \ 
  libgflags-dev \ 
  git \
  iputils-ping \
  && apt-get clean


RUN git clone -b ${GRPC_RELEASE_TAG} https://github.com/grpc/grpc /var/local/git/grpc && \
    cd /var/local/git/grpc && \
    git submodule update --init --recursive

# TODO - delete protobuf src
RUN echo "-- installing protobuf" && \
    cd /var/local/git/grpc/third_party/protobuf && \
    ./autogen.sh && ./configure --enable-shared && \
    if [ "${PARALLEL_MAKE}" = "off" ]; then NPROC=1; else NPROC=$(nproc); fi && \
    make -j${NPROC} && make -j${NPROC} check && make install && make clean && ldconfig

# TODO - delete gRPC src
RUN echo "-- installing grpc & grpc_cli" && \
    cd /var/local/git/grpc && \
    if [ "${PARALLEL_MAKE}" = "off" ]; then NPROC=1; else NPROC=$(nproc); fi && \
    make -j${NPROC} && make install && make grpc_cli && cp bins/opt/grpc_cli /usr/local/bin && make clean && ldconfig

RUN echo "-- install pip, protobuf, grpc tools, reflections, deprecated, scapy" && \
    apt-get update && apt-get install -y python-pip python-setuptools &&\
    pip install protobuf==3.18.0rc2 grpcio-tools pytest==2.9.1 grpcio-reflection deprecated scapy

# Default run a bash session, but usually a make script or cmd will be run
CMD /bin/bash
