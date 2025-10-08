"""
Test file handling in OSC mode
"""

import os
import time
from pythonosc.udp_client import SimpleUDPClient
import csv


def create_test_files():
    """Create various test QUBO files"""
    
    # Test file 1: 3x3 Ising chain
    with open('test_3x3.csv', 'w') as f:
        f.write('h1,s0,s1,s2\n')
        f.write('s0, 1.0,-0.5, 0.0\n')
        f.write('s1,-0.5, 1.0,-0.5\n')
        f.write('s2, 0.0,-0.5, 1.0\n')
    print("Created test_3x3.csv")
    
    # Test file 2: 5x5 fully connected
    with open('test_5x5.csv', 'w') as f:
        f.write('h1,s0,s1,s2,s3,s4\n')
        for i in range(5):
            row = [f's{i}']
            for j in range(5):
                if i == j:
                    row.append(' 2.0')
                else:
                    row.append('-0.3')
            f.write(','.join(row) + '\n')
    print("Created test_5x5.csv")
    
    # Test file 3: 4x4 with specific pattern
    with open('my_matrix.csv', 'w') as f:
        f.write('h1,s0,s1,s2,s3\n')
        f.write('s0, 1.5, 0.0,-0.2, 0.0\n')
        f.write('s1, 0.0, 1.5, 0.0,-0.2\n')
        f.write('s2,-0.2, 0.0, 1.5, 0.0\n')
        f.write('s3, 0.0,-0.2, 0.0, 1.5\n')
    print("Created my_matrix.csv")


def test_file_specification():
    """Test 1: Verify --qubo_file argument works"""
    print("\n" + "="*60)
    print("TEST 1: File Specification")
    print("="*60)
    
    create_test_files()
    
    print("\nStart VQH with specific file:")
    print("python VQH.py Test1 local qubo --qubo_source osc --qubo_file my_matrix.csv")
    print("\nThen run:")
    print("  init")
    print("  qubo info  (should show it's using my_matrix.csv)")
    
    input("\nPress Enter when ready to verify...")
    
    # The QUBO info should show:
    # - file: my_matrix.csv
    # - size: 4x4
    # - Initial values from my_matrix.csv
    
    print("✓ Test 1 complete\n")


def test_osc_save_load():
    """Test 2: OSC save and load operations"""
    print("\n" + "="*60)
    print("TEST 2: OSC Save/Load Operations")
    print("="*60)
    
    print("\nStart VQH:")
    print("python VQH.py Test2 local qubo --qubo_source osc")
    input("\nPress Enter when VQH is ready with 'init'...")
    
    client = SimpleUDPClient("127.0.0.1", 1451)
    
    # Set up a matrix
    print("\nSetting up a test matrix via OSC...")
    client.send_message("/vqh/qubo/size", 3)
    time.sleep(0.1)
    client.send_message("/vqh/qubo/entry", [0, 0, 2.5])
    client.send_message("/vqh/qubo/entry", [1, 1, 2.5])
    client.send_message("/vqh/qubo/entry", [2, 2, 2.5])
    client.send_message("/vqh/qubo/entry", [0, 1, -1.0])
    client.send_message("/vqh/qubo/entry", [1, 0, -1.0])
    time.sleep(0.5)
    
    # Save it
    print("Saving via OSC to 'osc_saved.csv'...")
    client.send_message("/vqh/qubo/save", "osc_saved.csv")
    time.sleep(0.5)
    
    # Verify file was created
    if os.path.exists("osc_saved.csv"):
        print("✓ File osc_saved.csv created")
        with open("osc_saved.csv", 'r') as f:
            print("Contents:")
            print(f.read())
    else:
        print("✗ File not created!")
    
    # Clear and reload
    print("\nClearing matrix...")
    client.send_message("/vqh/qubo/clear", [])
    time.sleep(0.5)
    
    print("Run 'qubo info' in VQH (should show all zeros)")
    input("Press Enter after checking...")
    
    print("\nLoading back from file...")
    client.send_message("/vqh/qubo/load", "osc_saved.csv")
    time.sleep(0.5)
    
    print("Run 'qubo info' again (should show loaded values)")
    input("Press Enter after checking...")
    
    print("✓ Test 2 complete\n")


def test_cli_commands():
    """Test 3: CLI QUBO commands"""
    print("\n" + "="*60)
    print("TEST 3: CLI QUBO Commands")
    print("="*60)
    
    print("\nStart VQH:")
    print("python VQH.py Test3 local qubo --qubo_source osc --qubo_file test_3x3.csv")
    print("\nRun these commands in order:")
    print("  init")
    print("  qubo info         # Should show 3x3 from test_3x3.csv")
    print("  qubo save         # Save snapshot with timestamp")
    print("  qubo save backup.csv  # Save with specific name")
    print("  qubo load test_5x5.csv  # Load different file")
    print("  qubo info         # Should now show 5x5")
    print("  qubo reload       # Reload original test_3x3.csv")
    print("  qubo info         # Should be back to 3x3")
    
    input("\nPress Enter when all commands tested...")
    print("✓ Test 3 complete\n")


