import pytest
import subprocess
import sys
import os
# Make sure script can find and import modules from directories relative to the script’s location
# ensures that the directory containing this script is searched first when we import modules.
tests_dir = os.path.join(os.path.dirname(__file__))
hi_dir = os.path.dirname(tests_dir)
app_dir = hi_dir + "/hi"
sys.path.insert(0, os.path.abspath(tests_dir))
sys.path.insert(0, os.path.abspath(app_dir))


import io
import re
import host_information
import check_os_eol
import df_bargraph

@pytest.fixture(autouse=True)
def capture_stdout(monkeypatch):
    held_output = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = held_output
    yield held_output
    sys.stdout = original_stdout

def test_hi_config_argv_watch_info_config(capsys):
    # backup original sys.argv for restoration later
    original_argv = sys.argv.copy()
    
    # set argv for this test
    sys.argv = ['watch', 'info', 'config', 'example.yml']
    #pattern = r"\[\🔴\]|\[\✅\]"
    pattern = r"🔴|✅"
    
    try:
        host_information.hi_report()
        captured = capsys.readouterr()
        output = captured.out
        assert "HOST INFORMATION" in output
        assert re.search(pattern, output), "No standard check indicators detected"
        print("Test passed: 'HOST INFORMATION' in output")

    finally:
        sys.argv = original_argv

def test_hi_config_argv_config(capsys):
    # backup original sys.argv for restoration later
    original_argv = sys.argv.copy()
    #pattern = r"\[\🔴\]|\[\✅\]"
    pattern = r"🔴|✅"
    
    # set argv for this test
    sys.argv = ['config', 'example.yml']
    
    try:
        host_information.hi_report()
        captured = capsys.readouterr()
        output = captured.out
        assert "HOST INFORMATION" in output
        assert re.search(pattern, output), "No standard check indicators detected"
        print("Test passed: 'HOST INFORMATION' in output")

    finally:
        sys.argv = original_argv
    
def test_hi_config_argv_info(capsys):
    # backup original sys.argv for restoration later
    original_argv = sys.argv.copy()
    #pattern = r"\[\🔴\]|\[\✅\]"
    pattern = r"🔴|✅"
    
    # set argv for this test
    sys.argv = ['info']

    try:
        host_information.hi_report()
        captured = capsys.readouterr()
        output = captured.out
        assert "HOST INFORMATION" in output
        assert re.search(pattern, output), "No standard check indicators detected"
        print("pass: host_information.main() | output confirmed.")

    finally:
        sys.argv = original_argv

def test_hi_config_argv_watch_info(capsys):
    # backup original sys.argv for restoration later
    original_argv = sys.argv.copy()
    #pattern = r"\[\🔴\]|\[\✅\]"
    pattern = r"🔴|✅"
    
    # set argv for this test
    sys.argv = ['watch', 'info']

    try:
        host_information.hi_report()
        captured = capsys.readouterr()
        output = captured.out
        assert "HOST INFORMATION" in output
        assert re.search(pattern, output), "No standard check indicators detected"
        print("pass: host_information.main() | output confirmed.")

    finally:
        sys.argv = original_argv

def test_hi_config_argv_defaults(capsys):
    host_information.hi_report()
    #pattern = r"\[\🔴\]|\[\✅\]"
    pattern = r"🔴|✅"

    captured = capsys.readouterr()
    output = captured.out
    
    assert "HOST INFORMATION" in output
    assert re.search(pattern, output), "No standard check indicators detected"
    print("pass: host_information.main() | output confirmed.")
    

def test_hi_output_get_ip_address(capsys):
    print(host_information.get_ip_address())

    # Capture the output after calling df_bargraph.display_bar_graph
    captured = capsys.readouterr()
    output = captured.out
    print("Captured Output", output)
    
    ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    assert re.search(ip_pattern, output), "No IP address found in the output"
    print("pass: host_information.get_ip_address() | output confirmed.")

def test_hi_df_bargraph_combind_output(capsys):
    pattern = r"🔴|✅"
    host_information.hi_report()
    df_bargraph.display_bar_graph()
    captured = capsys.readouterr()
    output = captured.out
    print("Captured Output: ", output)
    assert "Filesystem" in output
    assert "root (/)" in output
    assert "Used" in output
    assert "Total" in output
    assert "Free" in output
    assert "% Used" in output
    print("Test passed: Filesystem bargraph elements confirmed.")


def test_df_bargraph_output_display_bar_graph(capsys):
    print("df_bargraph assertions")
    
    df_bargraph.display_bar_graph()

    captured = capsys.readouterr()
    output = captured.out
    print("Captured Output: ", output)
    
    assert "Filesystem" in output
    assert "root (/)" in output
    assert "Used" in output
    assert "Total" in output
    assert "Free" in output
    assert "% Used" in output
    print("Test passed: Filesystem bargraph elements confirmed.")

def test_check_os_eol_output_main(capsys):
    check_os_eol.main()

    captured = capsys.readouterr()
    output = captured.out
    print("Captured Output: ", output)
    
    assert "Operating System:" in output
    print("pass: check_os_eol.mail() | output confirmed.")

if __name__ == '__main__':
    pytest.main()

