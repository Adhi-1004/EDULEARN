"""
API Documentation Templates
Templates for generating comprehensive API documentation
"""

# API Endpoint Documentation Template
ENDPOINT_DOC_TEMPLATE = """
## {endpoint_name}

**Method:** `{method}`  
**Path:** `{path}`  
**Description:** {description}

### Parameters

{parameters}

### Request Body

{request_body}

### Response

{response}

### Example Request

```bash
curl -X {method} "{base_url}{path}" \\
  -H "Authorization: Bearer {token}" \\
  -H "Content-Type: application/json" \\
  -d '{request_example}'
```

### Example Response

```json
{response_example}
```

### Error Responses

{error_responses}

---
"""

# Authentication Documentation
AUTH_DOC = """
## Authentication

EDULEARN API uses JWT (JSON Web Token) for authentication. All protected endpoints require a valid JWT token.

### Getting a Token

1. **Register** a new account:
   ```bash
   POST /api/auth/register
   ```

2. **Login** with your credentials:
   ```bash
   POST /api/auth/login
   ```

3. **Use the token** in subsequent requests:
   ```bash
   Authorization: Bearer <your-jwt-token>
   ```

### Token Expiration

- Access tokens expire after 24 hours
- Refresh tokens expire after 7 days
- Use the refresh endpoint to get a new access token

### Role-Based Access

- **Student**: Can take assessments, view results
- **Teacher**: Can create assessments, manage batches, view analytics
- **Admin**: Full system access and user management
"""

# Error Handling Documentation
ERROR_DOC = """
## Error Handling

All API errors return structured JSON responses with the following format:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_CREDENTIALS` | 401 | Invalid email/password |
| `TOKEN_EXPIRED` | 401 | JWT token has expired |
| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks required permissions |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource doesn't exist |
| `VALIDATION_ERROR` | 422 | Request data validation failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_SERVER_ERROR` | 500 | Server error |

### Validation Errors

Validation errors include detailed field information:

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
"""

# Rate Limiting Documentation
RATE_LIMIT_DOC = """
## Rate Limiting

API requests are rate-limited to ensure fair usage and system stability.

### Limits by Endpoint Category

| Category | Limit | Window |
|----------|-------|--------|
| General API | 100 requests | 1 minute |
| Assessment Creation | 10 requests | 1 minute |
| Code Execution | 20 requests | 1 minute |
| Authentication | 5 requests | 1 minute |

### Rate Limit Headers

All responses include rate limit information:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Exceeding Limits

When rate limits are exceeded, the API returns:

```json
{
  "detail": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```
"""

# Webhook Documentation
WEBHOOK_DOC = """
## Webhooks

EDULEARN supports webhooks for real-time event notifications.

### Supported Events

- `assessment.completed` - Student completes an assessment
- `assessment.published` - Teacher publishes an assessment
- `batch.created` - New batch is created
- `user.registered` - New user registration

### Webhook Payload

```json
{
  "event": "assessment.completed",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "assessment_id": "assessment_123",
    "student_id": "student_456",
    "score": 85,
    "completion_time": 45
  }
}
```

### Security

Webhooks are secured using HMAC signatures. Include the signature in the `X-Webhook-Signature` header.
"""

# SDK Documentation
SDK_DOC = """
## SDKs and Libraries

### JavaScript/TypeScript

```bash
npm install @edulearn/api-client
```

```javascript
import { EduLearnClient } from '@edulearn/api-client';

const client = new EduLearnClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.edulearn.com'
});

// Create an assessment
const assessment = await client.assessments.create({
  title: 'Math Quiz',
  subject: 'Mathematics',
  difficulty: 'intermediate'
});
```

### Python

```bash
pip install edulearn-api
```

```python
from edulearn import EduLearnClient

client = EduLearnClient(
    api_key='your-api-key',
    base_url='https://api.edulearn.com'
)

# Create an assessment
assessment = client.assessments.create(
    title='Math Quiz',
    subject='Mathematics',
    difficulty='intermediate'
)
```

### cURL Examples

```bash
# Get all assessments
curl -H "Authorization: Bearer $TOKEN" \\
  https://api.edulearn.com/api/assessments

# Create a new assessment
curl -X POST \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"title":"Math Quiz","subject":"Mathematics"}' \\
  https://api.edulearn.com/api/assessments
```
"""
