import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, BookOpen } from 'lucide-react'
import { Button } from '@/components/ui/button'
import DocumentPanel from '@/components/DocumentPanel'
import ChatPanel from '@/components/ChatPanel'
import { getCollection } from '@/api/client'
import type { Collection } from '@/types'

export default function CollectionPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [collection, setCollection] = useState<Collection | null>(null)

  useEffect(() => {
    if (id) getCollection(id).then(setCollection)
  }, [id])

  if (!id) return null

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <div className="border-b">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <BookOpen className="h-5 w-5 text-primary" />
          <div>
            <h1 className="font-semibold leading-none">
              {collection?.name ?? 'Loading...'}
            </h1>
            {collection?.description && (
              <p className="text-xs text-muted-foreground mt-0.5">
                {collection.description}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Two panel layout */}
      <div className="flex-1 max-w-7xl mx-auto w-full px-6 py-6 grid grid-cols-[320px_1fr] gap-6 overflow-hidden" style={{ height: 'calc(100vh - 65px)' }}>
        {/* Left — Documents */}
        <div className="overflow-y-auto">
          <DocumentPanel collectionId={id} />
        </div>

        {/* Right — Chat */}
        <div className="border rounded-xl p-5 flex flex-col overflow-hidden">
          <ChatPanel collectionId={id} />
        </div>
      </div>
    </div>
  )
}