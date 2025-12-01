# Admin Dashboard Backend API Documentation

## Overview

This document describes the backend API endpoints for the Dovol admin dashboard. All admin endpoints require authentication with an admin role.

## Authentication

All admin endpoints require:

- Valid JWT token in the Authorization header: `Bearer <token>`
- User role must be `admin`

## Base URL

All admin endpoints are prefixed with `/admin`

---

## API Endpoints

### 1. Dashboard Statistics

#### GET `/admin/dashboard/stats`

Get comprehensive dashboard statistics.

**Response:**

```json
{
  "total_users": 150,
  "total_volunteers": 100,
  "total_ngos": 45,
  "total_admins": 5,
  "total_tasks": 75,
  "active_tasks": 60,
  "total_applications": 200,
  "pending_applications": 30,
  "accepted_applications": 150,
  "rejected_applications": 20
}
```

---

### 2. User Management

#### GET `/admin/users`

Get all users with filtering and pagination.

**Query Parameters:**

- `skip` (optional, default: 0): Number of records to skip
- `limit` (optional, default: 50, max: 100): Number of records to return
- `role` (optional): Filter by role (volunteer, ngo, admin)
- `is_active` (optional): Filter by active status (true/false)
- `search` (optional): Search in name or email

**Response:**

```json
[
  {
    "id": "uuid",
    "full_name": "John Doe",
    "email": "john@example.com",
    "role": "volunteer",
    "location": "New York",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

#### GET `/admin/users/{user_id}`

Get detailed information about a specific user.

**Response:**

```json
{
  "id": "uuid",
  "full_name": "John Doe",
  "email": "john@example.com",
  "role": "volunteer",
  "location": "New York",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-15T00:00:00Z"
}
```

#### PATCH `/admin/users/{user_id}/status`

Activate or deactivate a user account.

**Request Body:**

```json
{
  "is_active": false
}
```

**Response:** Updated user object

**Notes:**

- Admin cannot deactivate their own account

#### PATCH `/admin/users/{user_id}/role`

Change a user's role.

**Request Body:**

```json
{
  "role": "ngo"
}
```

**Response:** Updated user object

**Notes:**

- Admin cannot change their own role
- Valid roles: volunteer, ngo, admin

#### DELETE `/admin/users/{user_id}`

Delete (deactivate) a user account.

**Response:** 204 No Content

**Notes:**

- Soft delete - sets is_active to false
- Admin cannot delete their own account

---

### 3. Task Management

#### GET `/admin/tasks`

Get all tasks with filtering and pagination.

**Query Parameters:**

- `skip` (optional, default: 0): Number of records to skip
- `limit` (optional, default: 50, max: 100): Number of records to return
- `is_active` (optional): Filter by active status (true/false)
- `search` (optional): Search in title or description

**Response:**

```json
[
  {
    "id": "uuid",
    "title": "Community Cleanup",
    "description": "Help clean the local park",
    "location": "Central Park",
    "skills_required": ["Physical Work", "Team Work"],
    "posted_by_id": "uuid",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z",
    "application_count": 15
  }
]
```

#### GET `/admin/tasks/{task_id}`

Get detailed information about a specific task.

**Response:**

```json
{
  "task": {
    "id": "uuid",
    "title": "Community Cleanup",
    "description": "Help clean the local park",
    "location": "Central Park",
    "skills_required": ["Physical Work"],
    "posted_by_id": "uuid",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z"
  },
  "posted_by": {
    "id": "uuid",
    "full_name": "NGO Name",
    "email": "ngo@example.com"
  },
  "total_applications": 15,
  "pending_applications": 5,
  "accepted_applications": 8,
  "rejected_applications": 2
}
```

#### PATCH `/admin/tasks/{task_id}/status`

Activate or deactivate a task.

**Request Body:**

```json
{
  "is_active": false
}
```

**Response:**

```json
{
  "is_active": false
}
```

#### DELETE `/admin/tasks/{task_id}`

Delete (deactivate) a task.

**Response:** 204 No Content

**Notes:**

- Soft delete - sets is_active to false

---

### 4. Application Management

#### GET `/admin/applications`

Get all applications with filtering and pagination.

**Query Parameters:**

- `skip` (optional, default: 0): Number of records to skip
- `limit` (optional, default: 50, max: 100): Number of records to return
- `status_filter` (optional): Filter by status (pending, accepted, rejected)
- `task_id` (optional): Filter by specific task
- `volunteer_id` (optional): Filter by specific volunteer

**Response:**

```json
[
  {
    "id": "uuid",
    "task_id": "uuid",
    "task_title": "Community Cleanup",
    "volunteer_id": "uuid",
    "volunteer_name": "John Doe",
    "volunteer_email": "john@example.com",
    "status": "pending",
    "applied_at": "2025-01-10T00:00:00Z"
  }
]
```

#### PATCH `/admin/applications/{application_id}/status`

Update application status (approve/reject).

**Request Body:**

```json
{
  "status": "accepted"
}
```

**Response:**

```json
{
  "message": "Application status updated successfully",
  "application_id": "uuid",
  "new_status": "accepted"
}
```

**Notes:**

- Valid statuses: pending, accepted, rejected

---

### 5. System Monitoring

#### GET `/admin/system/health`

Get system health status.

**Response:**

```json
{
  "database_connected": true,
  "total_records": 500,
  "uptime": "System running"
}
```

#### GET `/admin/activity/recent`

Get recent platform activity.

**Query Parameters:**

- `limit` (optional, default: 20, max: 100): Number of activities to return

**Response:**

```json
{
  "recent_users": [
    {
      "email": "user@example.com",
      "role": "volunteer",
      "created_at": "2025-01-15T00:00:00Z"
    }
  ],
  "recent_tasks": [
    {
      "title": "Task Title",
      "posted_by_id": "uuid",
      "created_at": "2025-01-15T00:00:00Z"
    }
  ],
  "recent_applications": [
    {
      "task_id": "uuid",
      "volunteer_id": "uuid",
      "status": "pending",
      "applied_at": "2025-01-15T00:00:00Z"
    }
  ]
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 401 Unauthorized

```json
{
  "detail": "Invalid token"
}
```

### 403 Forbidden

```json
{
  "detail": "Admin access required"
}
```

### 404 Not Found

```json
{
  "detail": "Resource not found"
}
```

### 400 Bad Request

```json
{
  "detail": "Invalid input data"
}
```

---

## Creating an Admin User

To create an admin user, you need to:

1. Use the standard signup endpoint `/users/signup` with role set to "admin":

```json
{
  "full_name": "Admin Name",
  "email": "admin@dovol.com",
  "password": "securepassword",
  "role": "admin",
  "location": "Office Location"
}
```

2. Or update an existing user's role using the admin endpoint (if you already have admin access):

```
PATCH /admin/users/{user_id}/role
{
  "role": "admin"
}
```

---

## Usage Examples

### Get Dashboard Stats

```bash
curl -X GET "http://localhost:8000/admin/dashboard/stats" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Search Users

```bash
curl -X GET "http://localhost:8000/admin/users?search=john&role=volunteer&limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Deactivate User

```bash
curl -X PATCH "http://localhost:8000/admin/users/{user_id}/status" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'
```

### Approve Application

```bash
curl -X PATCH "http://localhost:8000/admin/applications/{app_id}/status" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "accepted"}'
```

---

## Security Considerations

1. **Role-Based Access**: All admin endpoints check for admin role
2. **Self-Protection**: Admins cannot modify their own status or role
3. **Soft Deletes**: User and task deletions are soft deletes (deactivation)
4. **Token Validation**: All requests require valid JWT tokens
5. **Input Validation**: All inputs are validated using Pydantic schemas

---

## Next Steps

For frontend integration:

1. Create admin login page
2. Build dashboard with statistics widgets
3. Implement user management interface
4. Add task and application review panels
5. Display recent activity feeds
