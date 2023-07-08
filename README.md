# vimeotools
These are Python Tools for Vimeo, using the Vimeo API and the official PyVimeo Python package.

This package is aimed at being more convenient than using the Vimeo API or PyVimeo directly:
it provides the classes:

- **VimeoConnection**
- **VimeoData**
- **VimeoVideo**
- **VimeoShowcase** (Album)
- **VimeoFolder** (project) 

which invoke the API for you. So you don't have to worry about the intricacies of the data structure or the URIs to use for specific queries or actions.

These classes also store the data internally once they have retrieved them from Vimeo, so as to avoid unnecessary requests if data are queried multiple times. If an instance changes data, the internal data representation is updated accordingly. 

It is of course possible to re-query (*refresh*) the data via the API.

You can also opt to create or set an object in live mode, so everytime a property is queried, the appropriate request is made on Vimeo first.
