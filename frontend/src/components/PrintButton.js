import React from 'react';
import { Button } from '@mui/material';
import PrintIcon from '@mui/icons-material/Print';
import { printElement, printPage, printTable } from '../utils/print';

const PrintButton = ({ 
  elementId = null,
  data = null,
  columns = null,
  title = 'Print',
  variant = 'outlined',
  size = 'medium',
  fullWidth = false
}) => {
  const handlePrint = () => {
    if (elementId) {
      printElement(elementId, title);
    } else if (data && columns) {
      printTable(data, columns, title);
    } else {
      printPage();
    }
  };

  return (
    <Button
      variant={variant}
      size={size}
      startIcon={<PrintIcon />}
      onClick={handlePrint}
      fullWidth={fullWidth}
    >
      Print
    </Button>
  );
};

export default PrintButton;


