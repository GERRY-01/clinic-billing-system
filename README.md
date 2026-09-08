# Clinic Billing System

A simple clinic billing system built with **Django REST Framework, PostgreSQL, React, and Docker**.

## How to run

Make sure Docker is installed, then from the project root run:

```bash
sudo docker compose up --build
```

The frontend is available at:

```text
http://localhost:5173
```

The API is available at:

```text
http://localhost:8000/api/
```

Docker Compose runs the React frontend, Django backend, and PostgreSQL database together. Database migrations are applied automatically when the backend starts.

## What I chose and why

I used **Django REST Framework** because it provides a simple way to build the required API endpoints. **PostgreSQL** was used as the relational database because bills, bill items, and payments have clear relationships.

Money is represented using Django's **DecimalField** rather than floating-point numbers. This avoids precision problems that can occur with values such as `0.1 + 0.2`.

Bills, bill items, and payments are separate models because one bill can contain multiple items and can also have multiple payments.

For M-Pesa payments, the transaction ID is unique. This means that if the provider sends the same successful webhook more than once, the same payment is not recorded twice.

## Production scenarios

* **Duplicate webhook:** handled.
* **Webhook for an already fully paid bill:** handled by rejecting payments greater than the outstanding balance.
* **Late M-Pesa webhook after the same payment was recorded as cash:** not fully handled. A production system would need payment reconciliation or a way to match the two transactions.
* **FAILED webhook:** handled; no payment is created.
* **Partial payment:** handled; the remaining balance stays outstanding.
* **Overpayment:** handled; the payment is rejected.

## Tests

Automated tests cover successful cash and M-Pesa payments, duplicate webhooks, failed webhooks, partial payments, and overpayments.

Run the tests with:

```bash
sudo docker compose exec backend python manage.py test billing
```

## What I would do next

For a production system, I would add database transactions/locking for safer concurrent payment processing, authenticate and validate incoming webhooks from the mobile-money provider, and add reconciliation for cases where the same payment is recorded through different channels.

This project intentionally does not include authentication, user management, an admin panel, or a real mobile-money provider integration because they were outside the assessment scope.
