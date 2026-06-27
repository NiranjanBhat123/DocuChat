import { useEffect, useRef, useState } from 'react'
import { Upload, FileText, CheckCircle, XCircle, Loader2, Clock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { uploadDocument, getDocuments } from '@/api/client'
import type { Document } from '@/types'

interface Props {
  collectionId: string
}

const statusConfig = {
  pending:    { label: 'Pending',    icon: Clock,     variant: 'secondary' as const },
  processing: { label: 'Processing', icon: Loader2,   variant: 'secondary' as const },
  done:       { label: 'Ready',      icon: CheckCircle, variant: 'default' as const },
  failed:     { label: 'Failed',     icon: XCircle,   variant: 'destructive' as const },
}

export default function DocumentPanel({ collectionId }: Props) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [title, setTitle] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const fetchDocs = async () => {
    const data = await getDocuments(collectionId)
    setDocuments(data)
  }

  // Poll every 3s while any doc is pending/processing
  useEffect(() => {
    fetchDocs()
    pollRef.current = setInterval(() => {
      fetchDocs()
    }, 3000)
    return () => { if (pollRef.current) clearInterval(pollRef.current) }
  }, [collectionId])

  const handleUpload = async () => {
    if (!file) { setError('Please select a PDF file'); return }
    if (!title.trim()) { setError('Please enter a title'); return }

    setUploading(true)
    setError('')
    try {
      await uploadDocument(collectionId, title.trim(), file)
      setTitle('')
      setFile(null)
      if (fileRef.current) fileRef.current.value = ''
      await fetchDocs()
    } catch (e: any) {
      setError(e?.response?.data?.file?.[0] || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <h2 className="font-semibold text-sm uppercase tracking-wide text-muted-foreground">
        Documents
      </h2>

      {/* Upload form */}
      <div className="border rounded-lg p-4 space-y-3 bg-muted/30">
        <Input
          placeholder="Document title"
          value={title}
          onChange={e => setTitle(e.target.value)}
        />
        <input
          ref={fileRef}
          type="file"
          accept=".pdf"
          className="text-sm text-muted-foreground file:mr-3 file:py-1 file:px-3 file:rounded file:border-0 file:text-sm file:bg-primary file:text-primary-foreground cursor-pointer"
          onChange={e => setFile(e.target.files?.[0] ?? null)}
        />
        {error && <p className="text-xs text-destructive">{error}</p>}
        <Button
          size="sm"
          onClick={handleUpload}
          disabled={uploading}
          className="w-full"
        >
          {uploading
            ? <><Loader2 className="h-3 w-3 mr-2 animate-spin" /> Uploading...</>
            : <><Upload className="h-3 w-3 mr-2" /> Upload PDF</>
          }
        </Button>
      </div>

      {/* Document list */}
      <div className="space-y-2">
        {documents.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">
            No documents yet. Upload a PDF to get started.
          </p>
        ) : (
          documents.map(doc => {
            const cfg = statusConfig[doc.status]
            const Icon = cfg.icon
            return (
              <div key={doc.id} className="flex items-start gap-3 p-3 rounded-lg border bg-background">
                <FileText className="h-4 w-4 mt-0.5 text-muted-foreground shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{doc.title}</p>
                  {doc.status === 'done' && (
                    <p className="text-xs text-muted-foreground">{doc.chunk_count} chunks</p>
                  )}
                  {doc.status === 'failed' && (
                    <p className="text-xs text-destructive truncate">{doc.error_message}</p>
                  )}
                </div>
                <Badge variant={cfg.variant} className="shrink-0 flex items-center gap-1">
                  <Icon className={`h-3 w-3 ${doc.status === 'processing' ? 'animate-spin' : ''}`} />
                  {cfg.label}
                </Badge>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}