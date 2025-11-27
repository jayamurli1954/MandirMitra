/**
 * Export utility functions
 */

/**
 * Export data to CSV
 */
export const exportToCSV = (data, filename = 'export.csv', headers = null) => {
  if (!data || data.length === 0) {
    console.error('No data to export');
    return;
  }

  // Get headers from first object if not provided
  const csvHeaders = headers || Object.keys(data[0]);
  
  // Create CSV content
  const csvContent = [
    csvHeaders.join(','), // Header row
    ...data.map(row => 
      csvHeaders.map(header => {
        const value = row[header];
        // Handle values with commas or quotes
        if (value === null || value === undefined) return '';
        const stringValue = String(value);
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
          return `"${stringValue.replace(/"/g, '""')}"`;
        }
        return stringValue;
      }).join(',')
    )
  ].join('\n');

  // Create blob and download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * Export data to Excel (using CSV format, can be opened in Excel)
 */
export const exportToExcel = (data, filename = 'export.xlsx', headers = null) => {
  // For now, export as CSV which Excel can open
  // In future, can use a library like xlsx for proper Excel format
  exportToCSV(data, filename.replace('.xlsx', '.csv'), headers);
};

/**
 * Export table to CSV
 */
export const exportTableToCSV = (tableId, filename = 'table-export.csv') => {
  const table = document.getElementById(tableId);
  if (!table) {
    console.error(`Table with id "${tableId}" not found`);
    return;
  }

  const rows = Array.from(table.querySelectorAll('tr'));
  const csvData = rows.map(row => {
    const cols = Array.from(row.querySelectorAll('th, td'));
    return cols.map(col => {
      const text = col.textContent.trim();
      if (text.includes(',') || text.includes('"') || text.includes('\n')) {
        return `"${text.replace(/"/g, '""')}"`;
      }
      return text;
    }).join(',');
  });

  const csvContent = csvData.join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * Export JSON data
 */
export const exportToJSON = (data, filename = 'export.json') => {
  const jsonContent = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonContent], { type: 'application/json' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};








