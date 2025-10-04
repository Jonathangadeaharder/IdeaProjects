# Page snapshot

```yaml
- generic [ref=e4]:
    - heading "LangPlug" [level=1] [ref=e5]
    - heading "Sign Up" [level=2] [ref=e6]
    - generic [ref=e7]:
        - textbox "Email" [disabled] [ref=e8]: e2e.1759568377109@langplug.com
        - textbox "Username" [disabled] [ref=e9]: e2euser_1759568377109
        - textbox "Password" [disabled] [ref=e10]: TestPass1759568377109!
        - textbox "Confirm Password" [disabled] [ref=e11]: TestPass1759568377109!
        - generic [ref=e12]:
            - text: "Password requirements:"
            - list [ref=e13]:
                - listitem [ref=e14]: At least 12 characters
                - listitem [ref=e15]: Passwords must match
        - button "Creating Account..." [disabled] [ref=e16]
    - paragraph [ref=e17]:
        - text: Already have an account?
        - link "Sign in now" [ref=e18] [cursor=pointer]:
            - /url: /login
        - text: .
```
