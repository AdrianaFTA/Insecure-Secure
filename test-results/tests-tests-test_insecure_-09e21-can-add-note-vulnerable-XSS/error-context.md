# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - heading "Your Notes" [level=1] [ref=e2]
  - link "Logout" [ref=e3] [cursor=pointer]:
    - /url: /logout
  - heading "Add Note" [level=3] [ref=e4]
  - generic [ref=e5]:
    - textbox [ref=e6]
    - button "Add Note" [ref=e7]
  - heading "Your Notes" [level=3] [ref=e8]
  - list [ref=e9]:
    - listitem [ref=e10]:
      - text: <script>alert("XSS")</script>
      - link "Edit" [ref=e11] [cursor=pointer]:
        - /url: /edit/6
      - link "Delete" [ref=e12] [cursor=pointer]:
        - /url: /delete/6
    - listitem [ref=e13]:
      - text: <script>alert("XSS")</script>
      - link "Edit" [ref=e14] [cursor=pointer]:
        - /url: /edit/7
      - link "Delete" [ref=e15] [cursor=pointer]:
        - /url: /delete/7
  - link "Back to Main Page" [ref=e16] [cursor=pointer]:
    - /url: /
```