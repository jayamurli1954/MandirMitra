# Backup & Restore Feature

## Overview

A comprehensive backup and restore feature has been added to the system, allowing administrators to protect their data.

## Location

**Menu:** "Backup & Restore" (visible in main navigation menu)
**Route:** `/backup-restore`
**Access:** Admin, Super Admin, and Temple Manager roles

## Features

### 1. Create Backup
- Creates a complete backup of all critical database tables
- Includes: temples, users, devotees, donations, sevas, accounts, journal entries, etc.
- Backup files are stored in JSON format
- Saved to `backend/backups/` directory
- Filename format: `backup_YYYYMMDD_HHMMSS.json`

### 2. Download Backup
- Download any backup file to your local machine
- Useful for external storage or off-site backups

### 3. Restore Backup
- Restore data from a backup file
- Merges data from backup with existing database
- **Warning:** Only super administrators can restore
- Requires confirmation before proceeding

### 4. Delete Backup
- Remove old backup files to save space
- Requires confirmation before deletion

## Security

- **Backup:** Admin, Super Admin, Temple Manager roles
- **Restore:** Super Admin only (highest security)
- All operations logged with user email and timestamp
- Path traversal protection on file operations

## Backup Contents

The backup includes the following tables:
- temples
- users
- devotees
- donation_categories
- donations
- sevas
- seva_bookings
- accounts
- journal_entries
- journal_lines
- bank_accounts

## Usage

### Creating a Backup
1. Navigate to "Backup & Restore" from the menu
2. Click "Create Backup" button
3. Wait for backup to complete
4. Backup file will appear in the list

### Restoring from Backup
1. Navigate to "Backup & Restore"
2. Click "Restore Backup" button
3. Select a backup JSON file
4. Confirm the restore operation
5. System will reload after successful restore

### Downloading a Backup
1. Click the download icon next to any backup file
2. File will download to your default download location

### Deleting a Backup
1. Click the delete icon next to any backup file
2. Confirm deletion
3. File will be permanently removed

## Important Notes

1. **Regular Backups:** It's recommended to create regular backups before major operations
2. **External Storage:** Download backups and store them in a safe location
3. **Restore Caution:** Restore operations merge data - be careful with conflicting records
4. **File Format:** Backups are in JSON format for easy inspection and portability
5. **Database Compatibility:** Works with both PostgreSQL and SQLite databases

## Technical Details

- **Backend API:** `/api/v1/backup-restore/`
- **Backup Directory:** `backend/backups/`
- **File Format:** JSON
- **Encoding:** UTF-8

## Future Enhancements

Possible improvements:
- Scheduled automatic backups
- Backup encryption
- Cloud storage integration
- Incremental backups
- Backup verification/validation