def test_segmented_with_files():
    """Test 4: Segmented mode with file tracking"""
    print("\n" + "="*60)
    print("TEST 4: Segmented Mode File Tracking")
    print("="*60)
    
    print("\nStart VQH:")
    print("python VQH.py Test4 local qubo segmented --qubo_source osc --qubo_file my_matrix.csv")
    print("\nRun:")
    print("  init")
    print("  qubo info    # Note the initial state from my_matrix.csv")
    print("  rt           # Start segmented mode")
    
    input("\nPress Enter when first segment is running...")
    
    client = SimpleUDPClient("127.0.0.1", 1451)
    
    # Send some updates
    print("\nSending OSC updates (will be buffered)...")
    client.send_message("/vqh/qubo/entry", [0, 0, 5.0])
    client.send_message("/vqh/qubo/entry", [1, 1, 5.0])
    time.sleep(0.5)
    
    print("\nTrigger next segment (edit rt_conf.json)")
    print("The console should show:")
    print("  - Applying pending updates")
    print("  - New operator values reflecting the changes")
    
    input("\nPress Enter after verifying...")
    
    print("\nNow in a new terminal, run:")
    print("  qubo info")
    print("It should show the updated values (5.0 on diagonal)")
    
    input("\nPress Enter when verified...")
    print("✓ Test 4 complete\n")

def test_rt_control():
    """Test 5: OSC with RT Segmented Control"""
    print("\n" + "="*60)
    print("TEST 5: OSC + RT CTRL")
    print("="*60)
    
    print("\nStart VQH:")
    print("python VQH.py Test5 local qubo --qubo_source osc --qubo_file test_3x3.csv")
    input("\nPress Enter when VQH is ready with 'init'...")
    
    client = SimpleUDPClient("127.0.0.1", 1451)
    client2 = SimpleUDPClient("127.0.0.1", 1452)
    
    # Set up a matrix
    print("\nSetting up a test matrix via OSC...")
    client.send_message("/vqh/qubo/size", 3)
    time.sleep(0.1)
    client.send_message("/vqh/qubo/entry", [0, 0, 2.5])
    client.send_message("/vqh/qubo/entry", [1, 1, 2.5])
    client.send_message("/vqh/qubo/entry", [2, 2, 2.5])
    client.send_message("/vqh/qubo/entry", [0, 1, -1.0])
    client.send_message("/vqh/qubo/entry", [1, 0, -1.0])
    time.sleep(0.5)
    print("Saving via OSC to 'osc_saved.csv'...")
    client.send_message("/vqh/qubo/save", "rt_test_3x3.csv")
    time.sleep(0.5)

    print("\nTrigger RT mode via OSC...")
    input("Press Enter to send RT start command...")
    client2.send_message("/vqh/rt/next", [])
    time.sleep(0.5)

    input("\nPress Enter when verified...")
    print("✓ Test 5 complete\n")




def cleanup():
    """Remove test files"""
    test_files = ['test_3x3.csv', 'test_5x5.csv', 'my_matrix.csv', 
                  'osc_saved.csv', 'backup.csv', 'osc_test.csv']
    
    print("\nCleaning up test files...")
    for f in test_files:
        if os.path.exists(f):
            os.remove(f)
            print(f"  Removed {f}")


if __name__ == "__main__":
    import sys
    
    print("VQH File Handling Test Suite")
    print("="*60)
    
    if len(sys.argv) > 1:
        test = sys.argv[1]
        if test == "1":
            test_file_specification()
        elif test == "2":
            test_osc_save_load()
        elif test == "3":
            test_cli_commands()
        elif test == "4":
            test_segmented_with_files()
        elif test == "5":
            test_rt_control()
        elif test == "all":
            test_file_specification()
            test_osc_save_load()
            test_cli_commands()
            test_segmented_with_files()
        elif test == "clean":
            cleanup()
        else:
            print(f"Unknown test: {test}")
    else:
        print("\nUsage: python test_file_handling.py [1|2|3|4|all|clean]")
        print("\n  1 - Test file specification with --qubo_file")
        print("  2 - Test OSC save/load operations")
        print("  3 - Test CLI QUBO commands")
        print("  4 - Test segmented mode with file tracking")
        print("  all - Run all tests")
        print("  clean - Remove test files")
        print("\nStart with test 1 to verify file handling")
