FROM ubuntu:20.04

RUN sed -i 's@archive.ubuntu.com@mirrors.aliyun.com@g' /etc/apt/sources.list && \
    sed -i 's@security.ubuntu.com@mirrors.aliyun.com@g' /etc/apt/sources.list

# 设置默认时区，后面按照依赖包安装时会用到
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo "Asia/Shanghai" > /etc/timezone

RUN apt update

RUN apt install -y build-essential llvm-9-dev cmake ninja-build clang-9 libclang-9-dev zlib1g-dev wget bear nodejs npm unzip software-properties-common

RUN add-apt-repository -y ppa:deadsnakes/ppa && apt install -y python3.12 python3.12-venv

WORKDIR /root/

COPY . .

ENV VIRTUAL_ENV=/root/venv

RUN python3.12 -m venv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV HF_ENDPOINT=https://hf-mirror.com

RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple && pip install -r requirements.txt

EXPOSE 31000

CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "31000"]