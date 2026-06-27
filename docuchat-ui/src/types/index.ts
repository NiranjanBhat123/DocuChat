export interface Collection {
  id: string
  name: string
  description: string
  document_count: number
  documents: Document[]
  created_at: string
}

export interface Document {
  id: string
  title: string
  file: string
  status: 'pending' | 'processing' | 'done' | 'failed'
  chunk_count: number
  error_message: string
  uploaded_at: string
}

export interface ChatSession {
  id: string
  collection: string
  title: string
  messages: Message[]
  created_at: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources: Source[]
  created_at: string
}

export interface Source {
  text: string
  chunk_index: number
  document_id: string
}