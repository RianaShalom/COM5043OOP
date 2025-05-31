import unittest, os, sys

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
    while True:
        print("\n=== Test Runner ===")
        test_files = [f for f in os.listdir(test_dir) if f.startswith('t_') and f.endswith('.py')]
        if not test_files:
            print("No test files found in Unit_Tests folder.")
            break

        print("Select a test to run:")
        for idx, f in enumerate(test_files, 1):
            print(f"{idx}. {f}")
        print(f"{len(test_files)+1}. Run ALL tests")
        print(f"{len(test_files)+2}. Exit")
        
        choice = input("Enter choice: ").strip()
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(test_files): # Run just the selected test file
                module_name = test_files[choice - 1][:-3] 
                print(f"\nRunning tests in {test_files[choice - 1]}...\n")
                success = run_tests_from_module(module_name)
                print("\nTest run " + ("PASSED" if success else "FAILED"))
            elif choice == len(test_files) + 1: # If all tests are selected - written like this so adding tests is dynamic here
                print("\nRunning ALL tests...\n")
                success = run_all_tests()
                print("\nAll tests " + ("PASSED" if success else "FAILED"))
            elif choice == len(test_files) + 2: # Final option is always exit
                print("Exiting.")
                break
            else:
                print("Invalid choice. Try again.")
        else:
            print("Invalid input. Enter a number.")

# Entry point for the script
if __name__ == "__main__":
    main_menu()