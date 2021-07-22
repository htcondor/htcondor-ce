HTCondor-CE Documentation
=========================

[![Deploy static MkDocs pages](https://github.com/htcondor/htcondor-ce/actions/workflows/deploy-mkdocs.yaml/badge.svg?branch=docs)](https://github.com/htcondor/htcondor-ce/actions/workflows/deploy-mkdocs.yaml) [![Valdate static MkDocs pages](https://github.com/htcondor/htcondor-ce/actions/workflows/validate-mkdocs.yml/badge.svg?branch=docs)](https://github.com/htcondor/htcondor-ce/actions/workflows/validate-mkdocs.yml)

---

Source documents and [MkDocs](https://www.mkdocs.org/) configuration for <http://htcondor-ce.org> served by
[GitHub Pages](https://pages.github.com/).
The documentation is built using the [mkdocs-material container](https://hub.docker.com/r/squidfunk/mkdocs-material/)
with a [GitHub Action](https://github.com/htcondor/htcondor-ce/blob/docs/.github/workflows/deploy-mkdocs.yaml).

Previewing the Pages
--------------------

To preview the pages, start a MkDocs development server.
The development server will automatically detect any content changes and make them viewable in your browser.

1. `cd` into the directory containing the local clone of your GitHub fork

1. Start a MkDocs development server to preview your changes:

        $ docker run --rm -p 8000:8000 -v ${PWD}:/docs squidfunk/mkdocs-material:7.1.0

    To preview your changes visit `localhost:8000` in the browser of your choice.
    The server can be stopped with `Ctrl-C`.

Contributing Documentation
--------------------------

To contribute changes to the documentation, please submit a
[pull request](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests).
The reason for this is two-fold: document and link validation CI checks are run on pull requests and anything pushed to
the `docs` branch is immediately published to <http://htcondor-ce.org>.
