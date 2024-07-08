import pytest
import subprocess
import sys
import io
import re
import host_information  # Ensure this is the correct name of your main script without the .py extension
import check_ubuntu_eol
import df_bargraph

@pytest.fixture(autouse=True)
def capture_stdout(monkeypatch):
    held_output = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = held_output
    yield held_output
    sys.stdout = original_stdout

def test_host_information_header_line_in_output(capsys):
    # Now call the actual df_bargraph.display_bar_graph function
    host_information.display_checks()

    # Capture the output after calling df_bargraph.display_bar_graph
    captured = capsys.readouterr()
    output = captured.out
    
    # Assert that "Filesystem" is in the output
    assert "Host Information:" in output
    print("Test passed: 'Filesystem' found in the output.")

def test_host_information_get_ip_address(capsys):
    # Now call the actual df_bargraph.display_bar_graph function
    print(host_information.get_ip_address())

    # Capture the output after calling df_bargraph.display_bar_graph
    captured = capsys.readouterr()
    output = captured.out
    print("Captured Output", output)
    
    ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    assert re.search(ip_pattern, output), "No IP address found in the output"

    print("Test passed: 'ip_address' found in the output.")

def test_df_bargraph_output(capsys):
    print("df_bargraph assertions")
    
    # Now call the actual df_bargraph.display_bar_graph function
    df_bargraph.display_bar_graph()

    # Capture the output after calling df_bargraph.display_bar_graph
    captured = capsys.readouterr()
    output = captured.out
    print("Captured Output: ", output)
    
    # Assert that "Filesystem" is in the output
    assert "Filesystem" in output
    assert "root (/)" in output
    assert "Used" in output
    assert "Total" in output
    assert "Free" in output
    assert "% Used" in output
    print("Test passed: 'Filesystem' found in the output.")

def test_check_ubuntu_eol_line_in_output(capsys):
    print("JBL starting test..")
    
    # Now call the actual df_bargraph.display_bar_graph function
    check_ubuntu_eol.main()

    # Capture the output after calling df_bargraph.display_bar_graph
    captured = capsys.readouterr()
    output = captured.out
    print("Captured Output: ", output)
    
    # Assert that "Filesystem" is in the output
    assert "Operating System:" in output
    print("Test passed: 'Filesystem' found in the output.")

if __name__ == '__main__':
    pytest.main()

