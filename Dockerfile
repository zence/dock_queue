################### BASE IMAGE ##################
FROM continuumio/miniconda3:4.5.4

################### SET ENVS ####################
ENV CCTOOLS_NAME="cctools-7.0.9-x86_64-redhat7"

################# INSTALL CCTOOLS ###############
RUN apt-get update \
 && apt-get install -y build-essential zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*
RUN cd /home \
 && wget http://ccl.cse.nd.edu/software/files/${CCTOOLS_NAME}.tar.gz \
 && tar zxvf ${CCTOOLS_NAME}.tar.gz
ENV PATH=/home/${CCTOOLS_NAME}/bin:${PATH}
ENV PYTHONPATH=/home/cctools-7.0.9-x86_64-redhat7/lib/python3.6/site-packages

################ INSTALL PACKAGES ###############
RUN conda install pandas

################# ADD SCRIPTS ###################
ADD hello_world.py /usr/local/bin/hello_world
ADD bwa_mem.py /usr/local/bin/run_work_queue
ADD cmd_rdr.py /usr/local/bin/cmd_rdr
ADD hello_world.sh /home/hello_world.sh
ADD cmd_line.py /usr/local/bin/cmd_line
ADD commands.txt /home/commands.txt

WORKDIR /home

################# MAKE INTERACTIVE ##############
#ENTRYPOINT ["bash"]