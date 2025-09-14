import React, { useState, useEffect, useRef } from 'react';
import { 
  Upload, 
  Download, 
  Pin, 
  Unpin, 
  Search, 
  Filter, 
  FolderPlus, 
  File, 
  Image, 
  FileText, 
  Archive,
  MoreHorizontal,
  Copy,
  Trash2,
  Eye,
  Share2,
  Tag,
  Calendar,
  HardDrive
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DataTable } from '@/components/common/DataTable';
// Tenant context removed for Community Edition
import { ipfsService, IPFSFile, IPFSDirectory } from '@/services/ipfsService';

export default function IPFSManager() {
  const [files, setFiles] = useState<IPFSFile[]>([]);
  const [directories, setDirectories] = useState<IPFSDirectory[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<IPFSFile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Tenant context removed for Community Edition

  // Check if IPFS is enabled
  const isIPFSEnabled = true; // Always enabled for Community Edition

  useEffect(() => {
    if (isIPFSEnabled) {
      loadFiles();
    }
  }, [isIPFSEnabled]);

  const loadFiles = async () => {
    try {
      setIsLoading(true);
      await ipfsService.initialize();
      const pinnedFiles = await ipfsService.getPinnedFiles();
      setFiles(pinnedFiles);
    } catch (error) {
      console.error('Failed to load files:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (file: File, metadata?: Record<string, any>) => {
    try {
      setUploadProgress(0);
      const ipfsFile = await ipfsService.uploadFile(file, {
        pin: true,
        metadata,
        progressCallback: (progress) => setUploadProgress(progress),
      });
      setFiles(prev => [ipfsFile, ...prev]);
      setIsUploadModalOpen(false);
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploadProgress(0);
    }
  };

  const handleFileDownload = async (file: IPFSFile) => {
    try {
      const blob = await ipfsService.downloadFile(file.hash);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = file.name;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const handlePinFile = async (file: IPFSFile) => {
    try {
      await ipfsService.pinFile(file.hash, {
        name: file.name,
        metadata: file.metadata,
      });
      setFiles(prev => prev.map(f => 
        f.hash === file.hash ? { ...f, pinned: true } : f
      ));
    } catch (error) {
      console.error('Pin failed:', error);
    }
  };

  const handleUnpinFile = async (file: IPFSFile) => {
    try {
      await ipfsService.unpinFile(file.hash);
      setFiles(prev => prev.map(f => 
        f.hash === file.hash ? { ...f, pinned: false } : f
      ));
    } catch (error) {
      console.error('Unpin failed:', error);
    }
  };

  const handleCopyHash = async (file: IPFSFile) => {
    try {
      await navigator.clipboard.writeText(file.hash);
      // Show toast notification
    } catch (error) {
      console.error('Copy failed:', error);
    }
  };

  const handleCopyUrl = async (file: IPFSFile) => {
    try {
      await navigator.clipboard.writeText(file.url);
      // Show toast notification
    } catch (error) {
      console.error('Copy failed:', error);
    }
  };

  const getFileIcon = (file: IPFSFile) => {
    if (file.type.startsWith('image/')) return Image;
    if (file.type.includes('pdf') || file.type.includes('document')) return FileText;
    if (file.type.includes('zip') || file.type.includes('archive')) return Archive;
    return File;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  // Filter files based on search and type
  const filteredFiles = files.filter(file => {
    const matchesSearch = file.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         file.metadata?.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         file.metadata?.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesType = filterType === 'all' || 
                       (filterType === 'images' && file.type.startsWith('image/')) ||
                       (filterType === 'documents' && (file.type.includes('pdf') || file.type.includes('document'))) ||
                       (filterType === 'archives' && (file.type.includes('zip') || file.type.includes('archive'))) ||
                       (filterType === 'pinned' && file.pinned);

    return matchesSearch && matchesType;
  });

  // File columns
  const fileColumns = [
    {
      key: 'name',
      label: 'Name',
      render: (file: IPFSFile) => {
        const Icon = getFileIcon(file);
        return (
          <div className="flex items-center space-x-3">
            <div className="h-8 w-8 bg-primary/10 rounded-lg flex items-center justify-center">
              <Icon className="h-4 w-4 text-primary" />
            </div>
            <div>
              <div className="font-medium">{file.name}</div>
              <div className="text-sm text-muted-foreground">
                {file.type} • {formatFileSize(file.size)}
              </div>
            </div>
          </div>
        );
      },
    },
    {
      key: 'hash',
      label: 'IPFS Hash',
      render: (file: IPFSFile) => (
        <div className="font-mono text-sm">
          {file.hash}
        </div>
      ),
    },
    {
      key: 'pinned',
      label: 'Status',
      render: (file: IPFSFile) => (
        <Badge variant={file.pinned ? 'default' : 'secondary'}>
          {file.pinned ? (
            <>
              <Pin className="h-3 w-3 mr-1" />
              Pinned
            </>
          ) : (
            'Unpinned'
          )}
        </Badge>
      ),
    },
    {
      key: 'createdAt',
      label: 'Uploaded',
      render: (file: IPFSFile) => formatDate(file.createdAt),
    },
  ];

  if (!isIPFSEnabled) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card>
          <CardContent className="text-center py-8">
            <HardDrive className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">IPFS Storage Not Enabled</h3>
            <p className="text-muted-foreground mb-4">
              IPFS file storage is not enabled for your current plan.
            </p>
            <Button onClick={() => window.location.href = '/pricing'}>
              Upgrade Plan
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const actions = (
    <div className="flex items-center space-x-2">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search files..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10 w-64"
        />
      </div>
      <select
        value={filterType}
        onChange={(e) => setFilterType(e.target.value)}
        className="px-3 py-2 border rounded-md"
      >
        <option value="all">All Files</option>
        <option value="images">Images</option>
        <option value="documents">Documents</option>
        <option value="archives">Archives</option>
        <option value="pinned">Pinned</option>
      </select>
      <Button variant="outline" onClick={() => setIsUploadModalOpen(true)}>
        <Upload className="h-4 w-4 mr-2" />
        Upload
      </Button>
    </div>
  );

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">IPFS File Storage</h1>
            <p className="text-muted-foreground">Decentralized file storage and management</p>
          </div>
          <div className="flex items-center space-x-2">
            {actions}
          </div>
        </div>

        {/* Storage Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Files</p>
                  <p className="text-2xl font-bold">{files.length}</p>
                </div>
                <div className="h-8 w-8 bg-primary/10 rounded-lg flex items-center justify-center">
                  <File className="h-4 w-4 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Pinned Files</p>
                  <p className="text-2xl font-bold">
                    {files.filter(f => f.pinned).length}
                  </p>
                </div>
                <div className="h-8 w-8 bg-success/10 rounded-lg flex items-center justify-center">
                  <Pin className="h-4 w-4 text-success" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Size</p>
                  <p className="text-2xl font-bold">
                    {formatFileSize(files.reduce((sum, f) => sum + f.size, 0))}
                  </p>
                </div>
                <div className="h-8 w-8 bg-warning/10 rounded-lg flex items-center justify-center">
                  <HardDrive className="h-4 w-4 text-warning" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Directories</p>
                  <p className="text-2xl font-bold">{directories.length}</p>
                </div>
                <div className="h-8 w-8 bg-info/10 rounded-lg flex items-center justify-center">
                  <FolderPlus className="h-4 w-4 text-info" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Files Table */}
        <Card>
          <CardHeader>
            <CardTitle>Files</CardTitle>
          </CardHeader>
          <CardContent>
            <DataTable
              columns={fileColumns}
              data={filteredFiles}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
