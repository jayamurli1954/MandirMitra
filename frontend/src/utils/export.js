import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

/**
 * Export data to CSV format
 */
export const exportToCSV = (data, filename = 'export') => {
  if (!data || data.length === 0) {
    alert('No data to export');
    return;
  }

  // Get headers from first object
  const headers = Object.keys(data[0]);
  
  // Create CSV content
  const csvContent = [
    headers.join(','),
    ...data.map(row => 
      headers.map(header => {
        const value = row[header];
        // Handle values with commas, quotes, or newlines
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
  link.setAttribute('download', `${filename}.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * Export data to Excel format
 */
export const exportToExcel = (data, filename = 'export', sheetName = 'Sheet1') => {
  if (!data || data.length === 0) {
    alert('No data to export');
    return;
  }

  // Create workbook and worksheet
  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.json_to_sheet(data);
  
  // Add worksheet to workbook
  XLSX.utils.book_append_sheet(wb, ws, sheetName);
  
  // Write file
  XLSX.writeFile(wb, `${filename}.xlsx`);
};

/**
 * Export data to PDF format
 */
export const exportToPDF = (data, filename = 'export', title = 'Report', columns = null) => {
  if (!data || data.length === 0) {
    alert('No data to export');
    return;
  }

  const doc = new jsPDF();
  
  // Add title
  doc.setFontSize(16);
  doc.text(title, 14, 15);
  
  // Add date
  doc.setFontSize(10);
  doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 14, 22);
  
  // Prepare table data
  const headers = columns || Object.keys(data[0]);
  const rows = data.map(row => 
    headers.map(header => {
      const value = row[header];
      return value === null || value === undefined ? '' : String(value);
    })
  );

  // Add table
  doc.autoTable({
    head: [headers],
    body: rows,
    startY: 30,
    styles: { fontSize: 8 },
    headStyles: { fillColor: [255, 153, 51] }, // Saffron color
    alternateRowStyles: { fillColor: [255, 255, 255] },
  });

  // Save PDF
  doc.save(`${filename}.pdf`);
};

/**
 * Export accounting report to Excel
 */
export const exportAccountingReportToExcel = (reportData, reportType, dateRange = {}) => {
  if (!reportData) {
    alert('No report data to export');
    return;
  }

  const wb = XLSX.utils.book_new();
  let filename = `${reportType}-report`;

  switch (reportType) {
    case 'day-book':
      filename = `day-book-${dateRange.date || 'report'}`;
      const dayBookData = [
        ['Day Book Report', dateRange.date || ''],
        ['Opening Balance', reportData.opening_balance || 0],
        ['Closing Balance', reportData.closing_balance || 0],
        [],
        ['Receipts'],
        ['Entry #', 'Narration', 'Account', 'Amount'],
        ...(reportData.receipts || []).map(r => [
          r.entry_number,
          r.narration,
          r.account_name,
          r.debit_amount || r.credit_amount || 0
        ]),
        [],
        ['Payments'],
        ['Entry #', 'Narration', 'Account', 'Amount'],
        ...(reportData.payments || []).map(p => [
          p.entry_number,
          p.narration,
          p.account_name,
          p.debit_amount || p.credit_amount || 0
        ])
      ];
      const dayBookWs = XLSX.utils.aoa_to_sheet(dayBookData);
      XLSX.utils.book_append_sheet(wb, dayBookWs, 'Day Book');
      break;

    case 'cash-book':
      filename = `cash-book-${dateRange.from_date || ''}-${dateRange.to_date || ''}`;
      const cashBookData = [
        ['Cash Book Report', `${dateRange.from_date || ''} to ${dateRange.to_date || ''}`],
        ['Opening Balance', reportData.opening_balance || 0],
        ['Closing Balance', reportData.closing_balance || 0],
        [],
        ['Date', 'Entry #', 'Narration', 'Receipt', 'Payment', 'Balance'],
        ...(reportData.entries || []).map(e => [
          e.date,
          e.entry_number,
          e.narration,
          e.receipt_amount || 0,
          e.payment_amount || 0,
          e.running_balance || 0
        ])
      ];
      const cashBookWs = XLSX.utils.aoa_to_sheet(cashBookData);
      XLSX.utils.book_append_sheet(wb, cashBookWs, 'Cash Book');
      break;

    case 'bank-book':
      filename = `bank-book-${reportData.account_code || 'report'}-${dateRange.from_date || ''}`;
      const bankBookData = [
        ['Bank Book Report', `${reportData.account_name || ''} (${reportData.account_code || ''})`],
        ['Period', `${dateRange.from_date || ''} to ${dateRange.to_date || ''}`],
        ['Opening Balance', reportData.opening_balance || 0],
        ['Closing Balance', reportData.closing_balance || 0],
        [],
        ['Date', 'Entry #', 'Narration', 'Cheque #', 'Deposit', 'Withdrawal', 'Balance'],
        ...(reportData.entries || []).map(e => [
          e.date,
          e.entry_number,
          e.narration,
          e.cheque_number || '',
          e.deposit_amount || 0,
          e.withdrawal_amount || 0,
          e.running_balance || 0
        ])
      ];
      const bankBookWs = XLSX.utils.aoa_to_sheet(bankBookData);
      XLSX.utils.book_append_sheet(wb, bankBookWs, 'Bank Book');
      break;

    case 'balance-sheet':
      filename = `balance-sheet-${dateRange.as_of_date || 'report'}`;
      const balanceSheetData = [
        ['Balance Sheet', dateRange.as_of_date || ''],
        [],
        ['ASSETS'],
        ['Fixed Assets'],
        ...(reportData.fixed_assets || []).flatMap(g => [
          [g.group_name],
          ...(g.accounts || []).map(a => ['', a.account_name, a.current_year || 0])
        ]),
        [],
        ['Current Assets'],
        ...(reportData.current_assets || []).flatMap(g => [
          [g.group_name],
          ...(g.accounts || []).map(a => ['', a.account_name, a.current_year || 0])
        ]),
        ['TOTAL ASSETS', '', reportData.total_assets || 0],
        [],
        ['LIABILITIES & FUNDS'],
        ['Corpus Fund', '', reportData.corpus_fund || 0],
        ...(reportData.designated_funds || []).flatMap(g => [
          [g.group_name],
          ...(g.accounts || []).map(a => ['', a.account_name, a.current_year || 0])
        ]),
        ['Current Liabilities'],
        ...(reportData.current_liabilities || []).flatMap(g => [
          [g.group_name],
          ...(g.accounts || []).map(a => ['', a.account_name, a.current_year || 0])
        ]),
        ['TOTAL LIABILITIES & FUNDS', '', reportData.total_liabilities_and_funds || 0]
      ];
      const balanceSheetWs = XLSX.utils.aoa_to_sheet(balanceSheetData);
      XLSX.utils.book_append_sheet(wb, balanceSheetWs, 'Balance Sheet');
      break;

    case 'trial-balance':
      filename = `trial-balance-${dateRange.as_of_date || 'report'}`;
      const trialBalanceData = [
        ['Trial Balance', dateRange.as_of_date || ''],
        [],
        ['Account Code', 'Account Name', 'Debit', 'Credit'],
        ...(reportData.accounts || []).map(a => [
          a.account_code,
          a.account_name,
          a.debit_balance || 0,
          a.credit_balance || 0
        ]),
        ['TOTAL', '', reportData.total_debits || 0, reportData.total_credits || 0]
      ];
      const trialBalanceWs = XLSX.utils.aoa_to_sheet(trialBalanceData);
      XLSX.utils.book_append_sheet(wb, trialBalanceWs, 'Trial Balance');
      break;

    case 'profit-loss':
      filename = `profit-loss-${dateRange.from_date || ''}-${dateRange.to_date || ''}`;
      const profitLossData = [
        ['Profit & Loss Statement', `${dateRange.from_date || ''} to ${dateRange.to_date || ''}`],
        [],
        ['INCOME'],
        ...(reportData.income_groups || []).flatMap(g => [
          [g.category_name],
          ...(g.accounts || []).map(a => ['', a.account_code, a.account_name, a.amount || 0]),
          ['', '', `Total ${g.category_name}`, g.total || 0],
          []
        ]),
        ['TOTAL INCOME', '', '', reportData.total_income || 0],
        [],
        ['EXPENSES'],
        ...(reportData.expense_groups || []).flatMap(g => [
          [g.category_name],
          ...(g.accounts || []).map(a => ['', a.account_code, a.account_name, a.amount || 0]),
          ['', '', `Total ${g.category_name}`, g.total || 0],
          []
        ]),
        ['TOTAL EXPENSES', '', '', reportData.total_expenses || 0],
        [],
        ['NET SURPLUS/DEFICIT', '', '', reportData.net_surplus || 0]
      ];
      const profitLossWs = XLSX.utils.aoa_to_sheet(profitLossData);
      XLSX.utils.book_append_sheet(wb, profitLossWs, 'Profit & Loss');
      break;

    default:
      // Generic export
      const ws = XLSX.utils.json_to_sheet(Array.isArray(reportData) ? reportData : [reportData]);
      XLSX.utils.book_append_sheet(wb, ws, 'Report');
  }

  XLSX.writeFile(wb, `${filename}.xlsx`);
};

/**
 * Export accounting report to PDF
 */
export const exportAccountingReportToPDF = (reportData, reportType, dateRange = {}, templeInfo = {}) => {
  if (!reportData) {
    alert('No report data to export');
    return;
  }

  const doc = new jsPDF();
  let filename = `${reportType}-report`;
  let yPos = 20;

  // Add temple header
  if (templeInfo.name) {
    doc.setFontSize(18);
    doc.setTextColor(255, 153, 51); // Saffron color
    doc.text(templeInfo.name, 105, yPos, { align: 'center' });
    yPos += 8;
  }

  // Add report title
  doc.setFontSize(16);
  doc.setTextColor(0, 0, 0);
  const reportTitle = reportType.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  doc.text(reportTitle, 105, yPos, { align: 'center' });
  yPos += 8;

  // Add date range
  doc.setFontSize(10);
  doc.setTextColor(100, 100, 100);
  if (dateRange.date) {
    doc.text(`Date: ${dateRange.date}`, 105, yPos, { align: 'center' });
  } else if (dateRange.from_date && dateRange.to_date) {
    doc.text(`Period: ${dateRange.from_date} to ${dateRange.to_date}`, 105, yPos, { align: 'center' });
  } else if (dateRange.as_of_date) {
    doc.text(`As of: ${dateRange.as_of_date}`, 105, yPos, { align: 'center' });
  }
  yPos += 10;

  switch (reportType) {
    case 'day-book':
      filename = `day-book-${dateRange.date || 'report'}`;
      // Receipts table
      doc.autoTable({
        head: [['Entry #', 'Narration', 'Account', 'Amount (₹)']],
        body: (reportData.receipts || []).map(r => [
          r.entry_number || '',
          r.narration || '',
          r.account_name || '',
          (r.debit_amount || r.credit_amount || 0).toFixed(2)
        ]),
        startY: yPos,
        headStyles: { fillColor: [255, 153, 51] },
        styles: { fontSize: 8 },
        margin: { left: 14, right: 14 }
      });
      
      yPos = doc.lastAutoTable.finalY + 10;
      doc.setFontSize(12);
      doc.text(`Total Receipts: ₹${(reportData.total_receipts || 0).toFixed(2)}`, 14, yPos);
      yPos += 10;

      // Payments table
      doc.autoTable({
        head: [['Entry #', 'Narration', 'Account', 'Amount (₹)']],
        body: (reportData.payments || []).map(p => [
          p.entry_number || '',
          p.narration || '',
          p.account_name || '',
          (p.debit_amount || p.credit_amount || 0).toFixed(2)
        ]),
        startY: yPos,
        headStyles: { fillColor: [255, 153, 51] },
        styles: { fontSize: 8 },
        margin: { left: 14, right: 14 }
      });

      yPos = doc.lastAutoTable.finalY + 10;
      doc.setFontSize(12);
      doc.text(`Total Payments: ₹${(reportData.total_payments || 0).toFixed(2)}`, 14, yPos);
      yPos += 8;
      doc.text(`Opening Balance: ₹${(reportData.opening_balance || 0).toFixed(2)}`, 14, yPos);
      yPos += 8;
      doc.text(`Closing Balance: ₹${(reportData.closing_balance || 0).toFixed(2)}`, 14, yPos);
      break;

    case 'cash-book':
      filename = `cash-book-${dateRange.from_date || ''}-${dateRange.to_date || ''}`;
      doc.autoTable({
        head: [['Date', 'Entry #', 'Narration', 'Receipt (₹)', 'Payment (₹)', 'Balance (₹)']],
        body: (reportData.entries || []).map(e => [
          e.date || '',
          e.entry_number || '',
          e.narration || '',
          (e.receipt_amount || 0).toFixed(2),
          (e.payment_amount || 0).toFixed(2),
          (e.running_balance || 0).toFixed(2)
        ]),
        startY: yPos,
        headStyles: { fillColor: [255, 153, 51] },
        styles: { fontSize: 8 },
        margin: { left: 14, right: 14 }
      });
      break;

    case 'bank-book':
      filename = `bank-book-${reportData.account_code || 'report'}-${dateRange.from_date || ''}`;
      doc.autoTable({
        head: [['Date', 'Entry #', 'Narration', 'Cheque #', 'Deposit (₹)', 'Withdrawal (₹)', 'Balance (₹)']],
        body: (reportData.entries || []).map(e => [
          e.date || '',
          e.entry_number || '',
          e.narration || '',
          e.cheque_number || '',
          (e.deposit_amount || 0).toFixed(2),
          (e.withdrawal_amount || 0).toFixed(2),
          (e.running_balance || 0).toFixed(2)
        ]),
        startY: yPos,
        headStyles: { fillColor: [255, 153, 51] },
        styles: { fontSize: 8 },
        margin: { left: 14, right: 14 }
      });
      break;

    case 'balance-sheet':
      filename = `balance-sheet-${dateRange.as_of_date || 'report'}`;
      // Assets section
      const assetsData = [
        ...(reportData.fixed_assets || []).flatMap(g => [
          [g.group_name, '', ''],
          ...(g.accounts || []).map(a => ['', a.account_name, (a.current_year || 0).toFixed(2)])
        ]),
        ...(reportData.current_assets || []).flatMap(g => [
          [g.group_name, '', ''],
          ...(g.accounts || []).map(a => ['', a.account_name, (a.current_year || 0).toFixed(2)])
        ]),
        ['TOTAL ASSETS', '', (reportData.total_assets || 0).toFixed(2)]
      ];
      
      doc.autoTable({
        head: [['ASSETS', '', 'Amount (₹)']],
        body: assetsData,
        startY: yPos,
        headStyles: { fillColor: [19, 136, 8] }, // Green
        styles: { fontSize: 8 },
        margin: { left: 14, right: 14 }
      });

      yPos = doc.lastAutoTable.finalY + 10;

      // Liabilities section
      const liabilitiesData = [
        ['Corpus Fund', '', (reportData.corpus_fund || 0).toFixed(2)],
        ...(reportData.designated_funds || []).flatMap(g => [
          [g.group_name, '', ''],
          ...(g.accounts || []).map(a => ['', a.account_name, (a.current_year || 0).toFixed(2)])
        ]),
        ...(reportData.current_liabilities || []).flatMap(g => [
          [g.group_name, '', ''],
          ...(g.accounts || []).map(a => ['', a.account_name, (a.current_year || 0).toFixed(2)])
        ]),
        ['TOTAL LIABILITIES & FUNDS', '', (reportData.total_liabilities_and_funds || 0).toFixed(2)]
      ];

      doc.autoTable({
        head: [['LIABILITIES & FUNDS', '', 'Amount (₹)']],
        body: liabilitiesData,
        startY: yPos,
        headStyles: { fillColor: [19, 136, 8] }, // Green
        styles: { fontSize: 8 },
        margin: { left: 14, right: 14 }
      });
      break;

    case 'trial-balance':
      filename = `trial-balance-${dateRange.as_of_date || 'report'}`;
      doc.autoTable({
        head: [['Account Code', 'Account Name', 'Debit (₹)', 'Credit (₹)']],
        body: (reportData.accounts || []).map(a => [
          a.account_code || '',
          a.account_name || '',
          (a.debit_balance || 0).toFixed(2),
          (a.credit_balance || 0).toFixed(2)
        ]),
        startY: yPos,
        foot: [[
          'TOTAL',
          '',
          (reportData.total_debits || 0).toFixed(2),
          (reportData.total_credits || 0).toFixed(2)
        ]],
        headStyles: { fillColor: [255, 153, 51] },
        footStyles: { fillColor: [255, 243, 224] },
        styles: { fontSize: 8 },
        margin: { left: 14, right: 14 }
      });
      break;

    case 'profit-loss':
      filename = `profit-loss-${dateRange.from_date || ''}-${dateRange.to_date || ''}`;
      // Income section
      const incomeData = (reportData.income_groups || []).flatMap(g => [
        [g.category_name, '', ''],
        ...(g.accounts || []).map(a => ['', a.account_name, (a.amount || 0).toFixed(2)]),
        ['', `Total ${g.category_name}`, (g.total || 0).toFixed(2)],
        []
      ]);
      incomeData.push(['TOTAL INCOME', '', (reportData.total_income || 0).toFixed(2)]);

      doc.autoTable({
        head: [['INCOME', '', 'Amount (₹)']],
        body: incomeData,
        startY: yPos,
        headStyles: { fillColor: [19, 136, 8] },
        styles: { fontSize: 8 },
        margin: { left: 14, right: 14 }
      });

      yPos = doc.lastAutoTable.finalY + 10;

      // Expenses section
      const expenseData = (reportData.expense_groups || []).flatMap(g => [
        [g.category_name, '', ''],
        ...(g.accounts || []).map(a => ['', a.account_name, (a.amount || 0).toFixed(2)]),
        ['', `Total ${g.category_name}`, (g.total || 0).toFixed(2)],
        []
      ]);
      expenseData.push(['TOTAL EXPENSES', '', (reportData.total_expenses || 0).toFixed(2)]);
      expenseData.push(['NET SURPLUS/DEFICIT', '', (reportData.net_surplus || 0).toFixed(2)]);

      doc.autoTable({
        head: [['EXPENSES', '', 'Amount (₹)']],
        body: expenseData,
        startY: yPos,
        headStyles: { fillColor: [255, 153, 51] },
        styles: { fontSize: 8 },
        margin: { left: 14, right: 14 }
      });
      break;

    default:
      // Generic table export
      const headers = Object.keys(Array.isArray(reportData) ? reportData[0] : reportData);
      const rows = Array.isArray(reportData) 
        ? reportData.map(row => headers.map(h => String(row[h] || '')))
        : [headers.map(h => String(reportData[h] || ''))];
      
      doc.autoTable({
        head: [headers],
        body: rows,
        startY: yPos,
        headStyles: { fillColor: [255, 153, 51] },
        styles: { fontSize: 8 },
        margin: { left: 14, right: 14 }
      });
  }

  // Add footer
  const pageCount = doc.internal.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(8);
    doc.setTextColor(100, 100, 100);
    doc.text(
      `Page ${i} of ${pageCount} | Generated on ${new Date().toLocaleString()}`,
      105,
      doc.internal.pageSize.height - 10,
      { align: 'center' }
    );
  }

  doc.save(`${filename}.pdf`);
};
