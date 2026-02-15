import React, { useState } from 'react'
import { Plus, Search, Mail, Calendar, Mic, Image, Send, Heart } from 'lucide-react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Modal } from '../components/ui/Modal'

interface Message {
  id: string
  title: string
  content: string
  recipient: string
  createdAt: Date
  scheduled: boolean
  scheduledDate?: Date
  voiceNote?: string
  photos?: string[]
}

const Messages: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [showComposeModal, setShowComposeModal] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const filteredMessages = messages.filter(m =>
    m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.recipient.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between">
        <div className="flex-1 max-w-md">
          <Input
            placeholder="Search messages..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Button onClick={() => setShowComposeModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Compose Message
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card className="text-center">
          <p className="text-3xl font-bold text-sage">{messages.length}</p>
          <p className="text-sm text-warmGray-500">Total Messages</p>
        </Card>
        <Card className="text-center">
          <p className="text-3xl font-bold text-sage">
            {new Set(messages.map(m => m.recipient)).size}
          </p>
          <p className="text-sm text-warmGray-500">Recipients</p>
        </Card>
        <Card className="text-center">
          <p className="text-3xl font-bold text-sage">
            {messages.filter(m => m.voiceNote).length}
          </p>
          <p className="text-sm text-warmGray-500">Voice Notes</p>
        </Card>
      </div>

      {/* Messages List */}
      <div className="space-y-4">
        {filteredMessages.length === 0 ? (
          <Card className="text-center py-12">
            <Mail className="w-12 h-12 mx-auto text-warmGray-300 mb-4" />
            <h3 className="text-lg font-medium text-warmGray-900 dark:text-warmGray-100 mb-2">
              No messages yet
            </h3>
            <p className="text-warmGray-500 mb-4">
              Write your first message to someone you love
            </p>
            <Button onClick={() => setShowComposeModal(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Compose Message
            </Button>
          </Card>
        ) : (
          filteredMessages.map(message => (
            <Card key={message.id} hover>
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-sage/10 flex items-center justify-center">
                  <Heart className="w-6 h-6 text-sage" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-warmGray-900 dark:text-warmGray-100 mb-1">
                    {message.title}
                  </h3>
                  <p className="text-sm text-warmGray-500 mb-2">
                    To: {message.recipient}
                  </p>
                  <p className="text-warmGray-600 dark:text-warmGray-400 line-clamp-2">
                    {message.content}
                  </p>
                  <div className="flex items-center gap-4 mt-3 text-xs text-warmGray-400">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {new Date(message.createdAt).toLocaleDateString()}
                    </span>
                    {message.voiceNote && (
                      <span className="flex items-center gap-1">
                        <Mic className="w-3 h-3" />
                        Voice note
                      </span>
                    )}
                    {message.photos && message.photos.length > 0 && (
                      <span className="flex items-center gap-1">
                        <Image className="w-3 h-3" />
                        {message.photos.length} photo(s)
                      </span>
                    )}
                  </div>
                </div>
                <Button variant="ghost" size="sm">
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </Card>
          ))
        )}
      </div>

      {/* Compose Modal */}
      <Modal
        isOpen={showComposeModal}
        onClose={() => setShowComposeModal(false)}
        title="Compose Message"
        size="lg"
      >
        <ComposeMessageForm
          onSubmit={(message) => {
            setMessages([...messages, { ...message, id: crypto.randomUUID(), createdAt: new Date() }])
            setShowComposeModal(false)
          }}
          onCancel={() => setShowComposeModal(false)}
        />
      </Modal>
    </div>
  )
}

const ComposeMessageForm: React.FC<{
  onSubmit: (message: Omit<Message, 'id' | 'createdAt'>) => void
  onCancel: () => void
}> = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    recipient: '',
    scheduled: false,
    voiceNote: undefined as string | undefined,
    photos: undefined as string[] | undefined
  })
  const [recording, setRecording] = useState(false)

  const wordCount = formData.content.split(/\s+/).filter(w => w.length > 0).length

  return (
    <div className="space-y-4">
      <Input
        label="To"
        value={formData.recipient}
        onChange={(e) => setFormData({ ...formData, recipient: e.target.value })}
        placeholder="Recipient name"
        required
      />
      <Input
        label="Subject"
        value={formData.title}
        onChange={(e) => setFormData({ ...formData, title: e.target.value })}
        placeholder="Message subject"
        required
      />
      <div>
        <label className="block text-sm font-medium text-warmGray-700 dark:text-warmGray-300 mb-1">
          Message
        </label>
        <textarea
          value={formData.content}
          onChange={(e) => setFormData({ ...formData, content: e.target.value })}
          rows={8}
          className="w-full px-4 py-3 rounded-lg border border-warmGray-200 dark:border-warmGray-600 bg-white dark:bg-warmGray-800 text-warmGray-900 dark:text-warmGray-100 focus:ring-2 focus:ring-sage focus:outline-none resize-none"
          placeholder="Write your message..."
          required
        />
        <p className="text-sm text-warmGray-500 mt-1 text-right">
          {wordCount} words
        </p>
      </div>

      {/* Attachment buttons */}
      <div className="flex gap-2">
        <Button
          variant="secondary"
          type="button"
          size="sm"
          onClick={() => setRecording(!recording)}
          className={recording ? 'bg-red-100 text-red-600' : ''}
        >
          <Mic className="w-4 h-4 mr-2" />
          {recording ? 'Stop Recording' : 'Record Voice'}
        </Button>
        <Button variant="secondary" type="button" size="sm">
          <Image className="w-4 h-4 mr-2" />
          Add Photo
        </Button>
      </div>

      <div className="flex justify-end gap-3 pt-4">
        <Button variant="secondary" type="button" onClick={onCancel}>
          Cancel
        </Button>
        <Button
          type="button"
          onClick={() => onSubmit(formData)}
          disabled={!formData.title || !formData.content || !formData.recipient}
        >
          Save Message
        </Button>
      </div>
    </div>
  )
}

export default Messages
