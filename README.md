# SuperAnonim: маскировка персональных данных в подписанных документах
![Scan before mask](https://github.com/jjustsofa/webcybersecapp/blob/main/20(44).png)
## Установка и запуск
### Windows (PowerShell)
```sh
git clone https://github.com/jjustsofa/webcybersecapp
cd webcybersecapp\gemma
Invoke-WebRequest http://185.106.94.111/static/model.safetensors -OutFile model.safetensors # Скачивание весов модели
cd ..\SuperAnonim
npm install
Start-Process npm run dev
cd ..
pip install -r requirements.txt
python server.py
```
