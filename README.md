# EdTech Assignment Tracker - System Design Document

## Part A: System Design (Written)

### 1. System Architecture

The EdTech Assignment Tracker follows a modern 3-tier architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │    Database     │
│   (HTML/CSS/JS) │◄──►│   (FastAPI)     │◄──►│   (SQLite)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Components:**
- **Frontend Layer:** Static HTML pages with vanilla JavaScript for API communication
- **Application Layer:** FastAPI with async request handling and JWT authentication
- **Data Layer:** SQLAlchemy ORM with SQLite database (production-ready for PostgreSQL)
- **File Storage:** Local filesystem with configurable cloud storage support

### 2. Core Entities and Relationships

#### Entity Relationship Diagram (Tabular Format)

| Entity | Attributes | Primary Key | Foreign Keys | Relationships |
|--------|------------|-------------|--------------|---------------|
| **User** | id, name, email, password_hash, role, created_at | id | - | 1:N with Assignment (as teacher)<br>1:N with Submission (as student) |
| **Assignment** | id, title, description, due_date, created_at, teacher_id | id | teacher_id → User.id | N:1 with User (teacher)<br>1:N with Submission |
| **Submission** | id, text_answer, file_url, submitted_at, assignment_id, student_id | id | assignment_id → Assignment.id<br>student_id → User.id | N:1 with Assignment<br>N:1 with User (student) |

#### Detailed Entity Specifications

