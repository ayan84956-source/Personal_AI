# Personal AI

A private, single-user AI workspace for conversations, project context, and
long-term memory. It runs locally with SQLite or can use PostgreSQL for
persistent access across deployments; access is protected by `APP_PASSWORD`.

## Personalization and memory

- Choose an assistant role and response style, and save profile context that
  is reused in future conversations.
- Search, edit, or delete saved memories. Automatic memory extraction can be
  turned off independently of memory retrieval.
- Conversation history and saved memories persist in the configured database.
- Full chat history stays saved and visible, while replies use the latest 20
  exchanges to keep long conversations focused without resending the entire
  transcript on every turn.

## Actions and files

When app actions are enabled, the assistant can save or search memories and
rename the active conversation. These are the only assistant-executable
actions; it cannot run shell commands or act on external accounts. Uploaded
PDFs, text files, and images can be analyzed, with explicit consent before
their contents are sent to Groq.

## Privacy and data ownership

Messages and relevant saved profile or memory context are sent to Groq to
generate replies. Data is stored in the configured SQLite or PostgreSQL
database. Uploaded file contents are sent only after consent and are not
retained as attachments by this app. Use the data export in the sidebar to
download conversations, memories, and preferences.
The app does not encrypt its SQLite database; secure the device and any
backups, and review Groq's data-processing policies before sending content.
See [DEPLOYMENT.md](./DEPLOYMENT.md) for setup and hosted deployment details.
