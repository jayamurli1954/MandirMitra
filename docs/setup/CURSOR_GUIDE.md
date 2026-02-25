# Using Cursor.ai with Claude Sonnet 4.5 - MandirMitra - Temple Management System

**Guide for building this project with AI assistance**

---

## What is Cursor.ai?

Cursor is an AI-powered IDE (basically VS Code++) that integrates Claude Sonnet 4.5 to help you code faster and smarter. Think of it as having an expert developer pair-programming with you 24/7.

---

## Setup Cursor for This Project

### 1. Install Cursor

Download from: https://cursor.sh/

### 2. Open This Project

```bash
# Clone your repo
git clone https://github.com/yourusername/temple-management.git
cd temple-management

# Open in Cursor
cursor .
```

### 3. Configure Cursor Settings

1. **Open Settings** (Cmd/Ctrl + ,)
2. **Select Claude Sonnet 4.5** as your model
3. **Enable "Use project context"** - This lets Claude see your whole codebase

---

## How to Use Cursor.ai Effectively

### 1. Chat Mode (Cmd/Ctrl + L)

Ask questions about your code or get help:

**Examples:**
```
You: "How do I add a new API endpoint for donations?"
Claude: [Explains and shows code]

You: "What's wrong with this function?"
Claude: [Reviews and suggests fixes]

You: "How should I structure the seva booking module?"
Claude: [Provides architecture guidance]
```

### 2. Inline Edit (Cmd/Ctrl + K)

Select code and ask Claude to modify it:

**Examples:**
```
1. Select a function
2. Press Cmd/Ctrl + K
3. Type: "Add error handling and logging"
4. Claude rewrites the function

OR

1. Highlight a block
2. Cmd/Ctrl + K
3. "Convert this to use async/await"
4. Done!
```

### 3. Generate Code from Scratch

**Example Workflow:**
```
1. Create new file: app/api/donations.py
2. Cmd/Ctrl + K
3. Type: "Create a FastAPI router for donations with endpoints for:
   - POST /donations (create donation)
   - GET /donations (list donations)
   - GET /donations/{id} (get single donation)
   - Include proper validation and error handling"
4. Claude generates complete code!
```

---

## Best Practices for This Project

### 1. Always Provide Context

**❌ Bad:**
```
"Write a donation function"
```

**✅ Good:**
```
"Write a donation creation function that:
- Takes devotee_id, amount, category, payment_mode
- Validates amount > 0
- Generates receipt number (format: TEMPLE-YEAR-SEQUENCE)
- Saves to PostgreSQL using SQLAlchemy
- Returns the created donation object
- Follows the schema in DATABASE_SCHEMA.md"
```

### 2. Reference Documentation

When asking questions, point Claude to relevant docs:

```
"Based on PRD.md, implement the seva booking feature with:
- Date selection
- Availability check
- Payment collection
- Booking confirmation
Follow the database schema in DATABASE_SCHEMA.md"
```

### 3. Iterate and Refine

Start simple, then improve:

```
1st prompt: "Create basic donation form"
2nd prompt: "Add validation for phone number (10 digits)"
3rd prompt: "Add loading state and error handling"
4th prompt: "Make it mobile responsive"
```

---

## Cursor Features You'll Love

### 1. Tab Autocomplete

Claude suggests entire functions or blocks:

```python
def create_donation(devotee_id: int, amount: float):
    # Just start typing and press Tab to accept suggestions
    [Claude suggests the entire function implementation]
```

### 2. Multi-File Editing

```
1. Open multiple files
2. Cmd/Ctrl + K in chat
3. "Update both donation.py and donation_service.py to add refund functionality"
4. Claude edits both files!
```

### 3. Terminal Integration

```
Ask: "What command do I run to create a database migration?"
Claude: "Run: alembic revision --autogenerate -m 'add_seva_table'"
```

### 4. Bug Fixing

```
1. See an error
2. Cmd/Ctrl + K
3. Paste error message
4. "Fix this error"
5. Claude debugs and fixes!
```

---

## Prompts for Common Tasks

### Creating API Endpoints

```
"Create a FastAPI endpoint for [feature] that:
- Method: POST
- Route: /api/v1/[resource]
- Accepts: [list fields]
- Validates: [list rules]
- Returns: [describe response]
- Handles errors: [list error cases]
- Follows the pattern in app/api/donations.py"
```

### Creating Database Models

```
"Create a SQLAlchemy model for [table_name] with:
- Fields: [list fields with types]
- Relationships: [describe relationships]
- Indexes: [list indexes]
- Follow the pattern in app/models/donation.py
- Match the schema in DATABASE_SCHEMA.md"
```

### Creating React Components

```
"Create a React component for [feature] that:
- Uses Material-UI
- Has fields: [list fields]
- Validates: [list rules]
- Calls API: [endpoint]
- Shows loading state
- Handles errors
- Follow pattern in src/components/DonationForm.js"
```

### Debugging

```
"I'm getting this error: [paste error]
In file: [file path]
Function: [function name]
What's wrong and how do I fix it?"
```

### Refactoring

```
"Refactor this code to:
- Extract reusable logic into helper functions
- Add type hints
- Improve error handling
- Add docstrings
- Follow Python best practices"
```

### Testing

```
"Write pytest tests for this function that cover:
- Happy path (valid inputs)
- Edge cases (boundary values)
- Error cases (invalid inputs)
- Mock external dependencies
- Aim for 100% coverage"
```

