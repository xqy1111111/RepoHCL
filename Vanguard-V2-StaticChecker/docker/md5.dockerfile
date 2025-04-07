FROM cg

ENV CC=clang-9
ENV CXX=clang++-9

WORKDIR /root/resource

RUN wget https://github.com/talent518/md5/archive/refs/heads/master.zip

RUN unzip master.zip && mv md5-master md5

WORKDIR /root/resource/md5

RUN bear make -j`nproc`
RUN cp ~/vanguard/benchmark/genastcmd.py .
RUN python3 genastcmd.py
RUN chmod +x buildast.sh
RUN ./buildast.sh | tee buildast.log

WORKDIR /root/output
RUN ~/vanguard/cmake-build-debug/tools/CallGraphGen/cge ~/resource/md5/astList.txt
