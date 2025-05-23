FROM ubuntu:20.04

RUN sed -i 's@archive.ubuntu.com@mirrors.aliyun.com@g' /etc/apt/sources.list && \
    sed -i 's@security.ubuntu.com@mirrors.aliyun.com@g' /etc/apt/sources.list

# 设置默认时区，后面按照依赖包安装时会用到
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo "Asia/Shanghai" > /etc/timezone

RUN apt-get update

RUN apt-get install -y build-essential llvm-9-dev cmake ninja-build clang-9 libclang-9-dev zlib1g-dev wget bear python3-dev python-dev unzip

WORKDIR /root/vanguard

COPY . .

RUN mkdir cmake-build-debug

WORKDIR /root/vanguard/cmake-build-debug

RUN cmake -G Ninja -DLLVM_PREFIX=/lib/llvm-9 ..

RUN ninja