import unittest
import os
import sys

test_dir = os.path.join(os.path.dirname(__file__), 'Unit_Tests') # Locates the directory containing the test files
sys.path.insert(0, test_dir) # Adds a test directory so the tests can be imported

def run_tests_from_module(module_name): # Loads and runs tests from a specific module by name provided
    loader = unittest.TestLoader()  # These create a test loader and empty test suite for new environment testing (isolated)
    suite = unittest.TestSuite()

    try: # Loading the module by name provided
        module = __import__(module_name)
        suite.addTests(loader.loadTestsFromModule(module))
    except Exception as e: # Just in case loading the module fails, the error is caught
        print(f"Failed to load tests from {module_name}: {e}")
        return False

    runner = unittest.TextTestRunner(verbosity=2) # Once everything's loaded, run the tests with some terminal feedback
    result = runner.run(suite)
    return result.wasSuccessful()

def run_all_tests(): # Loads and runs all test modules in the Unit_Tests directory
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for filename in os.listdir(test_dir):
        if filename.startswith('t_') and filename.endswith('.py'): # This was used in testing the tests (:]) however is a good failsafe for erronous files, especially due to pycache
            module_name = filename[:-3]  # Remve the '.py' extension so it can be grabbed as a module name
            try:
                module = __import__(module_name)
                suite.addTests(loader.loadTestsFromModule(module))
            except Exception as e:
                print(f"Failed to load tests from {filename}: {e}")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

def main_menu(): # Nav menu for testing the backend
    pass

# Entry point for the script
if __name__ == "__main__":
    main_menu()