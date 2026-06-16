# GitHub Webhooks with FastAPI - Production Learning Project

## Goal

Build a FastAPI application that receives GitHub webhook events, validates signatures, stores events in PostgreSQL, processes them asynchronously, and exposes APIs to inspect received events.

By the end of this project, you will understand:

* Webhook fundamentals
* Public callback URLs
* Event-driven architecture
* Signature verification
* Idempotency
* Retry handling
* Background processing
* Database persistence
* Production webhook patterns

---

# Architecture

```text
Developer
    |
git push
    |
    v
GitHub Repository
    |
Webhook Event
    |
    v
FastAPI Webhook Endpoint
    |
Verify Signature
    |
Persist Event
    |
Queue Background Task
    |
    v
PostgreSQL
```

---

# Technology Stack

Backend:

* FastAPI
* SQLAlchemy
* PostgreSQL
* Alembic

Background Processing:

* Celery
* Redis

Webhook Exposure:

* Cloudflare Tunnel or should we use ngrok??

Testing:

* Pytest
* HTTPX

---

# Project Structure

```text
github-webhooks/

app/
|
├── api/
│   ├── webhooks.py
│   └── events.py
│
├── core/
│   ├── config.py
│   ├── security.py
│   └── logging.py
│
├── db/
│   ├── models.py
│   ├── session.py
│   └── migrations/
│
├── services/
│   ├── github_service.py
│   └── event_processor.py
│
├── workers/
│   └── celery_worker.py
│
├── tests/
│   ├── test_signature.py
│   ├── test_webhooks.py
│   └── test_events.py
│
├── main.py
├── requirements.txt
└── README.md
```

---

# Features

## Receive GitHub Events

Endpoint:

```http
POST /webhooks/github
```

Supported Events:

* push
* pull_request
* issues
* release

---

## Store Events

Every webhook should be stored.

Table:

```sql
webhook_events
```

Columns:

```text
id
event_id
event_type
repository
payload
received_at
processed
```

Reason:

Never lose incoming events.

---

## Verify GitHub Signature

GitHub sends:

```http
X-Hub-Signature-256
```

Never trust incoming payloads.

Verification Flow:

```text
Request
   |
Verify HMAC
   |
Valid?
 / \
No  Yes
 |    |
401 Continue
```

Reject invalid signatures.

---

# Idempotency

Very important.

GitHub may resend events.

Header:

```http
X-GitHub-Delivery
```

Example:

```text
12345-abcde
```

Store this ID.

Before processing:

```text
Already Exists?
    |
  Yes
    |
Ignore
```

This prevents duplicate processing.

---

# Background Processing

Never do heavy work inside the webhook endpoint.

Bad:

```python
receive_webhook()
    -> process_everything()
```

Good:

```python
receive_webhook()
    -> save_event()
    -> queue_task()
    -> return 200
```

Reason:

GitHub expects a fast response.

---

# Celery Integration

Webhook:

```python
process_event.delay(event_id)
```

Worker:

```python
process_event(event_id)
```

Responsibilities:

* Parse payload
* Extract metadata
* Generate analytics
* Send notifications

---

# Database Schema

## WebhookEvent

```python
id
delivery_id
event_type
repository_name
payload
processed
created_at
```

## ProcessedPush

```python
id
repository
branch
author
commit_count
created_at
```

---

# GitHub Setup

Create repository.

Navigate:

Settings
→ Webhooks
→ Add Webhook

Payload URL:

```text
https://your-domain.com/webhooks/github
```

Content Type:

```text
application/json
```

Secret:

```text
super-secret-key
```

Events:

* Pushes
* Pull Requests
* Issues

Save.

---

# Local Development

Run FastAPI:

```bash
uvicorn app.main:app --reload
```

Expose publicly:

```bash
cloudflared tunnel --url http://localhost:8000
```

Generated URL:

```text
https://random.trycloudflare.com
```

Use this URL in GitHub webhook settings.

---

# Event Flow

## Push Event

Developer:

```bash
git push
```

GitHub:

```text
push event
```

Webhook Payload:

```json
{
  "ref": "refs/heads/main",
  "repository": {
    "name": "learning-webhooks"
  }
}
```

FastAPI:

```text
Receive
Validate
Store
Queue
Respond
```

Worker:

```text
Process
Persist
Generate metrics
```

---

# Error Handling

Handle:

## Invalid Signature

Response:

```http
401 Unauthorized
```

---

## Invalid Payload

Response:

```http
400 Bad Request
```

---

## Database Failure

Log error.

Return:

```http
500 Internal Server Error
```

---

## Duplicate Event

Return:

```http
200 OK
```

Ignore processing.

---

# Logging

Log:

```text
delivery_id
event_type
repository
processing_time
status
```

Example:

```text
Webhook received
Event=push
Repo=backend
Delivery=abc123
```

---

# Security Best Practices

1. Always validate signatures.
2. Never trust payload content.
3. Store secrets in environment variables.
4. Use HTTPS.
5. Implement idempotency.
6. Log every request.
7. Limit endpoint exposure.
8. Validate headers.
9. Return responses quickly.
10. Move heavy work to workers.

---

# Testing Strategy

Unit Tests:

* Signature verification
* Payload parsing
* Event extraction

Integration Tests:

* Webhook endpoint
* Database persistence

End-to-End Tests:

* Receive webhook
* Store event
* Trigger worker
* Verify processed record

---

# Future Improvements

* Kafka integration
* Event replay mechanism
* Dead Letter Queue
* Multi-provider webhooks
* Slack notifications
* GitHub App integration
* Event analytics dashboard

---

# What You Will Learn

After completing this project you should be comfortable with:

* Webhooks
* FastAPI
* GitHub integrations
* Signature verification
* Background jobs
* Celery
* PostgreSQL
* Event-driven architecture
* Production backend design
* Reliability patterns
* Observability and logging
