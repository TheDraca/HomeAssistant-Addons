ARG BUILD_FROM
FROM $BUILD_FROM

LABEL maintainer="TheDraca"


# Install requirements for add-on i.e Python
RUN \
  apk add --no-cache \
    python3

    
# Copy all files in the app dir into the container
COPY app/*  /home/app/
RUN chmod a+x /home/app/main.py

# Copy launch script
COPY run.sh /
RUN chmod a+x /run.sh

#Run launch script
CMD [ "/run.sh" ]