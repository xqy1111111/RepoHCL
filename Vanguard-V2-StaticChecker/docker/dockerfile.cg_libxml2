FROM cg

ENV CC=clang-9
ENV CXX=clang++-9

WORKDIR /root/resource

RUN wget https://download.gnome.org/sources/libxml2/2.9/libxml2-2.9.9.tar.xz

RUN tar xvf libxml2-2.9.9.tar.xz && mv libxml2-2.9.9 libxml2

WORKDIR /root/resource/libxml2

RUN ./configure

RUN bear make -j`nproc`
RUN cp ~/vanguard/benchmark/genastcmd.py .
RUN python3 genastcmd.py
RUN chmod +x buildast.sh
RUN ./buildast.sh | tee buildast.log

WORKDIR /root/output
RUN ~/vanguard/cmake-build-debug/tools/CallGraphGen/cge ~/resource/libxml2/astList.txt
