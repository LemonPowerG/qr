# უკუკავშირის სისტემა QR კოდებით

ეს არის ვებ აპლიკაცია, რომელიც საშუალებას გაძლევთ შექმნათ და მართოთ უკუკავშირის სისტემა QR კოდების გამოყენებით. სისტემა განკუთვნილია მიკროსაფინანსო ორგანიზაციებისთვის, რომლებსაც სურთ მიიღონ უკუკავშირი მომხმარებლებისგან სხვადასხვა ფილიალებში.

## ფუნქციონალი

- QR კოდების გენერაცია თითოეული ფილიალისთვის
- უკუკავშირის ფორმა მომხმარებლებისთვის
- ადმინისტრატორის პანელი ფილიალების მართვისთვის
- უკუკავშირების სტატისტიკა და ანალიზი
- მოქნილი და მობილურად მორგებული ინტერფეისი

## ინსტალაცია

1. დააკლონირეთ რეპოზიტორია:
```bash
git clone [repository-url]
cd feedback-system
```

2. შექმენით ვირტუალური გარემო და გააქტიურეთ:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. დააინსტალირეთ დამოკიდებულებები:
```bash
pip install -r requirements.txt
```

4. შექმენით ადმინისტრატორის მომხმარებელი:
```python
from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = User(
        username='admin',
        password_hash=generate_password_hash('your-password'),
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()
```

5. გაუშვით აპლიკაცია:
```bash
python app.py
```

## გამოყენება

1. შედით ადმინისტრატორის პანელზე (`/admin`)
2. დაამატეთ ფილიალები
3. ჩამოტვირთეთ QR კოდები და განათავსეთ ფილიალებში
4. მომხმარებლები შეძლებენ QR კოდის სკანირებას და მისცემენ უკუკავშირს

## ტექნოლოგიები

- Python 3.8+
- Flask
- SQLAlchemy
- QR Code
- Bootstrap 5
- Font Awesome

## ლიცენზია

MIT License 