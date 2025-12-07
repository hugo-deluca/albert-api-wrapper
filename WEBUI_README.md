# Albert API Web UI

A web-based dashboard for managing documents and collections with the Albert API.

## Features

### 📊 Dashboard
- API health status monitoring
- Quick overview of collections and models
- Quick action buttons

### 📁 Collections Management
- View all collections
- Create new collections with name and description
- Delete collections
- Direct links to view documents in each collection

### 📄 Documents Management
- View all documents across collections
- Filter documents by collection
- Upload new documents (PDF, TXT, DOCX, JSON, etc.)
- Delete documents
- View document metadata (chunks, creation date)

### 💬 Chat Interface
- Chat with Albert AI models
- Choose from available models (albert-small, albert-large)
- **RAG Mode**: Search through your documents using collections
- Real-time message streaming
- Clear chat history

## Installation

```bash
# Install with web UI dependencies
uv sync --extra web

# Or with pip
pip install -e ".[web]"
```

## Configuration

Create a `.env` file in the project root:

```env
ALBERT_API_KEY=your_api_key_here
ALBERT_API_BASE_URL=https://albert.api.etalab.gouv.fr
SECRET_KEY=your-secret-key-for-flask-sessions
```

## Running

```bash
# Using the command
albert-ui

# Or run directly
uv run python -m web_ui.app

# Development mode with auto-reload
FLASK_ENV=development albert-ui
```

The web interface will be available at: **http://localhost:5000**

## Usage

### Managing Collections

1. Navigate to **Collections**
2. Click **+ New Collection**
3. Enter a name and optional description
4. Click **Create**

### Uploading Documents

1. Navigate to **Documents**
2. Click **+ Upload Document**
3. Select a collection
4. Choose your file (max 16MB)
5. Click **Upload**

The document will be processed and chunked by the Albert API.

### Using Chat

#### Simple Chat
1. Navigate to **Chat**
2. Select a model
3. Type your message and press Enter

#### RAG Chat (Search in Documents)
1. Navigate to **Chat**
2. Check **Use RAG**
3. Select one or more collections to search
4. Type your question
5. Albert will search your documents and provide an answer based on the content

## Architecture

```
web_ui/
├── app.py              # Flask application factory
├── routes.py           # API routes and view handlers
├── templates/          # Jinja2 HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── collections.html
│   ├── documents.html
│   └── chat.html
└── static/
    ├── css/
    │   └── style.css   # Custom styles
    └── js/
        └── main.js     # Shared JavaScript utilities
```

## API Endpoints

### Collections
- `GET /api/collections` - List all collections
- `POST /api/collections` - Create a collection
- `DELETE /api/collections/<id>` - Delete a collection

### Documents
- `GET /api/documents` - List documents (with optional collection filter)
- `POST /api/documents` - Upload a document
- `DELETE /api/documents/<id>` - Delete a document

### Chat
- `POST /api/chat` - Send a chat message (with optional RAG)
- `POST /api/search` - Search in collections

## Development

### Adding New Features

To add a new page:

1. Create a route in `routes.py`
2. Create a template in `templates/`
3. Add navigation link in the navbar
4. Add any new styles to `static/css/style.css`

### Customization

- **Styling**: Edit `static/css/style.css`
- **Colors**: Change CSS variables for primary colors
- **Models**: Available models are fetched from the API
- **Max File Size**: Adjust `MAX_CONTENT_LENGTH` in `app.py`

## Troubleshooting

### Port already in use
```bash
# Change the port in app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

### API connection errors
- Check your `ALBERT_API_KEY` in `.env`
- Verify the `ALBERT_API_BASE_URL` is correct
- Test the API wrapper directly first

### File upload fails
- Check file size (max 16MB by default)
- Verify file format is supported by Albert API
- Check collection exists

## Security Notes

- Never commit your `.env` file
- Use a strong `SECRET_KEY` in production
- Consider adding authentication for production use
- The web UI is designed for local/internal use

## Future Enhancements

Potential features to add:
- User authentication and authorization
- Document preview and viewing
- Search history
- Export chat conversations
- Batch document upload
- Collection statistics and analytics
- Document version management