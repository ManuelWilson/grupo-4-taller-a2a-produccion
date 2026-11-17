FROM public.ecr.aws/lambda/python:3.12

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}" --no-cache-dir

# Copiar el handler
COPY lambda_handler.py ${LAMBDA_TASK_ROOT}

# Comando de inicio
CMD ["lambda_handler.lambda_handler"]
