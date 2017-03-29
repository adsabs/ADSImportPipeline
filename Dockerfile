FROM phusion/baseimage:0.9.17

# Regenerate SSH host keys. baseimage-docker does not contain any
# RUN /usr/bin/ssh-keygen -A
RUN /etc/my_init.d/00_regen_ssh_host_keys.sh

# enable SSH service
RUN rm -f /etc/service/sshd/down


RUN apt-get update
RUN apt-get install -y python-pip ipython python-dev libpq-dev
RUN pip install --upgrade pip

RUN mkdir -p /etc/service/app
ADD run /etc/service/app/run
RUN chmod +x /etc/service/app/run

#RUN service ssh start
CMD /bin/bash
