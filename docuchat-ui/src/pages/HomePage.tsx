import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, BookOpen, FileText } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import CreateCollectionModal from '@/components/CreateCollectionModal'
import { getCollections } from '@/api/client'
import type { Collection } from '@/types'

export default function HomePage() {
  const [collections, setCollections] = useState<Collection[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const navigate = useNavigate()

  const fetchCollections = async () => {
    try {
      const data = await getCollections()
      setCollections(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchCollections() }, [])

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-primary" />
            <span className="text-xl font-semibold">DocuChat</span>
          </div>
          <Button onClick={() => setModalOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Collection
          </Button>
        </div>
      </div>

      {/* Body */}
      <div className="max-w-5xl mx-auto px-6 py-10">
        <h1 className="text-2xl font-bold mb-1">Your Collections</h1>
        <p className="text-muted-foreground mb-8">
          Upload PDFs and chat with them using AI.
        </p>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Spinner />
          </div>
        ) : collections.length === 0 ? (
          <div className="text-center py-20 text-muted-foreground">
            <FileText className="h-12 w-12 mx-auto mb-4 opacity-30" />
            <p>No collections yet. Create one to get started.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {collections.map(col => (
              <Card
                key={col.id}
                className="cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => navigate(`/collections/${col.id}`)}
              >
                <CardHeader className="pb-2">
                  <CardTitle className="text-base">{col.name}</CardTitle>
                  {col.description && (
                    <CardDescription className="text-sm line-clamp-2">
                      {col.description}
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent>
                  <Badge variant="secondary">
                    {col.document_count} {col.document_count === 1 ? 'document' : 'documents'}
                  </Badge>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      <CreateCollectionModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onCreated={(col) => {
          setCollections(prev => [col, ...prev])
          setModalOpen(false)
          navigate(`/collections/${col.id}`)
        }}
      />
    </div>
  )
}

function Spinner() {
  return (
    <div className="h-6 w-6 rounded-full border-2 border-primary border-t-transparent animate-spin" />
  )
}