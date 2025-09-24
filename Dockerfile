# Dockerfile
# FROM public.ecr.aws/lambda/python:3.11

# RUN yum install -y unzip wget fontconfig GConf2-devel alsa-lib atk cups-libs libXcomposite \
#     libXcursor libXdamage libXext libXi libXinerama libXrandr libXScrnSaver libXtst pango

# RUN wget https://storage.googleapis.com/chrome-for-testing-public/129.0.6647.0/linux64/chrome-linux64.zip -P /tmp/
# RUN unzip /tmp/chrome-linux64.zip -d /opt/ && mv /opt/chrome-linux64 /opt/chrome && rm /tmp/chrome-linux64.zip

# RUN wget https://storage.googleapis.com/chrome-for-testing-public/129.0.6647.0/linux64/chromedriver-linux64.zip -P /tmp/
# RUN unzip /tmp/chromedriver-linux64.zip -d /opt/ && mv /opt/chromedriver-linux64/chromedriver /opt/chromedriver && rm /tmp/chromedriver-linux64.zip

# COPY lambda/requirements.txt .
# RUN pip install -r requirements.txt
# COPY lambda/script.py ${LAMBDA_TASK_ROOT}
# CMD [ "script.lambda_handler" ]

FROM public.ecr.aws/lambda/python:3.12
# Install chrome dependencies
RUN dnf install -y atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel nss mesa-libgbm jq unzip
# Copy and run the chrome installer script
COPY ./chrome-installer.sh ./chrome-installer.sh
RUN chmod +x ./chrome-installer.sh
RUN ./chrome-installer.sh
RUN rm ./chrome-installer.sh
# Install selenium
RUN pip install selenium
# Copy the main application code
COPY lambda/tester.py ${LAMBDA_TASK_ROOT}
# Command to run the Lambda function
CMD [ "tester.lambda_handler" ]