# Web Directory Brute-Forcer 🌐

A Python-based offensive security utility designed to map a web application's attack surface by enumerating hidden directories, exposed administrative panels, and unlinked backup files. 

**Features:**
* Utilizes the `requests` library to rapidly dispatch HTTP GET requests against a target web server.
* Intelligently parses HTTP Response Codes, discarding `404 Not Found` noise while flagging `200 OK`, `301 Redirect`, and `403 Forbidden` anomalies.
* Implements multi-threading to ensure the GUI remains fully responsive during extensive wordlist processing.
* Includes custom User-Agent spoofing and connection timeout handling to ensure reliable execution.

*Built as Day 20 of a 30-Day Network Engineering & Security portfolio streak. Note: For authorized testing and educational purposes only.*
