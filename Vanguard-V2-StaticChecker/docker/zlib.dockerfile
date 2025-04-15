FROM cg

ENV CC=clang-9
ENV CXX=clang++-9

WORKDIR /root/resource

ENV ROOT=zlib

RUN wget https://github.com/madler/zlib/archive/refs/tags/v1.3.1.zip && unzip v1.3.1.zip && mv zlib-1.3.1 ${ROOT}

WORKDIR /root/resource/${ROOT}

RUN ./configure
RUN bear make -j`nproc`
RUN cp ~/vanguard/benchmark/genastcmd.py .
RUN python3 genastcmd.py
RUN chmod +x buildast.sh
RUN ./buildast.sh | tee buildast.log

WORKDIR /root/output
RUN ~/vanguard/cmake-build-debug/tools/CallGraphGen/cge ~/resource/${ROOT}/astList.txt
