# GitHub Wiki publication

## Current state

The GitHub repository API reports `has_wiki: true`. This means the Wiki
feature is enabled, **not** that the independent Wiki Git repository has been
initialized or populated. The connected GitHub app cannot write Wiki pages.

The version-controlled source lives under `wiki/` in `main`.
The public Wiki is a separate Git repository:
`https://github.com/tobe4it/bergen-mq-lab.wiki.git`.

## Initialize once, then publish

1. Open https://github.com/tobe4it/bergen-mq-lab/wiki while logged in.
2. If the Wiki is empty, create and save the first `Home` page in GitHub.
   If the Wiki tab is hidden, check **Settings → General → Features → Wikis**.
3. From a workstation with authenticated Git write access and a current
   `bergen-mq-lab` checkout, run:

```bash
bash tools/publish_wiki.sh
bash tools/publish_wiki.sh --push
```

Without `--push`, the publisher only prepares a temporary Wiki clone and
shows the staged changes. With `--push`, it commits and pushes the 24
`Quick-Start-XX.md` language pages, `Home.md`, `_Sidebar.md`, and copies
the existing long-form `wiki/en/Guide.md`, `wiki/de/Guide.md` and
`wiki/fr/Guide.md` to uniquely named Wiki pages `Guide-EN.md`, `Guide-DE.md`,
`Guide-FR.md`. The original sources remain untouched. The publisher also rewrites
source-relative technical-reference links in the long guides to stable
repository URLs so they resolve after Wiki publication.

Verify all 24 pages, the navigation and three long-form guides on the live Wiki.
Pushing `main` by itself does not publish Wiki content.

The 24 EU Quick Starts share identical executable command sequences and
structural checks; their translations have not undergone external native-speaker
technical review. Credentials, site-local inventory and evidence must never
be published to the Wiki.
