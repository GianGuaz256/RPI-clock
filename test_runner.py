#!/usr/bin/env python3
"""
Comprehensive test runner for the Raspberry Pi Dashboard.

This script runs all tests with coverage reporting and generates
detailed reports about the application's functionality.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_colored(text, color):
    """Print colored text to terminal."""
    print(f"{color}{text}{Colors.ENDC}")

def check_dependencies():
    """Check if all required testing dependencies are installed."""
    print_colored("🔍 Checking test dependencies...", Colors.OKBLUE)
    
    required_packages = [
        'pytest',
        'pytest-cov',
        'pytest-mock', 
        'responses'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print_colored(f"  ✗ {package} (missing)", Colors.FAIL)
    
    if missing_packages:
        print_colored("\n⚠️  Missing dependencies detected!", Colors.WARNING)
        print("Please install missing packages:")
        print(f"  pip install {' '.join(missing_packages)}")
        print("\nOr install all test dependencies:")
        print("  pip install -r requirements.txt")
        return False
    
    print_colored("✓ All test dependencies are installed", Colors.OKGREEN)
    return True

def run_tests(test_type="all", verbose=False, coverage=True, report_format="terminal"):
    """Run the test suite with specified options."""
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test selection
    if test_type == "unit":
        cmd.extend([
            "tests/test_config.py",
            "tests/test_api_managers.py", 
            "tests/test_screens.py",
            "tests/test_core_components.py",
            "tests/test_utils.py"
        ])
    elif test_type == "integration":
        cmd.extend(["tests/test_integration.py"])
    elif test_type == "all":
        cmd.extend(["tests/"])
    else:
        cmd.extend([f"tests/test_{test_type}.py"])
    
    # Add coverage reporting
    if coverage:
        cmd.extend([
            "--cov=config",
            "--cov=core", 
            "--cov=api",
            "--cov=screens",
            "--cov=utils",
            "--cov-report=term-missing"
        ])
        
        if report_format == "html":
            cmd.extend(["--cov-report=html:htmlcov"])
        elif report_format == "xml":
            cmd.extend(["--cov-report=xml"])
    
    # Add verbosity
    if verbose:
        cmd.extend(["-v", "-s"])
    else:
        cmd.extend(["-q"])
    
    # Add other useful options
    cmd.extend([
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker checking
        "--durations=10"  # Show 10 slowest tests
    ])
    
    print_colored(f"\n🚀 Running {test_type} tests...", Colors.OKBLUE)
    print(f"Command: {' '.join(cmd)}")
    
    # Set environment variables for testing
    env = os.environ.copy()
    env['SDL_VIDEODRIVER'] = 'dummy'  # Prevent pygame display issues
    
    # Run the tests
    try:
        result = subprocess.run(cmd, env=env, capture_output=False)
        return result.returncode == 0
    except KeyboardInterrupt:
        print_colored("\n⚠️  Tests interrupted by user", Colors.WARNING)
        return False
    except Exception as e:
        print_colored(f"\n❌ Error running tests: {e}", Colors.FAIL)
        return False

def validate_application():
    """Run basic validation checks on the application."""
    print_colored("\n🔧 Validating application structure...", Colors.OKBLUE)
    
    # Check that all required files exist
    required_files = [
        "app.py",
        "config/config_manager.py",
        "core/dashboard_app.py", 
        "core/cache.py",
        "core/touch_handler.py",
        "api/base_api.py",
        "api/weather_api.py",
        "api/bitcoin_api.py",
        "api/calendar_api.py",
        "screens/base_screen.py",
        "screens/clock_calendar_screen.py",
        "screens/weather_screen.py",
        "screens/bitcoin_screen.py",
        "screens/system_stats_screen.py",
        "utils/constants.py",
        "utils/system_monitor.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print_colored(f"  ✗ {file_path} (missing)", Colors.FAIL)
        else:
            print(f"  ✓ {file_path}")
    
    if missing_files:
        print_colored(f"\n❌ Missing {len(missing_files)} required files!", Colors.FAIL)
        return False
    
    print_colored("✓ All required files present", Colors.OKGREEN)
    
    # Check import syntax
    print_colored("\n🔍 Checking Python syntax...", Colors.OKBLUE)
    for file_path in required_files:
        if file_path.endswith('.py'):
            try:
                with open(file_path, 'r') as f:
                    compile(f.read(), file_path, 'exec')
                print(f"  ✓ {file_path}")
            except SyntaxError as e:
                print_colored(f"  ✗ {file_path} - Syntax Error: {e}", Colors.FAIL)
                return False
            except Exception as e:
                print_colored(f"  ⚠ {file_path} - Warning: {e}", Colors.WARNING)
    
    print_colored("✓ All Python files have valid syntax", Colors.OKGREEN)
    return True

def generate_test_report():
    """Generate a comprehensive test report."""
    print_colored("\n📊 Generating test coverage report...", Colors.OKBLUE)
    
    # Run tests with HTML coverage report
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "--cov=config",
        "--cov=core", 
        "--cov=api",
        "--cov=screens",
        "--cov=utils",
        "--cov-report=html:test_reports/coverage",
        "--cov-report=xml:test_reports/coverage.xml",
        "--junit-xml=test_reports/junit.xml",
        "-q"
    ]
    
    # Create reports directory
    Path("test_reports").mkdir(exist_ok=True)
    
    # Set environment for testing
    env = os.environ.copy()
    env['SDL_VIDEODRIVER'] = 'dummy'
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print_colored("✓ Test report generated successfully", Colors.OKGREEN)
            print(f"  📁 Coverage report: test_reports/coverage/index.html")
            print(f"  📄 XML coverage: test_reports/coverage.xml")
            print(f"  📄 JUnit XML: test_reports/junit.xml")
            return True
        else:
            print_colored("❌ Failed to generate test report", Colors.FAIL)
            print(result.stderr)
            return False
            
    except Exception as e:
        print_colored(f"❌ Error generating report: {e}", Colors.FAIL)
        return False

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Comprehensive test runner for Raspberry Pi Dashboard"
    )
    
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "config", "api", "screens", "core", "utils"],
        default="all",
        help="Type of tests to run (default: all)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true", 
        help="Skip coverage reporting"
    )
    
    parser.add_argument(
        "--report",
        choices=["terminal", "html", "xml"],
        default="terminal",
        help="Coverage report format (default: terminal)"
    )
    
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate application structure, don't run tests"
    )
    
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Only generate test reports"
    )
    
    args = parser.parse_args()
    
    # Print header
    print_colored("=" * 60, Colors.HEADER)
    print_colored("🧪 RASPBERRY PI DASHBOARD TEST SUITE", Colors.HEADER)
    print_colored("=" * 60, Colors.HEADER)
    
    # Validate application structure
    if not validate_application():
        print_colored("\n❌ Application validation failed!", Colors.FAIL)
        sys.exit(1)
    
    if args.validate_only:
        print_colored("\n✅ Application validation completed successfully!", Colors.OKGREEN)
        sys.exit(0)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Generate report only
    if args.report_only:
        success = generate_test_report()
        sys.exit(0 if success else 1)
    
    # Run tests
    coverage = not args.no_coverage
    success = run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=coverage,
        report_format=args.report
    )
    
    if success:
        print_colored("\n🎉 All tests passed!", Colors.OKGREEN)
        
        # Generate detailed report for full test runs
        if args.type == "all" and coverage:
            generate_test_report()
            
        print_colored("\n✅ Dashboard is ready for deployment!", Colors.OKGREEN)
    else:
        print_colored("\n❌ Some tests failed!", Colors.FAIL)
        print_colored("Please fix the issues before deploying.", Colors.WARNING)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 