---

## Development Workflow with Cursor

### Phase 1: Backend MVP

**Step 1: Database Models**
```
File: app/models/donation.py

Prompt: "Create SQLAlchemy models based on DATABASE_SCHEMA.md:
- Temple
- User
- Devotee
- DonationCategory
- Donation

Include all fields, relationships, indexes as specified."
```

**Step 2: Pydantic Schemas**
```
File: app/schemas/donation.py

Prompt: "Create Pydantic schemas for donation API:
- DonationCreate (input validation)
- DonationUpdate
- DonationResponse (output)
Include validators for amount, phone, etc."
```

**Step 3: Service Layer**
```
File: app/services/donation_service.py

Prompt: "Create DonationService class with methods:
- create_donation()
- get_donation()
- get_donations_list()
- get_daily_report()
Include proper error handling and logging."
```

**Step 4: API Routes**
```
File: app/api/donations.py

Prompt: "Create FastAPI router for donations following RESTful conventions.
Reference PRD.md for requirements.
Include authentication using get_current_user dependency."
```

**Step 5: Tests**
```
File: tests/test_donations.py

Prompt: "Write comprehensive tests for donation API covering all endpoints and edge cases."
```

### Phase 2: Frontend

**Step 1: API Service**
```
File: src/services/donationService.js

Prompt: "Create Axios-based service for donation API with methods for all CRUD operations.
Include error handling and request/response interceptors."
```

**Step 2: Components**
```
File: src/components/DonationForm.js

Prompt: "Create Material-UI form component for recording donations.
Include validation, loading states, error handling."
```

**Step 3: Pages**
```
File: src/pages/DonationsPage.js

Prompt: "Create page component with:
- DonationForm
- DonationList (table with MUI DataGrid)
- Daily summary cards
- Filters and search"
```

---

## Tips for Speed & Quality

### 1. Use the Documentation

Before coding, tell Claude to read the docs:

```
"Read PRD.md and ARCHITECTURE.md, then help me implement the seva booking feature."
```

### 2. Be Specific About Style

```
"Write this following:
- Python: PEP 8, type hints, docstrings
- React: Functional components, hooks, no class components
- Use async/await, not callbacks
- Material-UI v5 styling
- Error handling with try/catch"
```

### 3. Ask for Explanations

```
"Explain this code line by line"
"Why did you use this approach?"
"What are the alternatives?"
```

### 4. Incremental Development

Don't try to build everything at once:

```
Week 1: "Build donation recording only"
Week 2: "Add donation listing and search"
Week 3: "Add reports"
Week 4: "Add SMS notifications"
```

---

## Common Issues & Solutions

### Claude Doesn't Have Context

**Problem:** Claude gives generic answers

**Solution:**
```
"I'm working on a temple management system.
See PRD.md for requirements.
See ARCHITECTURE.md for tech stack.
See DATABASE_SCHEMA.md for database design.
Now help me with [specific task]."
```

### Code Doesn't Work

**Problem:** Generated code has bugs

**Solution:**
```
1. Copy the error message
2. Paste into Cursor chat
3. "This code isn't working. Error: [paste error]"
4. Claude will debug and fix
```

### Need to Understand Existing Code

```
"Explain what this file does and how it fits into the overall architecture"
```

### Performance Issues

```
"This query is slow. How can I optimize it?"
"Add indexes to improve performance"
"Suggest caching strategy for this endpoint"
```

---

## Keyboard Shortcuts

- **Cmd/Ctrl + L** - Open chat
- **Cmd/Ctrl + K** - Inline edit
- **Cmd/Ctrl + Shift + L** - New chat with code context
- **Tab** - Accept autocomplete
- **Escape** - Cancel/close

---

## Remember

1. **Claude is your pair programmer** - Ask questions, brainstorm, debug together
2. **Provide context** - More context = better code
3. **Iterate** - Start simple, improve incrementally
4. **Review generated code** - Don't blindly accept, understand what Claude writes
5. **Test everything** - Claude's code is good but always test

---

## Example: Building Donation Module End-to-End

### Conversation with Claude:

```
You: "I want to build the donation management module. 
I have the requirements in PRD.md and database schema in DATABASE_SCHEMA.md.
Let's start with the backend."

Claude: "Great! I'll help you build this step by step. Let's start with:
1. Database models
2. API schemas
3. Service layer
4. API endpoints
5. Tests

Ready to begin?"

You: "Yes, let's start with database models."

Claude: [Generates models/donation.py with complete code]

You: "Perfect! Now the Pydantic schemas."

Claude: [Generates schemas/donation.py]

You: "Now the service layer with business logic."

Claude: [Generates services/donation_service.py]

You: "Great! Now the FastAPI endpoints."

Claude: [Generates api/donations.py]

You: "Excellent! Now write tests."

Claude: [Generates tests/test_donations.py]

You: "All done! Now let's build the React frontend."

Claude: "Let's create..."
[And so on...]
```

---

## Resources

- **Cursor Docs:** https://docs.cursor.sh/
- **Claude AI Docs:** https://www.anthropic.com/claude
- **This Project's Docs:** See `/docs` folder

---

**Happy Coding with Cursor + Claude! 🚀**

You've got a powerful AI assistant - use it to build something amazing! 🙏

---
