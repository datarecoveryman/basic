// C++ program to take lines, a la BASIC, from the user
// Available commands: list! exit! quit! and help!

#include <iostream>
#include <string>

using namespace std;

int main() {
    string help = "Available commands: exit!, help!, list!, line!, next!, run!";

    cout << "Oh god, we're still doing cout?" << endl;
    cout << "Hello. Commands end with ! so try help! or quit! to exit!" << endl;

    // Get line from the user
    string line;
    cout << "Enter a line: ";
    getline(cin, line);

    // Split the line on spaces
    string command;
    string rest;
    size_t space = line.find(' ');
    size_t bang = line.find('!');
    if (bang != string::npos && (space == string::npos || bang < space)) {
        // Treat as command
        command = line.substr(0, bang);
        cout << "Command: " << endl;
    } else
    if (space != string::npos) {
        command = line.substr(0, space);
        rest = line.substr(space + 1);
    } else {
        command = line;
    }
}
