# Classify the weakness

You are given the published description of one software vulnerability (a CVE).

Decide which weakness class best describes it, choosing **exactly one** of the
30 options below. These are CWE identifiers from MITRE's Common Weakness
Enumeration; the reference answer is the CWE that the assigning security
organisation recorded for that CVE in the National Vulnerability Database.

Read `description.txt` in the case directory.

## Options

CWE-120: Buffer Copy without Checking Size of Input ('Classic Buffer Overflow')
CWE-125: Out-of-bounds Read
CWE-787: Out-of-bounds Write
CWE-502: Deserialization of Untrusted Data
CWE-400: Uncontrolled Resource Consumption
CWE-352: Cross-Site Request Forgery (CSRF)
CWE-306: Missing Authentication for Critical Function
CWE-284: Improper Access Control
CWE-416: Use After Free
CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')
CWE-287: Improper Authentication
CWE-190: Integer Overflow or Wraparound
CWE-20: Improper Input Validation
CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')
CWE-269: Improper Privilege Management
CWE-94: Improper Control of Generation of Code ('Code Injection')
CWE-476: NULL Pointer Dereference
CWE-770: Allocation of Resources Without Limits or Throttling
CWE-200: Exposure of Sensitive Information to an Unauthorized Actor
CWE-693: Protection Mechanism Failure
CWE-639: Authorization Bypass Through User-Controlled Key
CWE-78: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')
CWE-863: Incorrect Authorization
CWE-121: Stack-based Buffer Overflow
CWE-362: Concurrent Execution using Shared Resource with Improper Synchronization ('Race Condition')
CWE-862: Missing Authorization
CWE-918: Server-Side Request Forgery (SSRF)
CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')
CWE-122: Heap-based Buffer Overflow
CWE-434: Unrestricted Upload of File with Dangerous Type

## Output

Print one line, nothing else required:

    ANSWER: CWE-79

The identifier must be one of the 30 listed above. Any other text is ignored.
