#FROM public.ecr.aws/lambda/provided:al2
#RUN yum update && yum install python3-pip
FROM public.ecr.aws/lambda/python:3.8

# Create app directory
WORKDIR ${LAMBDA_TASK_ROOT}

#Installs
RUN pip install pillow -q --target "${LAMBDA_TASK_ROOT}"
RUN pip install tensorflow -q --target "${LAMBDA_TASK_ROOT}"
RUN pip install numpy -q --target "${LAMBDA_TASK_ROOT}"
#RUN pip install tqdm -q --target "${LAMBDA_TASK_ROOT}"
RUN pip install boto3 -q --target "${LAMBDA_TASK_ROOT}"
RUN yum install curl

#Pull Down Code
RUN curl -k -o ${LAMBDA_TASK_ROOT}/app.py https://raw.githubusercontent.com/GDIT-MissionAI/img-search/main/img-similarity-encoding.py

#handle the loading of the models.

#Entry point for the call
#ENTRYPOINT ["app.py"]
#ENTRYPOINT ["sentencetransformer", "app.py"]

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD ["app.lambda_handler"]
