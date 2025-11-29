#!/usr/bin/env python3
"""
License Management CLI Tool for MandirSync

This script helps administrators manage licenses:
- Create trial licenses
- Activate full licenses
- Check license status
- Extend trials
- Deactivate licenses

Usage:
    python manage_license.py status
    python manage_license.py create-trial "Sri Krishna Temple" --days 15
    python manage_license.py activate-full "Sri Krishna Temple" --key XXXXX
    python manage_license.py extend-trial 5
    python manage_license.py deactivate
"""

import argparse
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.licensing import get_license_manager, LicenseType


def print_banner():
    """Print banner"""
    print("=" * 70)
    print(" " * 15 + "MandirSync License Manager")
    print("=" * 70)
    print()


def status_command(args):
    """Show license status"""
    manager = get_license_manager()
    status_info = manager.check_license_status()

    print("License Status:")
    print("-" * 50)
    print(f"Status: {status_info.get('status')}")
    print(f"Active: {status_info.get('is_active')}")
    print(f"Message: {status_info.get('message')}")

    if status_info.get('temple_name'):
        print(f"Temple: {status_info.get('temple_name')}")

    if status_info.get('license_type'):
        print(f"Type: {status_info.get('license_type')}")

    if status_info.get('days_remaining'):
        print(f"Days Remaining: {status_info.get('days_remaining')}")

    if status_info.get('expires_at'):
        print(f"Expires: {status_info.get('expires_at')}")

    if status_info.get('is_grace_period'):
        print(f"⚠️  Grace Period: {status_info.get('grace_days_left')} days left")

    print("-" * 50)


def create_trial_command(args):
    """Create trial license"""
    manager = get_license_manager()

    try:
        license_data = manager.create_trial_license(
            temple_name=args.temple_name,
            trial_days=args.days,
            contact_email=args.email,
        )

        print("✅ Trial License Created Successfully!")
        print("-" * 50)
        print(f"Temple: {license_data['temple_name']}")
        print(f"Trial Days: {license_data['trial_days']}")
        print(f"Created: {license_data['created_at']}")
        print(f"Expires: {license_data['expires_at']}")
        if args.email:
            print(f"Email: {args.email}")
        print("-" * 50)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def activate_full_command(args):
    """Activate full license"""
    manager = get_license_manager()

    try:
        license_data = manager.create_full_license(
            temple_name=args.temple_name,
            license_key=args.key,
            license_type=LicenseType.FULL,
            contact_email=args.email,
            expires_at=None,  # Lifetime
        )

        print("✅ Full License Activated Successfully!")
        print("-" * 50)
        print(f"Temple: {license_data['temple_name']}")
        print(f"License Key: {license_data['license_key']}")
        print(f"Type: {license_data['license_type']}")
        print(f"Expires: Lifetime (No Expiry)")
        if args.email:
            print(f"Email: {args.email}")
        print("-" * 50)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def extend_trial_command(args):
    """Extend trial period"""
    manager = get_license_manager()

    try:
        license_data = manager.extend_trial(additional_days=args.days)

        print("✅ Trial Extended Successfully!")
        print("-" * 50)
        print(f"Extended by: {args.days} days")
        print(f"New Expiry: {license_data['expires_at']}")
        print(f"Total Trial Days: {license_data['trial_days']}")
        print("-" * 50)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def deactivate_command(args):
    """Deactivate license"""
    manager = get_license_manager()

    # Confirm
    if not args.yes:
        response = input("⚠️  Are you sure you want to deactivate the license? (yes/no): ")
        if response.lower() != "yes":
            print("Cancelled.")
            return

    try:
        success = manager.deactivate_license()

        if success:
            print("✅ License deactivated successfully!")
        else:
            print("ℹ️  No license found to deactivate.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def info_command(args):
    """Show license file information"""
    manager = get_license_manager()

    print("License File Information:")
    print("-" * 50)
    print(f"Location: {manager.license_file}")
    print(f"Exists: {manager.license_file.exists()}")

    if manager.license_file.exists():
        license_info = manager.get_license_info()
        if license_info:
            print("\nLicense Data:")
            for key, value in license_info.items():
                print(f"  {key}: {value}")

    print("-" * 50)


def main():
    """Main CLI handler"""
    parser = argparse.ArgumentParser(
        description="MandirSync License Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Status command
    subparsers.add_parser("status", help="Show license status")

    # Create trial command
    trial_parser = subparsers.add_parser("create-trial", help="Create trial license")
    trial_parser.add_argument("temple_name", help="Temple name")
    trial_parser.add_argument("--days", type=int, default=15, help="Trial days (default: 15)")
    trial_parser.add_argument("--email", help="Contact email")

    # Activate full license
    full_parser = subparsers.add_parser("activate-full", help="Activate full license")
    full_parser.add_argument("temple_name", help="Temple name")
    full_parser.add_argument("--key", required=True, help="License key")
    full_parser.add_argument("--email", help="Contact email")

    # Extend trial
    extend_parser = subparsers.add_parser("extend-trial", help="Extend trial period")
    extend_parser.add_argument("days", type=int, help="Days to extend")

    # Deactivate
    deactivate_parser = subparsers.add_parser("deactivate", help="Deactivate license")
    deactivate_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")

    # Info
    subparsers.add_parser("info", help="Show license file information")

    args = parser.parse_args()

    print_banner()

    if args.command == "status":
        status_command(args)
    elif args.command == "create-trial":
        create_trial_command(args)
    elif args.command == "activate-full":
        activate_full_command(args)
    elif args.command == "extend-trial":
        extend_trial_command(args)
    elif args.command == "deactivate":
        deactivate_command(args)
    elif args.command == "info":
        info_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
