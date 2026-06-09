# tests/test_s16.py

modeDebug = False

import os
import importlib.util
from time import sleep  

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # type: ignore 
module_path = os.path.join(root_dir, "scripts/functions.py") # type: ignore | Construct the path to the functions.py module based on the root directory
spec = importlib.util.spec_from_file_location("scripts/functions", module_path)
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main) # type: ignore | Import the s16 function from the Function module for converting raw data to signed integers

def test_positive_value():
    assert main.s16(0x01, 0x2C) == 300        

def test_negative_one():
    assert main.s16(0xFF, 0xFF) == -1

def test_negative_100():
    assert main.s16(0xFF, 0x9C) == -100

if modeDebug == True:
    print("Root directory:", root_dir)
    print("Module path:", module_path)
    print(spec)
    print(main)
    print("Pausing to allow inspection of debug output...")
    sleep(5) 

if __name__ == "__main__":
    tests = [test_positive_value, test_negative_one, test_negative_100]
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError:
            failed += 1
    
    print(f"Tests Passed: {passed}/{len(tests)}")
    print(f"Tests Failed: {failed}/{len(tests)}")
