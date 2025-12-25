RUN PROJECT



backend:

.\.venv\Scripts\Activate.ps1


python .\manage.py runserver

frontend:

cd .\backend\frontend\

npm run dev
