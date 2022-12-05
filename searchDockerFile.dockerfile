#FROM public.ecr.aws/lambda/provided:al2
#RUN yum update && yum install python3-pip
FROM public.ecr.aws/lambda/python:3.8

# Create app directory
WORKDIR ${LAMBDA_TASK_ROOT}

#Installs
RUN python3.8 -m pip install --upgrade pip
#RUN pip install sklearn -q --target "${LAMBDA_TASK_ROOT}"
RUN pip install wheel -q --target "${LAMBDA_TASK_ROOT}"
RUN pip install scikit-learn -q --target "${LAMBDA_TASK_ROOT}"
RUN pip install boto3 -q --target "${LAMBDA_TASK_ROOT}"
RUN yum install curl -y -q

#Pull Down Code
RUN curl -k -o ${LAMBDA_TASK_ROOT}/app.py https://raw.githubusercontent.com/GDIT-MissionAI/img-search/main/img-similarity-search.py

#handle the loading of the models.

#Entry point for the call
#ENTRYPOINT ["app.py"]
#ENTRYPOINT ["sentencetransformer", "app.py"]

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD ["app.lambda_handler"]
