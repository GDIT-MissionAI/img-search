FROM public.ecr.aws/lambda/python:3.8

# Create app directory
WORKDIR ${LAMBDA_TASK_ROOT}

#Installs
RUN pip install pickle -q --target "${LAMBDA_TASK_ROOT}"
RUN pip install numpy -q --target "${LAMBDA_TASK_ROOT}"
RUN pip install tensorflow -q --target "${LAMBDA_TASK_ROOT}"
RUN pip install tqdm -q --target "${LAMBDA_TASK_ROOT}"
RUN pip install boto3 -q --target "${LAMBDA_TASK_ROOT}"
RUN yum install curl
