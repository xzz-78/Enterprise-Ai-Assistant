import React, { useState, useEffect } from 'react'
import {
  Upload,
  FileText,
  Trash2,
  UploadCloud,
  Loader2,
  File,
  Calendar,
  HardDrive,
} from 'lucide-react'
import { getDocuments, uploadDocument, deleteDocument } from '../services/document'
import type { Document } from '../types'

const DocumentsPage: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const [total, setTotal] = useState(0)

  const fetchDocuments = async () => {
    setLoading(true)
    try {
      const result = await getDocuments()
      setDocuments(result.documents)
      setTotal(result.total)
    } catch (error) {
      console.error('获取文档列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  const handleFileUpload = async (file: File) => {
    setUploading(true)
    try {
      await uploadDocument(file)
      await fetchDocuments()
    } catch (error: any) {
      alert(error.response?.data?.detail || '上传失败')
    } finally {
      setUploading(false)
    }
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFileUpload(files[0])
    }
    e.target.value = ''
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      handleFileUpload(files[0])
    }
  }

  const handleDelete = async (docId: number) => {
    if (!confirm('确定要删除这个文档吗？')) return

    try {
      await deleteDocument(docId)
      await fetchDocuments()
    } catch (error: any) {
      alert(error.response?.data?.detail || '删除失败')
    }
  }

  const formatFileSize = (bytes: number | null) => {
    if (!bytes) return '未知'
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const getFileIcon = (fileType: string) => {
    const colorMap: Record<string, string> = {
      pdf: 'text-red-400 bg-red-500/10',
      txt: 'text-accent-400 bg-accent-500/10',
    }
    return colorMap[fileType] || 'text-dark-400 bg-dark-600/50'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-dark-100">知识库管理</h1>
          <p className="mt-1 text-sm text-dark-400">
            管理企业知识文档，支持 PDF 和 TXT 格式上传
          </p>
        </div>
        <div className="text-sm text-dark-400">
          共 <span className="font-semibold text-dark-100">{total}</span> 个文档
        </div>
      </div>

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 cursor-pointer ${
          dragOver
            ? 'border-primary-500 bg-primary-500/5 shadow-glow'
            : 'border-dark-600/50 bg-dark-700/40 hover:border-primary-500/50 hover:bg-dark-700/60'
        }`}
      >
        <input
          type="file"
          accept=".pdf,.txt"
          onChange={handleFileInputChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={uploading}
        />
        <div className="flex flex-col items-center">
          {uploading ? (
            <Loader2 className="w-12 h-12 text-primary-500 animate-spin mb-4" />
          ) : (
            <div className={`p-4 rounded-2xl ${dragOver ? 'bg-primary-500/20' : 'bg-dark-600/50'} transition-all duration-300`}>
              <UploadCloud className={`w-10 h-10 ${dragOver ? 'text-primary-400' : 'text-dark-400'} transition-colors duration-300`} />
            </div>
          )}
          <p className="text-lg font-medium text-dark-100 mb-2 mt-4">
            {uploading ? '正在上传并处理文档...' : '拖拽文件到此处上传'}
          </p>
          <p className="text-sm text-dark-400">
            或点击选择文件，支持 PDF 和 TXT 格式，单个文件不超过 10MB
          </p>
          <button
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
            }}
            className="mt-4 px-6 py-2.5 gradient-primary text-white rounded-xl hover:opacity-90 transition-all text-sm font-medium shadow-glow"
          >
            <Upload className="w-4 h-4 inline mr-2" />
            选择文件
          </button>
        </div>
      </div>

      <div className="glass-card overflow-hidden">
        <div className="px-6 py-4 border-b border-dark-600/30">
          <h2 className="text-lg font-semibold text-dark-100 flex items-center gap-2">
            <span className="w-2 h-2 bg-accent-500 rounded-full" />
            文档列表
          </h2>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 text-dark-600/50 mx-auto mb-4" />
            <p className="text-dark-400">暂无文档，开始上传您的第一个文档吧</p>
          </div>
        ) : (
          <div className="divide-y divide-dark-600/20">
            {documents.map((doc, index) => (
              <div
                key={doc.id}
                className="px-6 py-4 flex items-center justify-between hover:bg-dark-600/20 transition-all duration-200 group animate-fade-in-up"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <div className="flex items-center gap-4">
                  <div
                    className={`w-12 h-12 rounded-xl flex items-center justify-center transition-transform duration-200 group-hover:scale-110 ${getFileIcon(
                      doc.file_type
                    )}`}
                  >
                    <File className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-medium text-dark-100 group-hover:text-primary-400 transition-colors">
                      {doc.filename}
                    </h3>
                    <div className="flex items-center gap-4 mt-1 text-sm text-dark-400">
                      <span className="flex items-center gap-1.5">
                        <HardDrive className="w-4 h-4" />
                        {formatFileSize(doc.file_size)}
                      </span>
                      <span className="flex items-center gap-1.5">
                        <Calendar className="w-4 h-4" />
                        {formatDate(doc.upload_time)}
                      </span>
                      <span className="px-2 py-0.5 bg-dark-600/50 rounded-lg text-xs uppercase text-dark-300">
                        {doc.file_type}
                      </span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="p-2.5 text-dark-500 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-all duration-200 opacity-0 group-hover:opacity-100"
                  title="删除文档"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default DocumentsPage
