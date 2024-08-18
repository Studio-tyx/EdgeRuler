FROM python
WORKDIR /code
COPY ./pythonProjectFolder /code
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
EXPOSE 5001
CMD ["python","turn_on_light.py"]

