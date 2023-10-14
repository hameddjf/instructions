import numpy as np
from sklearn.linear_model import LinearRegression

from .models import Report


def predict_faulty(report_id):
    # بازیابی گزارش با استفاده از شناسه
    report = Report.objects.get(id=report_id)

    # تبدیل داده‌ها به آرایه NumPy
    X = np.array([[report.min_temperature, report.max_temperature]])
    y = np.array([report.is_faulty])

    # ساخت یک مدل رگرسیون خطی و آموزش آن با داده‌ها
    model = LinearRegression()
    model.fit(X, y)

    # پیش‌بینی مشکل برای داده فعلی
    prediction = model.predict(X)

    return prediction[0]