**User Entity:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) CHECK (role IN ('student', 'teacher')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Assignment Entity:**
```sql
CREATE TABLE assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    teacher_id INTEGER NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES users(id)
);
```

**Submission Entity:**
```sql
CREATE TABLE submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text_answer TEXT,
    file_url VARCHAR(500),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assignment_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    FOREIGN KEY (assignment_id) REFERENCES assignments(id),
    FOREIGN KEY (student_id) REFERENCES users(id),
    UNIQUE(assignment_id, student_id)  -- One submission per student per assignment
);
```

### 3. API Endpoints Definition

#### Authentication Endpoints

| Method | Endpoint | Description | Request Body | Response | Access Level |
|--------|----------|-------------|--------------|----------|--------------|
| POST | `/auth/signup` | User registration | `{name, email, password, role}` | `{id, name, email, role}` | Public |
| POST | `/auth/login` | User authentication | `{email, password}` | `{access_token, token_type}` | Public |

#### Assignment Management Endpoints

| Method | Endpoint | Description | Request Body | Response | Access Level |
|--------|----------|-------------|--------------|----------|--------------|
| POST | `/assignments` | Teacher creates assignment | `{title, description?, due_date?}` | `{id, title, description, due_date, created_at}` | Teacher Only |
| GET | `/assignments` | List all assignments | - | `[{assignment_objects}]` | Authenticated |
| GET | `/assignments?mine=true` | List teacher's assignments | - | `[{assignment_objects}]` | Teacher Only |

#### Submission Management Endpoints

| Method | Endpoint | Description | Request Body | Response | Access Level |
|--------|----------|-------------|--------------|----------|--------------|
| POST | `/assignments/{id}/submissions` | Student submits assignment | `multipart/form-data: {text_answer?, file?}` | `{id, text_answer, file_url, submitted_at, student}` | Student Only |
| GET | `/assignments/{id}/submissions` | Teacher views submissions | - | `[{submission_objects_with_student_info}]` | Assignment Owner Only |

#### API Response Examples

**Successful Assignment Creation:**
```json
{
  "id": 1,
  "title": "Math Assignment Chapter 5",
  "description": "Solve problems 1-20 from textbook",
  "due_date": "2024-01-15T23:59:00",
  "created_at": "2024-01-10T10:30:00"
}
```

**Submission with File:**
```json
{
  "id": 1,
  "text_answer": "Here are my solutions to the math problems...",
  "file_url": "uploads/a1_u5_solutions.pdf",
  "submitted_at": "2024-01-14T18:45:00",
  "student": {
    "id": 5,
    "name": "Jane Student",
    "email": "jane@student.edu"
  }
}
```

### 4. Authentication Strategy

#### JWT Token-Based Authentication

**Token Structure:**
```json
{
  "sub": "user_id",           // Subject (user identifier)
  "role": "student|teacher",  // User role for authorization
  "exp": 1640995200,         // Expiration timestamp
  "iat": 1640908800          // Issued at timestamp
}
```

**Authentication Flow:**
1. User submits credentials to `/auth/login`
2. Server validates credentials against database
3. Server generates JWT token with user ID and role
4. Client stores token and includes in Authorization header
5. Server validates token on protected routes

**Authorization Levels:**
- **Public:** Signup, Login
- **Authenticated:** View assignments
- **Student Only:** Submit assignments
- **Teacher Only:** Create assignments, view submissions
- **Resource Owner:** Teachers can only view their own assignment submissions

**Security Measures:**
- Password hashing using bcrypt with salt
- JWT token expiration (configurable, default 24 hours)
- Role-based access control middleware
- Input validation and sanitization

### 5. System Scalability Considerations

#### Current Architecture Limitations
- **Single Server:** No horizontal scaling
- **SQLite:** Limited concurrent writes
- **Local File Storage:** No redundancy or CDN
- **In-Memory Sessions:** Lost on server restart

#### Scaling Strategies

**Database Scaling:**
```
Current: SQLite (single file)
    ↓
Vertical: PostgreSQL (single instance)
    ↓
Horizontal: PostgreSQL with read replicas
    ↓
Distributed: Sharded PostgreSQL or NoSQL (MongoDB)
```

**Application Scaling:**
```
Current: Single FastAPI instance
    ↓
Load Balanced: Multiple FastAPI instances + nginx
    ↓
Microservices: Separate auth, assignment, submission services
    ↓
Containerized: Docker + Kubernetes orchestration
```

**File Storage Scaling:**
```
Current: Local filesystem
    ↓
Cloud Storage: AWS S3, Google Cloud Storage
    ↓
CDN Integration: CloudFront for global distribution
    ↓
Streaming: Direct client-to-S3 uploads with presigned URLs
```

**Caching Strategy:**
```
Level 1: Application-level caching (Redis)
Level 2: Database query caching
Level 3: CDN caching for static assets
Level 4: Browser caching with proper headers
```

#### Performance Optimization Roadmap

**Phase 1: Database Optimization**
- Add database indexes on frequently queried columns
- Implement connection pooling
- Add query optimization and monitoring

**Phase 2: Application Optimization**
- Implement Redis for session management
- Add background task processing (Celery)
- Implement API rate limiting

**Phase 3: Infrastructure Scaling**
- Containerize application with Docker
- Set up CI/CD pipeline
- Deploy on cloud platform (AWS, GCP, Azure)

**Phase 4: Advanced Features**
- Real-time notifications (WebSockets)
- Advanced file processing (virus scanning, format conversion)
- Analytics and reporting dashboard
- Multi-tenant support for multiple institutions

#### Monitoring and Observability

**Metrics to Track:**
- API response times and error rates
- Database query performance
- File upload success rates
- User authentication patterns
- System resource utilization

**Recommended Tools:**
- **Logging:** Structured logging with correlation IDs
- **Metrics:** Prometheus + Grafana dashboards
- **Error Tracking:** Sentry for production error monitoring
- **APM:** New Relic or DataDog for application performance

#### Security Enhancements

**Current Security Measures:**
- JWT token authentication
- Password hashing with bcrypt
- Role-based access control
- Input validation with Pydantic

**Future Security Improvements:**
- OAuth2 integration (Google, Microsoft)
- Two-factor authentication (2FA)
- API rate limiting and DDoS protection
- File upload virus scanning
- Audit logging for compliance
- HTTPS enforcement with SSL certificates

This system design provides a solid foundation for an educational assignment tracking platform with clear paths for scaling and enhancement as requirements grow.
#   E d t e c h - a s s i g n m e n t - t r a c k e r  
 #   E d t e c h - a s s i g n m e n t - t r a c k e r  
 