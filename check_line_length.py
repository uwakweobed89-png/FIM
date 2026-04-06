#!/usr/bin/env python3
"""
PEP 8 Line Length Checker
Verifies that all lines in a Python file are ≤ 79 characters.
"""

import sys
from pathlib import Path


def check_line_length(filepath: Path, max_length: int = 79) -> bool:
    """Check if all lines in a file are within max_length."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

    # Find lines exceeding max_length
    long_lines = [
        (i + 1, len(line.rstrip('\n')), line.rstrip('\n'))
        for i, line in enumerate(lines)
        if len(line.rstrip('\n')) > max_length
    ]

    # Display results
    print("=" * 70)
    print(f"PEP 8 Line Length Check: {filepath.name}")
    print("=" * 70)
    print(f"Maximum allowed: {max_length} characters")
    print(f"Total lines: {len(lines)}")

    if long_lines:
        print(f"\n❌ FAILED: Found {len(long_lines)} lines "
              f"exceeding {max_length} characters\n")

        # Show first 20 violations
        for line_num, length, content in long_lines[:20]:
            # Truncate very long lines for display
            display_content = (
                content[:60] + '...'
                if len(content) > 60
                else content
            )
            print(f"Line {line_num:4d} ({length:3d} chars): "
                  f"{display_content}")

        if len(long_lines) > 20:
            print(f"\n... and {len(long_lines) - 20} more violations")

        return False
    else:
        longest = max(len(line.rstrip('\n')) for line in lines)
        print("\n✅ PASSED: All lines comply with PEP 8")
        print(f"Longest line: {longest} characters")
        print(f"Margin: {max_length - longest} characters\n")
        return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python check_line_length.py <file.py> "
              "[max_length]")
        print("\nExample:")
        print("  python check_line_length.py "
              "login_detector_modernized.py")
        print("  python check_line_length.py my_script.py 100")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    max_length = int(sys.argv[2]) if len(sys.argv) > 2 else 79

    passed = check_line_length(filepath, max_length)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
