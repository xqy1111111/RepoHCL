FROM cg

ENV CC=clang-9
ENV CXX=clang++-9

WORKDIR /root/resource

RUN wget https://github.com/leethomason/tinyxml2/archive/refs/heads/master.zip && unzip master.zip && mv tinyxml2-master tinyxml2

WORKDIR /root/resource/tinyxml2

RUN cmake -DCMAKE_BUILD_TYPE=Release -DLLVM_PREFIX=/lib/llvm-9 .

RUN bear make -j`nproc`
RUN cp ~/vanguard/benchmark/genastcmd.py .
RUN python3 genastcmd.py
RUN chmod +x buildast.sh
RUN ./buildast.sh | tee buildast.log

WORKDIR /root/output
RUN ~/vanguard/cmake-build-debug/tools/CallGraphGen/cge ~/resource/tinyxml2/astList.txt
