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
- Replies appear progressively, and each assistant response can be read aloud
  with the browser's built-in speech service.

## Actions and files

Choose Assistant, Search agent, Research agent, or Developer tools mode in
the sidebar. Web search is optional and disabled by default; when enabled,
the search agent can use DuckDuckGo results and cite their source links.
Search queries go to DuckDuckGo, and returned results are included in the
request sent to Groq.

File and document tools can read PDF, DOCX, common text/document formats,
source code, and images. Sending attachment contents to Groq requires the
file-tools setting and the separate chat consent control. The developer
mode can explain, debug, and review supplied code, but does not run code or
shell commands. When app actions are enabled, the assistant can also save or
search memories and rename the active conversation; it cannot act on
external accounts. The chat composer supports microphone recording and
sends voice messages to Groq for transcription only after explicit consent.
Microphone access requires a secure browser context (HTTPS or localhost).

Agentic memory retrieves relevant saved facts for each reply and, when
enabled, learns durable non-sensitive details from user messages. Memories
remain editable and deletable in the sidebar.

## Privacy and data ownership

Messages and relevant saved profile or memory context are sent to Groq to
generate replies. Data is stored in the configured SQLite or PostgreSQL
database. Uploaded file contents and voice recordings are sent only after
consent and are not retained as attachments by this app. Read-aloud playback
uses the browser's local speech synthesis. Use the data export in the sidebar
to download conversations, memories, and preferences.
The app does not encrypt its SQLite database; secure the device and any
backups, and review Groq's data-processing policies before sending content.
See [DEPLOYMENT.md](./DEPLOYMENT.md) for setup and hosted deployment details.
