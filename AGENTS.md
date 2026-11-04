# Project rules

- Keep this as a self-contained static app in `index.html`; do not add a server, framework, or external dependencies.
- Keep user-facing text in Korean and preserve the quiz's current behavior unless a change is requested.
- Use semantic, keyboard-accessible HTML and maintain responsive layout, reduced-motion support, and `prefers-color-scheme` styling.
- Keep CSS and JavaScript with the page; organize quiz content as data and avoid unsafe HTML insertion for dynamic text.
- After behavior changes, smoke-test the page in the integrated browser, including answer feedback, score/progress, and the results/restart flow.
