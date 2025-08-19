# API Reference - Research-to-Insights Agent

Complete API documentation for the Research-to-Insights Agent backend services.

## 🔐 Authentication

All API endpoints require authentication via JWT tokens obtained through Supabase Auth.

### **Headers**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### **Error Responses**
```json
{
  "detail": "Not authenticated"
}
```

## 📥 Content Ingestion API

### **Process Content**

Process a URL or text content for AI analysis and storage.

#### **Endpoint**
```http
POST /api/v1/ingest/
```

#### **Request Body**
```json
{
  "source_url": "https://example.com/article",
  "text_content": "Optional direct text input"
}
```

#### **Response**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Content processing started with enhanced pipeline",
  "progress": null,
  "result": null
}
```

#### **Status Codes**
- `201 Created`: Processing started successfully
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Processing failed

### **Get Processing Status**

Check the status of a content processing job.

#### **Endpoint**
```http
GET /api/v1/ingest/{job_id}/status
```

#### **Response**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Stage: ai_analysis",
  "progress": 0.6,
  "result": {
    "content_length": 2500,
    "chunks_count": 5,
    "embeddings_count": 5
  }
}
```

#### **Status Values**
- `pending`: Job queued for processing
- `processing`: Currently being processed
- `completed`: Successfully completed
- `failed`: Processing failed
- `cancelled`: Job was cancelled

## 🔍 Search API

### **Enhanced Search (GET)**

Search documents using query parameters.

#### **Endpoint**
```http
GET /api/v1/search/
```

#### **Query Parameters**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | string | required | Search query |
| `search_type` | string | `hybrid` | Search type (semantic, keyword, hybrid, tag, content_type, quality, date_range) |
| `content_type` | string | - | Filter by content type |
| `quality` | string | - | Filter by quality level |
| `language` | string | - | Filter by language |
| `sort_by` | string | `relevance` | Sort order (relevance, date_newest, date_oldest, quality, reading_time, complexity, word_count) |
| `limit` | integer | `20` | Maximum number of results |
| `offset` | integer | `0` | Number of results to skip |

#### **Example Request**
```http
GET /api/v1/search/?q=artificial intelligence&search_type=hybrid&content_type=technical&quality=excellent&sort_by=relevance&limit=10
```

#### **Response**
```json
{
  "results": [
    {
      "document_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Introduction to Artificial Intelligence",
      "summary": "A comprehensive guide to AI fundamentals...",
      "source_url": "https://example.com/ai-guide",
      "similarity_score": 0.95,
      "document_tags": ["ai", "machine-learning", "technology"],
      "content_type": "technical",
      "quality": "excellent",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_count": 1,
  "query": "artificial intelligence",
  "search_type": "hybrid",
  "metadata": {
    "query": "artificial intelligence",
    "search_type": "hybrid",
    "filters_applied": {},
    "sort_by": "relevance",
    "total_results": 1,
    "limit": 10,
    "offset": 0,
    "search_timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### **Enhanced Search (POST)**

Search with advanced filtering options.

#### **Endpoint**
```http
POST /api/v1/search/
```

#### **Request Body**
```json
{
  "query": "machine learning algorithms",
  "search_type": "semantic",
  "filters": {
    "content_type": "technical",
    "quality": "excellent",
    "language": "en",
    "tags": ["python", "ai"],
    "word_count": [1000, 5000],
    "reading_time": [5, 30],
    "complexity": [0.3, 0.8],
    "date_range": ["2024-01-01", "2024-01-31"]
  },
  "sort_by": "relevance",
  "limit": 20,
  "offset": 0
}
```

#### **Filter Options**
- `content_type`: technical, academic, news, blog_post, documentation
- `quality`: excellent, good, fair, poor
- `language`: en, es, fr, de, etc.
- `tags`: Array of tags to include
- `word_count`: [min, max] word count range
- `reading_time`: [min, max] reading time in minutes
- `complexity`: [min, max] complexity score (0-1)
- `date_range`: [start_date, end_date] in ISO format

## 📚 Document Management API

### **List Documents**

Retrieve a list of user's documents with optional filtering.

#### **Endpoint**
```http
GET /api/v1/documents/
```

#### **Query Parameters**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | `20` | Maximum number of results |
| `offset` | integer | `0` | Number of results to skip |
| `content_type` | string | - | Filter by content type |
| `quality` | string | - | Filter by quality level |
| `processing_status` | string | - | Filter by processing status |

#### **Response**
```json
{
  "documents": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "user-uuid",
      "source_url": "https://example.com/article",
      "title": "Document Title",
      "summary": "Document summary...",
      "tags": ["tag1", "tag2"],
      "insights": ["insight1", "insight2"],
      "action_items": ["action1", "action2"],
      "quotable_snippets": [
        {
          "text": "Notable quote",
          "context": "Quote context"
        }
      ],
      "processing_status": "completed",
      "content_type": "technical",
      "quality": "excellent",
      "language": "en",
      "word_count": 1500,
      "sentence_count": 75,
      "paragraph_count": 15,
      "reading_time_minutes": 8,
      "complexity_score": 0.65,
      "key_phrases": ["phrase1", "phrase2"],
      "structure": {
        "headers": ["header1", "header2"],
        "lists": 3,
        "code_blocks": 2
      },
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_count": 1,
  "limit": 20,
  "offset": 0
}
```

### **Get Document**

Retrieve a specific document by ID.

#### **Endpoint**
```http
GET /api/v1/documents/{document_id}
```

#### **Response**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-uuid",
  "source_url": "https://example.com/article",
  "title": "Document Title",
  "summary": "Document summary...",
  "tags": ["tag1", "tag2"],
  "insights": ["insight1", "insight2"],
  "action_items": ["action1", "action2"],
  "quotable_snippets": [
    {
      "text": "Notable quote",
      "context": "Quote context"
    }
  ],
  "processing_status": "completed",
  "content_type": "technical",
  "quality": "excellent",
  "language": "en",
  "word_count": 1500,
  "sentence_count": 75,
  "paragraph_count": 15,
  "reading_time_minutes": 8,
  "complexity_score": 0.65,
  "key_phrases": ["phrase1", "phrase2"],
  "structure": {
    "headers": ["header1", "header2"],
    "lists": 3,
    "code_blocks": 2
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### **Update Document**

Update document metadata.

#### **Endpoint**
```http
PUT /api/v1/documents/{document_id}
```

#### **Request Body**
```json
{
  "title": "Updated Title",
  "summary": "Updated summary",
  "tags": ["updated", "tags"],
  "insights": ["updated", "insights"],
  "action_items": ["updated", "actions"]
}
```

#### **Response**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Updated Title",
  "summary": "Updated summary",
  "tags": ["updated", "tags"],
  "insights": ["updated", "insights"],
  "action_items": ["updated", "actions"],
  "updated_at": "2024-01-15T11:00:00Z"
}
```

