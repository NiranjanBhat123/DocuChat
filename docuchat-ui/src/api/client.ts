import axios from 'axios'
import type { Collection, ChatSession, Message } from '../types'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
})

// Collections
export const getCollections = () =>
  api.get<Collection[]>('/collections/').then(r => r.data)

export const createCollection = (name: string, description: string) =>
  api.post<Collection>('/collections/', { name, description }).then(r => r.data)

export const getCollection = (id: string) =>
  api.get<Collection>(`/collections/${id}/`).then(r => r.data)

// Documents
export const uploadDocument = (collectionId: string, title: string, file: File) => {
  const form = new FormData()
  form.append('title', title)
  form.append('file', file)
  return api.post(`/collections/${collectionId}/documents/`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(r => r.data)
}

export const getDocuments = (collectionId: string) =>
  api.get(`/collections/${collectionId}/documents/`).then(r => r.data)

// Chat
export const createSession = (collectionId: string) =>
  api.post<ChatSession>(`/collections/${collectionId}/sessions/`, {
    title: 'Chat',
  }).then(r => r.data)

export const getSession = (collectionId: string, sessionId: string) =>
  api.get<ChatSession>(`/collections/${collectionId}/sessions/${sessionId}/`).then(r => r.data)

export const askQuestion = (collectionId: string, sessionId: string, question: string) =>
  api.post<Message>(`/collections/${collectionId}/sessions/${sessionId}/ask/`, {
    question,
  }).then(r => r.data)