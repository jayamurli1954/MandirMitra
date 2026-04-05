function env(name, fallback) {
  const value = process.env[name];
  return value && String(value).trim() ? String(value).trim() : fallback;
}

function getUiProfile() {
  return {
    appName: env('PLAYWRIGHT_APP_NAME', 'MandirMitra'),
    appVariant: env('PLAYWRIGHT_APP_VARIANT', 'mandirmitra'),
    loginEmailLabel: env('PLAYWRIGHT_LOGIN_EMAIL_LABEL', 'Email Address'),
    loginPasswordSelector: env('PLAYWRIGHT_LOGIN_PASSWORD_SELECTOR', '#password'),
    loginButtonName: env('PLAYWRIGHT_LOGIN_BUTTON_NAME', 'Sign In'),
    dashboardHeading: env('PLAYWRIGHT_DASHBOARD_HEADING', 'Dashboard'),
    quickDonationHeading: env('PLAYWRIGHT_QUICK_DONATION_HEADING', 'Quick Donation Entry'),
    donationsHeading: env('PLAYWRIGHT_DONATIONS_HEADING', 'Donations'),
    recentDonationsText: env('PLAYWRIGHT_RECENT_DONATIONS_TEXT', 'Recent Donations'),
    sevasHeading: env('PLAYWRIGHT_SEVAS_HEADING', 'Sevas'),
    bookingsRescheduleText: env('PLAYWRIGHT_BOOKINGS_RESCHEDULE_TEXT', 'Bookings / Reschedule'),
    panchangHeading: env('PLAYWRIGHT_PANCHANG_HEADING', "Today's Panchang"),
    recordDonationButtonName: env('PLAYWRIGHT_RECORD_DONATION_BUTTON_NAME', 'Record Donation'),
    generateReportButtonName: env('PLAYWRIGHT_GENERATE_REPORT_BUTTON_NAME', 'Generate Report'),
    accountLedgerTabName: env('PLAYWRIGHT_ACCOUNT_LEDGER_TAB_NAME', 'Account Ledger'),
    viewLedgerButtonName: env('PLAYWRIGHT_VIEW_LEDGER_BUTTON_NAME', 'View Ledger'),
    itemMasterTabName: env('PLAYWRIGHT_ITEM_MASTER_TAB_NAME', 'Item Master'),
    itemMasterRegisterText: env('PLAYWRIGHT_ITEM_MASTER_REGISTER_TEXT', 'Item Master Register'),
    employeeDirectoryText: env('PLAYWRIGHT_EMPLOYEE_DIRECTORY_TEXT', 'Employee & Priest Directory'),
    payrollTabName: env('PLAYWRIGHT_PAYROLL_TAB_NAME', 'Payroll & Salaries'),
    upiHeading: env('PLAYWRIGHT_UPI_HEADING', 'UPI Payment Logging'),
    quickLogUpiText: env('PLAYWRIGHT_QUICK_LOG_UPI_TEXT', 'Quick Log UPI Payment'),
    trialBalanceHeading: env('PLAYWRIGHT_TRIAL_BALANCE_HEADING', 'Trial Balance as of'),
    categoryWiseDonationButtonName: env('PLAYWRIGHT_CATEGORY_WISE_DONATION_BUTTON_NAME', 'Category-Wise Donation'),
    detailedDonationReportButtonName: env('PLAYWRIGHT_DETAILED_DONATION_REPORT_BUTTON_NAME', 'Detailed Donation Report'),
    detailedSevaReportButtonName: env('PLAYWRIGHT_DETAILED_SEVA_REPORT_BUTTON_NAME', 'Detailed Seva Report'),
    threeDaySevaScheduleButtonName: env('PLAYWRIGHT_THREE_DAY_SEVA_SCHEDULE_BUTTON_NAME', '3-Day Seva Schedule'),
    bookNowButtonName: env('PLAYWRIGHT_BOOK_NOW_BUTTON_NAME', 'Book Now'),
    cashAccountCodeLabel: env('PLAYWRIGHT_CASH_ACCOUNT_CODE_LABEL', 'Cash Account Code'),
    amountLabel: env('PLAYWRIGHT_AMOUNT_LABEL', 'Amount'),
    categoryLabel: env('PLAYWRIGHT_CATEGORY_LABEL', 'Category'),
    mobileNumberLabel: env('PLAYWRIGHT_MOBILE_NUMBER_LABEL', 'Mobile Number'),
    searchButtonName: env('PLAYWRIGHT_SEARCH_BUTTON_NAME', 'Search'),
    createContinueButtonName: env('PLAYWRIGHT_CREATE_CONTINUE_BUTTON_NAME', 'Create & Continue'),
  };
}

module.exports = { getUiProfile };
