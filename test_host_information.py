import pytest
import subprocess
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
import io
import re
import host_information
import check_ubuntu_eol
import df_bargraph

@pytest.fixture(autouse=True)
def capture_stdout(monkeypatch):
    held_output = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = held_output
    yield held_output
    sys.stdout = original_stdout

def test_hi_config_argv_config(capsys):
    # backup original sys.argv for restoration later
    original_argv = sys.argv.copy()
    
    # set argv for this test
    sys.argv = ['config', 'config/example.yml']
    
    try:
        host_information.display_checks()
        captured = capsys.readouterr()
        output = captured.out
        assert "Host Information:" in output
        print("Test passed: 'Host Information' in output")

    finally:
        sys.argv = original_argv
    
def test_hi_config_argv_watch_info(capsys):
    # backup original sys.argv for restoration later
    original_argv = sys.argv.copy()
    
    # set argv for this test
    sys.argv = ['watch', 'info']

    try:
        host_information.display_checks()
        captured = capsys.readouterr()
        output = captured.out
        assert "Host Information:" in output
        print("pass: host_information.main() | output confirmed.")

    finally:
        sys.argv = original_argv

def test_hi_output_header_line(capsys):
    host_information.display_checks()

    captured = capsys.readouterr()
    output = captured.out
    
    assert "Host Information:" in output
    print("Test passed: 'Host Information' found in the output.")

def test_hi_output_get_ip_address(capsys):
    print(host_information.get_ip_address())

    # Capture the output after calling df_bargraph.display_bar_graph
    captured = capsys.readouterr()
    output = captured.out
    print("Captured Output", output)
    
    ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    assert re.search(ip_pattern, output), "No IP address found in the output"

    print("Test passed: 'ip_address' confirmed.")

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

def test_check_ubuntu_eol_output_main(capsys):
    check_ubuntu_eol.main()

    captured = capsys.readouterr()
    output = captured.out
    print("Captured Output: ", output)
    
    assert "Operating System:" in output
    print("pass: check_ubuntu_eol.mail() | output confirmed.")

if __name__ == '__main__':
    pytest.main()