### **Delete Document**

Delete a document and all associated data.

#### **Endpoint**
```http
DELETE /api/v1/documents/{document_id}
```

#### **Response**
```json
{
  "message": "Document deleted successfully"
}
```

## 🔧 Processing Pipeline API

### **Get Processing Metrics**

Retrieve processing pipeline performance metrics.

#### **Endpoint**
```http
GET /api/v1/processing/metrics
```

#### **Response**
```json
{
  "total_processed": 150,
  "successful": 142,
  "failed": 8,
  "average_processing_time": 4.2,
  "success_rate": 0.947,
  "total_processing_time": 630.0
}
```

### **Cancel Processing Task**

Cancel an ongoing processing task.

#### **Endpoint**
```http
POST /api/v1/processing/{task_id}/cancel
```

#### **Response**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "cancelled",
  "message": "Task cancelled successfully"
}
```

## 📊 Search Types Reference

### **Semantic Search**
- **Description**: Finds conceptually similar content using vector embeddings
- **Best For**: Finding content similar to a concept or idea
- **Example**: "artificial intelligence" finds AI, ML, neural networks content

### **Keyword Search**
- **Description**: Exact word and phrase matching
- **Best For**: Finding specific terms or phrases
- **Example**: "Python API documentation" finds exact matches

### **Tag Search**
- **Description**: Search using hashtags or extracted tags
- **Best For**: Finding content with specific tags
- **Example**: "#python #api #authentication"

### **Content Type Search**
- **Description**: Filter by content category
- **Best For**: Finding specific types of content
- **Example**: "technical documentation" finds only technical content

### **Quality Search**
- **Description**: Filter by content quality level
- **Best For**: Finding high-quality articles
- **Example**: "excellent quality" finds premium content

### **Date Range Search**
- **Description**: Filter by publication date
- **Best For**: Finding recent or historical content
- **Examples**: "today", "this week", "last month"

### **Hybrid Search**
- **Description**: Combines multiple search methods
- **Best For**: Most accurate and comprehensive results
- **Default**: Used when no specific search type is specified

## 📋 Content Types

### **Available Content Types**
- `technical`: Technical documentation, code guides, API docs
- `academic`: Research papers, scholarly articles, academic content
- `news`: News articles, current events, announcements
- `blog_post`: Blog posts, opinion pieces, personal content
- `documentation`: User guides, manuals, tutorials

### **Quality Levels**
- `excellent`: High-quality, well-written, comprehensive content
- `good`: Good quality, informative content
- `fair`: Average quality, basic information
- `poor`: Low quality, minimal value content

## 🔄 Error Handling

### **Standard Error Response**
```json
{
  "detail": "Error message description"
}
```

### **Validation Error Response**
```json
{
  "detail": [
    {
      "loc": ["body", "source_url"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### **Common Error Codes**
- `400 Bad Request`: Invalid input data or parameters
- `401 Unauthorized`: Authentication required or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## 📈 Rate Limiting

API endpoints are rate-limited to ensure fair usage:

- **Search endpoints**: 100 requests per minute per user
- **Ingestion endpoints**: 10 requests per minute per user
- **Document management**: 50 requests per minute per user

### **Rate Limit Response**
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

```json
{
  "detail": "Rate limit exceeded. Please try again in 60 seconds."
}
```

## 🔗 Pagination

List endpoints support pagination using `limit` and `offset` parameters:

### **Example**
```http
GET /api/v1/documents/?limit=10&offset=20
```

### **Response Headers**
```http
X-Total-Count: 150
X-Page-Size: 10
X-Current-Page: 3
```

## 📝 Data Types

### **UUID**
- Format: `550e8400-e29b-41d4-a716-446655440000`
- Used for: Document IDs, User IDs, Task IDs

### **Timestamp**
- Format: ISO 8601 (`2024-01-15T10:30:00Z`)
- Used for: Created/updated dates, processing times

### **Vector**
- Format: Array of 1536 floating-point numbers
- Used for: Document embeddings

### **JSONB**
- Format: JSON object
- Used for: Complex metadata, insights, structure data

### **Array**
- Format: JSON array
- Used for: Tags, insights, action items, key phrases

---

**For interactive API documentation, visit `/docs` when the backend server is running.**
