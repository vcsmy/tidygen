import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { 
  Search, 
  Filter, 
  MoreHorizontal, 
  Eye, 
  Edit, 
  Trash2,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

export interface Column {
  key: string;
  label: string;
  sortable?: boolean;
  render?: (value: any, row: any) => React.ReactNode;
}

export interface DataTableProps {
  data: any[];
  columns: Column[];
  searchable?: boolean;
  filterable?: boolean;
  actions?: boolean;
  onView?: (row: any) => void;
  onEdit?: (row: any) => void;
  onDelete?: (row: any) => void;
  className?: string;
  pageSize?: number;
}

export function DataTable({
  data,
  columns,
  searchable = true,
  filterable = true,
  actions = true,
  onView,
  onEdit,
  onDelete,
  className,
  pageSize = 10,
}: DataTableProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: "asc" | "desc";
  } | null>(null);

  // Filter data based on search term
  const filteredData = (data || []).filter((row) => {
    if (!row) return false;
    return Object.values(row).some((value) =>
      String(value || '').toLowerCase().includes(searchTerm.toLowerCase())
    );
  });

  // Sort data
  const sortedData = sortConfig
    ? [...filteredData].sort((a, b) => {
        const aValue = a[sortConfig.key];
        const bValue = b[sortConfig.key];
        
        if (aValue < bValue) {
          return sortConfig.direction === "asc" ? -1 : 1;
        }
        if (aValue > bValue) {
          return sortConfig.direction === "asc" ? 1 : -1;
        }
        return 0;
      })
    : filteredData;

  // Paginate data
  const startIndex = (currentPage - 1) * pageSize;
  const paginatedData = sortedData.slice(startIndex, startIndex + pageSize);
  const totalPages = Math.ceil(sortedData.length / pageSize);

  const handleSort = (key: string) => {
    setSortConfig((current) => {
      if (current?.key === key) {
        return {
          key,
          direction: current.direction === "asc" ? "desc" : "asc",
        };
      }
      return { key, direction: "asc" };
    });
  };

  const renderCellValue = (column: Column, row: any) => {
    if (!row) return null;
    
    const value = row[column.key];
    
    if (column.render) {
      return column.render(value, row);
    }
    
    // Handle common data types
    if (typeof value === "boolean") {
      return (
        <Badge variant={value ? "default" : "secondary"}>
          {value ? "Active" : "Inactive"}
        </Badge>
      );
    }
    
    if (value instanceof Date) {
      return value.toLocaleDateString();
    }
    
    return value || '';
  };

  return (
    <div className={cn("data-grid", className)}>
      {/* Table Controls */}
      {(searchable || filterable) && (
        <div className="data-grid-header">
          <div className="flex items-center justify-between gap-4">
            {searchable && (
              <div className="relative flex-1 max-w-sm">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            )}
            
            {filterable && (
              <Button variant="outline" size="sm">
                <Filter className="h-4 w-4 mr-2" />
                Filter
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Table */}
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((column) => (
              <TableHead 
                key={column.key}
                className={cn(
                  column.sortable && "cursor-pointer hover:bg-muted/50",
                  "font-medium"
                )}
                onClick={() => column.sortable && handleSort(column.key)}
              >
                <div className="flex items-center gap-2">
                  {column.label}
                  {sortConfig?.key === column.key && (
                    <span className="text-xs">
                      {sortConfig.direction === "asc" ? "↑" : "↓"}
                    </span>
                  )}
                </div>
              </TableHead>
            ))}
            {actions && <TableHead className="w-[70px]">Actions</TableHead>}
          </TableRow>
        </TableHeader>
        <TableBody>
          {paginatedData.map((row, index) => (
            <TableRow key={index} className="data-grid-row">
              {columns.map((column) => (
                <TableCell key={column.key} className="data-grid-cell">
                  {renderCellValue(column, row)}
                </TableCell>
              ))}
              {actions && (
                <TableCell className="data-grid-cell">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      {onView && (
                        <DropdownMenuItem onClick={() => onView(row)}>
                          <Eye className="h-4 w-4 mr-2" />
                          View
                        </DropdownMenuItem>
                      )}
                      {onEdit && (
                        <DropdownMenuItem onClick={() => onEdit(row)}>
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </DropdownMenuItem>
                      )}
                      {onDelete && (
                        <DropdownMenuItem 
                          onClick={() => onDelete(row)}
                          className="text-destructive"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      )}
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              )}
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between p-4 border-t border-border">
          <div className="text-sm text-muted-foreground">
            Showing {startIndex + 1} to {Math.min(startIndex + pageSize, sortedData.length)} of {sortedData.length} results
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(currentPage - 1)}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>
            <span className="text-sm font-medium">
              Page {currentPage} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}