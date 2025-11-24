/**
 * Print utility functions
 */

/**
 * Print a specific element by ID
 */
export const printElement = (elementId, title = 'Print') => {
  const element = document.getElementById(elementId);
  if (!element) {
    console.error(`Element with id "${elementId}" not found`);
    return;
  }

  const printWindow = window.open('', '_blank');
  const printContent = element.innerHTML;
  
  printWindow.document.write(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>${title}</title>
        <style>
          @media print {
            @page {
              margin: 1cm;
            }
            body {
              font-family: Arial, sans-serif;
              font-size: 12px;
            }
            table {
              width: 100%;
              border-collapse: collapse;
            }
            th, td {
              border: 1px solid #ddd;
              padding: 8px;
              text-align: left;
            }
            th {
              background-color: #f2f2f2;
              font-weight: bold;
            }
            .no-print {
              display: none;
            }
          }
        </style>
      </head>
      <body>
        ${printContent}
      </body>
    </html>
  `);
  
  printWindow.document.close();
  printWindow.focus();
  setTimeout(() => {
    printWindow.print();
    printWindow.close();
  }, 250);
};

/**
 * Print current page
 */
export const printPage = () => {
  window.print();
};

/**
 * Print table data
 */
export const printTable = (data, columns, title = 'Report') => {
  const printWindow = window.open('', '_blank');
  
  let tableHTML = `
    <table>
      <thead>
        <tr>
          ${columns.map(col => `<th>${col.label || col.field}</th>`).join('')}
        </tr>
      </thead>
      <tbody>
        ${data.map(row => `
          <tr>
            ${columns.map(col => `<td>${row[col.field] || ''}</td>`).join('')}
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
  
  printWindow.document.write(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>${title}</title>
        <style>
          @media print {
            @page { margin: 1cm; }
            body { font-family: Arial, sans-serif; font-size: 12px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; font-weight: bold; }
          }
        </style>
      </head>
      <body>
        <h2>${title}</h2>
        <p>Printed on: ${new Date().toLocaleString()}</p>
        ${tableHTML}
      </body>
    </html>
  `);
  
  printWindow.document.close();
  printWindow.focus();
  setTimeout(() => {
    printWindow.print();
    printWindow.close();
  }, 250);
};

