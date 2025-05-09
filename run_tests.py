#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test runner for the Intelligent Knowledge Aggregation Platform.
Run all tests or specific test types.
"""

import os
import sys
import unittest
import argparse
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_runner')


def discover_and_run_tests(pattern='test_*.py', test_dir='tests', verbosity=1):
    """Discover and run tests matching the given pattern.
    
    Args:
        pattern: Pattern for test file names.
        test_dir: Directory containing tests.
        verbosity: Verbosity level (1-3).
    
    Returns:
        Test result object.
    """
    logger.info(f"Discovering tests with pattern '{pattern}' in '{test_dir}'")
    
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern=pattern)
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result


def main():
    """Main function for the test runner."""
    parser = argparse.ArgumentParser(description='Run tests for the Knowledge Aggregation Platform')
    
    parser.add_argument(
        '--integration', 
        action='store_true',
        help='Run only integration tests'
    )
    
    parser.add_argument(
        '--unit', 
        action='store_true',
        help='Run only unit tests'
    )
    
    parser.add_argument(
        '--pattern', 
        type=str,
        default='test_*.py',
        help='Pattern to match test files (default: test_*.py)'
    )
    
    parser.add_argument(
        '--verbosity', 
        type=int,
        choices=[1, 2, 3],
        default=2,
        help='Verbosity level (1-3, default: 2)'
    )
    
    args = parser.parse_args()
    
    # Determine test directories based on arguments
    test_dirs = []
    
    if args.integration:
        test_dirs.append('tests/integration')
    elif args.unit:
        test_dirs.append('tests/unit')
    else:
        # By default, run all tests
        test_dirs.append('tests')
    
    # Run tests in each directory
    success = True
    for test_dir in test_dirs:
        if not os.path.exists(test_dir):
            logger.warning(f"Test directory '{test_dir}' does not exist, skipping")
            continue
            
        logger.info(f"Running tests in {test_dir}")
        result = discover_and_run_tests(args.pattern, test_dir, args.verbosity)
        
        # Check if all tests passed
        if not result.wasSuccessful():
            success = False
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main() 