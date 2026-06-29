# Usa uma imagem oficial do Python leve
FROM python:3.14-slim

# Define variáveis de ambiente para o Python operar de forma otimizada no container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala as dependências do sistema necessárias para o PostgreSQL e compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências do projeto
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código do projeto para o container
COPY . /app/

# Expõe a porta que o Gunicorn/Django vai rodar
EXPOSE 8000

# Comando para rodar as migrações e iniciar o servidor de produção (Gunicorn)
CMD python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    gunicorn salvaguarda.wsgi:application --bind 0.0.0.0:8000